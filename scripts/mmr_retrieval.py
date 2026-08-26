"""
Retrieval Pipeline — MMR (Maximal Marginal Relevance)
Přidává diverzitu do výsledků — zabrání duplicitám v top-5.

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
# TOKENIZER
# ============================================================


def tokenize(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9à-ž\-\_]+", " ", text)
    return [t for t in text.split() if len(t) >= 2]


# ============================================================
# BM25
# ============================================================


class BM25:
    def __init__(self, k1=1.5, b=0.75):
        self.k1 = k1
        self.b = b

    def fit(self, documents):
        self.docs = documents
        self.doc_tokens = [tokenize(doc) for doc in documents]
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
        query_tokens = tokenize(query)
        scores = []
        for i in range(self.N):
            score = self._score_doc(query_tokens, i)
            scores.append((i, score))
        scores.sort(key=lambda x: -x[1])
        return scores[:top_k]


# ============================================================
# SEQUENCEMATCHER
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
# QUERY EXPANSION
# ============================================================

SYNONYM_MAP = {
    "timeout": ["deadlock", "zaseknuti", "time-out", "hang"],
    "cache": ["invalidace", "vyprseni", "stale"],
    "encoding": ["kodovani", "utf-8", "cp1250"],
    "error": ["chyba", "exception", "selhani"],
    "server": ["sluzba", "service", "daemon"],
    "config": ["konfigurace", "nastaveni", "settings"],
    "memory": ["pamet", "ram", "spotreba"],
    "network": ["sit", "pripojeni", "connection"],
    "browser": ["prohlizec", "chromium", "playwright"],
    "git": ["verzovani", "repozitar", "repository"],
    "docker": ["kontejner", "container", "image"],
    "test": ["testovani", "testing", "overeni"],
}


def expand_query(query):
    tokens = tokenize(query)
    expanded = list(tokens)
    for t in tokens:
        if t in SYNONYM_MAP:
            expanded.extend(SYNONYM_MAP[t][:2])
    return expanded


# ============================================================
# RRF FUSION
# ============================================================


def rrf_fusion(results_list, k=60):
    scores = defaultdict(float)
    for results in results_list:
        for rank, (doc_idx, _) in enumerate(results, 1):
            scores[doc_idx] += 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda x: -x[1])


# ============================================================
# MMR (Maximal Marginal Relevance)
# ============================================================


def mmr_score(query_vec, doc_vec, selected_vecs, lambda_param=0.7):
    """
    MMR skóre = λ * sim(d, q) - (1-λ) * max(sim(d, d_j))
    lambda=0.7 = 70% relevance, 30% diverzita
    """
    # Relevance s query
    relevance = cosine_sim(query_vec, doc_vec)

    # Max similarity s již vybranými
    if selected_vecs:
        max_sim = max(cosine_sim(doc_vec, sv) for sv in selected_vecs)
    else:
        max_sim = 0

    return lambda_param * relevance - (1 - lambda_param) * max_sim


def cosine_sim(v1, v2):
    """Kosinusová podobnost dvou vektorů."""
    dot = np.dot(v1, v2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0
    return dot / (norm1 * norm2)


def text_to_vec(text, vocab):
    """Převede text na TF-IDF vektor."""
    tokens = tokenize(text)
    vec = np.zeros(len(vocab))
    for t in tokens:
        if t in vocab:
            vec[vocab[t]] += 1
    # L2 normalize
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec /= norm
    return vec


def mmr_rerank(query, texts, candidate_indices, top_k=5, lambda_param=0.7):
    """
    MMR reranking — vybírá diversifikované výsledky.
    """
    # Build vocab
    all_tokens = []
    for txt in texts:
        all_tokens.extend(tokenize(txt))
    vocab = {t: i for i, t in enumerate(set(all_tokens))}

    query_vec = text_to_vec(query, vocab)

    selected = []
    selected_vecs = []
    candidates = list(candidate_indices)

    for _ in range(min(top_k, len(candidates))):
        best_score = -float("inf")
        best_idx = -1

        for idx in candidates:
            doc_vec = text_to_vec(texts[idx], vocab)
            score = mmr_score(query_vec, doc_vec, selected_vecs, lambda_param)

            if score > best_score:
                best_score = score
                best_idx = idx

        if best_idx >= 0:
            selected.append(best_idx)
            selected_vecs.append(text_to_vec(texts[best_idx], vocab))
            candidates.remove(best_idx)

    return selected


# ============================================================
# SEARCHABLE TEXT
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
# METRICS
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
# MAIN
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
    print("MMR (Maximal Marginal Relevance) — Diverzita výsledků")
    print("=" * 70)

    entries = load_jsonl(os.path.join(DATA, "gt_full.jsonl"))
    queries = load_queries(os.path.join(DATA, "test_queries.json"))
    print("Loaded %d entries, %d queries" % (len(entries), len(queries)))

    texts = [build_searchable_text(e) for e in entries]
    id_to_idx = {e["id"]: i for i, e in enumerate(entries)}

    # Build indices
    print("\nBuilding indices...")
    bm25 = BM25(k1=1.5, b=0.75)
    bm25.fit(texts)

    # Run queries
    print("\nRunning queries...")
    methods = {
        "bm25_seq_rrf": [],
        "mmr_lambda0.7": [],
        "mmr_lambda0.5": [],
        "mmr_lambda0.3": [],
    }

    for q in queries:
        expected_idxs = set(id_to_idx[eid] for eid in q["expected"] if eid in id_to_idx)

        for lang in ["cz", "en"]:
            query = q["query_%s" % lang]

            # BM25+Seq RRF (baseline vítěz)
            res_bm25 = bm25.search(query, top_k=10)
            res_seq = search_fuzzy(query, texts, top_k=10)
            rrf_results = rrf_fusion([res_bm25, res_seq], k=60)
            rrf_indices = [idx for idx, _ in rrf_results[:10]]

            # Without MMR
            methods["bm25_seq_rrf"].append(
                {
                    "qid": q["id"],
                    "lang": lang,
                    **compute_metrics(rrf_results[:5], expected_idxs),
                }
            )

            # With MMR (different lambda)
            for lambda_param, method_name in [
                (0.7, "mmr_lambda0.7"),
                (0.5, "mmr_lambda0.5"),
                (0.3, "mmr_lambda0.3"),
            ]:
                mmr_indices = mmr_rerank(
                    query, texts, rrf_indices, top_k=5, lambda_param=lambda_param
                )
                mmr_results = [(idx, 0) for idx in mmr_indices]
                methods[method_name].append(
                    {
                        "qid": q["id"],
                        "lang": lang,
                        **compute_metrics(mmr_results, expected_idxs),
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
        "bm25_seq_rrf": "BM25+Seq RRF",
        "mmr_lambda0.7": "MMR λ=0.7",
        "mmr_lambda0.5": "MMR λ=0.5",
        "mmr_lambda0.3": "MMR λ=0.3",
    }

    print("\n%-20s %10s %10s %10s %10s" % ("Method", "Prec@3", "Recall", "MRR", "Hits"))
    print("-" * 65)
    for method in methods:
        s = summary[method]
        print(
            "%-20s %10.4f %10.4f %10.4f %7d/%d"
            % (
                labels[method],
                s["precision_at_3"],
                s["recall"],
                s["mrr"],
                s["hits"],
                s["total"],
            )
        )

    # Save
    output = {"summary": summary}
    out_path = os.path.join(RESULTS, "mmr_benchmark.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print("\nSaved: %s" % out_path)


if __name__ == "__main__":
    main()
