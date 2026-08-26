"""
Retrieval Pipeline — Varianta 7-9: SVD + Query Expansion + Weighted RRF
Kombinace: scikit-learn TF-IDF/SVD + synonymní slovník + vážená fúze

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
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity

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
# 3. SEQUENCEMATCHER
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
# 4. TF-IDF + SVD (Latent Semantic Analysis)
# ============================================================


class TFIDF_SVD:
    """TF-IDF + TruncatedSVD pro latentní sémantiku."""

    def __init__(self, n_components=50):
        self.n_components = n_components
        self.vectorizer = TfidfVectorizer(
            analyzer="word",
            tokenizer=lambda x: x,
            preprocessor=lambda x: x,
            token_pattern=None,
            max_features=5000,
        )
        self.svd = TruncatedSVD(n_components=n_components, random_state=42)
        self.doc_vectors = None

    def fit(self, documents):
        tokenized = [
            tokenize(doc) if isinstance(doc, str) else doc for doc in documents
        ]
        tfidf_matrix = self.vectorizer.fit_transform(tokenized)
        print(
            "  TF-IDF matrix: %s (vocab: %d)"
            % (str(tfidf_matrix.shape), len(self.vectorizer.vocabulary_))
        )

        self.doc_vectors = self.svd.fit_transform(tfidf_matrix)
        # L2 normalize
        norms = np.linalg.norm(self.doc_vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1
        self.doc_vectors = self.doc_vectors / norms

        explained = self.svd.explained_variance_ratio_.sum()
        print("  SVD explained variance: %.1f%%" % (explained * 100))
        return self

    def search(self, query, top_k=5):
        query_tokens = tokenize(query) if isinstance(query, str) else query
        q_tfidf = self.vectorizer.transform([query_tokens])
        q_vec = self.svd.transform(q_tfidf)
        # L2 normalize
        norm = np.linalg.norm(q_vec)
        if norm > 0:
            q_vec = q_vec / norm

        scores = self.doc_vectors @ q_vec.T
        scores = scores.flatten()
        top_idx = np.argsort(-scores)[:top_k]
        return [(int(idx), float(scores[idx])) for idx in top_idx]


# ============================================================
# 5. QUERY EXPANSION
# ============================================================

SYNONYM_MAP = {
    "timeout": ["deadlock", "zaseknuti", "time-out", "hang", "freeze"],
    "cache": ["invalidace", "vyprseni", "stale", "refresh"],
    "encoding": ["kodovani", "utf-8", "cp1250", "ascii", "unicode"],
    "error": ["chyba", "exception", "selhani", "bug"],
    "server": ["sluzba", "service", "daemon", "proces"],
    "config": ["konfigurace", "nastaveni", "settings", "setup"],
    "memory": ["pamet", "ram", "spotreba", "allocation"],
    "network": ["sit", "pripojeni", "connection", "internet"],
    "database": ["db", "databaze", "uloziste", "storage"],
    "api": ["rozhrani", "endpoint", "volani", "request"],
    "browser": ["prohlizec", "chromium", "playwright", "puppeteer"],
    "git": ["verzovani", "repozitar", "repository", "commit"],
    "docker": ["kontejner", "container", "image", "build"],
    "test": ["testovani", "testing", "overeni", "validation"],
    "deploy": ["nasazeni", "deployment", "release", "publish"],
    "log": ["logging", "zaznam", "monitoring", "trace"],
    "auth": ["autentizace", "overeni", "login", "token"],
    "permission": ["oprávneni", "pristup", "access", "rights"],
    "file": ["soubor", "dokument", "data", "content"],
    "process": ["proces", "vlakno", "thread", "task"],
}


def expand_query(query):
    """Rozšíří query o synonymní termíny."""
    tokens = tokenize(query)
    expanded = list(tokens)
    for t in tokens:
        if t in SYNONYM_MAP:
            expanded.extend(SYNONYM_MAP[t][:2])  # max 2 synonyma
    return expanded


def search_fuzzy_expanded(query, texts, top_k=5):
    """SequenceMatcher s rozšířeným query."""
    expanded = expand_query(query)
    expanded_text = " ".join(expanded)
    scores = []
    for i, txt in enumerate(texts):
        # Kombinace původního + rozšířeného skóre
        score_orig = fuzzy_score(query, txt)
        score_exp = fuzzy_score(expanded_text, txt)
        scores.append((i, max(score_orig, score_exp * 0.9)))
    scores.sort(key=lambda x: -x[1])
    return scores[:top_k]


def search_bm25_expanded(bm25, query, top_k=5):
    """BM25 s rozšířeným query."""
    expanded = expand_query(query)
    return bm25.search(expanded, top_k)


# ============================================================
# 6. RRF FUSION (standardní + weighted)
# ============================================================


def rrf_fusion(results_list, k=60):
    scores = defaultdict(float)
    for results in results_list:
        for rank, (doc_idx, _) in enumerate(results, 1):
            scores[doc_idx] += 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda x: -x[1])


def weighted_rrf(results_list, weights, k=60):
    """Weighted RRF: každý výsledek má svou váhu."""
    scores = defaultdict(float)
    for results, weight in zip(results_list, weights):
        for rank, (doc_idx, _) in enumerate(results, 1):
            scores[doc_idx] += weight / (k + rank)
    return sorted(scores.items(), key=lambda x: -x[1])


# ============================================================
# 7. SEARCHABLE TEXT BUILDER
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
# 8. METRICS
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
# 9. MAIN
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
    print("VARIANTA 7-9: SVD + Query Expansion + Weighted RRF")
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
    print("  BM25: %.3f s" % (time.time() - t0))

    t0 = time.time()
    svd = TFIDF_SVD(n_components=50)
    svd.fit(texts)
    print("  TF-IDF+SVD: %.3f s" % (time.time() - t0))

    # Run queries
    print("\nRunning queries...")
    methods = {
        "sequence_matcher": [],
        "bm25": [],
        "svd": [],
        "bm25_seq_rrf": [],
        "bm25_expanded": [],
        "bm25_exp_seq_rrf": [],
        "weighted_rrf": [],
    }

    for q in queries:
        expected_idxs = set(id_to_idx[eid] for eid in q["expected"] if eid in id_to_idx)

        for lang in ["cz", "en"]:
            query = q["query_%s" % lang]

            # SequenceMatcher
            res_seq = search_fuzzy(query, texts, top_k=5)
            methods["sequence_matcher"].append(
                {
                    "qid": q["id"],
                    "lang": lang,
                    **compute_metrics(res_seq, expected_idxs),
                }
            )

            # BM25
            res_bm25 = bm25.search(query, top_k=5)
            methods["bm25"].append(
                {
                    "qid": q["id"],
                    "lang": lang,
                    **compute_metrics(res_bm25, expected_idxs),
                }
            )

            # SVD
            res_svd = svd.search(query, top_k=5)
            methods["svd"].append(
                {
                    "qid": q["id"],
                    "lang": lang,
                    **compute_metrics(res_svd, expected_idxs),
                }
            )

            # BM25 + Seq RRF (baseline vítěz)
            res_bm25_seq = rrf_fusion([res_bm25, res_seq], k=60)
            methods["bm25_seq_rrf"].append(
                {
                    "qid": q["id"],
                    "lang": lang,
                    **compute_metrics(res_bm25_seq, expected_idxs),
                }
            )

            # BM25 + query expansion
            res_bm25_exp = search_bm25_expanded(bm25, query, top_k=5)
            methods["bm25_expanded"].append(
                {
                    "qid": q["id"],
                    "lang": lang,
                    **compute_metrics(res_bm25_exp, expected_idxs),
                }
            )

            # BM25 expanded + Seq RRF
            res_exp_seq = rrf_fusion([res_bm25_exp, res_seq], k=60)
            methods["bm25_exp_seq_rrf"].append(
                {
                    "qid": q["id"],
                    "lang": lang,
                    **compute_metrics(res_exp_seq, expected_idxs),
                }
            )

            # Weighted RRF (BM25=0.6, Seq=0.4)
            res_weighted = weighted_rrf([res_bm25, res_seq], [0.6, 0.4], k=60)
            methods["weighted_rrf"].append(
                {
                    "qid": q["id"],
                    "lang": lang,
                    **compute_metrics(res_weighted, expected_idxs),
                }
            )

    # Aggregate
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)

    summary = {}
    for method, data in methods.items():
        n = len(data)
        summary[method] = {
            "precision_at_3": round(sum(r["precision_at_3"] for r in data) / n, 4),
            "recall": round(sum(r["recall"] for r in data) / n, 4),
            "mrr": round(sum(r["mrr"] for r in data) / n, 4),
            "hits": sum(1 for r in data if r["mrr"] > 0),
            "total": n,
        }

    labels = {
        "sequence_matcher": "SequenceMatcher",
        "bm25": "BM25",
        "svd": "TF-IDF+SVD",
        "bm25_seq_rrf": "BM25+Seq RRF",
        "bm25_expanded": "BM25+Expand",
        "bm25_exp_seq_rrf": "Exp+Seq RRF",
        "weighted_rrf": "Weighted RRF",
    }

    print("\n%-22s %10s %10s %10s %10s" % ("Method", "Prec@3", "Recall", "MRR", "Hits"))
    print("-" * 65)
    for method in methods:
        s = summary[method]
        print(
            "%-22s %10.4f %10.4f %10.4f %7d/%d"
            % (
                labels[method],
                s["precision_at_3"],
                s["recall"],
                s["mrr"],
                s["hits"],
                s["total"],
            )
        )

    # Delta vs baseline
    baseline = summary["sequence_matcher"]
    print("\n%-22s %10s %10s %10s" % ("Delta vs SeqMatcher", "Prec@3", "Recall", "MRR"))
    print("-" * 55)
    for method in list(methods.keys())[1:]:
        s = summary[method]
        d_p3 = ((s["precision_at_3"] / baseline["precision_at_3"]) - 1) * 100
        d_r = ((s["recall"] / baseline["recall"]) - 1) * 100
        d_mrr = ((s["mrr"] / baseline["mrr"]) - 1) * 100
        print("%-22s %+9.1f%% %+9.1f%% %+9.1f%%" % (labels[method], d_p3, d_r, d_mrr))

    # Best
    best = max(summary.items(), key=lambda x: x[1]["mrr"])
    print(
        "\nBest: %s (MRR=%.4f, Recall=%.4f, Hits=%d/%d)"
        % (
            labels[best[0]],
            best[1]["mrr"],
            best[1]["recall"],
            best[1]["hits"],
            best[1]["total"],
        )
    )

    # Save
    output = {"summary": summary, "config": {"svd_components": 50, "rrf_k": 60}}
    out_path = os.path.join(RESULTS, "svd_expansion_benchmark.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print("\nSaved: %s" % out_path)


if __name__ == "__main__":
    main()
