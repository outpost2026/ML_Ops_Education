"""Before/after measurement: git HEAD (code+data) vs working tree (P0 bundle).

Both configurations are fed the same 50 CZ/EN queries and the same metric code.
"""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = r"C:\Users\PC\Documents\Repozitar_Dev\_github\mcp-retrieval"
BASELINE_COMMIT = "68f6e67"  # posledni commit pred P0 balikem (pin, ne HEAD)
SRC = os.path.join(REPO, "src", "mcp_retrieval")
QS = (
    r"C:\Users\PC\Documents\Repozitar_Dev\_github\ML_Ops_edukace\data\test_queries.json"
)
OUT = r"C:\Users\PC\Documents\Repozitar_Dev\_github\ML_Ops_edukace\results\p0_baseline.json"

queries = json.load(open(QS, encoding="utf-8"))


def git_show(rel):
    return subprocess.run(
        ["git", "-C", REPO, "show", BASELINE_COMMIT + ":" + rel],
        capture_output=True,
        check=True,
    ).stdout


def load_legacy(tmp):
    path = os.path.join(tmp, "legacy_retrieval.py")
    with open(path, "wb") as f:
        f.write(git_show("src/mcp_retrieval/retrieval.py"))
    spec = importlib.util.spec_from_file_location("legacy_retrieval", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def evaluate(engine, data_dir):
    """engine: object with .search(query, top_k) -> {'matched', 'results'}"""
    import hashlib

    with open(os.path.join(data_dir, "gt_full.jsonl"), "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    rr = p3 = rec = 0.0
    hits = n = abst = 0
    lat = []
    per_query = []

    # warm up (first call pays for lazy import/lookup overhead)
    for _ in range(3):
        engine.search("timeout MCP server", top_k=5)

    for q in queries:
        exp = set(q["expected"])
        for lang in ("query_cz", "query_en"):
            query = q[lang]
            t = time.perf_counter()
            out = engine.search(query, top_k=5)
            lat.append((time.perf_counter() - t) * 1000)
            n += 1
            if not out["matched"]:
                abst += 1
            ids = [x["id"] for x in out["results"]]
            rank = next((i + 1 for i, x in enumerate(ids) if x in exp), None)
            if rank:
                rr += 1.0 / rank
                hits += 1
            p3 += len(set(ids[:3]) & exp) / min(3, len(exp))
            rec += len(set(ids) & exp) / len(exp)
            per_query.append(
                {
                    "query_id": q["id"],
                    "lang": "CZ" if lang == "query_cz" else "EN",
                    "rank": rank,
                    "top_ids": ids,
                    "abstained": not out["matched"],
                }
            )
    return {
        "entries": len(engine.entries),
        "rules": len(engine.rules),
        "dataset_sha256": sha,
        "n": n,
        "hits": hits,
        "mrr": round(rr / n, 4),
        "prec3": round(p3 / n, 4),
        "recall5": round(rec / n, 4),
        "abstained": abst,
        "latency_ms_avg": round(sum(lat) / len(lat), 2),
        "per_query": per_query,
    }


class LegacyAdapter:
    """Wraps the HEAD retriever (list return) into the new dict contract."""

    def __init__(self, mod, data_dir):
        self.r = mod.GTRetriever(data_dir=data_dir).load()
        self.entries = self.r.entries
        self.rules = self.r.rules
        self._mod = mod

    def search(self, query, top_k=5):
        results = self.r.search(query, top_k)
        # HEAD had no abstention: emulate abstention with the same BM25 gate
        tokens = self._mod.tokenize(query)
        top = max(
            (self.r.bm25._score_doc(tokens, i) for i in range(self.r.bm25.N)),
            default=0.0,
        )
        matched = bool(results) and top > 0
        return {"matched": matched, "results": results if matched else []}


tmp = tempfile.mkdtemp(prefix="gt_before_")
try:
    legacy = load_legacy(tmp)
    old_data = os.path.join(tmp, "data")
    os.makedirs(old_data)
    with open(os.path.join(old_data, "gt_full.jsonl"), "wb") as f:
        f.write(git_show("src/mcp_retrieval/data/gt_full.jsonl"))
    with open(os.path.join(old_data, "gt_rules.json"), "wb") as f:
        f.write(git_show("src/mcp_retrieval/data/gt_rules.json"))

    before = evaluate(LegacyAdapter(legacy, old_data), old_data)

    sys.path.insert(0, os.path.join(REPO, "src"))
    from mcp_retrieval.retrieval import GTRetriever

    new_data = os.path.join(SRC, "data")
    after = evaluate(GTRetriever(data_dir=new_data).load(), new_data)
finally:
    shutil.rmtree(tmp, ignore_errors=True)

for label, res in (("BEFORE (HEAD)", before), ("AFTER (P0)", after)):
    print(
        label,
        "entries",
        res["entries"],
        "rules",
        res["rules"],
        "sha",
        res["dataset_sha256"][:12],
        "| hits",
        res["hits"],
        "/",
        res["n"],
        "MRR",
        res["mrr"],
        "Prec@3",
        res["prec3"],
        "Recall@5",
        res["recall5"],
        "abstain",
        res["abstained"],
        "lat",
        res["latency_ms_avg"],
        "ms",
    )

print("delta_mrr_pct", round((after["mrr"] / before["mrr"] - 1) * 100, 1))
print("delta_hits", after["hits"] - before["hits"])
print("delta_prec3_pct", round((after["prec3"] / before["prec3"] - 1) * 100, 1))

payload = {
    "measured": time.strftime("%Y-%m-%d"),
    "queries": str(QS),
    "query_count": len(queries) * 2,
    "engine": {
        "before": "git "
        + BASELINE_COMMIT
        + " (bm25 k1=1.5 b=0.75, rrf k=60, no abstention)",
        "after": "P0 bundle (freshness guard, abstention, rules catalog, re-extraction)",
    },
    "before": {k: v for k, v in before.items() if k != "per_query"},
    "after": {k: v for k, v in after.items() if k != "per_query"},
}
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)
    f.write("\n")
print("written", OUT)
