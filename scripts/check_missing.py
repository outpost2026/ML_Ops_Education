import json, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
entries = []
with open(
    r"C:\Users\PC\Documents\Repozitar_Dev\_github\TEMP_TRIMMING\formalization_demo\gt_full.jsonl",
    encoding="utf-8",
) as f:
    for line in f:
        if line.strip():
            entries.append(json.loads(line))
for e in entries:
    if "rule" not in e:
        print("%s: %s | %s" % (e["id"], e.get("typ", "?"), e["symptom"][:80]))
