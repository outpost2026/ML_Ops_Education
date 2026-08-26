import sys, os, json, re, time
from difflib import SequenceMatcher

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE = r"C:\Users\PC\Documents\Repozitar_Dev\_github\TEMP_TRIMMING\formalization_demo"
V2 = r"C:\Users\PC\Documents\Repozitar_Dev\_github\B2B-Knowledge-Base\04_KNOWLEDGE_BASE\01_MCP\MCP_GROUND_TRUTH_postmortem_agregovany_v2.md"
RESULTS = os.path.join(BASE, "results")

os.makedirs(RESULTS, exist_ok=True)

# ============================================================
# PART 1: Parse v2 markdown into structured entries (baseline)
# ============================================================


def parse_v2_entries(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    entries = {}
    pattern = r"#### (GT-(?:GCP-)?\d{3})\s*(?:\([^)]*\))?:\s*(.+?)\n"
    for m in re.finditer(pattern, text):
        gt_id = m.group(1)
        title = m.group(2).strip()
        start = m.end()
        next_header = re.search(r"\n####|\n## [0-9]", text[start:])
        end = start + next_header.start() if next_header else len(text)
        block = text[start:end].strip()
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
                rf"\*\*{re.escape(field)}\*\*\s*(.+?)(?=\n\*\*|\n####|\n##|\Z)",
                block,
                re.S,
            )
            if fm:
                entry[key] = fm.group(1).strip()
        entries[gt_id] = entry
    return entries


# ============================================================
# PART 2: Load JSONL entries
# ============================================================


def load_jsonl(path):
    entries = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            entries[rec["id"]] = rec
    return entries


# ============================================================
# PART 3: Fuzzy retrieval
# ============================================================


def searchable_text_v2(entry):
    parts = []
    for k in ["title", "symptom", "root_cause", "fix", "server", "status"]:
        v = entry.get(k, "")
        if isinstance(v, list):
            v = " ".join(str(x) for x in v)
        parts.append(str(v))
    return " ".join(parts).lower()


def searchable_text_jsonl(entry):
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


# ============================================================
# PART 4: Compression metrics
# ============================================================


def measure_tokens(text):
    try:
        import tiktoken

        enc = tiktoken.get_encoding("o200k_base")
        return len(enc.encode(text))
    except Exception:
        return len(text) // 4


def compression_metrics(entries, text_fn, label):
    total_bytes = 0
    total_tokens = 0
    total_chars = 0
    for gid, entry in entries.items():
        txt = text_fn(entry)
        total_bytes += len(txt.encode("utf-8"))
        total_tokens += measure_tokens(txt)
        total_chars += len(txt)
    n = len(entries)
    return {
        "format": label,
        "entries": n,
        "total_bytes": total_bytes,
        "total_tokens": total_tokens,
        "avg_bytes_per_entry": total_bytes / n if n else 0,
        "avg_tokens_per_entry": total_tokens / n if n else 0,
        "avg_chars_per_entry": total_chars / n if n else 0,
    }


# ============================================================
# PART 5: Load queries and run
# ============================================================

print("=" * 60)
print("GT FORMALIZATION DEMO — Retrieval + Compression Test")
print("=" * 60)

# Load data
v2_entries = parse_v2_entries(V2)
jsonl_entries = load_jsonl(os.path.join(BASE, "gt_sample.jsonl"))
with open(os.path.join(BASE, "test_queries.json"), encoding="utf-8") as f:
    queries = json.load(f)

print(
    f"\nLoaded: {len(v2_entries)} v2 entries, {len(jsonl_entries)} JSONL entries, {len(queries)} queries"
)

# Filter v2 to only entries present in JSONL sample
jsonl_ids = set(jsonl_entries.keys())
v2_filtered = {k: v for k, v in v2_entries.items() if k in jsonl_ids}
print(f"Filtered v2 to {len(v2_filtered)} entries (matching JSONL sample)")

# ============================================================
# RETRIEVAL TEST
# ============================================================

print("\n" + "=" * 60)
print("RETRIEVAL TEST")
print("=" * 60)

results_retrieval = []

