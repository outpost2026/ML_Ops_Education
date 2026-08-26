"""
Hybrid Retrieval Pipeline — Varianta A+B
Kombinace: BM25 + SequenceMatcher + Ensemble BM25 + RRF

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
# 6. METRICS
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
# 7. MAIN
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
    print("VARIANTA A+B: BM25 + SequenceMatcher + Ensemble + RRF")
    print("=" * 70)

    entries = load_jsonl(os.path.join(DATA, "gt_full.jsonl"))
    queries = load_queries(os.path.join(DATA, "test_queries.json"))
    print("Loaded %d entries, %d queries" % (len(entries), len(queries)))

    texts = [build_searchable_text(e) for e in entries]
    id_to_idx = {e["id"]: i for i, e in enumerate(entries)}

    # Build all BM25 variants
    print("\nBuilding indices...")
    configs = [
        ("BM25_k1.0_b0.75", 1.0, 0.75),
        ("BM25_k1.5_b0.75", 1.5, 0.75),
        ("BM25_k2.0_b0.75", 2.0, 0.75),
        ("BM25_k1.5_b0.50", 1.5, 0.50),
        ("BM25_k1.5_b0.90", 1.5, 0.90),
    ]

    bm25_models = {}
    for name, k1, b in configs:
        t0 = time.time()
        model = BM25(k1=k1, b=b)
        model.fit(texts)
        bm25_models[name] = model
        print("  %s: %.3f s" % (name, time.time() - t0))

    # Run queries
    print("\nRunning queries...")
    methods = {
        "sequence_matcher": [],
        "bm25_default": [],
        "bm25_ensemble": [],
        "bm25_seq_rrf": [],
        "ensemble_seq_rrf": [],
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

            # BM25 default
            res_bm25 = bm25_models["BM25_k1.5_b0.75"].search(query, top_k=5)
            methods["bm25_default"].append(
                {
                    "qid": q["id"],
                    "lang": lang,
                    **compute_metrics(res_bm25, expected_idxs),
                }
            )

            # BM25 Ensemble (5 variants + RRF)
            ensemble_results = [
                bm25_models[name].search(query, top_k=5) for name in bm25_models
            ]
            res_ensemble = rrf_fusion(ensemble_results, k=60)
            methods["bm25_ensemble"].append(
                {
                    "qid": q["id"],
                    "lang": lang,
                    **compute_metrics(res_ensemble, expected_idxs),
                }
            )

            # BM25 + SequenceMatcher RRF
            res_bm25_seq = rrf_fusion([res_bm25, res_seq], k=60)
            methods["bm25_seq_rrf"].append(
                {
                    "qid": q["id"],
                    "lang": lang,
                    **compute_metrics(res_bm25_seq, expected_idxs),
                }
            )

            # Ensemble + SequenceMatcher RRF
            res_all = rrf_fusion(ensemble_results + [res_seq], k=60)
            methods["ensemble_seq_rrf"].append(
                {
                    "qid": q["id"],
                    "lang": lang,
                    **compute_metrics(res_all, expected_idxs),
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
        "bm25_default": "BM25 default",
        "bm25_ensemble": "BM25 ensemble",
        "bm25_seq_rrf": "BM25+Seq RRF",
        "ensemble_seq_rrf": "Ensemble+Seq RRF",
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

    # Delta vs SequenceMatcher
    baseline = summary["sequence_matcher"]
    print("\n%-22s %10s %10s %10s" % ("Delta vs SeqMatcher", "Prec@3", "Recall", "MRR"))
    print("-" * 55)
    for method in list(methods.keys())[1:]:
        s = summary[method]
        d_p3 = ((s["precision_at_3"] / baseline["precision_at_3"]) - 1) * 100
        d_r = ((s["recall"] / baseline["recall"]) - 1) * 100
        d_mrr = ((s["mrr"] / baseline["mrr"]) - 1) * 100
        print("%-22s %+9.1f%% %+9.1f%% %+9.1f%%" % (labels[method], d_p3, d_r, d_mrr))

    # Head-to-head
    print("\n" + "=" * 70)
    print("HEAD-TO-HEAD (MRR wins vs SequenceMatcher)")
    print("=" * 70)
    for method in list(methods.keys())[1:]:
        wins = losses = ties = 0
        for i in range(len(methods["sequence_matcher"])):
            m_base = methods["sequence_matcher"][i]["mrr"]
            m_new = methods[method][i]["mrr"]
            if m_new > m_base:
                wins += 1
            elif m_new < m_base:
                losses += 1
            else:
                ties += 1
        print("%-22s %dW / %dL / %dT" % (labels[method], wins, losses, ties))

    # Best configuration
    best_method = max(summary.items(), key=lambda x: x[1]["mrr"])
    print(
        "\nBest: %s (MRR=%.4f, Recall=%.4f, Hits=%d/%d)"
        % (
            labels[best_method[0]],
            best_method[1]["mrr"],
            best_method[1]["recall"],
            best_method[1]["hits"],
            best_method[1]["total"],
        )
    )

    # Save
    output = {
        "summary": summary,
        "config": {
            "bm25_configs": {name: {"k1": k1, "b": b} for name, k1, b in configs},
            "rrf_k": 60,
            "entries": len(entries),
            "queries": len(queries),
        },
    }
    out_path = os.path.join(RESULTS, "ensemble_benchmark.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print("\nSaved: %s" % out_path)


if __name__ == "__main__":
    main()
