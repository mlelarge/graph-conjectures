#!/usr/bin/env python3
"""Find OPG <-> erdosproblems.com intersection.

Strategy:
  1. Detect "Erdős-related" OPG problems — bibliography mentions Erdős
     (case- and diacritic-insensitive: matches Erdős, Erdos, P. Erdős, etc).
  2. For those candidates, fuzzy-match the OPG statement text against every
     erdosproblems statement (rapidfuzz token_set_ratio after light normalisation).
  3. Also do a global fuzzy pass on titles vs erdos statements (cheap; catches
     cases where Erdős wasn't named in the bibliography but the problem is the same).

Outputs:
  data/intersection.tsv   — sortable review table
  data/intersection.json  — opg_slug -> {erdos_id, score, ...}
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import unicodedata
from pathlib import Path

from rapidfuzz import fuzz

log = logging.getLogger("intersect")

# Match "Erdős" / "Erdos" / "Erdös" etc., or the bib-key fragment "Er<digits>"
# in a reference's raw text — but the latter alone is too noisy, so we require
# the surname-form for the candidate filter and use bib-key only as a soft signal.
ERDOS_NAME = re.compile(r"\berd[oöő]s\b", re.IGNORECASE)


def _strip_diacritics(s: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c)
    )


def _normalise(s: str) -> str:
    """Lowercase, strip diacritics, drop $ delimiters, collapse whitespace."""
    s = _strip_diacritics(s).lower()
    s = s.replace("$", " ")
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def has_erdos_in_bib(problem: dict) -> bool:
    for ref in problem.get("references", []):
        if ERDOS_NAME.search(_strip_diacritics(ref.get("raw_text", ""))):
            return True
    # Also count Erdős listed as an author
    for a in problem.get("authors", []):
        if ERDOS_NAME.search(_strip_diacritics(a.get("label", ""))):
            return True
    return False


def opg_search_text(p: dict) -> str:
    parts = [p.get("title", "")]
    for s in p.get("statements", []):
        parts.append(s.get("text", ""))
    if not p.get("statements"):
        # Fall back to the whole problem block text (the 2 problems with no envtheorem)
        parts.append(p.get("statement_text", ""))
    return _normalise(" ".join(parts))


def erdos_search_text(e: dict) -> str:
    return _normalise(e.get("statement", ""))


def best_match(query: str, candidates: list[tuple[int, str]], threshold: int) -> list[tuple[int, int]]:
    """Return [(erdos_id, score)] sorted desc by score, filtered by threshold."""
    out = []
    for eid, etext in candidates:
        score = max(
            int(fuzz.token_set_ratio(query, etext)),
            int(fuzz.partial_ratio(query, etext)),
        )
        if score >= threshold:
            out.append((eid, score))
    out.sort(key=lambda x: -x[1])
    return out


def main(argv: list[str] | None = None) -> int:
    here = Path(__file__).resolve().parent
    project = here.parent
    p = argparse.ArgumentParser(description="Cross-reference OPG with erdosproblems.com.")
    p.add_argument("--data-dir", type=Path, default=project / "data")
    p.add_argument(
        "--threshold-shortlist",
        type=int,
        default=70,
        help="min score to include in TSV (Erdős-bib OPG problems)",
    )
    p.add_argument(
        "--threshold-global",
        type=int,
        default=85,
        help="min score for global pass on non-Erdős-bib OPG problems",
    )
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )

    opg = json.loads((args.data_dir / "problems.json").read_text(encoding="utf-8"))
    erd = json.loads((args.data_dir / "erdos_graph.json").read_text(encoding="utf-8"))
    log.info("loaded %d OPG problems and %d erdos problems", len(opg), len(erd))

    erd_index = [(e["number"], erdos_search_text(e)) for e in erd]
    erd_by_id = {e["number"]: e for e in erd}

    rows: list[dict] = []
    erdos_bib_count = 0

    for p in opg:
        is_erdos = has_erdos_in_bib(p)
        if is_erdos:
            erdos_bib_count += 1
        threshold = args.threshold_shortlist if is_erdos else args.threshold_global
        q = opg_search_text(p)
        if not q:
            continue
        for eid, score in best_match(q, erd_index, threshold)[:3]:
            rows.append(
                {
                    "opg_slug": p["slug"],
                    "opg_title": p["title"],
                    "erdos_id": eid,
                    "erdos_url": erd_by_id[eid]["url"],
                    "erdos_status": erd_by_id[eid]["status"],
                    "score": score,
                    "erdos_in_bib": is_erdos,
                    "opg_statement_excerpt": (p["statements"][0]["text"][:160] if p["statements"] else p.get("statement_text", "")[:160]),
                    "erdos_statement_excerpt": erd_by_id[eid]["statement"][:160],
                }
            )

    rows.sort(key=lambda r: (-r["score"], r["opg_slug"]))
    log.info("Erdős-in-bibliography OPG problems: %d", erdos_bib_count)
    log.info("candidate matches above threshold: %d", len(rows))

    # TSV for review
    tsv = args.data_dir / "intersection.tsv"
    cols = [
        "score",
        "erdos_in_bib",
        "opg_slug",
        "erdos_id",
        "erdos_status",
        "erdos_url",
        "opg_title",
        "opg_statement_excerpt",
        "erdos_statement_excerpt",
    ]
    with tsv.open("w", encoding="utf-8") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(str(r[c]).replace("\t", " ").replace("\n", " ") for c in cols) + "\n")
    log.info("wrote %s", tsv)

    # JSON: keep only the highest-scoring match per OPG slug
    best_per_slug: dict[str, dict] = {}
    for r in rows:
        cur = best_per_slug.get(r["opg_slug"])
        if cur is None or r["score"] > cur["score"]:
            best_per_slug[r["opg_slug"]] = r
    out = args.data_dir / "intersection.json"
    out.write_text(json.dumps(best_per_slug, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info("wrote %s (%d slug(s))", out, len(best_per_slug))

    return 0


if __name__ == "__main__":
    sys.exit(main())
