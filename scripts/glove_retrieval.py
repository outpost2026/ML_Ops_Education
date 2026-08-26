"""
Hybrid Retrieval Pipeline — Varianta 2: GloVe Pre-trained + BM25 + RRF
Pouziva predtrenovane GloVe vektory z Wikipedia/Gigaword

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
MODEL_PATH = os.path.join(
    BASE, "..", "_stahovani", "models", "glove-wiki-gigaword-100.model"
)
os.makedirs(RESULTS, exist_ok=True)


# ============================================================
# 1. TOKENIZER
# ============================================================


def tokenize(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9à-ž\-\_]+", " ", text)
    return [t for t in text.split() if len(t) >= 2]


# ============================================================
# 2. BM25
# ============================================================


class BM25:
    def __init__(self, k1=1.5, b=0.75):
        self.k1 = k1
        self.b = b

    def fit(self, documents):
        self.docs = documents
        self.doc_tokens = [
            tokenize(doc) if isinstance(doc, str) else doc for doc in documents
        ]
        self.doc_lens = [len(d) for d in self.doc_tokens]
        self.avg_dl = sum(self.doc_lens) / len(self.doc_lens) if self.doc_lens else 1
        self.N = len(documents)
        self.df = Counter()
        self.inverted_index = defaultdict(list)
        for i, tokens in enumerate(self.doc_tokens):
            for t in set(tokens):
                self.df[t] += 1
                tf = tokens.count(t)
                self.inverted_index[t].append((i, tf))
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
        query_tokens = tokenize(query) if isinstance(query, str) else query
        scores = []
        for i in range(self.N):
            score = self._score_doc(query_tokens, i)
            scores.append((i, score))
        scores.sort(key=lambda x: -x[1])
        return scores[:top_k]


# ============================================================
# 3. GLOVE DENSE RETRIEVAL
# ============================================================


class GloVeDense:
    """Dense retrieval using pre-trained GloVe embeddings."""

    def __init__(self, model_path=None):
        self.model = None
        self.model_path = model_path or MODEL_PATH
        self.vector_size = 100
        self.doc_vectors = None

    def fit(self, documents):
        """Build document vectors from pre-trained GloVe."""
        print("  Loading GloVe model from: %s" % self.model_path)

        from gensim.models import KeyedVectors

        self.model = KeyedVectors.load(self.model_path)
        self.vector_size = self.model.vector_size
        print(
            "  Vocabulary: %d words, vector_size: %d"
            % (len(self.model), self.vector_size)
        )

        # Build document vectors
        self.doc_vectors = np.zeros(
            (len(documents), self.vector_size), dtype=np.float32
        )
        oov_count = 0
        total_count = 0

        for i, doc in enumerate(documents):
            tokens = tokenize(doc) if isinstance(doc, str) else doc
            word_vecs = []
            for t in tokens:
                total_count += 1
                if t in self.model:
                    word_vecs.append(self.model[t])
                else:
                    oov_count += 1
            if word_vecs:
                self.doc_vectors[i] = np.mean(word_vecs, axis=0)
            # L2 normalize
            norm = np.linalg.norm(self.doc_vectors[i])
            if norm > 0:
                self.doc_vectors[i] /= norm

        print(
            "  OOV rate: %.1f%% (%d/%d)"
            % (
                oov_count / total_count * 100 if total_count > 0 else 0,
                oov_count,
                total_count,
            )
        )
        return self

    def search(self, query, top_k=5):
        """Search with a string query."""
        query_tokens = tokenize(query) if isinstance(query, str) else query

        # Encode query
        word_vecs = [self.model[t] for t in query_tokens if t in self.model]
        if not word_vecs:
            return [(i, 0.0) for i in range(len(self.doc_vectors))][:top_k]

        q_vec = np.mean(word_vecs, axis=0)
        norm = np.linalg.norm(q_vec)
        if norm > 0:
            q_vec /= norm

        # Cosine similarity
        scores = self.doc_vectors @ q_vec

        top_idx = np.argsort(-scores)[:top_k]
        return [(int(idx), float(scores[idx])) for idx in top_idx]


# ============================================================
# 4. RRF FUSION
# ============================================================


def rrf_fusion(results_list, k=60):
    scores = defaultdict(float)
    for results in results_list:
        for rank, (doc_idx, _) in enumerate(results, 1):
            scores[doc_idx] += 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda x: -x[1])


# ============================================================
# 5. SEARCHABLE TEXT BUILDER
# ============================================================


def build_searchable_text(entry):
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


# ============================================================
# 6. SEQUENCEMATCHER BASELINE
# ============================================================


def fuzzy_score(query, text):
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
    scores = [(i, fuzzy_score(query, txt)) for i, txt in enumerate(texts)]
    scores.sort(key=lambda x: -x[1])
    return scores[:top_k]


# ============================================================
# 7. METRICS
# ============================================================


def compute_metrics(results, expected_set):
    top3 = [r[0] for r in results[:3]]
    top5 = [r[0] for r in results[:5]]
    hits_top3 = len(expected_set & set(top3))
    precision_at_3 = hits_top3 / min(3, len(expected_set)) if expected_set else 0
    hits_top5 = len(expected_set & set(top5))
    recall = hits_top5 / len(expected_set) if expected_set else 0
    mrr = 0
    for rank, (doc_idx, _) in enumerate(results, 1):
        if doc_idx in expected_set:
            mrr = 1.0 / rank
            break
    return {"precision_at_3": precision_at_3, "recall": recall, "mrr": mrr}


# ============================================================
# 8. MAIN
# ============================================================


def load_jsonl(path):
    entries = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))
    return entries


def load_queries(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main():
    print("=" * 70)
    print("GLOVE + BM25 + RRF — Diff Test")
    print("=" * 70)

    entries = load_jsonl(os.path.join(DATA, "gt_full.jsonl"))
    queries = load_queries(os.path.join(DATA, "test_queries.json"))
    print("Loaded %d entries, %d queries" % (len(entries), len(queries)))

    texts = [build_searchable_text(e) for e in entries]
    id_to_idx = {e["id"]: i for i, e in enumerate(entries)}

    # Build indices
    print("\nBuilding indices...")
    t0 = time.time()
    bm25 = BM25(k1=1.5, b=0.75)
    bm25.fit(texts)
    t_bm25 = time.time() - t0
    print("  BM25: %.3f s" % t_bm25)

    t0 = time.time()
    glove = GloVeDense()
    glove.fit(texts)
    t_glove = time.time() - t0
    print("  GloVe: %.3f s" % t_glove)

    # Run queries
    print("\nRunning queries...")
    results = {
        "sequence_matcher": [],
        "bm25": [],
        "glove": [],
        "hybrid_rrf": [],
    }

    for q in queries:
        expected_idxs = set(id_to_idx[eid] for eid in q["expected"] if eid in id_to_idx)

        for lang in ["cz", "en"]:
            query = q["query_%s" % lang]

            # SequenceMatcher
            res_fuzzy = search_fuzzy(query, texts, top_k=5)
            results["sequence_matcher"].append(
                {
                    "qid": q["id"],
                    "lang": lang,
                    **compute_metrics(res_fuzzy, expected_idxs),
                }
            )

            # BM25
            res_bm25 = bm25.search(query, top_k=5)
            results["bm25"].append(
                {
                    "qid": q["id"],
                    "lang": lang,
                    **compute_metrics(res_bm25, expected_idxs),
                }
            )

            # GloVe
            res_glove = glove.search(query, top_k=5)
            results["glove"].append(
                {
                    "qid": q["id"],
                    "lang": lang,
                    **compute_metrics(res_glove, expected_idxs),
                }
            )

            # Hybrid RRF
            res_rrf = rrf_fusion([res_bm25, res_glove], k=60)
            results["hybrid_rrf"].append(
                {
                    "qid": q["id"],
                    "lang": lang,
                    **compute_metrics(res_rrf, expected_idxs),
                }
            )

    # Aggregate
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)

    summary = {}
    for method, data in results.items():
        n = len(data)
        summary[method] = {
            "precision_at_3": round(sum(r["precision_at_3"] for r in data) / n, 4),
            "recall": round(sum(r["recall"] for r in data) / n, 4),
            "mrr": round(sum(r["mrr"] for r in data) / n, 4),
            "hits": sum(1 for r in data if r["mrr"] > 0),
            "total": n,
        }

    methods = ["sequence_matcher", "bm25", "glove", "hybrid_rrf"]
    labels = ["SequenceMatcher", "BM25", "GloVe", "Hybrid RRF"]

    print("\n%-20s %12s %12s %12s %12s" % ("Method", "Prec@3", "Recall", "MRR", "Hits"))
    print("-" * 70)
    for method, label in zip(methods, labels):
        s = summary[method]
        print(
            "%-20s %12.4f %12.4f %12.4f %5d/%d"
            % (label, s["precision_at_3"], s["recall"], s["mrr"], s["hits"], s["total"])
        )

    # Delta vs baseline
    baseline = summary["sequence_matcher"]
    print("\n%-20s %12s %12s %12s" % ("Delta vs SeqMatcher", "Prec@3", "Recall", "MRR"))
    print("-" * 55)
    for method, label in zip(methods[1:], labels[1:]):
        s = summary[method]
        d_p3 = ((s["precision_at_3"] / baseline["precision_at_3"]) - 1) * 100
        d_r = ((s["recall"] / baseline["recall"]) - 1) * 100
        d_mrr = ((s["mrr"] / baseline["mrr"]) - 1) * 100
        print("%-20s %+11.1f%% %+11.1f%% %+11.1f%%" % (label, d_p3, d_r, d_mrr))

    # Head-to-head
    print("\n" + "=" * 70)
    print("HEAD-TO-HEAD (MRR wins)")
    print("=" * 70)
    for method, label in zip(methods[1:], labels[1:]):
        wins = losses = ties = 0
        for i in range(len(results["sequence_matcher"])):
            m_base = results["sequence_matcher"][i]["mrr"]
            m_new = results[method][i]["mrr"]
            if m_new > m_base:
                wins += 1
            elif m_new < m_base:
                losses += 1
            else:
                ties += 1
        print("%-20s vs SequenceMatcher: %dW / %dL / %dT" % (label, wins, losses, ties))

    # Save
    output = {
        "summary": summary,
        "config": {
            "glove_model": "glove-wiki-gigaword-100",
            "glove_vocab": 400000,
            "glove_dims": 100,
            "bm25_k1": 1.5,
            "bm25_b": 0.75,
            "rrf_k": 60,
        },
    }
    out_path = os.path.join(RESULTS, "glove_benchmark.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print("\nSaved: %s" % out_path)


if __name__ == "__main__":
    main()
