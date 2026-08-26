import json, sys, os

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")
BASE = r"C:\Users\PC\Documents\Repozitar_Dev\_github\TEMP_TRIMMING\formalization_demo"

entries = []
with open(os.path.join(BASE, "gt_full.jsonl"), encoding="utf-8") as f:
    for line in f:
        if line.strip():
            entries.append(json.loads(line))

# Infer rules for entries missing them based on content/title
rule_inference = {
    "GT-015": ("P9", ["playwright", "browser"]),
    "GT-019": ("P9", ["scraping", "pagination"]),
    "GT-021": ("P9", ["scraping", "extraction"]),
    "GT-022": ("P9", ["dedup", "data-integrity"]),
    "GT-023": ("P9", ["idempotency", "scraping"]),
    "GT-024": ("P11", ["python", "version"]),
    "GT-027": ("P9", ["cookies", "export"]),
    "GT-028": ("P9", ["git", "auth"]),
    "GT-029": ("P27", ["testing", "scorer"]),
    "GT-032": ("P9", ["parsing", "exclude"]),
    "GT-033": ("P13", ["pipeline", "etl"]),
    "GT-034": ("P9", ["llm", "dev"]),
    "GT-035": ("P9", ["parsing", "ast"]),
    "GT-036": ("P13", ["guardrails", "rate-limit"]),
    "GT-039": ("P9", ["config", "lint"]),
    "GT-042": ("P17", ["mcp", "session"]),
    "GT-051": ("P36", ["llm", "provider"]),
    "GT-053": ("P37", ["llm", "cost"]),
    "GT-054": ("P39", ["llm", "api-key"]),
    "GT-057": ("P42", ["nvidia", "timeout"]),
    "GT-066": ("P50", ["pipeline", "clamp"]),
    "GT-067": ("P51", ["pipeline", "warning"]),
    "GT-068": ("P52", ["berserk", "api"]),
    "GT-069": ("P53", ["mcp", "tool-cache"]),
    "GT-086": ("P72", ["lint", "config"]),
    "GT-092": ("P76", ["scraping", "bot-detection"]),
    "GT-093": ("P27", ["testing", "pollution"]),
    "GT-094": ("P77", ["scraping", "end-of-list"]),
    "GT-099": ("P90", ["frontend", "streamlit"]),
    "GT-101": ("P92", ["packaging", "dependency"]),
    "GT-102": ("P93", ["packaging", "wheel"]),
    "GT-103": ("P94", ["parsing", "introspection"]),
    "GT-104": ("P95", ["logging", "framework"]),
    "GT-105": ("P96", ["testing", "flaky"]),
}

updated = 0
for e in entries:
    if "rule" not in e:
        if e["id"] in rule_inference:
            rule, extra_tags = rule_inference[e["id"]]
            e["rule"] = rule
            if "tags" not in e:
                e["tags"] = []
            e["tags"].extend(extra_tags)
            updated += 1

# Write back
with open(
    os.path.join(BASE, "gt_full.jsonl"), "w", encoding="utf-8", newline="\n"
) as f:
    for e in entries:
        f.write(json.dumps(e, ensure_ascii=False) + "\n")

valid = sum(1 for e in entries if "rule" in e)
print(f"Updated {updated} entries with inferred rules")
print(f"Total: {len(entries)} entries, {valid} valid (with rule)")
