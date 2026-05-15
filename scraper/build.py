#!/usr/bin/env python3
"""Render parsed OPG JSON + arxiv-extracted conjectures into a static site under /site.

Inputs:
  data/problems.json
  data/categories.json
  data/intersection.json        (optional)
  data/arxiv_conjectures.json   (optional; produced by scripts/arxiv_aggregate.py)
  data/arxiv_opg_matches.json   (optional; same)
  data/arxiv_authors.json       (optional; used for the author-slug → display-name map)

Outputs:
  site/index.html                 — merged index (OPG + arXiv rows)
  site/op/<slug>/index.html       — OPG problem pages
  site/arxiv/<safe_id>/index.html — arxiv conjecture pages
  site/author/<slug>/index.html
  site/tag/<slug>/index.html
  site/about/index.html
  site/static/style.css           (copied from scraper/static/)
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import shutil
import sys
import unicodedata
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

log = logging.getLogger("build")


# ── helpers ────────────────────────────────────────────────────────────────────

def _safe_id_from_arxiv(arxiv_id: str) -> str:
    return arxiv_id.replace("/", "_")


def _asc(s: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", s or "")
        if not unicodedata.combining(c)
    ).lower()


def _author_slug_from_name(name: str) -> str:
    """Mirror of arxiv_fetch.parse_author_name's slug logic."""
    parts = name.strip().split()
    if len(parts) < 2:
        return re.sub(r"[^a-z0-9]+", "-", _asc(name)).strip("-")
    last  = re.sub(r"[^a-z0-9\-]+", "-", _asc(parts[-1])).strip("-")
    first = re.sub(r"[^a-z0-9\-]+", "-", _asc(" ".join(parts[:-1]))).strip("-")
    return f"{last}_{first.replace('-', '_')}"


def _build_search_text(p: dict) -> str:
    """Lowercase concatenation of all searchable text for a row (used by index filter)."""
    parts = [p.get("title", ""), "source:" + p.get("_source", "opg")]
    if p.get("_source") == "arxiv":
        parts += [p.get("statement_text", "")]
        parts += [a.get("label", "") for a in p.get("authors", [])]
        parts += [p.get("attributed_to", ""), p.get("kind", "")]
    else:
        parts += [s.get("text", "") for s in p.get("statements", [])]
        parts += [a.get("label", "") for a in p.get("authors", [])]
        parts += [s.get("label", "") for s in p.get("subject_path", [])]
        parts += [k.get("label", "") for k in p.get("keywords", [])]
        if p.get("posted_by"):
            parts.append(p["posted_by"].get("name", ""))
    return " ".join(parts).lower().replace('"', "").replace("'", "")


def _virtual_problem_from_arxiv(rec: dict) -> dict:
    """Project a `states` arxiv record into the same row shape as an OPG problem.

    `authors` lists every co-author of the source paper. For curated authors
    (those whose slug appears in rec.matched_authors) the slug is set so the
    template links to /author/<slug>/; for non-curated co-authors the slug is
    empty and the template renders plain text.
    """
    arxiv_id = rec.get("arxiv_id", "") or ""
    safe_id  = _safe_id_from_arxiv(arxiv_id)
    title    = rec.get("title") or rec.get("paper_title") or arxiv_id

    paper_authors = rec.get("paper_authors") or []
    curated = {ma["slug"]: ma.get("display", "")
               for ma in rec.get("matched_authors", [])
               if ma.get("slug")}
    authors: list[dict] = []
    for name in paper_authors:
        s = _author_slug_from_name(name)
        if s in curated:
            authors.append({"label": name, "slug": s})
        else:
            authors.append({"label": name, "slug": ""})  # plain text in template

    statements = [{
        "kind": rec.get("kind", "Conjecture"),
        "text": rec.get("statement_text", ""),
        "html": "",
    }]

    return {
        "_source":         "arxiv",
        "slug":            safe_id,                       # used for URL path
        "arxiv_id":        arxiv_id,
        "safe_id":         safe_id,
        "title":           title,
        "statements":      statements,
        "statement_text":  rec.get("statement_text", ""),
        "context_text":    rec.get("context_text", ""),
        "attributed_to":   rec.get("attributed_to", ""),
        "attributed_year": rec.get("attributed_year"),
        "kind":            rec.get("kind", "Conjecture"),
        "confidence":      rec.get("confidence", "medium"),
        "notes":           rec.get("notes", ""),
        "also_stated_in":  rec.get("also_stated_in", []),
        "paper_title":     rec.get("paper_title", ""),
        "paper_authors":   paper_authors,
        "published":       rec.get("published", ""),
        "abs_url":         rec.get("abs_url", f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else ""),
        "source":          rec.get("source", ""),         # "html" | "pdf"
        "author_slug":     rec.get("author_slug", ""),

        # Fields shared with OPG problems so the same templates can render them.
        "authors":         authors,
        "subject_path":    [],
        "keywords":        [],
        "discussion_text": "",
        "references":      [],
        "importance":      {"label": "—", "stars": 0},
        "posted_by":       None,
        "posted_at":       rec.get("published", ""),
        "canonical_url":   rec.get("abs_url", f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else ""),
        "_erdos":          None,
        "_review":         rec.get("_review"),
        "_review_id":      rec.get("_review_id"),
    }


