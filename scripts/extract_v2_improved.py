import re, json, sys, os

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

V2 = r"C:\Users\PC\Documents\Repozitar_Dev\_github\B2B-Knowledge-Base\04_KNOWLEDGE_BASE\01_MCP\MCP_GROUND_TRUTH_postmortem_agregovany_v2.md"
OUT = r"C:\Users\PC\Documents\Repozitar_Dev\_github\TEMP_TRIMMING\formalization_demo\gt_full.jsonl"

with open(V2, encoding="utf-8") as f:
    text = f.read()

# ============================================================
# Section -> server mapping
# ============================================================
section_map = {}
for m in re.finditer(r"^###\s+3\.(\d+)\s+(.+)$", text, re.M):
    sec = m.group(1)
    names = {
        "1": "cnc-tools",
        "2": "linkedin-mcp-custom",
        "3": "mcp-jobs",
        "5": "lichess-analyzer",
        "6": "lichess-analyzer",
        "7": "gcp",
    }
    section_map[m.start()] = names.get(sec, "workspace")


def get_server(pos):
    best = "unknown"
    for start, srv in section_map.items():
        if start <= pos:
            best = srv
    return best


# ============================================================
# Extract GT entry blocks
# ============================================================
header_re = r"####\s+(GT-(?:GCP-)?\d{3})\s*(?:\(([^)]*)\))?:\s*(.+?)$"
headers = list(re.finditer(header_re, text, re.M))

entries = []
for i, m in enumerate(headers):
    gt_id = m.group(1)
    aliases_raw = m.group(2)
    title = m.group(3).strip()
    start = m.end()

    if i + 1 < len(headers):
        end = headers[i + 1].start()
    else:
        nxt = re.search(r"\n## [0-9]", text[start:])
        end = start + nxt.start() if nxt else len(text)

    block = text[start:end].strip()
    block = re.sub(r"\n---\s*$", "", block).strip()

    server = get_server(m.start())
    aliases = (
        [a.strip() for a in aliases_raw.split(",") if a.strip()] if aliases_raw else []
    )

    # ============================================================
    # Improved field extraction — handle variants
    # ============================================================
    def extract_field(block, *field_names):
        for fn in field_names:
            # Match **Field:** ... up to next **Field:** or #### or ## or --- or end
            pattern = rf"\*\*{re.escape(fn)}:\*\*\s*(.+?)(?=\n\*\*[^*]+\*\*|\n####|\n## [0-9]|\n---|\Z)"
            fm = re.search(pattern, block, re.S)
            if fm:
                val = fm.group(1).strip()
                # Clean: collapse internal newlines but keep structure
                val = re.sub(r"\n(?!\n)", " ", val)
                val = re.sub(r"\s+", " ", val)
                return val
        return None

    symptom = extract_field(block, "Symptom") or title
    root_cause = (
        extract_field(block, "Root cause", "Root cause (společný)")
        or extract_field(block, "Root cause (spolecny)")
        or extract_field(block, "Společný root cause")
        or "see source"
    )
    fix_raw = extract_field(block, "Fix (fix bugu)", "Fix") or "see source"
    provenance = (
        extract_field(block, "Provenance") or extract_field(block, "Source") or None
    )

    # Rule(s)
    rule_raw = extract_field(block, "Pravidlo", "Pravidla") or ""
    all_rules = re.findall(r"(P\d{1,2}(?:\s*[–-]\s*P\d{1,2})?|P-GCP-\d{2})", rule_raw)
    rule_primary = all_rules[0] if all_rules else None
    rules_secondary = all_rules[1:] if len(all_rules) > 1 else []

    # Status
    status_raw = extract_field(block, "Status") or ""
    status = "documented"
    sl = status_raw.lower()
    if "fixed" in sl:
        status = "fixed"
    elif "mitigat" in sl:
        status = "mitigated"
    elif "implement" in sl:
        status = "implemented"
    elif "workaround" in sl:
        status = "workaround"
    elif "pending" in sl:
        status = "pending"
    elif "document" in sl:
        status = "documented"

    # Type
    tl = title.lower()
    typ = "general"
    if any(w in tl for w in ["timeout", "deadlock"]):
        typ = "timeout"
    elif any(w in tl for w in ["encoding", "unicode", "ascii", "mojibake"]):
        typ = "encoding"
    elif any(w in tl for w in ["cache", "invalid"]):
        typ = "cache"
    elif any(w in tl for w in ["json", "corrupt", "data"]):
        typ = "data-integrity"
    elif any(w in tl for w in ["auth", "cookie", "pat", "credential", "403"]):
        typ = "auth"
    elif any(w in tl for w in ["scrap", "css", "selector", "paginat", "bot", "card"]):
        typ = "scraping"
    elif any(w in tl for w in ["test", "ruff", "lint", "contract", "flaky"]):
        typ = "tooling"
    elif any(
        w in tl for w in ["llm", "prompt", "cascade", "provider", "model", "token"]
    ):
        typ = "llm"
    elif any(w in tl for w in ["engine", "stockfish", "pv", "analysis", "depth"]):
        typ = "chess-engine"
    elif any(w in tl for w in ["regex", "salary", "filter", "exclude"]):
        typ = "parsing"
    elif any(
        w in tl
        for w in ["import", "modul", "circular", "package", "wheel", "dependency"]
    ):
        typ = "packaging"
    elif any(w in tl for w in ["subprocess", "pipe", "stderr"]):
        typ = "subprocess"
    elif any(w in tl for w in ["path", "traversal", "fs"]):
        typ = "filesystem"
    elif any(w in tl for w in ["gcp", "vm", "serverless", "cron", "cloud"]):
        typ = "infrastructure"
    elif any(w in tl for w in ["git", "deploy", "ci/cd"]):
        typ = "devops"
    elif any(w in tl for w in ["pattern", "detection", "diagnostic", "snr"]):
        typ = "analytics"
    elif any(w in tl for w in ["frontend", "streamlit", "layout", "react"]):
        typ = "frontend"
    elif any(w in tl for w in ["overlap", "dedup", "fuzzy"]):
        typ = "dedup"

    # Complexity
    complexity = "simple"
    sub_bugs = []
    if "Bug list" in block or "merged bug" in tl or ("batch" in tl and "fix" in tl):
        complexity = "complex"
        bug_matches = re.findall(
            r"\*\*(B\d+)\*\*[:\.]\s*(.+?)(?=\n\d+\.|\n\*\*|\Z)", block, re.S
        )
        for bid, bdesc in bug_matches:
            sub_bugs.append({"id": bid, "description": bdesc.strip()[:200]})
    elif len(block) > 400:
        complexity = "moderate"

    # Tags
    tags = []
    if rule_primary:
        tags.append(rule_primary.lower())
    for kw in [
        "timeout",
        "encoding",
        "cache",
        "json",
        "auth",
        "scraping",
        "test",
        "llm",
        "engine",
        "regex",
        "import",
        "subprocess",
        "path",
        "gcp",
        "git",
        "deploy",
        "pattern",
        "frontend",
        "security",
        "dedup",
    ]:
        if kw in tl:
            tags.append(kw)

    # Build entry
    entry = {
        "id": gt_id,
        "aliases": aliases if aliases else None,
        "server": server,
        "status": status,
        "typ": typ,
        "symptom": symptom,
        "root_cause": root_cause,
        "fix": fix_raw,
        "rule": rule_primary,
        "rules_secondary": rules_secondary if rules_secondary else None,
        "provenance": provenance,
        "tags": tags if tags else None,
        "complexity": complexity,
        "sub_bugs": sub_bugs if sub_bugs else None,
    }
    entry = {k: v for k, v in entry.items() if v is not None}
    entries.append(entry)

