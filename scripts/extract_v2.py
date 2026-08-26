import re, json, sys, os

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

V2 = r"C:\Users\PC\Documents\Repozitar_Dev\_github\B2B-Knowledge-Base\04_KNOWLEDGE_BASE\01_MCP\MCP_GROUND_TRUTH_postmortem_agregovany_v2.md"
OUT = r"C:\Users\PC\Documents\Repozitar_Dev\_github\TEMP_TRIMMING\formalization_demo\gt_full.jsonl"
SCHEMA = r"C:\Users\PC\Documents\Repozitar_Dev\_github\TEMP_TRIMMING\formalization_demo\gt_schema.json"

with open(V2, encoding="utf-8") as f:
    text = f.read()

# ============================================================
# 1. Detect section boundaries (server mapping)
# ============================================================

section_map = {}
current_server = None
for m in re.finditer(r"^###\s+3\.(\d+)\s+(.+)$", text, re.M):
    sec_num = m.group(1)
    sec_title = m.group(2).strip()
    server_names = {
        "1": "cnc-tools",
        "2": "linkedin-mcp-custom",
        "3": "mcp-jobs",
        "5": "lichess-analyzer",
        "6": "lichess-analyzer",
        "7": "gcp",
    }
    current_server = server_names.get(sec_num, "workspace")
    section_map[m.start()] = current_server

# Also map GCP section
gcp_match = re.search(r"^###\s+3\.7\s+GCP", text, re.M)
if gcp_match:
    section_map[gcp_match.start()] = "gcp"

# workspace entries (GT-080)
workspace_match = re.search(r"GT-080.*workspace", text)
if workspace_match:
    section_map[workspace_match.start()] = "workspace"


def get_server(pos):
    best = "unknown"
    for start, srv in section_map.items():
        if start <= pos:
            best = srv
    return best


# ============================================================
# 2. Extract GT entry blocks
# ============================================================

header_pattern = r"####\s+(GT-(?:GCP-)?\d{3})\s*(?:\(([^)]*)\))?:\s*(.+?)$"
headers = list(re.finditer(header_pattern, text, re.M))

