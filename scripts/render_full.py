"""Regenerate data/gt_catalog_full_render.md from data/gt_full.jsonl.

The render is a read-only mirror of the JSONL, used for human review; it must
never carry a placeholder that the JSONL no longer has.
"""

import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")

with open(os.path.join(DATA, "gt_full.jsonl"), encoding="utf-8") as f:
    entries = [json.loads(line) for line in f if line.strip()]


def field(entry, key, ref_key):
    value = entry.get(key) or ""
    if isinstance(value, list):
        value = ", ".join(str(x) for x in value)
    if not value:
        ref = entry.get(ref_key, "")
        return (
            "_(nedokumentovano v kanonu; viz %s)_" % ref
            if ref
            else "_(nedokumentovano)_"
        )
    return value


lines = [
    "# MCP GT — Katalog chyb (generated from full JSONL)",
    "",
    "**Entries:** %d | **Format:** JSONL-derived markdown" % len(entries),
    "",
]
for e in entries:
    aliases = " (%s)" % e["aliases"][0] if e.get("aliases") else ""
    lines.append("#### %s%s: %s" % (e["id"], aliases, e.get("typ", "unknown")))
    lines.append("**Server:** %s | **Status:** %s" % (e["server"], e["status"]))
    lines.append("")
    lines.append("**Symptom:** %s" % e.get("symptom", ""))
    lines.append("**Root cause:** %s" % field(e, "root_cause", "root_cause_ref"))
    lines.append("**Fix:** %s" % field(e, "fix", "fix_ref"))
    lines.append("**Pravidlo:** %s" % e.get("rule", ""))
    if e.get("tags"):
        lines.append("**Tags:** %s" % " | ".join(e["tags"]))
    lines.append("")

out = os.path.join(DATA, "gt_catalog_full_render.md")
with open(out, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(lines).rstrip("\n") + "\n")

print(
    "Rendered: %d entries, %d bytes -> %s" % (len(entries), os.path.getsize(out), out)
)