def _attach_arxiv_matches_to_opg(
    problems: list[dict],
    matches:  dict,
    confirmed_only: bool,
) -> int:
    """For each `arxiv_opg_matches.json` entry, append a citation to the
    matched OPG problem's _review.since_posted list. Returns # attached."""
    by_slug = {p["slug"]: p for p in problems}
    n = 0
    for arxiv_id, m in matches.items():
        if confirmed_only and not m.get("manual_confirmed"):
            continue
        slug = m.get("opg_slug")
        if not slug or slug not in by_slug:
            continue
        opg = by_slug[slug]
        # If the OPG problem has no review yet, synthesise a minimal one so the
        # template's _review block still renders the citation.
        if not opg.get("_review"):
            opg["_review"] = {
                "status": "unclear",
                "confidence": "low",
                "summary": "Auto-derived: progress reported in an arXiv paper.",
                "since_posted": [],
                "reviewed_at": "",
                "model": "arxiv-aggregate",
                "search_enabled": False,
                "notes": "Citation surfaced by scripts/arxiv_aggregate.py — "
                         "the OPG problem has not been literature-reviewed yet.",
            }
        rev = opg["_review"]
        rev.setdefault("since_posted", []).append({
            "title":   m.get("paper_title", "") or m.get("title", ""),
            "authors": ", ".join(m.get("paper_authors", []) or []),
            "year":    int(m["published"][:4]) if m.get("published", "")[:4].isdigit() else None,
            "venue":   "arXiv preprint",
            "url":     m.get("abs_url", ""),
            "doi":     None,
            "arxiv_id": arxiv_id,
            "kind":    "partial",
            "claim":   m.get("paper_contribution", ""),
            "_arxiv_match_confidence": m.get("confidence", ""),
            "_arxiv_match_score":      m.get("score", 0),
            "_arxiv_manual_confirmed": bool(m.get("manual_confirmed")),
        })
        n += 1
    return n