entries = []
for i, m in enumerate(headers):
    gt_id = m.group(1)
    aliases_raw = m.group(2)
    title = m.group(3).strip()
    start = m.end()

    # End of block = next header or next ## section
    if i + 1 < len(headers):
        end = headers[i + 1].start()
    else:
        next_section = re.search(r"\n## [0-9]", text[start:])
        end = start + next_section.start() if next_section else len(text)

    block = text[start:end].strip()

    # Strip trailing --- separator
    block = re.sub(r"\n---\s*$", "", block).strip()

    # Server from section
    server = get_server(m.start())

    # Aliases
    aliases = []
    if aliases_raw:
        aliases = [a.strip() for a in aliases_raw.split(",") if a.strip()]

    # Parse fields
    def extract_field(field_name, block):
        pattern = (
            rf"\*\*{re.escape(field_name)}:\*\*\s*(.+?)(?=\n\*\*|\n####|\n## |\n---|\Z)"
        )
        fm = re.search(pattern, block, re.S)
        if fm:
            val = fm.group(1).strip()
            # Clean up markdown artifacts
            val = re.sub(r"\n\s*", " ", val)
            val = re.sub(r"\s+", " ", val)
            return val
        return None

    symptom = extract_field("Symptom", block)
    root_cause = extract_field("Root cause", block)
    fix_raw = extract_field("Fix", block) or extract_field("Fix (fix bugu)", block)
    provenance = extract_field("Provenance", block)

    # Rule(s)
    rule_raw = extract_field("Pravidlo", block) or extract_field("Pravidla", block)
    rule_primary = None
    rules_secondary = []
    if rule_raw:
        rule_match = re.findall(r"P(?:–|-)?(\d{1,2})|P-GCP-\d{2}", rule_raw)
        all_rules = re.findall(
            r"(P\d{1,2}(?:\s*[–-]\s*P\d{1,2})?|P-GCP-\d{2})", rule_raw
        )
        if all_rules:
            rule_primary = all_rules[0]
            rules_secondary = all_rules[1:]

    # Status
    status_raw = extract_field("Status", block)
    status = "documented"
    if status_raw:
        sl = status_raw.lower()
        if "fixed" in sl and "mitigat" in sl:
            status = "fixed"
        elif "fixed" in sl:
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

    # Type from title
    title_lower = title.lower()
    typ = "general"
    if any(w in title_lower for w in ["timeout", "deadlock"]):
        typ = "timeout"
    elif any(w in title_lower for w in ["encoding", "unicode", "ascii", "mojibake"]):
        typ = "encoding"
    elif any(w in title_lower for w in ["cache", "invalid"]):
        typ = "cache"
    elif any(w in title_lower for w in ["json", "corrupt", "data"]):
        typ = "data-integrity"
    elif any(w in title_lower for w in ["auth", "cookie", "pat", "credential", "403"]):
        typ = "auth"
    elif any(w in title_lower for w in ["scrap", "css", "selector", "paginat", "bot"]):
        typ = "scraping"
    elif any(w in title_lower for w in ["test", "ruff", "lint", "contract"]):
        typ = "tooling"
    elif any(
        w in title_lower for w in ["llm", "prompt", "cascade", "provider", "model"]
    ):
        typ = "llm"
    elif any(w in title_lower for w in ["engine", "stockfish", "pv", "analysis"]):
        typ = "chess-engine"
    elif any(w in title_lower for w in ["regex", "salary", "filter", "exclude"]):
        typ = "parsing"
    elif any(
        w in title_lower
        for w in ["import", "modul", "circular", "package", "wheel", "dependency"]
    ):
        typ = "packaging"
    elif any(w in title_lower for w in ["subprocess", "pipe", "stderr"]):
        typ = "subprocess"
    elif any(w in title_lower for w in ["path", "traversal", "fs"]):
        typ = "filesystem"
    elif any(w in title_lower for w in ["gcp", "vm", "serverless", "cron", "cloud"]):
        typ = "infrastructure"
    elif any(w in title_lower for w in ["git", "deploy", "ci/cd"]):
        typ = "devops"
    elif any(w in title_lower for w in ["pattern", "detection", "diagnostic"]):
        typ = "analytics"
    elif any(w in title_lower for w in ["frontend", "streamlit", "layout", "react"]):
        typ = "frontend"

    # Complexity
    complexity = "simple"
    sub_bugs = []
    if "Bug list" in block or "merged bug" in title_lower or "batch" in title_lower:
        complexity = "complex"
        bug_matches = re.findall(
            r"\*\*(B\d+)\*\*:\s*(.+?)(?=\n\d+\.|\n\*\*|\Z)", block, re.S
        )
        for bid, bdesc in bug_matches:
            sub_bugs.append({"id": bid, "description": bdesc.strip()[:200]})
    elif len(block) > 500 or fix_raw and len(fix_raw) > 200:
        complexity = "moderate"

    # Tags from rule + title keywords
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
    ]:
        if kw in title_lower:
            tags.append(kw)

    # Build entry
    entry = {
        "id": gt_id,
        "aliases": aliases if aliases else None,
        "server": server,
        "status": status,
        "typ": typ,
        "symptom": symptom or title,
        "root_cause": root_cause or "see source",
        "fix": fix_raw or "see source",
        "rule": rule_primary,
        "rules_secondary": rules_secondary if rules_secondary else None,
        "provenance": provenance,
        "tags": tags if tags else None,
        "complexity": complexity,
        "sub_bugs": sub_bugs if sub_bugs else None,
    }

    # Remove None values for cleaner output
    entry = {k: v for k, v in entry.items() if v is not None}

    entries.append(entry)

# ============================================================
# 3. Validate against schema (manual check)
# ============================================================

required = ["id", "server", "status", "symptom", "root_cause", "fix", "rule"]
valid = 0
issues = []
for e in entries:
    missing = [f for f in required if f not in e]
    if missing:
        issues.append(f"{e['id']}: missing {missing}")
    else:
        valid += 1

# ============================================================
# 4. Write JSONL
# ============================================================

with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    for e in entries:
        f.write(json.dumps(e, ensure_ascii=False) + "\n")

# ============================================================
# 5. Stats
# ============================================================

print(f"Extracted: {len(entries)} entries")
print(f"Valid: {valid}/{len(entries)}")
if issues:
    print(f"Issues:")
    for iss in issues[:10]:
        print(f"  {iss}")

# Status distribution
statuses = {}
servers = {}
types = {}
complexities = {}
for e in entries:
    statuses[e["status"]] = statuses.get(e["status"], 0) + 1
    servers[e["server"]] = servers.get(e["server"], 0) + 1
    types[e["typ"]] = types.get(e["typ"], 0) + 1
    complexities[e["complexity"]] = complexities.get(e["complexity"], 0) + 1

print(f"\nStatus: {statuses}")
print(f"Server: {servers}")
print(f"Type: {types}")
print(f"Complexity: {complexities}")

size = os.path.getsize(OUT)
print(f"\nOutput: {OUT}")
print(f"Size: {size:,} bytes")
