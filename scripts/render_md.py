import json, sys, os

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")
BASE = r"C:\Users\PC\Documents\Repozitar_Dev\_github\TEMP_TRIMMING\formalization_demo"
entries = []
with open(os.path.join(BASE, "gt_sample.jsonl"), encoding="utf-8") as f:
    for line in f:
        if line.strip():
            entries.append(json.loads(line))
lines = [
    "# MCP GT Katalog chyb (generated from JSONL)",
    "",
    "Entries: %d | Format: JSONL-derived markdown" % len(entries),
    "",
]
for e in entries:
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
with open(
    os.path.join(BASE, "gt_catalog_render.md"), "w", encoding="utf-8", newline="\n"
) as f:
    f.write("\n".join(lines) + "\n")
print(
    "Rendered: %d entries, %d bytes"
    % (len(entries), os.path.getsize(os.path.join(BASE, "gt_catalog_render.md")))
)