for q in queries:
    qid = q["id"]
    qcz = q["query_cz"]
    qen = q["query_en"]
    expected = set(q["expected"])

    for lang, query in [("CZ", qcz), ("EN", qen)]:
        t0 = time.time()
        res_v2 = retrieve(query, v2_filtered, searchable_text_v2, top_k=5)
        lat_v2 = (time.time() - t0) * 1000

        t0 = time.time()
        res_jsonl = retrieve(query, jsonl_entries, searchable_text_jsonl, top_k=5)
        lat_jsonl = (time.time() - t0) * 1000

        top3_v2 = [r[0] for r in res_v2[:3]]
        top3_jsonl = [r[0] for r in res_jsonl[:3]]

        hits_v2 = len(expected & set(top3_v2))
        hits_jsonl = len(expected & set(top3_jsonl))

        mrr_v2 = 0
        for rank, (gid, score, _) in enumerate(res_v2, 1):
            if gid in expected:
                mrr_v2 = 1.0 / rank
                break

        mrr_jsonl = 0
        for rank, (gid, score, _) in enumerate(res_jsonl, 1):
            if gid in expected:
                mrr_jsonl = 1.0 / rank
                break

        recall_v2 = len(expected & set(top3_v2)) / len(expected) if expected else 0
        recall_jsonl = (
            len(expected & set(top3_jsonl)) / len(expected) if expected else 0
        )

        rec = {
            "query_id": qid,
            "lang": lang,
            "query": query,
            "expected": list(expected),
            "v2_top3": top3_v2,
            "jsonl_top3": top3_jsonl,
            "v2_precision@3": hits_v2 / 3,
            "jsonl_precision@3": hits_jsonl / 3,
            "v2_recall": recall_v2,
            "jsonl_recall": recall_jsonl,
            "v2_mrr": mrr_v2,
            "jsonl_mrr": mrr_jsonl,
            "v2_latency_ms": round(lat_v2, 2),
            "jsonl_latency_ms": round(lat_jsonl, 2),
            "winner": "jsonl"
            if (mrr_jsonl > mrr_v2 or hits_jsonl > hits_v2)
            else ("v2" if hits_v2 > hits_jsonl else "tie"),
        }
        results_retrieval.append(rec)

# Aggregate
total = len(results_retrieval)
v2_wins = sum(1 for r in results_retrieval if r["winner"] == "v2")
jsonl_wins = sum(1 for r in results_retrieval if r["winner"] == "jsonl")
ties = sum(1 for r in results_retrieval if r["winner"] == "tie")

avg_v2_p3 = sum(r["v2_precision@3"] for r in results_retrieval) / total
avg_jsonl_p3 = sum(r["jsonl_precision@3"] for r in results_retrieval) / total
avg_v2_recall = sum(r["v2_recall"] for r in results_retrieval) / total
avg_jsonl_recall = sum(r["jsonl_recall"] for r in results_retrieval) / total
avg_v2_mrr = sum(r["v2_mrr"] for r in results_retrieval) / total
avg_jsonl_mrr = sum(r["jsonl_mrr"] for r in results_retrieval) / total
avg_v2_lat = sum(r["v2_latency_ms"] for r in results_retrieval) / total
avg_jsonl_lat = sum(r["jsonl_latency_ms"] for r in results_retrieval) / total

print(f"\n--- Aggregate Results ({total} queries) ---")
print(f"{'Metric':<25} {'v2 Markdown':>15} {'JSONL':>15} {'Winner':>10}")
print("-" * 65)
print(
    f"{'Precision@3':<25} {avg_v2_p3:>15.3f} {avg_jsonl_p3:>15.3f} {'JSONL' if avg_jsonl_p3 > avg_v2_p3 else 'v2':>10}"
)
print(
    f"{'Recall':<25} {avg_v2_recall:>15.3f} {avg_jsonl_recall:>15.3f} {'JSONL' if avg_jsonl_recall > avg_v2_recall else 'v2':>10}"
)
print(
    f"{'MRR':<25} {avg_v2_mrr:>15.3f} {avg_jsonl_mrr:>15.3f} {'JSONL' if avg_jsonl_mrr > avg_v2_mrr else 'v2':>10}"
)
print(
    f"{'Avg latency (ms)':<25} {avg_v2_lat:>15.1f} {avg_jsonl_lat:>15.1f} {'JSONL' if avg_jsonl_lat < avg_v2_lat else 'v2':>10}"
)
print(
    f"{'Win/Loss/Tie':<25} {'  ' + str(v2_wins) + 'W':>15} {'  ' + str(jsonl_wins) + 'W':>15} {str(ties) + 'T':>10}"
)

# ============================================================
# COMPRESSION TEST
# ============================================================

print("\n" + "=" * 60)
print("COMPRESSION TEST")
print("=" * 60)

