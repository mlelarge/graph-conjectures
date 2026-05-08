#!/usr/bin/env python3
"""Render parsed OPG JSON into a static site under /site.

Inputs:
  data/problems.json
  data/categories.json
  data/intersection.json   (optional)

Outputs:
  site/index.html
  site/op/<slug>/index.html
  site/about/index.html
  site/static/style.css       (copied from scraper/static/)
"""

from __future__ import annotations

import argparse
import json
import logging
import shutil
import sys
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

log = logging.getLogger("build")


def _build_search_text(p: dict) -> str:
    """Lowercase concatenation of all searchable text for a problem (used by index filter)."""
    parts = [p.get("title", "")]
    parts += [s.get("text", "") for s in p.get("statements", [])]
    parts += [a.get("label", "") for a in p.get("authors", [])]
    parts += [s.get("label", "") for s in p.get("subject_path", [])]
    parts += [k.get("label", "") for k in p.get("keywords", [])]
    if p.get("posted_by"):
        parts.append(p["posted_by"].get("name", ""))
    return " ".join(parts).lower().replace('"', "").replace("'", "")


def main(argv: list[str] | None = None) -> int:
    here = Path(__file__).resolve().parent
    project = here.parent
    p = argparse.ArgumentParser(description="Render the static site.")
    p.add_argument("--data-dir", type=Path, default=project / "data")
    p.add_argument("--site-dir", type=Path, default=project / "site")
    p.add_argument("--templates-dir", type=Path, default=here / "templates")
    p.add_argument("--static-dir", type=Path, default=here / "static")
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )

    problems = json.loads((args.data_dir / "problems.json").read_text(encoding="utf-8"))
    categories = json.loads((args.data_dir / "categories.json").read_text(encoding="utf-8"))
    intersection_path = args.data_dir / "intersection.json"
    intersection = (
        json.loads(intersection_path.read_text(encoding="utf-8"))
        if intersection_path.exists()
        else {}
    )

    # Load per-slug literature reviews (if any have been generated yet).
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
            except Exception as e:
                log.warning("could not load review %s: %s", f.name, e)
    log.info("loaded %d review(s)", len(reviews))

    # Manually-curated set of confirmed cross-refs. The fuzzy-match output is
    # advisory only — do not surface low-confidence guesses on the public site.
    confirmed_intersection_slugs = {
        "erdos_faber_lovasz_conjecture",
        "the_erdos_hajnal_conjecture",
    }

    # Decorate each problem with computed fields used by templates.
    for prob in problems:
        prob["_search"] = _build_search_text(prob)
        if prob["slug"] in confirmed_intersection_slugs and prob["slug"] in intersection:
            prob["_erdos"] = intersection[prob["slug"]]
        else:
            prob["_erdos"] = None
        prob["_review"] = reviews.get(prob["slug"])

    problems_sorted = sorted(
        problems,
        key=lambda p: (-p["importance"]["stars"], p["title"].lower()),
    )

    erdos_match_count = sum(1 for p in problems if p["_erdos"])
    review_count = sum(1 for p in problems if p["_review"])
    review_status_counts: dict[str, int] = {}
    for p in problems:
        if p["_review"]:
            s = p["_review"].get("status", "unclear")
            review_status_counts[s] = review_status_counts.get(s, 0) + 1

    env = Environment(
        loader=FileSystemLoader(str(args.templates_dir)),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    common = {
        "build_date": date.today().isoformat(),
        "problem_count": len(problems),
        "category_count": len(categories),
        "erdos_match_count": erdos_match_count,
        "review_count": review_count,
        "review_status_counts": review_status_counts,
    }

    args.site_dir.mkdir(parents=True, exist_ok=True)
    static_out = args.site_dir / "static"
    if static_out.exists():
        shutil.rmtree(static_out)
    shutil.copytree(args.static_dir, static_out)
    log.info("copied static assets to %s", static_out)

    # Index page
    (args.site_dir / "index.html").write_text(
        env.get_template("index.html").render(
            root="", problems=problems_sorted, **common
        ),
        encoding="utf-8",
    )
    log.info("wrote index.html")

    # About page
    about_dir = args.site_dir / "about"
    about_dir.mkdir(parents=True, exist_ok=True)
    (about_dir / "index.html").write_text(
        env.get_template("about.html").render(root="../", **common),
        encoding="utf-8",
    )
    log.info("wrote about/")

    # Problem pages
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
    log.info("wrote %d problem page(s) under op/", len(problems))

    # Tag and author landing pages
    tag_template = env.get_template("tag.html")
    by_slug = {p["slug"]: p for p in problems}
    n_authors = n_tags = 0

    for cat in categories:
        cat_problems = sorted(
            (by_slug[s] for s in cat["problem_slugs"] if s in by_slug),
            key=lambda p: (-p["importance"]["stars"], p["title"].lower()),
        )
        if not cat_problems:
            continue
        kinds = set(cat.get("kinds", []))
        # Pick a single label (categories may have multiple display variants).
        label = (cat.get("labels") or [cat["slug"]])[0]
        is_author = "author" in kinds
        sub = "author" if is_author else "tag"
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
    log.info("wrote %d author page(s) and %d tag page(s)", n_authors, n_tags)

    log.info("done. Serve with: python -m http.server --directory %s 8000", args.site_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
