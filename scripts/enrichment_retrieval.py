"""
Hybrid Retrieval Pipeline — Varianta 1: BM25 + Metadata Enrichment
Zero-Download, zlepšení přesbohatší searchable text

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
        self.docs = []
        self.doc_tokens = []
        self.doc_lens = []
        self.avg_dl = 0
        self.df = Counter()
        self.N = 0
        self.inverted_index = defaultdict(list)

    def fit(self, documents):
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
        query_tokens = tokenize(query) if isinstance(query, str) else query
        scores = []
        for i in range(self.N):
            score = self._score_doc(query_tokens, i)
            scores.append((i, score))
        scores.sort(key=lambda x: -x[1])
        return scores[:top_k]


# ============================================================
# 3. SEARCHABLE TEXT BUILDERS
# ============================================================


def build_text_baseline(entry):
    """Baseline: základní pole."""
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


def build_text_enriched_v1(entry):
    """Enrichment v1: duplikace high-value fields (tags, server, status)."""
    parts = []
    # Základní pole
    for key in ["symptom", "root_cause", "fix"]:
        val = entry.get(key, "")
        if isinstance(val, list):
            val = " ".join(str(x) for x in val)
        parts.append(str(val))
    # Metadata — zdvojené pro vyšší váhu
    for key in ["server", "status", "typ", "rule"]:
        val = entry.get(key, "")
        if isinstance(val, list):
            val = " ".join(str(x) for x in val)
        parts.append(str(val))
        parts.append(str(val))  # duplikace
    # Tags — trojitě pro maximální váhu
    tags = entry.get("tags", "")
    if isinstance(tags, list):
        tags = " ".join(str(x) for x in tags)
    parts.append(str(tags))
    parts.append(str(tags))
    parts.append(str(tags))
    return " ".join(parts)


def build_text_enriched_v2(entry):
    """Enrichment v2: v1 + ID jako searchable term + aliases."""
    base = build_text_enriched_v1(entry)
    extra = []
    # Přidat ID jako termín
    eid = entry.get("id", "")
    if eid:
        extra.append(eid.lower())
        # Přidat bez pomlčky (GT001 místo GT-001)
        extra.append(eid.lower().replace("-", ""))
    # Přidat aliases
    aliases = entry.get("aliases", [])
    if aliases:
        for a in aliases:
            extra.append(a.lower())
    return base + " " + " ".join(extra)


def build_text_enriched_v3(entry):
    """Enrichment v3: v2 + kontextová slova z pole fix."""
    base = build_text_enriched_v2(entry)
    fix = entry.get("fix", "")
    if isinstance(fix, list):
        fix = " ".join(str(x) for x in fix)
    # Přidat klíčová slova z fixu
    fix_lower = fix.lower()
    keywords = []
    for kw in [
        "timeout",
        "deadlock",
        "cache",
        "encoding",
        "playwright",
        "browser",
        "mcp",
        "api",
        "git",
        "docker",
        "kubernetes",
        "python",
        "numpy",
        "regex",
        "json",
        "subprocess",
        "thread",
        "async",
        "await",
    ]:
        if kw in fix_lower:
            keywords.append(kw)
    return base + " " + " ".join(keywords)


# ============================================================
# 4. SEQUENCEMATCHER BASELINE
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
# 5. METRICS
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
# 6. MAIN
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


def run_benchmark(entries, queries, texts_builder, label):
    """Spustí benchmark pro daný text builder."""
    texts = [texts_builder(e) for e in entries]
    id_to_idx = {e["id"]: i for i, e in enumerate(entries)}

    bm25 = BM25(k1=1.5, b=0.75)
    bm25.fit(texts)

    results = []
    for q in queries:
        expected_idxs = set(id_to_idx[eid] for eid in q["expected"] if eid in id_to_idx)
        for lang in ["cz", "en"]:
            query = q["query_%s" % lang]
            res = bm25.search(query, top_k=5)
            m = compute_metrics(res, expected_idxs)
            results.append({"qid": q["id"], "lang": lang, **m})

    n = len(results)
    return {
        "label": label,
        "precision_at_3": round(sum(r["precision_at_3"] for r in results) / n, 4),
        "recall": round(sum(r["recall"] for r in results) / n, 4),
        "mrr": round(sum(r["mrr"] for r in results) / n, 4),
        "hits": sum(1 for r in results if r["mrr"] > 0),
        "total": n,
    }


def main():
    print("=" * 70)
    print("BM25 + METADATA ENRICHMENT — Diff Test")
    print("=" * 70)

    entries = load_jsonl(os.path.join(DATA, "gt_full.jsonl"))
    queries = load_queries(os.path.join(DATA, "test_queries.json"))
    print("Loaded %d entries, %d queries" % (len(entries), len(queries)))

    # SequenceMatcher baseline
    texts_base = [build_text_baseline(e) for e in entries]
    id_to_idx = {e["id"]: i for i, e in enumerate(entries)}
    sm_results = []
    for q in queries:
        expected_idxs = set(id_to_idx[eid] for eid in q["expected"] if eid in id_to_idx)
        for lang in ["cz", "en"]:
            query = q["query_%s" % lang]
            res = search_fuzzy(query, texts_base, top_k=5)
            m = compute_metrics(res, expected_idxs)
            sm_results.append({"qid": q["id"], "lang": lang, **m})
    n = len(sm_results)
    sm_summary = {
        "label": "SequenceMatcher",
        "precision_at_3": round(sum(r["precision_at_3"] for r in sm_results) / n, 4),
        "recall": round(sum(r["recall"] for r in sm_results) / n, 4),
        "mrr": round(sum(r["mrr"] for r in sm_results) / n, 4),
        "hits": sum(1 for r in sm_results if r["mrr"] > 0),
        "total": n,
    }

    # Run all variants
    variants = [
        ("BM25 baseline", build_text_baseline),
        ("BM25 + enrichment v1", build_text_enriched_v1),
        ("BM25 + enrichment v2", build_text_enriched_v2),
        ("BM25 + enrichment v3", build_text_enriched_v3),
    ]

    all_results = [sm_summary]
    for label, builder in variants:
        t0 = time.time()
        res = run_benchmark(entries, queries, builder, label)
        t = time.time() - t0
        res["time_s"] = round(t, 3)
        all_results.append(res)

    # Print results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(
        "\n%-25s %10s %10s %10s %8s %8s"
        % ("Method", "Prec@3", "Recall", "MRR", "Hits", "Time")
    )
    print("-" * 75)
    for r in all_results:
        print(
            "%-25s %10.4f %10.4f %10.4f %5d/%d %7.3fs"
            % (
                r["label"],
                r["precision_at_3"],
                r["recall"],
                r["mrr"],
                r["hits"],
                r["total"],
                r.get("time_s", 0),
            )
        )

    # Delta vs SequenceMatcher
    baseline = sm_summary
    print("\n%-25s %10s %10s %10s" % ("Delta vs SeqMatcher", "Prec@3", "Recall", "MRR"))
    print("-" * 55)
    for r in all_results[1:]:
        d_p3 = ((r["precision_at_3"] / baseline["precision_at_3"]) - 1) * 100
        d_r = ((r["recall"] / baseline["recall"]) - 1) * 100
        d_mrr = ((r["mrr"] / baseline["mrr"]) - 1) * 100
        print("%-25s %+9.1f%% %+9.1f%% %+9.1f%%" % (r["label"], d_p3, d_r, d_mrr))

    # Save
    out = {"summary": all_results, "baseline": "SequenceMatcher"}
    out_path = os.path.join(RESULTS, "enrichment_benchmark.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("\nSaved: %s" % out_path)


if __name__ == "__main__":
    main()