# ============================================================
# Post-fix: infer missing rules
# ============================================================
rule_inference = {
    "GT-015": ("P9", ["playwright"]),
    "GT-019": ("P9", ["pagination"]),
    "GT-021": ("P9", ["extraction"]),
    "GT-022": ("P9", ["dedup"]),
    "GT-023": ("P9", ["idempotency"]),
    "GT-024": ("P11", ["python"]),
    "GT-027": ("P9", ["cookies"]),
    "GT-028": ("P9", ["git"]),
    "GT-029": ("P27", ["testing"]),
    "GT-032": ("P9", ["parsing"]),
    "GT-033": ("P13", ["pipeline"]),
    "GT-034": ("P9", ["llm"]),
    "GT-035": ("P9", ["parsing"]),
    "GT-036": ("P13", ["guardrails"]),
    "GT-037": ("P9", ["config"]),
    "GT-038": ("P9", ["mcp"]),
    "GT-039": ("P9", ["config"]),
    "GT-041": ("P23", ["encoding"]),
    "GT-042": ("P17", ["session"]),
    "GT-051": ("P36", ["provider"]),
    "GT-053": ("P37", ["cost"]),
    "GT-054": ("P39", ["api-key"]),
    "GT-057": ("P42", ["timeout"]),
    "GT-064": ("P48", ["analytics"]),
    "GT-066": ("P50", ["pipeline"]),
    "GT-067": ("P51", ["warning"]),
    "GT-068": ("P52", ["api"]),
    "GT-069": ("P53", ["tool-cache"]),
    "GT-073": ("P56", ["depth"]),
    "GT-086": ("P72", ["lint"]),
    "GT-092": ("P76", ["bot-detection"]),
    "GT-093": ("P27", ["testing"]),
    "GT-094": ("P77", ["end-of-list"]),
    "GT-099": ("P90", ["frontend"]),
    "GT-101": ("P92", ["dependency"]),
    "GT-102": ("P93", ["wheel"]),
    "GT-103": ("P94", ["introspection"]),
    "GT-104": ("P95", ["logging"]),
    "GT-105": ("P96", ["testing"]),
}

for e in entries:
    if "rule" not in e and e["id"] in rule_inference:
        rule, extra = rule_inference[e["id"]]
        e["rule"] = rule
        if "tags" not in e:
            e["tags"] = []
        e["tags"].extend(extra)

# ============================================================
# Write JSONL
# ============================================================
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    for e in entries:
        f.write(json.dumps(e, ensure_ascii=False) + "\n")

# Stats
valid = sum(1 for e in entries if "rule" in e)
has_rootcause = sum(1 for e in entries if e.get("root_cause") != "see source")
has_fix = sum(1 for e in entries if e.get("fix") != "see source")
print("Extracted: %d entries" % len(entries))
print("Valid (rule): %d/%d" % (valid, len(entries)))
print("Has root_cause: %d/%d" % (has_rootcause, len(entries)))
print("Has fix: %d/%d" % (has_fix, len(entries)))
print("Size: %d bytes" % os.path.getsize(OUT))
