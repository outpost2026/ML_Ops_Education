import json, sys, os, time
from difflib import SequenceMatcher

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE = r"C:\Users\PC\Documents\Repozitar_Dev\_github\TEMP_TRIMMING\formalization_demo"
V2 = r"C:\Users\PC\Documents\Repozitar_Dev\_github\B2B-Knowledge-Base\04_KNOWLEDGE_BASE\01_MCP\MCP_GROUND_TRUTH_postmortem_agregovany_v2.md"
RESULTS = os.path.join(BASE, "results")
os.makedirs(RESULTS, exist_ok=True)

print("=" * 70)
print("GT FORMALIZATION POC — Full Benchmark (108 entries)")
print("=" * 70)

# ============================================================
# 1. Load JSONL
# ============================================================
jsonl_entries = {}
with open(os.path.join(BASE, "gt_full.jsonl"), encoding="utf-8") as f:
    for line in f:
        if line.strip():
            rec = json.loads(line)
            jsonl_entries[rec["id"]] = rec

print("Loaded %d JSONL entries" % len(jsonl_entries))

# ============================================================
# 2. Parse v2 markdown
# ============================================================
with open(V2, encoding="utf-8") as f:
    v2_text = f.read()

import re

v2_entries = {}
pattern = r"#### (GT-(?:GCP-)?\d{3})\s*(?:\([^)]*\))?:\s*(.+?)\n"
for m in re.finditer(pattern, v2_text):
    gt_id = m.group(1)
    title = m.group(2).strip()
    start = m.end()
    next_header = re.search(r"\n####|\n## [0-9]", v2_text[start:])
    end = start + next_header.start() if next_header else len(v2_text)
    block = v2_text[start:end].strip()
    entry = {"id": gt_id, "title": title}
    for field, key in [
        ("Server:", "server"),
        ("Status:", "status"),
        ("Symptom:", "symptom"),
        ("Root cause:", "root_cause"),
        ("Fix:", "fix"),
        ("Pravidlo:", "rule"),
        ("Provenance:", "provenance"),
    ]:
        fm = re.search(
            rf"\*\*{re.escape(field)}\*\*\s*(.+?)(?=\n\*\*|\n####|\n##|\Z)", block, re.S
        )
        if fm:
            entry[key] = fm.group(1).strip()
    v2_entries[gt_id] = entry

print("Parsed %d v2 entries" % len(v2_entries))

# ============================================================
# 3. Render markdown from JSONL
# ============================================================
lines = [
    "# MCP GT — Katalog chyb (generated from full JSONL)",
    "",
    "**Entries:** %d | **Format:** JSONL-derived markdown" % len(jsonl_entries),
    "",
]
for e in jsonl_entries.values():
    aliases = " (%s)" % e["aliases"][0] if e.get("aliases") else ""
    lines.append("#### %s%s: %s" % (e["id"], aliases, e.get("typ", "unknown")))
    lines.append("**Server:** %s | **Status:** %s" % (e["server"], e["status"]))
    lines.append("")
    lines.append("**Symptom:** %s" % e["symptom"])
    lines.append("**Root cause:** %s" % e["root_cause"])
    fix = e["fix"]
    if isinstance(fix, list):
        fix = ", ".join(str(x) for x in fix)
    lines.append("**Fix:** %s" % fix)
    lines.append("**Pravidlo:** %s" % e["rule"])
    if e.get("tags"):
        lines.append("**Tags:** %s" % " | ".join(e["tags"]))
    lines.append("")

rendered_md = os.path.join(BASE, "gt_catalog_full_render.md")
with open(rendered_md, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(lines) + "\n")
print("Rendered markdown: %d bytes" % os.path.getsize(rendered_md))


# ============================================================
# 4. Compression metrics
# ============================================================
def measure_tokens(text):
    try:
        import tiktoken

        enc = tiktoken.get_encoding("o200k_base")
        return len(enc.encode(text))
    except:
        return len(text) // 4


v2_size = os.path.getsize(V2)
v2_tokens = measure_tokens(v2_text)
jsonl_size = os.path.getsize(os.path.join(BASE, "gt_full.jsonl"))
jsonl_tokens = 0
with open(os.path.join(BASE, "gt_full.jsonl"), encoding="utf-8") as f:
    for line in f:
        if line.strip():
            jsonl_tokens += measure_tokens(line)

render_size = os.path.getsize(rendered_md)
render_tokens = measure_tokens(open(rendered_md, encoding="utf-8").read())

print("\n" + "=" * 70)
print("COMPRESSION COMPARISON")
print("=" * 70)
print("Format                    Size (B)    Tokens    Avg B/entry  Avg T/entry")
print("-" * 70)
print(
    "v2 Markdown (full)      %10d  %8d  %10.0f  %10.0f"
    % (v2_size, v2_tokens, v2_size / 108, v2_tokens / 108)
)
print(
    "JSONL (full)            %10d  %8d  %10.0f  %10.0f"
    % (jsonl_size, jsonl_tokens, jsonl_size / 108, jsonl_tokens / 108)
)
print(
    "Rendered MD (from JSONL)%10d  %8d  %10.0f  %10.0f"
    % (render_size, render_tokens, render_size / 108, render_tokens / 108)
)
print("-" * 70)
print(
    "JSONL vs v2 delta:      %+.1f%%      %+.1f%%"
    % (((jsonl_size / v2_size) - 1) * 100, ((jsonl_tokens / v2_tokens) - 1) * 100)
)

# ============================================================
# 5. Retrieval test (25 queries, CZ+EN)
# ============================================================
with open(os.path.join(BASE, "test_queries.json"), encoding="utf-8") as f:
    queries = json.load(f)


