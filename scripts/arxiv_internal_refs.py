#!/usr/bin/env python3
"""
scripts/arxiv_internal_refs.py — Phase 1 of the arxiv-conjecture review.

For each of the deduped 'states' records in data/arxiv_conjectures.json (the 762
new conjectures), fuzzy-match its statement against every 'studies' record in
data/arxiv_extracted/ that comes from a DIFFERENT, LATER paper. This finds
internal cross-references: "paper A states conjecture C, paper B makes progress
on C." Pure offline computation, no claude calls.

Outputs
-------
    data/arxiv_internal_refs.json  — {safe_id: [{ref}, ...]} keyed by states-record safe_id
    data/arxiv_internal_refs.tsv   — flat review table

Each {ref} entry includes the matched studies paper's id/title/authors/year and
its 'paper_contribution' text from the LLM extraction, plus the fuzzy score and
last-name attribution overlap between the studies record's attributed_to and
the states record's paper_authors.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

from rapidfuzz import fuzz

PROJECT = Path(__file__).resolve().parent.parent
log = logging.getLogger("arxiv_internal_refs")


# ── normalisation ──────────────────────────────────────────────────────────────

def _ascii_lower(s: str) -> str:
    return unicodedata.normalize("NFD", s or "").encode("ascii","ignore").decode().lower()


def _normalise(s: str) -> str:
    s = _ascii_lower(s)
    s = s.replace("$$", " ").replace("$", " ")
    s = re.sub(r"\\(text|mathrm|mathbf|mathcal|operatorname|emph)\b\s*", " ", s)
    s = re.sub(r"[{}\\]", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def last_names_from_list(authors: list[str]) -> set[str]:
    out: set[str] = set()
    for a in authors or []:
        parts = a.split()
        if parts:
            out.add(_ascii_lower(parts[-1]))
    return out


def last_names_from_attribution(attr: str) -> set[str]:
    s = re.sub(r"\([^)]*\)", " ", attr or "")
    s = s.replace(" and ", ", ").replace("&", ",").replace(";", ",")
    out: set[str] = set()
    for chunk in s.split(","):
        toks = [t for t in chunk.split() if not re.match(r"^[A-Z]\.?$", t)]
        if toks:
            out.add(_ascii_lower(toks[-1]))
    return out


# ── main ───────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data-dir",   type=Path, default=PROJECT / "data")
    ap.add_argument("--threshold",  type=int, default=80,
                    help="Min fuzz.token_set_ratio for a match (default: 80)")
    ap.add_argument("--threshold-with-attrib", type=int, default=65,
                    help="Lower min when attribution overlap is non-empty (default: 65)")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s  %(levelname)-7s  %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stderr,
    )

    states = json.loads((args.data_dir / "arxiv_conjectures.json").read_text(encoding="utf-8"))
    log.info("loaded %d states records", len(states))

    studies: list[dict] = []
    extr_dir = args.data_dir / "arxiv_extracted"
    for f in sorted(extr_dir.glob("*.json")):
        try:
            arr = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        for r in arr:
            if isinstance(r, dict) and r.get("role") == "studies":
                studies.append(r)
    log.info("loaded %d studies records", len(studies))

    # Pre-compute normalised studies text
    studies_norm = []
    for u in studies:
        text = _normalise(u.get("statement_text", ""))
        if text:
            studies_norm.append((u, text))

    results: dict[str, list[dict]] = defaultdict(list)
    n_scanned = 0
    for s in states:
        s_safe = s.get("safe_id") or s.get("arxiv_id","").replace("/", "_")
        if not s_safe:
            continue
        s_pid = s.get("arxiv_id","")
        s_year = (s.get("published") or "0000")[:4]
        s_norm = _normalise(s.get("statement_text", ""))
        if not s_norm:
            continue
        s_authors_ln = last_names_from_list(s.get("paper_authors", []))

        n_scanned += 1
        if n_scanned % 100 == 0:
            log.info("  scanned %d/%d states records …", n_scanned, len(states))

        for u, u_norm in studies_norm:
            if u.get("arxiv_id") == s_pid:
                continue
            u_year = (u.get("published") or "0000")[:4]
            if u_year <= s_year:
                continue   # later paper required
            score = int(fuzz.token_set_ratio(s_norm, u_norm))
            attr_overlap = last_names_from_attribution(u.get("attributed_to", "")) & s_authors_ln
            if score >= args.threshold or (attr_overlap and score >= args.threshold_with_attrib):
                results[s_safe].append({
                    "studies_paper":         u.get("arxiv_id",""),
                    "studies_paper_title":   u.get("paper_title",""),
                    "studies_paper_authors": u.get("paper_authors", []),
                    "studies_published":     u.get("published",""),
                    "studies_abs_url":       u.get("abs_url",""),
                    "paper_contribution":    u.get("paper_contribution",""),
                    "attributed_to":         u.get("attributed_to",""),
                    "fuzzy_score":           score,
                    "attribution_overlap":   sorted(attr_overlap),
                })
        results[s_safe].sort(key=lambda r: -r["fuzzy_score"])

    # Keep only non-empty
    results = {k: v for k, v in results.items() if v}

    out_json = args.data_dir / "arxiv_internal_refs.json"
    out_json.write_text(json.dumps(results, indent=2, ensure_ascii=False),
                        encoding="utf-8")
    log.info("wrote %s (%d states records with ≥1 internal reference)",
             out_json, len(results))

    # TSV for human review — one line per (states, studies) pair
    states_by_safe = {s.get("safe_id") or s.get("arxiv_id","").replace("/","_"): s
                      for s in states}
    out_tsv = args.data_dir / "arxiv_internal_refs.tsv"
    cols = ["score","attr_overlap",
            "states_safe_id","states_title","states_attrib_paper",
            "studies_paper","studies_year",
            "paper_contribution"]
    with out_tsv.open("w", encoding="utf-8") as fh:
        fh.write("\t".join(cols) + "\n")
        # Flat rows sorted by score desc
        flat = []
        for safe_id, refs in results.items():
            s = states_by_safe.get(safe_id, {})
            for r in refs:
                flat.append({
                    "score":               r["fuzzy_score"],
                    "attr_overlap":        ",".join(r["attribution_overlap"]),
                    "states_safe_id":      safe_id,
                    "states_title":        (s.get("title") or "")[:60],
                    "states_attrib_paper": s.get("arxiv_id",""),
                    "studies_paper":       r["studies_paper"],
                    "studies_year":        (r["studies_published"] or "")[:4],
                    "paper_contribution":  r["paper_contribution"][:200].replace("\t"," ").replace("\n"," "),
                })
        flat.sort(key=lambda r: -r["score"])
        for row in flat:
            fh.write("\t".join(str(row[c]) for c in cols) + "\n")
    log.info("wrote %s (%d rows total)", out_tsv, sum(len(r) for r in results.values()))

    return 0


if __name__ == "__main__":
    sys.exit(main())
