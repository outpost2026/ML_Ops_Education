#!/usr/bin/env python3
"""
GT Postmortem Retrieval Tool
Rychlý retrieval relevantních hSNR dat pro dev workflow.

Použití:
  python -X utf8 retrieve.py "timeout v MCP serveru"
  python -X utf8 retrieve.py "encoding problem na Windows"
  python -X utf8 retrieve.py --interactive

Pipeline: BM25 + SequenceMatcher + RRF Fusion
"""

import json
import math
import os
import re
import sys
from collections import Counter, defaultdict
from difflib import SequenceMatcher

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")


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
        if isinstance(query, list):
            query_tokens = query
        else:
            query_tokens = tokenize(query)
        scores = []
        for i in range(self.N):
            score = self._score_doc(query_tokens, i)
            scores.append((i, score))
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
# SEARCHABLE TEXT
# ============================================================


def tokenize(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9à-ž\-\_]+", " ", text)
    return [t for t in text.split() if len(t) >= 2]


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
# FUZZY SEARCH
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
# RRF FUSION
# ============================================================


def rrf_fusion(results_list, k=60):
    scores = defaultdict(float)
    for results in results_list:
        for rank, (doc_idx, _) in enumerate(results, 1):
            scores[doc_idx] += 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda x: -x[1])


# ============================================================
# RETRIEVAL ENGINE
# ============================================================


class RetrievalEngine:
    def __init__(self):
        self.entries = []
        self.texts = []
        self.bm25 = None
        self.id_to_entry = {}

    def load(self, jsonl_path):
        with open(jsonl_path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    self.entries.append(entry)
                    self.id_to_entry[entry["id"]] = entry

        self.texts = [build_searchable_text(e) for e in self.entries]
        self.bm25 = BM25(k1=1.5, b=0.75)
        self.bm25.fit(self.texts)
        return self

    def search(self, query, top_k=5):
        expanded = expand_query(query)

        res_bm25 = self.bm25.search(query, top_k=top_k)
        res_bm25_exp = self.bm25.search(expanded, top_k=top_k)
        res_seq = search_fuzzy(query, self.texts, top_k=top_k)

        rrf_results = rrf_fusion([res_bm25, res_bm25_exp, res_seq], k=60)

        results = []
        for idx, score in rrf_results[:top_k]:
            entry = self.entries[idx]
            results.append(
                {
                    "id": entry["id"],
                    "score": round(score, 4),
                    "symptom": entry.get("symptom", "")[:100],
                    "root_cause": entry.get("root_cause", "")[:100],
                    "fix": entry.get("fix", "")[:100],
                    "server": entry.get("server", ""),
                    "tags": entry.get("tags", []),
                    "rule": entry.get("rule", ""),
                }
            )
        return results


# ============================================================
# CLI
# ============================================================


def print_results(results, query):
    print("\n" + "=" * 70)
    print("Dotaz: %s" % query)
    print("=" * 70)

    if not results:
        print("Žádné výsledky.")
        return

    for i, r in enumerate(results, 1):
        print("\n[%d] %s (score: %.4f)" % (i, r["id"], r["score"]))
        print("    Symptom:     %s" % r["symptom"])
        print("    Root cause:  %s" % r["root_cause"])
        print("    Fix:         %s" % r["fix"])
        print("    Server:      %s" % r["server"])
        print("    Tags:        %s" % ", ".join(r["tags"]) if r["tags"] else "")
        print("    Rule:        %s" % r["rule"])


def interactive_mode(engine):
    print("\n" + "=" * 70)
    print("GT POSTMORTEM RETRIEVAL — Interactive Mode")
    print("Napište dotaz nebo 'quit' pro ukončení.")
    print("=" * 70)

    while True:
        try:
            query = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nKonec.")
            break

        if not query or query.lower() in ["quit", "exit", "q"]:
            print("Konec.")
            break

        results = engine.search(query, top_k=5)
        print_results(results, query)


def main():
    jsonl_path = os.path.join(DATA, "gt_full.jsonl")

    if not os.path.exists(jsonl_path):
        print("CHYBA: gt_full.jsonl nenalezen v %s" % DATA)
        sys.exit(1)

    engine = RetrievalEngine()
    print("Načítám data...")
    engine.load(jsonl_path)
    print("Načteno %d entries." % len(engine.entries))

    if len(sys.argv) > 1:
        if sys.argv[1] in ["--interactive", "-i"]:
            interactive_mode(engine)
        else:
            query = " ".join(sys.argv[1:])
            results = engine.search(query, top_k=5)
            print_results(results, query)
    else:
        interactive_mode(engine)


if __name__ == "__main__":
    main()