v2_metrics = compression_metrics(
    v2_filtered, searchable_text_v2, "v2 Markdown (filtered)"
)
jsonl_metrics = compression_metrics(jsonl_entries, searchable_text_jsonl, "JSONL")
jsonl_raw = compression_metrics(
    jsonl_entries, lambda e: json.dumps(e, ensure_ascii=False), "JSONL (raw records)"
)

# Extrapolate to 108 entries
scale = 108 / len(jsonl_entries)

print(f"\n--- Per-Format Metrics ---")
print(f"{'Metric':<30} {'v2 (15 ent.)':>18} {'JSONL (22 ent.)':>18} {'JSONL raw':>18}")
print("-" * 84)
print(
    f"{'Total bytes':<30} {v2_metrics['total_bytes']:>18,} {jsonl_metrics['total_bytes']:>18,} {jsonl_raw['total_bytes']:>18,}"
)
print(
    f"{'Total tokens':<30} {v2_metrics['total_tokens']:>18,} {jsonl_metrics['total_tokens']:>18,} {jsonl_raw['total_tokens']:>18,}"
)
print(
    f"{'Avg bytes/entry':<30} {v2_metrics['avg_bytes_per_entry']:>18.0f} {jsonl_metrics['avg_bytes_per_entry']:>18.0f} {jsonl_raw['avg_bytes_per_entry']:>18.0f}"
)
print(
    f"{'Avg tokens/entry':<30} {v2_metrics['avg_tokens_per_entry']:>18.0f} {jsonl_metrics['avg_tokens_per_entry']:>18.0f} {jsonl_raw['avg_tokens_per_entry']:>18.0f}"
)

# Full file size comparison
v2_full_size = os.path.getsize(V2)
jsonl_extrapolated_bytes = jsonl_raw["avg_bytes_per_entry"] * 108
jsonl_extrapolated_tokens = jsonl_raw["avg_tokens_per_entry"] * 108

print(f"\n--- Extrapolation to 108 entries ---")
print(f"{'Metric':<30} {'v2 (full file)':>18} {'JSONL (extrapol.)':>18} {'Delta':>12}")
print("-" * 78)
print(
    f"{'Bytes':<30} {v2_full_size:>18,} {jsonl_extrapolated_bytes:>18,.0f} {((jsonl_extrapolated_bytes / v2_full_size) - 1) * 100:>+11.1f}%"
)
print(
    f"{'Tokens':<30} {measure_tokens(open(V2, encoding='utf-8').read()):>18,} {jsonl_extrapolated_tokens:>18,.0f} {((jsonl_extrapolated_tokens / measure_tokens(open(V2, encoding='utf-8').read())) - 1) * 100:>+11.1f}%"
)

# ============================================================
# SAVE RESULTS
# ============================================================

results_all = {
    "retrieval": {
        "aggregate": {
            "total_queries": total,
            "v2_precision@3": round(avg_v2_p3, 4),
            "jsonl_precision@3": round(avg_jsonl_p3, 4),
            "v2_recall": round(avg_v2_recall, 4),
            "jsonl_recall": round(avg_jsonl_recall, 4),
            "v2_mrr": round(avg_v2_mrr, 4),
            "jsonl_mrr": round(avg_jsonl_mrr, 4),
            "v2_avg_latency_ms": round(avg_v2_lat, 2),
            "jsonl_avg_latency_ms": round(avg_jsonl_lat, 2),
            "wins": {"v2": v2_wins, "jsonl": jsonl_wins, "tie": ties},
        },
        "per_query": results_retrieval,
    },
    "compression": {
        "v2_filtered": v2_metrics,
        "jsonl_text": jsonl_metrics,
        "jsonl_raw": jsonl_raw,
        "extrapolation": {
            "v2_full_bytes": v2_full_size,
            "v2_full_tokens": measure_tokens(open(V2, encoding="utf-8").read()),
            "jsonl_extrapolated_bytes": round(jsonl_extrapolated_bytes),
            "jsonl_extrapolated_tokens": round(jsonl_extrapolated_tokens),
        },
    },
}

with open(
    os.path.join(RESULTS, "retrieval_comparison.json"), "w", encoding="utf-8"
) as f:
    json.dump(results_all["retrieval"], f, ensure_ascii=False, indent=2)

with open(
    os.path.join(RESULTS, "compression_comparison.json"), "w", encoding="utf-8"
) as f:
    json.dump(results_all["compression"], f, ensure_ascii=False, indent=2)

print(f"\nResults saved to {RESULTS}")
print("=" * 60)
