#!/usr/bin/env python3
"""
scraper/arxiv_review.py — Phase-2 single-conjecture review via `claude -p`.

For one safe_id (a key in data/arxiv_conjectures.json):
  1. Pull the conjecture record + any internal references from Phase 1.
  2. Compose a user prompt embedding the conjecture statement, context, paper
     provenance, and internal refs.
  3. Shell out to `claude -p` with the system prompt at
     scraper/arxiv_review_system_prompt.md, --allowed-tools "WebSearch WebFetch Read Write",
     wrapped in scripts/timeout_claude.py for hard timeout.
  4. Claude is instructed to use the Write tool to save the review JSON to
     data/arxiv_reviews/<safe_id>.json directly.

This is the entry point invoked once per safe_id by scripts/arxiv_review_run_worker.sh.

Usage
-----
    PER_REVIEW_TIMEOUT=900 python scraper/arxiv_review.py --safe-id 2310.04265
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
from pathlib import Path

PROJECT            = Path(__file__).resolve().parent.parent
SYSTEM_PROMPT_PATH = Path(__file__).parent / "arxiv_review_system_prompt.md"
TIMEOUT_SCRIPT     = PROJECT / "scripts" / "timeout_claude.py"
PER_REVIEW_TIMEOUT = int(os.environ.get("PER_REVIEW_TIMEOUT", 900))

log = logging.getLogger(__name__)


def _load_record(review_id: str, states_file: Path) -> dict | None:
    """Resolve a review_id of the form <safe_id>__<NN> to the right states record.

    Each safe_id may correspond to multiple states records (one per conjecture in
    the source paper); NN is the 0-based position within that paper's records,
    matching the order in arxiv_conjectures.json.
    """
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


def _load_internal_refs(safe_id: str, path: Path) -> list[dict]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get(safe_id, []) or []


def _build_user_prompt(rec: dict, internal_refs: list[dict], out_path: Path) -> str:
    lines = [
        "Review the following graph-theory conjecture and determine its current status as of today.",
        "",
        "============================================================",
        "  SOURCE PAPER",
        "============================================================",
        f"Title      : {rec.get('paper_title','')}",
        f"Authors    : {', '.join(rec.get('paper_authors', []))}",
        f"Published  : {rec.get('published','')}",
        f"arXiv ID   : {rec.get('arxiv_id','')}",
        f"arXiv URL  : {rec.get('abs_url','')}",
        "",
        "============================================================",
        f"  CONJECTURE   ({rec.get('kind','Conjecture')})",
        "============================================================",
        f"Identifier in paper: {rec.get('title','')}",
        f"Attributed to      : {rec.get('attributed_to','paper authors')}",
        "",
        "Statement (verbatim LaTeX — do not paraphrase in the summary):",
        "------------------------------------------------------------",
        rec.get("statement_text",""),
        "",
        "Surrounding context from the paper:",
        "------------------------------------------------------------",
        rec.get("context_text","") or "(none extracted)",
    ]

    if rec.get("also_stated_in"):
        lines += [
            "",
            "Also stated in (the same authors restated this elsewhere):",
            "------------------------------------------------------------",
        ]
        for it in rec["also_stated_in"][:5]:
            lines.append(
                f"  - arXiv:{it.get('arxiv_id','?')} ({(it.get('published') or '')[:4]}) "
                f"\"{(it.get('title') or '')[:70]}\""
            )

    if internal_refs:
        lines += [
            "",
            "============================================================",
            f"  INTERNAL REFERENCES (Phase-1, {len(internal_refs)} candidate(s))",
            "============================================================",
            "These records were extracted from LATER papers in our 12-author curated",
            "corpus and may already cite this conjecture. Verify each with one WebFetch",
            "before incorporating into the review.",
            "",
        ]
        for r in internal_refs[:6]:
            lines += [
                f"  ─ arXiv:{r.get('studies_paper','')}  ({(r.get('studies_published') or '')[:4]})  fuzz={r.get('fuzzy_score','?')}",
                f"    title : {(r.get('studies_paper_title') or '')[:90]}",
                f"    by    : {', '.join((r.get('studies_paper_authors') or [])[:5])}",
                f"    attrib: {r.get('attributed_to','')}",
                f"    contribution: {(r.get('paper_contribution') or '')[:350]}",
                "",
            ]

    lines += [
        "",
        "============================================================",
        "  OUTPUT INSTRUCTIONS",
        "============================================================",
        "Issue your WebSearch / WebFetch calls in parallel where possible "
        "(multiple tool calls per assistant turn). Cap total web calls at 5. "
        "Verify every URL with WebFetch before citing.",
        "",
        f"Save the review as a JSON object (raw, no <tags>, no code fences) to "
        f"this EXACT path using the Write tool:",
        "",
        f"  {out_path}",
        "",
        "Include these extra fields in the JSON object on top of the schema in your instructions:",
        f"  - \"review_id\":     \"{out_path.stem}\"",
        f"  - \"safe_id\":       \"{rec.get('safe_id') or rec.get('arxiv_id','').replace('/','_')}\"",
        f"  - \"arxiv_id\":      \"{rec.get('arxiv_id','')}\"",
        f"  - \"conjecture_title\": \"{(rec.get('title') or '').replace(chr(34), chr(39))}\"",
        f"  - \"paper_title\":   \"{rec.get('paper_title','')[:120].replace(chr(34), chr(39))}\"",
        f"  - \"published\":     \"{rec.get('published','')}\"",
        f"  - \"reviewed_at\":   today's date in YYYY-MM-DD form",
        f"  - \"model\":         \"claude-sonnet-4-6\"",
        f"  - \"search_enabled\": true",
        "",
        f"After writing, output one line: "
        f"done: {rec.get('arxiv_id','')} -> <status> (<confidence>, <N> cites)",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--review-id",
                   help="Unique review key: <safe_id>__<NN> where NN is the conjecture's "
                        "position within the source paper.")
    g.add_argument("--safe-id",
                   help="Legacy form; treated as <safe_id>__00 (first conjecture of the paper).")
    ap.add_argument("--states-file",   type=Path, default=PROJECT / "data" / "arxiv_conjectures.json")
    ap.add_argument("--internal-refs", type=Path, default=PROJECT / "data" / "arxiv_internal_refs.json")
    ap.add_argument("--out-dir",       type=Path, default=PROJECT / "data" / "arxiv_reviews")
    ap.add_argument("--model",         default="claude-sonnet-4-6")
    ap.add_argument("--dry-run",       action="store_true",
                    help="Print the composed prompt; do not call claude.")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args(argv)

    review_id = args.review_id or f"{args.safe_id}__00"

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s  %(levelname)-7s  %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stderr,
    )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    out_path = args.out_dir / f"{review_id}.json"
    if out_path.exists():
        log.info("  skip (already reviewed): %s", review_id)
        return 0

    rec = _load_record(review_id, args.states_file)
    if rec is None:
        log.error("review_id %s not found in %s", review_id, args.states_file)
        return 1
    # Internal refs are keyed by safe_id (per-paper), not per-conjecture.
    safe_id = review_id.split("__")[0]
    internal_refs = _load_internal_refs(safe_id, args.internal_refs)

    user_prompt = _build_user_prompt(rec, internal_refs, out_path.resolve())

    if args.dry_run:
        print(user_prompt)
        return 0

    if not SYSTEM_PROMPT_PATH.exists():
        log.error("system prompt not found: %s", SYSTEM_PROMPT_PATH)
        return 1
    system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")

    cmd = [
        sys.executable, str(TIMEOUT_SCRIPT), str(PER_REVIEW_TIMEOUT),
        "claude", "-p", user_prompt,
        "--append-system-prompt", system_prompt,
        "--allowed-tools", "WebSearch WebFetch Read Write",
        "--output-format", "text",
        "--model", args.model,
        "--no-session-persistence",
    ]
    log.info("  running claude (timeout=%ds) for %s …", PER_REVIEW_TIMEOUT, review_id)
    try:
        result = subprocess.run(cmd, timeout=PER_REVIEW_TIMEOUT + 30)
    except subprocess.TimeoutExpired:
        log.error("  claude timed out for %s", review_id)
        return 1

    if not out_path.exists():
        log.error("  FAILED %s (exit=%d, no JSON written)",
                  review_id, result.returncode)
        return 1
    log.info("  saved %s", out_path.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
