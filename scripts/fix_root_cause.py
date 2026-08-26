"""
Oprava entries s 'see source' root_cause
Extrahuje skutečné root_cause ze zdrojového markdownu.

Build: 2026-08-26 | Author: outpost2026
"""

import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "..", "data")


def load_jsonl(path):
    entries = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))
    return entries


def save_jsonl(path, entries):
    with open(path, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def extract_root_causes_from_markdown(md_path):
    """Extrahuje root_cause ze zdrojového markdownu."""
    with open(md_path, encoding="utf-8") as f:
        content = f.read()

    root_causes = {}

    # Split by GT entries
    entries = re.split(r"(?=###\s*GT-\d+)", content)

    for entry in entries:
        # Extract GT ID
        id_match = re.match(r"###\s*(GT-\d+)", entry)
        if not id_match:
            continue
        gt_id = id_match.group(1)

        # Try to find root cause
        # Pattern 1: **Root cause:**
        rc_match = re.search(
            r"\*\*Root\s+cause.*?:\*\*\s*(.*?)(?=\n\s*\n|\n\s*\*\*|\Z)",
            entry,
            re.DOTALL | re.IGNORECASE,
        )
        if rc_match:
            root_causes[gt_id] = rc_match.group(1).strip()
            continue

        # Pattern 2: Root cause:
        rc_match = re.search(
            r"Root\s+cause.*?:\s*(.*?)(?=\n\s*\n|\n\s*\*\*|\Z)",
            entry,
            re.DOTALL | re.IGNORECASE,
        )
        if rc_match:
            root_causes[gt_id] = rc_match.group(1).strip()
            continue

        # Pattern 3: **ROOT CAUSE:**
        rc_match = re.search(
            r"\*\*ROOT\s+CAUSE.*?:\*\*\s*(.*?)(?=\n\s*\n|\n\s*\*\*|\Z)",
            entry,
            re.DOTALL | re.IGNORECASE,
        )
        if rc_match:
            root_causes[gt_id] = rc_match.group(1).strip()
            continue

        # Pattern 4: Look for fix section which often describes the root cause
        fix_match = re.search(
            r"(?:Fix| Oprava|Opraveno).*?:\s*(.*?)(?=\n\s*\n|\n\s*\*\*|\Z)",
            entry,
            re.DOTALL | re.IGNORECASE,
        )
        if fix_match:
            # Use first sentence of fix as root cause proxy
            fix_text = fix_match.group(1).strip()
            first_sentence = re.split(r"[.!?]\s", fix_text)[0]
            if len(first_sentence) > 20:
                root_causes[gt_id] = first_sentence

    return root_causes


def main():
    jsonl_path = os.path.join(DATA, "gt_full.jsonl")
    md_path = os.path.join(DATA, "MCP_GROUND_TRUTH_postmortem_agregovany_v2.md")

    entries = load_jsonl(jsonl_path)
    root_causes = extract_root_causes_from_markdown(md_path)

    print("Extrahováno %d root_cause ze markdownu" % len(root_causes))
    print(
        "Entries s 'see source': %d"
        % sum(1 for e in entries if "see source" in e.get("root_cause", "").lower())
    )

    # Update entries
    updated = 0
    for entry in entries:
        if "see source" in entry.get("root_cause", "").lower():
            gt_id = entry["id"]
            if gt_id in root_causes:
                new_rc = root_causes[gt_id]
                if len(new_rc) > 20:  # Only update if meaningful
                    entry["root_cause"] = new_rc
                    updated += 1
                    print("  Opraveno: %s -> %s" % (gt_id, new_rc[:80]))

    print("\nOpraveno %d/%d entries" % (updated, 30))

    # Save
    save_jsonl(jsonl_path, entries)
    print("Uloženo do %s" % jsonl_path)


if __name__ == "__main__":
    main()