# ── main ───────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    here = Path(__file__).resolve().parent
    project = here.parent
    p = argparse.ArgumentParser(description="Render the static site.")
    p.add_argument("--data-dir",      type=Path, default=project / "data")
    p.add_argument("--site-dir",      type=Path, default=project / "site")
    p.add_argument("--templates-dir", type=Path, default=here / "templates")
    p.add_argument("--static-dir",    type=Path, default=here / "static")
    p.add_argument("--confirmed-only", action="store_true",
                   help="Only attach manually-confirmed arxiv→OPG matches to "
                        "OPG problem pages (default: include auto-high matches)")
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )

    # ── load OPG data ──────────────────────────────────────────────────────────
    problems   = json.loads((args.data_dir / "problems.json").read_text(encoding="utf-8"))
    categories = json.loads((args.data_dir / "categories.json").read_text(encoding="utf-8"))

    intersection_path = args.data_dir / "intersection.json"
    intersection = (
        json.loads(intersection_path.read_text(encoding="utf-8"))
        if intersection_path.exists() else {}
    )

    # Per-slug literature reviews
    reviews: dict[str, dict] = {}
    reviews_dir = args.data_dir / "reviews"
    if reviews_dir.exists():
        for f in sorted(reviews_dir.glob("*.json")):
            if f.name.endswith(".raw.json"):
                continue
            try:
                r = json.loads(f.read_text(encoding="utf-8"))
                if isinstance(r, dict) and r.get("slug"):
                    reviews[r["slug"]] = r
            except Exception as e:  # noqa: BLE001
                log.warning("could not load review %s: %s", f.name, e)
    log.info("loaded %d review(s)", len(reviews))

    # ── load arxiv data (optional) ─────────────────────────────────────────────
    arxiv_states_path  = args.data_dir / "arxiv_conjectures.json"
    arxiv_matches_path = args.data_dir / "arxiv_opg_matches.json"
    arxiv_states  = (
        json.loads(arxiv_states_path.read_text(encoding="utf-8"))
        if arxiv_states_path.exists() else []
    )
    arxiv_matches = (
        json.loads(arxiv_matches_path.read_text(encoding="utf-8"))
        if arxiv_matches_path.exists() else {}
    )
    log.info("loaded %d arxiv states record(s) and %d match record(s)",
             len(arxiv_states), len(arxiv_matches))

    # Assign a stable review_id (<safe_id>__<NN>) to each states record by
    # paper-local index, then attach the matching arxiv review JSON if present.
    arxiv_reviews_dir = args.data_dir / "arxiv_reviews"
    counters: dict[str, int] = {}
    n_reviews_attached = 0
    for s in arxiv_states:
        sid = s.get("safe_id") or s.get("arxiv_id","").replace("/","_")
        idx = counters.get(sid, 0)
        counters[sid] = idx + 1
        s["_review_id"] = f"{sid}__{idx:02d}"
        if arxiv_reviews_dir.exists():
            rp = arxiv_reviews_dir / f"{s['_review_id']}.json"
            if rp.exists():
                try:
                    s["_review"] = json.loads(rp.read_text(encoding="utf-8"))
                    n_reviews_attached += 1
                except Exception as e:  # noqa: BLE001
                    log.warning("could not load arxiv review %s: %s", rp.name, e)
    log.info("attached %d arxiv reviews to states records", n_reviews_attached)

    # Manually-curated set of confirmed cross-refs to erdosproblems.com.
    confirmed_intersection_slugs = {
        "erdos_faber_lovasz_conjecture",
        "the_erdos_hajnal_conjecture",
    }

    # ── decorate OPG problems ──────────────────────────────────────────────────
    for prob in problems:
        prob["_source"] = "opg"
        if prob["slug"] in confirmed_intersection_slugs and prob["slug"] in intersection:
            prob["_erdos"] = intersection[prob["slug"]]
        else:
            prob["_erdos"] = None
        prob["_review"] = reviews.get(prob["slug"])

    n_attached = _attach_arxiv_matches_to_opg(
        problems, arxiv_matches, confirmed_only=args.confirmed_only,
    )
    log.info("attached %d arxiv citation(s) to OPG problems "
             "(confirmed_only=%s)", n_attached, args.confirmed_only)

    # ── virtualise arxiv `states` records as rows ──────────────────────────────
    arxiv_rows = [_virtual_problem_from_arxiv(r) for r in arxiv_states]
    log.info("built %d arxiv virtual row(s)", len(arxiv_rows))

    # ── compute _search for every row ──────────────────────────────────────────
    for row in problems + arxiv_rows:
        row["_search"] = _build_search_text(row)

    # ── stats for templates ────────────────────────────────────────────────────
    erdos_match_count = sum(1 for p in problems if p["_erdos"])
    review_count = sum(1 for p in problems if p["_review"])
    review_status_counts: dict[str, int] = {}
    for p in problems:
        if p["_review"]:
            s = p["_review"].get("status", "unclear")
            review_status_counts[s] = review_status_counts.get(s, 0) + 1

    arxiv_review_count = sum(1 for r in arxiv_rows if r.get("_review"))
    arxiv_review_status_counts: dict[str, int] = {}
    for r in arxiv_rows:
        if r.get("_review"):
            s = r["_review"].get("status", "unclear")
            arxiv_review_status_counts[s] = arxiv_review_status_counts.get(s, 0) + 1

    rows_sorted = sorted(
        problems + arxiv_rows,
        key=lambda r: (
            -r.get("importance", {}).get("stars", 0),
            -(int(r.get("posted_at", "0000")[:4])
              if r.get("posted_at", "0000")[:4].isdigit() else 0),
            r["title"].lower(),
        ),
    )

    # ── jinja env ──────────────────────────────────────────────────────────────
    env = Environment(
        loader=FileSystemLoader(str(args.templates_dir)),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    common = {
        "build_date":           date.today().isoformat(),
        "problem_count":        len(problems),
        "category_count":       len(categories),
        "erdos_match_count":    erdos_match_count,
        "review_count":         review_count,
        "review_status_counts": review_status_counts,
        "arxiv_count":          len(arxiv_rows),
        "arxiv_review_count":   arxiv_review_count,
        "arxiv_review_status_counts": arxiv_review_status_counts,
    }

    # ── output ─────────────────────────────────────────────────────────────────
    args.site_dir.mkdir(parents=True, exist_ok=True)
    static_out = args.site_dir / "static"
    if static_out.exists():
        shutil.rmtree(static_out)
    shutil.copytree(args.static_dir, static_out)
    log.info("copied static assets to %s", static_out)

    # Index page (merged rows)
    (args.site_dir / "index.html").write_text(
        env.get_template("index.html").render(root="", rows=rows_sorted, **common),
        encoding="utf-8",
    )
    log.info("wrote index.html (%d rows: %d OPG + %d arXiv)",
             len(rows_sorted), len(problems), len(arxiv_rows))

    # About page
    about_dir = args.site_dir / "about"
    about_dir.mkdir(parents=True, exist_ok=True)
    (about_dir / "index.html").write_text(
        env.get_template("about.html").render(root="../", **common),
        encoding="utf-8",
    )
    log.info("wrote about/")

    # OPG problem pages
    op_dir = args.site_dir / "op"
    op_dir.mkdir(parents=True, exist_ok=True)
    template = env.get_template("problem.html")
    for prob in problems:
        slug_dir = op_dir / prob["slug"]
        slug_dir.mkdir(parents=True, exist_ok=True)
        (slug_dir / "index.html").write_text(
            template.render(root="../../", p=prob, **common),
            encoding="utf-8",
        )
    log.info("wrote %d OPG problem page(s) under op/", len(problems))

    # arXiv detail pages
    if arxiv_rows:
        arxiv_dir = args.site_dir / "arxiv"
        arxiv_dir.mkdir(parents=True, exist_ok=True)
        ax_template = env.get_template("arxiv_problem.html")
        opg_titles = {p["slug"]: p["title"] for p in problems}
        # Reverse lookup: for the arXiv detail page, link back to any OPG slug
        # that has an arXiv→OPG match pointing AT this arxiv_id.
        for row in arxiv_rows:
            opg_match = None
            m = arxiv_matches.get(row["arxiv_id"])
            if m and m.get("opg_slug") in opg_titles:
                opg_match = {
                    "slug":  m["opg_slug"],
                    "title": opg_titles[m["opg_slug"]],
                    "score": m.get("score", 0),
                    "confirmed": bool(m.get("manual_confirmed")),
                }
            sub_dir = arxiv_dir / row["safe_id"]
            sub_dir.mkdir(parents=True, exist_ok=True)
            (sub_dir / "index.html").write_text(
                ax_template.render(
                    root="../../", p=row, opg_match=opg_match, **common,
                ),
                encoding="utf-8",
            )
        log.info("wrote %d arXiv page(s) under arxiv/", len(arxiv_rows))

    # Tag and author landing pages — same machinery, both OPG and arXiv rows
    tag_template = env.get_template("tag.html")
    by_slug = {p["slug"]: p for p in problems}
    arxiv_by_author: dict[str, list[dict]] = {}
    for row in arxiv_rows:
        for a in row["authors"]:
            slug = a.get("slug") or ""
            if not slug:
                continue   # non-curated co-authors don't get author pages
            arxiv_by_author.setdefault(slug, []).append(row)

    n_authors = n_tags = 0
    seen_author_slugs: set[str] = set()
    for cat in categories:
        cat_problems_opg = [by_slug[s] for s in cat["problem_slugs"] if s in by_slug]
        kinds     = set(cat.get("kinds", []))
        is_author = "author" in kinds
        # Merge in arXiv rows whose author matches this category's slug
        cat_problems_arxiv = arxiv_by_author.get(cat["slug"], []) if is_author else []
        cat_problems = cat_problems_opg + cat_problems_arxiv
        if not cat_problems:
            continue
        if is_author:
            seen_author_slugs.add(cat["slug"])

        # Sort: OPG rows first (by importance), then arxiv rows by year-desc.
        cat_problems.sort(
            key=lambda p: (
                p.get("_source", "opg") != "opg",   # opg first
                -p.get("importance", {}).get("stars", 0),
                -(int(p.get("posted_at", "0000")[:4])
                  if p.get("posted_at", "0000")[:4].isdigit() else 0),
                p["title"].lower(),
            )
        )
        label = (cat.get("labels") or [cat["slug"]])[0]
        sub   = "author" if is_author else "tag"
        kind_label = (
            "Author"
            if is_author
            else ", ".join(sorted(kinds)) + " tag" if kinds else "Tag"
        )
        target = args.site_dir / sub / cat["slug"]
        target.mkdir(parents=True, exist_ok=True)
        (target / "index.html").write_text(
            tag_template.render(
                root="../../",
                heading=label,
                kind_label=kind_label,
                problems=cat_problems,
                **common,
            ),
            encoding="utf-8",
        )
        if is_author:
            n_authors += 1
        else:
            n_tags += 1

    # Author pages for arXiv-only authors (no matching OPG category).
    for author_slug, rows in arxiv_by_author.items():
        if author_slug in seen_author_slugs:
            continue
        display_name = rows[0]["authors"][0]["label"] if rows[0]["authors"] else author_slug
        rows.sort(
            key=lambda p: -(int(p.get("posted_at", "0000")[:4])
                            if p.get("posted_at", "0000")[:4].isdigit() else 0)
        )
        target = args.site_dir / "author" / author_slug
        target.mkdir(parents=True, exist_ok=True)
        (target / "index.html").write_text(
            tag_template.render(
                root="../../",
                heading=display_name,
                kind_label="Author (arXiv only)",
                problems=rows,
                **common,
            ),
            encoding="utf-8",
        )
        n_authors += 1

    log.info("wrote %d author page(s) and %d tag page(s)", n_authors, n_tags)

    log.info("done. Serve with: python -m http.server --directory %s 8000", args.site_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