def searchable_v2(entry):
    parts = []
    for k in ["title", "symptom", "root_cause", "fix", "server", "status"]:
        v = entry.get(k, "")
        if isinstance(v, list):
            v = " ".join(str(x) for x in v)
        parts.append(str(v))
    return " ".join(parts).lower()


def searchable_jsonl(entry):
    parts = []
    for k in ["symptom", "root_cause", "fix", "server", "status", "typ", "tags"]:
        v = entry.get(k, "")
        if isinstance(v, list):
            v = " ".join(str(x) for x in v)
        parts.append(str(v))
    return " ".join(parts).lower()


def fuzzy_score(query, text):
    q = query.lower()
    t = text.lower()
    if q in t:
        return 1.0
    words = q.split()
    if len(words) > 1:
        matches = sum(1 for w in words if w in t)
        keyword_score = matches / len(words)
    else:
        keyword_score = 0.0
    seq_score = SequenceMatcher(None, q, t[:200]).ratio()
    return max(keyword_score, seq_score)


def retrieve(query, entries, text_fn, top_k=5):
    scores = []
    for gid, entry in entries.items():
        txt = text_fn(entry)
        score = fuzzy_score(query, txt)
        scores.append((gid, score, entry))
    scores.sort(key=lambda x: -x[1])
    return scores[:top_k]


print("\n" + "=" * 70)
print("RETRIEVAL COMPARISON")
print("=" * 70)

results = []
for q in queries:
    qid = q["id"]
    expected = set(q["expected"])
    for lang, query in [("CZ", q["query_cz"]), ("EN", q["query_en"])]:
        res_v2 = retrieve(query, v2_entries, searchable_v2, top_k=5)
        res_jsonl = retrieve(query, jsonl_entries, searchable_jsonl, top_k=5)

        top3_v2 = [r[0] for r in res_v2[:3]]
        top3_jsonl = [r[0] for r in res_jsonl[:3]]

        mrr_v2 = 0
        for rank, (gid, _, _) in enumerate(res_v2, 1):
            if gid in expected:
                mrr_v2 = 1.0 / rank
                break
        mrr_jsonl = 0
        for rank, (gid, _, _) in enumerate(res_jsonl, 1):
            if gid in expected:
                mrr_jsonl = 1.0 / rank
                break

        p3_v2 = len(expected & set(top3_v2)) / min(3, len(expected))
        p3_jsonl = len(expected & set(top3_jsonl)) / min(3, len(expected))
        recall_v2 = len(expected & set(top3_v2)) / len(expected) if expected else 0
        recall_jsonl = (
            len(expected & set(top3_jsonl)) / len(expected) if expected else 0
        )

        winner = (
            "jsonl" if mrr_jsonl > mrr_v2 else ("v2" if mrr_v2 > mrr_jsonl else "tie")
        )
        results.append(
            {
                "qid": qid,
                "lang": lang,
                "expected": list(expected),
                "v2_top3": top3_v2,
                "jsonl_top3": top3_jsonl,
                "v2_p3": p3_v2,
                "jsonl_p3": p3_jsonl,
                "v2_recall": recall_v2,
                "jsonl_recall": recall_jsonl,
                "v2_mrr": mrr_v2,
                "jsonl_mrr": mrr_jsonl,
                "winner": winner,
            }
        )

total = len(results)
avg = lambda key: sum(r[key] for r in results) / total
wins = lambda w: sum(1 for r in results if r["winner"] == w)

print("\nMetric                     v2 Markdown     JSONL       Delta")
print("-" * 60)
for label, vk, jk in [
    ("Precision@3", "v2_p3", "jsonl_p3"),
    ("Recall", "v2_recall", "jsonl_recall"),
    ("MRR", "v2_mrr", "jsonl_mrr"),
]:
    v, j = avg(vk), avg(jk)
    d = ((j / v) - 1) * 100 if v > 0 else 0
    print("%-25s %10.3f %10.3f %+8.1f%%" % (label, v, j, d))
print("-" * 60)
print(
    "Win/Loss/Tie                          %dW / %dW / %dT"
    % (wins("v2"), wins("jsonl"), wins("tie"))
)

# ============================================================
# 6. Save results
# ============================================================
final = {
    "compression": {
        "v2_full_bytes": v2_size,
        "v2_full_tokens": v2_tokens,
        "jsonl_full_bytes": jsonl_size,
        "jsonl_full_tokens": jsonl_tokens,
        "render_bytes": render_size,
        "render_tokens": render_tokens,
        "delta_bytes_pct": round(((jsonl_size / v2_size) - 1) * 100, 1),
        "delta_tokens_pct": round(((jsonl_tokens / v2_tokens) - 1) * 100, 1),
    },
    "retrieval": {
        "total_queries": total,
        "v2_precision@3": round(avg("v2_p3"), 4),
        "jsonl_precision@3": round(avg("jsonl_p3"), 4),
        "v2_recall": round(avg("v2_recall"), 4),
        "jsonl_recall": round(avg("jsonl_recall"), 4),
        "v2_mrr": round(avg("v2_mrr"), 4),
        "jsonl_mrr": round(avg("jsonl_mrr"), 4),
        "wins": {"v2": wins("v2"), "jsonl": wins("jsonl"), "tie": wins("tie")},
    },
    "per_query": results,
}

with open(os.path.join(RESULTS, "full_benchmark.json"), "w", encoding="utf-8") as f:
    json.dump(final, f, ensure_ascii=False, indent=2)

print("\nResults saved to: %s" % os.path.join(RESULTS, "full_benchmark.json"))
print("=" * 70)
