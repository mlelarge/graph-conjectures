#!/usr/bin/env python3
"""
scripts/arxiv_aggregate.py — collect per-paper extraction JSON into site-ready
artefacts.

Inputs:
    data/arxiv/<author_slug>/<safe_id>.json    — produced by arxiv_extract.py

Outputs:
    data/arxiv_conjectures.json    — flat list of `role:"states"` records
                                     (one record = one conjecture).
                                     Near-duplicates by the same first author
                                     are collapsed; earliest wins.

    data/arxiv_opg_matches.tsv     — `role:"studies"` records fuzzy-matched
                                     against data/problems.json. One line per
                                     candidate match for manual review.

    data/arxiv_opg_matches.json    — merged confirmed matches (initially empty
                                     dict; user edits or symlinks from .tsv).
                                     Schema: { arxiv_id: {
                                         opg_slug, score, paper_contribution,
                                         confidence, manual_confirmed: bool
                                     }}

Run after each extraction batch; idempotent.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import unicodedata
from pathlib import Path
from typing import Iterable

from rapidfuzz import fuzz

PROJECT = Path(__file__).resolve().parent.parent
log = logging.getLogger("arxiv_aggregate")


# ── curated-author lookup ──────────────────────────────────────────────────────

def load_curated_authors(path: Path) -> dict[str, str]:
    """Return {slug: display_name} for every entry in arxiv_authors.json."""
    import unicodedata, re
    def asc(s: str) -> str:
        return unicodedata.normalize("NFD", s or "").encode("ascii", "ignore").decode().lower()
    def slug_of(name: str) -> str:
        parts = name.strip().split()
        if len(parts) < 2:
            return re.sub(r"[^a-z0-9]+", "-", asc(name)).strip("-")
        last  = re.sub(r"[^a-z0-9\-]+", "-", asc(parts[-1])).strip("-")
        first = re.sub(r"[^a-z0-9\-]+", "-", asc(" ".join(parts[:-1]))).strip("-")
        return f"{last}_{first.replace('-', '_')}"
    out = {}
    for entry in json.loads(path.read_text(encoding="utf-8")):
        out[slug_of(entry["name"])] = entry["name"]
    return out


def build_matched_authors_index(cache_root: Path) -> dict[str, list[str]]:
    """Map safe_id → list of curated-author slugs whose manifest contains the paper."""
    idx: dict[str, list[str]] = {}
    for manifest in sorted(cache_root.glob("*/papers.json")):
        slug = manifest.parent.name
        try:
            papers = json.loads(manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        for p in papers:
            sid = p.get("safe_id")
            if not sid:
                continue
            idx.setdefault(sid, []).append(slug)
    return idx


# ── text normalisation ─────────────────────────────────────────────────────────

def _strip_diacritics(s: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", s)
        if not unicodedata.combining(c)
    )


def _normalise(s: str) -> str:
    s = _strip_diacritics(s or "").lower()
    s = s.replace("$$", " ").replace("$", " ")
    # drop common LaTeX command boilerplate that adds noise to the token-set match
    s = re.sub(r"\\(text|mathrm|mathbf|mathcal|operatorname|emph)\b\s*", " ", s)
    s = re.sub(r"[{}\\]", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


# ── input gathering ────────────────────────────────────────────────────────────

def iter_records(data_dir: Path) -> Iterable[dict]:
    """Yield every extracted record from data/arxiv_extracted/<safe_id>.json (flat)."""
    if not data_dir.exists():
        return
    for f in sorted(data_dir.glob("*.json")):
        try:
            records = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            log.warning("malformed JSON %s: %s — skip", f, exc)
            continue
        if not isinstance(records, list):
            log.warning("%s: expected a list, got %s — skip",
                        f, type(records).__name__)
            continue
        safe_id = f.stem
        for r in records:
            if not isinstance(r, dict):
                continue
            r["safe_id"] = safe_id
            yield r


# ── states-records dedup ───────────────────────────────────────────────────────

def _first_author_key(rec: dict) -> str:
    authors = rec.get("paper_authors") or []
    if not authors:
        return ""
    return _normalise(authors[0]).split()[-1] if authors[0] else ""


def dedup_states(records: list[dict], threshold: int = 90) -> list[dict]:
    """
    Collapse states-records that fuzzy-match each other AND share the same
    primary author. The earliest paper (by published date) is kept; duplicates
    are appended to `also_stated_in` on the survivor.
    """
    by_key: dict[str, list[dict]] = {}
    for r in records:
        by_key.setdefault(_first_author_key(r), []).append(r)

    out: list[dict] = []
    for key, group in by_key.items():
        # sort earliest-first so the iteration below preserves the oldest paper
        group.sort(key=lambda r: r.get("published", ""))
        kept: list[dict] = []
        for r in group:
            q = _normalise(r.get("statement_text", ""))
            if not q:
                kept.append(r)
                continue
            match = None
            for k in kept:
                if int(fuzz.token_set_ratio(q, _normalise(k.get("statement_text", "")))) >= threshold:
                    match = k
                    break
            if match is None:
                r["also_stated_in"] = []
                kept.append(r)
            else:
                match.setdefault("also_stated_in", []).append({
                    "arxiv_id":   r.get("arxiv_id"),
                    "abs_url":    r.get("abs_url"),
                    "published":  r.get("published"),
                    "title":      r.get("paper_title"),
                })
        out.extend(kept)
    out.sort(key=lambda r: r.get("published", ""), reverse=True)
    return out


# ── OPG match for studies-records ──────────────────────────────────────────────

def _opg_search_text(p: dict) -> str:
    parts = [p.get("title", "")]
    for s in p.get("statements", []):
        parts.append(s.get("text", ""))
    if not p.get("statements"):
        parts.append(p.get("statement_text", ""))
    return _normalise(" ".join(parts))


def match_to_opg(rec: dict, opg_index: list[tuple[str, str]],
                 threshold_lo: int, threshold_hi: int) -> list[tuple[str, int]]:
    """Return [(best_opg_slug, best_score)] — at most one — or [] if below threshold.

    Returning the single best match (not top-5) prevents the same arxiv record
    from generating spurious citations on multiple OPG pages: fuzzy noise was the
    dominant error in the pilot.
    """
    q = _normalise(rec.get("statement_text", ""))
    if not q:
        return []
    title_q = _normalise(rec.get("title", ""))
    best: tuple[str, int] | None = None
    for slug, otext in opg_index:
        if not otext:
            continue
        score_stmt  = int(fuzz.token_set_ratio(q, otext))
        score_title = int(fuzz.partial_ratio(title_q, otext)) if title_q else 0
        score = max(score_stmt, score_title)
        if score >= threshold_lo and (best is None or score > best[1]):
            best = (slug, score)
    return [best] if best is not None else []


# Phrases that signal the extractor flagged this as "mentioned only" rather than
# real progress. These records should not surface as OPG citations.
_MENTIONS_ONLY_RX = re.compile(
    r"(?i)("
    r"no\s+direct\s+progress|"
    r"no\s+progress\s+(made|on)|"
    r"mentioned\s+as\s+(context|motivation|a\s+corollary|an\s+equivalent|background)|"
    r"recalls\s+the\s+conjecture\s+as\s+(broader\s+)?context|"
    r"no\s+(direct\s+)?contribution|"
    # Patterns added after the full-corpus review: row 13 used "Not proved here"
    # and "mentioned in the concluding remarks", neither of which the original
    # regex caught.
    r"not\s+proved\s+(here|in\s+this\s+paper)|"
    r"mentioned\s+in\s+(the\s+)?(concluding|final|introductory|introduction)\s+(remarks|section)|"
    r"motivating\s+future\s+work|"
    r"discussed\s+as\s+(an?\s+)?(open\s+problem|open\s+question)|"
    r"appears\s+as\s+(motivation|background|context)|"
    r"this\s+conjecture\s+is\s+(only\s+)?(stated|recalled|mentioned)\b|"
    r"only\s+(stated|recalled|mentioned)\s+as\s+(motivation|context|background)|"
    r"used\s+as\s+a?\s*(tool|technique|reference|motivation)"
    r")"
)


def _has_real_progress(rec: dict) -> bool:
    """A studies-record is 'real progress' if paper_contribution is non-empty
    and does not match the mentions-only regex."""
    pc = (rec.get("paper_contribution") or "").strip()
    if not pc:
        return False
    if _MENTIONS_ONLY_RX.search(pc):
        return False
    return True


# ── main ───────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data-arxiv", type=Path, default=PROJECT / "data" / "arxiv_extracted",
                    help="Flat extraction directory (default: %(default)s)")
    ap.add_argument("--data-dir",   type=Path, default=PROJECT / "data",
                    help="Project data dir, source of problems.json (default: %(default)s)")
    ap.add_argument("--cache-root", type=Path, default=PROJECT / "cache" / "arxiv",
                    help="Where per-author manifests live (default: %(default)s)")
    ap.add_argument("--authors-file", type=Path, default=PROJECT / "data" / "arxiv_authors.json")
    ap.add_argument("--threshold-lo", type=int, default=75,
                    help="Lowest match score reported in the TSV (default: 75)")
    ap.add_argument("--threshold-hi", type=int, default=92,
                    help="Score above which a match is auto-attached to the OPG page "
                         "(default: 92; raised from 85 after pilot showed 100-score "
                         "matches on records that were only 'mentioned as context')")
    ap.add_argument("--allow-mentions-only", action="store_true",
                    help="Include records whose paper_contribution says 'no direct "
                         "progress' / 'mentioned as context' (default: filter them out)")
    ap.add_argument("--dedup-threshold", type=int, default=90,
                    help="Same-author statement dedup threshold (default: 90)")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s  %(levelname)-7s  %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stderr,
    )

    if not args.data_arxiv.exists():
        log.error("no extraction directory at %s — run scripts/arxiv_run_worker.sh first",
                  args.data_arxiv)
        return 1

    records = list(iter_records(args.data_arxiv))
    log.info("loaded %d extracted record(s) from %s", len(records), args.data_arxiv)

    # Build curated-author credit index.
    curated = load_curated_authors(args.authors_file) if args.authors_file.exists() else {}
    matched_idx = build_matched_authors_index(args.cache_root)
    for r in records:
        sid = r.get("safe_id") or r.get("arxiv_id", "").replace("/", "_")
        slugs = matched_idx.get(sid, [])
        r["matched_authors"] = [
            {"slug": s, "display": curated.get(s, s)} for s in slugs
        ]
    if curated:
        log.info("curated authors: %d  ·  papers with ≥1 curated co-author: %d",
                 len(curated),
                 sum(1 for r in records if r["matched_authors"]))

    states  = [r for r in records if r.get("role") == "states"]
    studies = [r for r in records if r.get("role") == "studies"]
    log.info("  states  : %d", len(states))
    log.info("  studies : %d", len(studies))

    # ── states: dedup ──
    deduped = dedup_states(states, threshold=args.dedup_threshold)
    log.info("after dedup: %d states records (was %d)", len(deduped), len(states))
    out_states = args.data_dir / "arxiv_conjectures.json"
    out_states.write_text(
        json.dumps(deduped, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    log.info("wrote %s (%d records)", out_states, len(deduped))

    # ── studies: OPG match ──
    opg_problems = json.loads(
        (args.data_dir / "problems.json").read_text(encoding="utf-8")
    )
    opg_index = [(p["slug"], _opg_search_text(p)) for p in opg_problems]

    tsv_rows: list[dict] = []
    auto_matches: dict[str, dict] = {}
    n_filtered_mentions = 0
    for r in studies:
        if not args.allow_mentions_only and not _has_real_progress(r):
            n_filtered_mentions += 1
            continue
        matches = match_to_opg(r, opg_index, args.threshold_lo, args.threshold_hi)
        if not matches:
            continue
        for slug, score in matches:
            tsv_rows.append({
                "score":     score,
                "arxiv_id":  r.get("arxiv_id", ""),
                "opg_slug":  slug,
                "attributed_to":   r.get("attributed_to", ""),
                "title":     r.get("title", ""),
                "arxiv_excerpt":   r.get("statement_text", "")[:160].replace("\t", " ").replace("\n", " "),
                "paper_contribution": (r.get("paper_contribution", "") or "")[:200].replace("\t", " ").replace("\n", " "),
                "abs_url":   r.get("abs_url", ""),
            })
        best_slug, best_score = matches[0]
        if best_score >= args.threshold_hi:
            cur = auto_matches.get(r["arxiv_id"])
            if cur is None or cur["score"] < best_score:
                auto_matches[r["arxiv_id"]] = {
                    "opg_slug":            best_slug,
                    "score":               best_score,
                    "paper_contribution":  r.get("paper_contribution", ""),
                    "confidence":          "auto-high" if best_score >= 90 else "auto-medium",
                    "manual_confirmed":    False,
                    "attributed_to":       r.get("attributed_to", ""),
                    "title":               r.get("title", ""),
                    "abs_url":             r.get("abs_url", ""),
                    "published":           r.get("published", ""),
                    "paper_title":         r.get("paper_title", ""),
                    "paper_authors":       r.get("paper_authors", []),
                }

    tsv_rows.sort(key=lambda r: (-r["score"], r["opg_slug"]))
    tsv_cols = ["score", "arxiv_id", "opg_slug", "attributed_to", "title",
                "arxiv_excerpt", "paper_contribution", "abs_url"]
    tsv_path = args.data_dir / "arxiv_opg_matches.tsv"
    with tsv_path.open("w", encoding="utf-8") as fh:
        fh.write("\t".join(tsv_cols) + "\n")
        for r in tsv_rows:
            fh.write("\t".join(str(r[c]) for c in tsv_cols) + "\n")
    log.info("wrote %s (%d candidate match lines, lo=%d hi=%d, "
             "mentions-only filtered out: %d)",
             tsv_path, len(tsv_rows), args.threshold_lo, args.threshold_hi,
             n_filtered_mentions)

    # Merge auto-matches with any existing manual confirmations.
    matches_path = args.data_dir / "arxiv_opg_matches.json"
    existing = {}
    if matches_path.exists():
        try:
            existing = json.loads(matches_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            log.warning("could not reload %s: %s — overwriting", matches_path, exc)
    for arxiv_id, m in auto_matches.items():
        # Manual-confirmed and manual-rejected entries are sticky across re-runs;
        # only un-flagged auto entries get refreshed.
        prior = existing.get(arxiv_id, {})
        if prior.get("manual_confirmed") or prior.get("manual_rejected"):
            continue
        existing[arxiv_id] = m
    matches_path.write_text(
        json.dumps(existing, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    log.info("wrote %s (%d total, %d auto-added/refreshed this run)",
             matches_path, len(existing), len(auto_matches))

    return 0


if __name__ == "__main__":
    sys.exit(main())
