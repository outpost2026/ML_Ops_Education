"""
Hybrid Retrieval Pipeline — Cesta A: Zero-Download (numpy only)
BM25 + TF-IDF + RRF Fusion

Build: 2026-08-26 | Author: outpost2026
"""

import json
import math
import os
import re
import sys
import time
from collections import Counter, defaultdict
from difflib import SequenceMatcher

import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "..", "data")
RESULTS = os.path.join(BASE, "..", "results")
os.makedirs(RESULTS, exist_ok=True)


# ============================================================
# 1. TOKENIZER
# ============================================================


def tokenize(text):
    """Simple whitespace + lowercase tokenizer with min length 2."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9à-ž\-\_]+", " ", text)
    tokens = [t for t in text.split() if len(t) >= 2]
    return tokens


# ============================================================
# 2. BM25 (from Python stdlib)
# ============================================================


class BM25:
    """BM25 retrieval model implemented from Python stdlib only."""

    def __init__(self, k1=1.5, b=0.75):
        self.k1 = k1
        self.b = b
        self.docs = []
        self.doc_tokens = []
        self.doc_lens = []
        self.avg_dl = 0
        self.df = Counter()
        self.N = 0
        self.inverted_index = defaultdict(list)

    def fit(self, documents):
        """Index a list of tokenized documents."""
        self.docs = documents
        self.doc_tokens = [
            tokenize(doc) if isinstance(doc, str) else doc for doc in documents
        ]
        self.doc_lens = [len(d) for d in self.doc_tokens]
        self.avg_dl = sum(self.doc_lens) / len(self.doc_lens) if self.doc_lens else 1
        self.N = len(documents)

        for i, tokens in enumerate(self.doc_tokens):
            unique_terms = set(tokens)
            for term in unique_terms:
                self.df[term] += 1
                tf = tokens.count(term)
                self.inverted_index[term].append((i, tf))

        return self

    def _idf(self, term):
        if term not in self.df:
            return 0
        df = self.df[term]
        return math.log((self.N - df + 0.5) / (df + 0.5) + 1)

    def _score_doc(self, query_tokens, doc_idx):
        score = 0.0
        dl = self.doc_lens[doc_idx]
        for term in query_tokens:
            if term not in self.inverted_index:
                continue
            for idx, tf in self.inverted_index[term]:
                if idx == doc_idx:
                    idf = self._idf(term)
                    numerator = tf * (self.k1 + 1)
                    denominator = tf + self.k1 * (
                        1 - self.b + self.b * dl / self.avg_dl
                    )
                    score += idf * numerator / denominator
                    break
        return score

    def search(self, query, top_k=5):
        """Search with a string query. Returns list of (doc_idx, score)."""
        query_tokens = tokenize(query) if isinstance(query, str) else query
        scores = []
        for i in range(self.N):
            score = self._score_doc(query_tokens, i)
            scores.append((i, score))
        scores.sort(key=lambda x: -x[1])
        return scores[:top_k]


# ============================================================
# 3. TF-IDF (numpy only)
# ============================================================


class TFIDF:
    """TF-IDF retrieval model using numpy for dense vector operations."""

    def __init__(self):
        self.vocab = {}
        self.vocab_inv = {}
        self.idf = None
        self.matrix = None
        self.doc_ids = []

    def fit(self, documents, doc_ids=None):
        """Build TF-IDF matrix from documents."""
        self.doc_ids = doc_ids or list(range(len(documents)))

        # Tokenize all documents
        tokenized = [
            tokenize(doc) if isinstance(doc, str) else doc for doc in documents
        ]

        # Build vocabulary
        all_terms = set()
        for tokens in tokenized:
            all_terms.update(tokens)
        sorted_terms = sorted(all_terms)
        self.vocab = {t: i for i, t in enumerate(sorted_terms)}
        self.vocab_inv = {i: t for t, i in self.vocab.items()}

        V = len(self.vocab)
        N = len(documents)

        # Compute IDF: log((N+1)/(df+1)) + 1
        df = np.zeros(V)
        for tokens in tokenized:
            for term in set(tokens):
                if term in self.vocab:
                    df[self.vocab[term]] += 1
        self.idf = np.log((N + 1) / (df + 1)) + 1

        # Build TF-IDF matrix (N x V)
        self.matrix = np.zeros((N, V), dtype=np.float32)
        for i, tokens in enumerate(tokenized):
            tf = Counter(tokens)
            for term, count in tf.items():
                if term in self.vocab:
                    j = self.vocab[term]
                    self.matrix[i, j] = count * self.idf[j]
            # L2 normalize
            norm = np.linalg.norm(self.matrix[i])
            if norm > 0:
                self.matrix[i] /= norm

        return self

    def search(self, query, top_k=5):
        """Search with a string query. Returns list of (doc_idx, score)."""
        query_tokens = tokenize(query) if isinstance(query, str) else query

        # Encode query
        q_vec = np.zeros(len(self.vocab), dtype=np.float32)
        for term in query_tokens:
            if term in self.vocab:
                j = self.vocab[term]
                q_vec[j] = self.idf[j]
        # L2 normalize query
        norm = np.linalg.norm(q_vec)
        if norm > 0:
            q_vec /= norm

        # Cosine similarity (dot product on normalized vectors)
        scores = self.matrix @ q_vec

        # Get top-k
        top_idx = np.argsort(-scores)[:top_k]
        return [(int(idx), float(scores[idx])) for idx in top_idx]


# ============================================================
# 4. RRF FUSION
# ============================================================


def rrf_fusion(results_list, k=60):
    """Reciprocal Rank Fusion from multiple ranked lists.

    Args:
        results_list: list of lists, each containing (doc_idx, score) tuples
        k: RRF parameter (default 60, lower = favor top-1)

    Returns:
        Merged list of (doc_idx, rrf_score) sorted descending
    """
    scores = defaultdict(float)
    for results in results_list:
        for rank, (doc_idx, _) in enumerate(results, 1):
            scores[doc_idx] += 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda x: -x[1])


# ============================================================
# 5. SEARCHABLE TEXT BUILDERS
# ============================================================


def build_searchable_text(entry):
    """Build searchable text from JSONL entry."""
    parts = []
    for key in [
        "symptom",
        "root_cause",
        "fix",
        "server",
        "status",
        "typ",
        "tags",
        "rule",
    ]:
        val = entry.get(key, "")
        if isinstance(val, list):
            val = " ".join(str(x) for x in val)
        parts.append(str(val))
    return " ".join(parts)


def build_searchable_text_v2(entry):
    """Build searchable text from v2 markdown parsed entry."""
    parts = []
    for key in ["title", "symptom", "root_cause", "fix", "server", "status"]:
        val = entry.get(key, "")
        if isinstance(val, list):
            val = " ".join(str(x) for x in val)
        parts.append(str(val))
    return " ".join(parts)


# ============================================================
# 6. SEQUENCEMATCHER BASELINE
# ============================================================


def fuzzy_score(query, text):
    """SequenceMatcher fuzzy scoring (baseline)."""
    q = query.lower()
    t = text.lower()
    if q in t:
        return 1.0
    words = q.split()
    if len(words) > 1:
        keyword_score = sum(1 for w in words if w in t) / len(words)
    else:
        keyword_score = 0.0
    seq_score = SequenceMatcher(None, q, t[:200]).ratio()
    return max(keyword_score, seq_score)


def search_fuzzy(query, texts, top_k=5):
    """Baseline fuzzy search using SequenceMatcher."""
    scores = [(i, fuzzy_score(query, txt)) for i, txt in enumerate(texts)]
    scores.sort(key=lambda x: -x[1])
    return scores[:top_k]


# ============================================================
# 7. METRICS
# ============================================================


def compute_metrics(results, expected_set, all_results=None):
    """Compute Precision@3, Recall, MRR for a single query."""
    top3 = [r[0] for r in results[:3]]
    top5 = [r[0] for r in results[:5]]

    # Precision@3
    hits_top3 = len(expected_set & set(top3))
    precision_at_3 = hits_top3 / min(3, len(expected_set)) if expected_set else 0

    # Recall
    hits_top5 = len(expected_set & set(top5))
    recall = hits_top5 / len(expected_set) if expected_set else 0

    # MRR
    mrr = 0
    for rank, (doc_idx, _) in enumerate(results, 1):
        if doc_idx in expected_set:
            mrr = 1.0 / rank
            break

    return {
        "precision_at_3": precision_at_3,
        "recall": recall,
        "mrr": mrr,
        "top3": top3,
        "top5": top5,
    }


# ============================================================
# 8. MAIN PIPELINE
# ============================================================


def load_jsonl(path):
    entries = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def load_queries(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main():
    print("=" * 70)
    print("HYBRID RETRIEVAL PIPELINE — Cesta A: Zero-Download")
    print("BM25 + TF-IDF + RRF Fusion vs SequenceMatcher Baseline")
    print("=" * 70)

    # Load data
    jsonl_path = os.path.join(DATA, "gt_full.jsonl")
    queries_path = os.path.join(DATA, "test_queries.json")

    entries = load_jsonl(jsonl_path)
    queries = load_queries(queries_path)

    print("\nLoaded %d entries, %d queries" % (len(entries), len(queries)))

    # Build searchable texts
    texts = [build_searchable_text(e) for e in entries]
    doc_ids = [e["id"] for e in entries]

    # Build index for ID lookup
    id_to_idx = {eid: i for i, eid in enumerate(doc_ids)}

    # ============================================================
    # BUILD RETRIEVAL MODELS
    # ============================================================
    print("\nBuilding indices...")

    t0 = time.time()
    bm25 = BM25(k1=1.5, b=0.75)
    bm25.fit(texts)
    t_bm25 = time.time() - t0
    print("  BM25 index: %.3f s" % t_bm25)

    t0 = time.time()
    tfidf = TFIDF()
    tfidf.fit(texts, doc_ids)
    t_tfidf = time.time() - t0
    print(
        "  TF-IDF matrix: %.3f s (%d x %d)"
        % (t_tfidf, tfidf.matrix.shape[0], tfidf.matrix.shape[1])
    )

    # ============================================================
    # RUN QUERIES
    # ============================================================
    print("\nRunning queries...")
    results_by_method = {
        "sequence_matcher": [],
        "bm25": [],
        "tfidf": [],
        "hybrid_rrf": [],
    }

    for q in queries:
        qid = q["id"]
        expected_ids = set(q["expected"])
        expected_idxs = set()
        for eid in expected_ids:
            if eid in id_to_idx:
                expected_idxs.add(id_to_idx[eid])

        for lang in ["cz", "en"]:
            query = q["query_%s" % lang]

            # SequenceMatcher baseline
            res_fuzzy = search_fuzzy(query, texts, top_k=5)
            metrics_fuzzy = compute_metrics(res_fuzzy, expected_idxs)
            results_by_method["sequence_matcher"].append(
                {
                    "qid": qid,
                    "lang": lang,
                    "query": query,
                    "expected": list(expected_idxs),
                    **metrics_fuzzy,
                }
            )

            # BM25
            res_bm25 = bm25.search(query, top_k=5)
            metrics_bm25 = compute_metrics(res_bm25, expected_idxs)
            results_by_method["bm25"].append(
                {
                    "qid": qid,
                    "lang": lang,
                    "query": query,
                    "expected": list(expected_idxs),
                    **metrics_bm25,
                }
            )

            # TF-IDF
            res_tfidf = tfidf.search(query, top_k=5)
            metrics_tfidf = compute_metrics(res_tfidf, expected_idxs)
            results_by_method["tfidf"].append(
                {
                    "qid": qid,
                    "lang": lang,
                    "query": query,
                    "expected": list(expected_idxs),
                    **metrics_tfidf,
                }
            )

            # Hybrid RRF (BM25 + TF-IDF)
            res_rrf = rrf_fusion([res_bm25, res_tfidf], k=60)
            metrics_rrf = compute_metrics(res_rrf, expected_idxs)
            results_by_method["hybrid_rrf"].append(
                {
                    "qid": qid,
                    "lang": lang,
                    "query": query,
                    "expected": list(expected_idxs),
                    **metrics_rrf,
                }
            )

    # ============================================================
    # AGGREGATE RESULTS
    # ============================================================
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)

    summary = {}
    for method, results in results_by_method.items():
        n = len(results)
        avg_p3 = sum(r["precision_at_3"] for r in results) / n
        avg_r = sum(r["recall"] for r in results) / n
        avg_mrr = sum(r["mrr"] for r in results) / n
        wins = sum(1 for r in results if r["mrr"] > 0)
        summary[method] = {
            "precision_at_3": round(avg_p3, 4),
            "recall": round(avg_r, 4),
            "mrr": round(avg_mrr, 4),
            "queries_with_hit": wins,
            "total_queries": n,
        }

    # Print comparison
    methods = ["sequence_matcher", "bm25", "tfidf", "hybrid_rrf"]
    labels = ["SequenceMatcher", "BM25", "TF-IDF", "Hybrid RRF"]

    print("\n%-20s %12s %12s %12s %12s" % ("Method", "Prec@3", "Recall", "MRR", "Hits"))
    print("-" * 70)
    for method, label in zip(methods, labels):
        s = summary[method]
        print(
            "%-20s %12.4f %12.4f %12.4f %5d/%d"
            % (
                label,
                s["precision_at_3"],
                s["recall"],
                s["mrr"],
                s["queries_with_hit"],
                s["total_queries"],
            )
        )

    # Delta vs baseline
    baseline_mrr = summary["sequence_matcher"]["mrr"]
    print("\n%20s %12s %12s %12s" % ("Delta vs baseline", "", "", "MRR"))
    print("-" * 70)
    for method, label in zip(methods[1:], labels[1:]):
        s = summary[method]
        delta = ((s["mrr"] / baseline_mrr) - 1) * 100 if baseline_mrr > 0 else 0
        print("%-20s %12s %12s %+11.1f%%" % (label, "", "", delta))

    # ============================================================
    # HEAD-TO-HEAD WINS
    # ============================================================
    print("\n" + "=" * 70)
    print("HEAD-TO-HEAD (MRR wins)")
    print("=" * 70)

    for method, label in zip(methods[1:], labels[1:]):
        wins = 0
        losses = 0
        ties = 0
        for i in range(len(results_by_method["sequence_matcher"])):
            mrr_base = results_by_method["sequence_matcher"][i]["mrr"]
            mrr_new = results_by_method[method][i]["mrr"]
            if mrr_new > mrr_base:
                wins += 1
            elif mrr_new < mrr_base:
                losses += 1
            else:
                ties += 1
        print("%-20s vs SequenceMatcher: %dW / %dL / %dT" % (label, wins, losses, ties))

    # ============================================================
    # SAVE RESULTS
    # ============================================================
    output = {
        "summary": summary,
        "per_query": results_by_method,
        "config": {
            "bm25_k1": 1.5,
            "bm25_b": 0.75,
            "rrf_k": 60,
            "entries": len(entries),
            "queries": len(queries),
        },
    }

    out_path = os.path.join(RESULTS, "hybrid_benchmark.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print("\nResults saved to: %s" % out_path)
    print("=" * 70)


if __name__ == "__main__":
    main()
