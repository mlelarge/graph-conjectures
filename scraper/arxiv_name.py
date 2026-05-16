#!/usr/bin/env python3
"""
scraper/arxiv_name.py — generate a short descriptive name for one arxiv
conjecture via `claude -p` (no web tools).

For one review_id (a key in data/arxiv_conjectures.json, format
<safe_id>__<NN>):
  1. Load the conjecture record.
  2. Compose a small user prompt with statement + context + paper metadata.
  3. Call `claude -p` with scraper/arxiv_name_system_prompt.md attached as
     --append-system-prompt, no allowed tools (text-only naming task).
  4. Read the response, take the first non-empty line, write
     data/arxiv_names/<review_id>.json with {review_id, nice_name, model,
     generated_at}.

Usage
-----
    python scraper/arxiv_name.py --review-id 1608.03040__00
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

PROJECT            = Path(__file__).resolve().parent.parent
SYSTEM_PROMPT_PATH = Path(__file__).parent / "arxiv_name_system_prompt.md"
TIMEOUT_SCRIPT     = PROJECT / "scripts" / "timeout_claude.py"
PER_NAME_TIMEOUT   = int(os.environ.get("PER_NAME_TIMEOUT", 120))

log = logging.getLogger(__name__)


def _load_record(review_id: str, states_file: Path) -> dict | None:
    """Same lookup logic as arxiv_review.py: review_id = <safe_id>__<NN>."""
    if "__" in review_id:
        safe_id, idx_str = review_id.rsplit("__", 1)
        try:
            target_idx = int(idx_str)
        except ValueError:
            safe_id, target_idx = review_id, 0
    else:
        safe_id, target_idx = review_id, 0

    states = json.loads(states_file.read_text(encoding="utf-8"))
    counters: dict[str, int] = {}
    for s in states:
        sid = s.get("safe_id") or s.get("arxiv_id","").replace("/","_")
        i = counters.get(sid, 0)
        if sid == safe_id and i == target_idx:
            return s
        counters[sid] = i + 1
    return None


def _build_user_prompt(rec: dict) -> str:
    """Compact prompt — statement + context + minimal metadata."""
    paper_internal = rec.get("title", "") or "?"
    attrib = rec.get("attributed_to", "paper authors") or "paper authors"
    return "\n".join([
        "Generate one short descriptive name (≤ 7 words) for this conjecture.",
        "",
        f"Paper-internal label: {paper_internal}",
        f"Kind                : {rec.get('kind','Conjecture')}",
        f"Source paper        : {rec.get('paper_title','')}",
        f"Source authors      : {', '.join(rec.get('paper_authors', []))}",
        f"Attribution recorded: {attrib}",
        "",
        "Statement (verbatim LaTeX):",
        rec.get("statement_text","") or "(empty)",
        "",
        "Context:",
        rec.get("context_text","") or "(none)",
        "",
        "Output: just the name on a single line. No quotes, no preamble.",
    ])


def _clean_name(raw: str) -> str:
    """Pull the first non-empty line; strip quotes / surrounding noise.

    Hard-caps at 80 chars so a runaway response doesn't pollute the index.
    """
    if not raw:
        return ""
    for line in raw.strip().splitlines():
        line = line.strip().strip('"').strip("'").strip()
        # Drop common preambles the model might emit despite instructions.
        line = re.sub(r"^(name\s*:\s*)", "", line, flags=re.IGNORECASE)
        if line:
            return line[:80]
    return ""


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--review-id",
                   help="Unique key <safe_id>__<NN>.")
    g.add_argument("--safe-id",
                   help="Legacy form; treated as <safe_id>__00.")
    ap.add_argument("--states-file", type=Path,
                    default=PROJECT / "data" / "arxiv_conjectures.json")
    ap.add_argument("--out-dir",     type=Path,
                    default=PROJECT / "data" / "arxiv_names")
    ap.add_argument("--model",       default="claude-sonnet-4-6")
    ap.add_argument("--dry-run",     action="store_true",
                    help="Print the composed prompt; do not call claude.")
    ap.add_argument("--verbose","-v", action="store_true")
    args = ap.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s  %(levelname)-7s  %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stderr,
    )

    review_id = args.review_id or f"{args.safe_id}__00"
    args.out_dir.mkdir(parents=True, exist_ok=True)
    out_path = args.out_dir / f"{review_id}.json"
    if out_path.exists():
        log.info("  skip (already named): %s", review_id)
        return 0

    rec = _load_record(review_id, args.states_file)
    if rec is None:
        log.error("review_id %s not found in %s", review_id, args.states_file)
        return 1

    user_prompt = _build_user_prompt(rec)
    if args.dry_run:
        print(user_prompt)
        return 0

    if not SYSTEM_PROMPT_PATH.exists():
        log.error("system prompt not found: %s", SYSTEM_PROMPT_PATH)
        return 1
    system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")

    cmd = [
        sys.executable, str(TIMEOUT_SCRIPT), str(PER_NAME_TIMEOUT),
        "claude", "-p", user_prompt,
        "--append-system-prompt", system_prompt,
        "--output-format", "text",
        "--model", args.model,
        "--no-session-persistence",
    ]
    log.info("  naming %s …", review_id)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True,
                                timeout=PER_NAME_TIMEOUT + 15)
    except subprocess.TimeoutExpired:
        log.error("  claude timed out for %s", review_id)
        return 1

    if result.returncode != 0:
        log.error("  claude exited %d for %s: %s",
                  result.returncode, review_id, result.stderr[:200])
        return 1

    nice_name = _clean_name(result.stdout)
    if not nice_name:
        log.error("  empty name returned for %s; raw=%r",
                  review_id, result.stdout[:200])
        return 1

    out_path.write_text(json.dumps({
        "review_id":     review_id,
        "nice_name":     nice_name,
        "paper_label":   rec.get("title",""),
        "model":         args.model,
        "generated_at":  date.today().isoformat(),
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info("  saved %s  →  %r", out_path.name, nice_name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
