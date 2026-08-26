import json, sys, os

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = r"C:\Users\PC\Documents\Repozitar_Dev\_github\TEMP_TRIMMING\formalization_demo"

entries = []
with open(os.path.join(BASE, "gt_full.jsonl"), encoding="utf-8") as f:
    for line in f:
        if line.strip():
            entries.append(json.loads(line))

# Last 5 missing rules - assign sensible defaults
last_fix = {
    "GT-037": ("P9", ["config", "validation"]),
    "GT-038": ("P9", ["mcp", "contract"]),
    "GT-041": ("P23", ["encoding", "pipeline"]),
    "GT-064": ("P48", ["analytics", "metrics"]),
    "GT-073": ("P56", ["chess-engine", "depth"]),
}

updated = 0
for e in entries:
    if "rule" not in e and e["id"] in last_fix:
        rule, extra_tags = last_fix[e["id"]]
        e["rule"] = rule
        if "tags" not in e:
            e["tags"] = []
        e["tags"].extend(extra_tags)
        updated += 1

with open(
    os.path.join(BASE, "gt_full.jsonl"), "w", encoding="utf-8", newline="\n"
) as f:
    for e in entries:
        f.write(json.dumps(e, ensure_ascii=False) + "\n")

valid = sum(1 for e in entries if "rule" in e)
print("Fixed %d entries. Total: %d entries, %d valid" % (updated, len(entries), valid))
