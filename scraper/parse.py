#!/usr/bin/env python3
"""Parse cached OPG problem pages into structured JSON.

Reads cache/op/<slug>.html files produced by crawl.py and writes:
  data/problems/<slug>.json  — one record per problem
  data/problems.json         — aggregated array of all records
  data/categories.json       — category slug -> {labels[], kinds[], problem_slugs[]}
  data/authors.json          — author slug -> {name, problem_slugs[]}

Selectors and quirks follow PLAN.md Appendix A.
"""

from __future__ import annotations

import argparse
import html
import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup, Tag

BASE = "http://www.openproblemgarden.org"
log = logging.getLogger("parse")


# ---- helpers ---------------------------------------------------------------

def _clean(s: str) -> str:
    s = html.unescape(s)
    s = s.replace("\xa0", " ")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n\n", s)
    return s.strip()


def _replace_teximages(node: Tag) -> None:
    """In-place: replace each <img class="teximage"> with its alt (already $...$-wrapped)."""
    for img in node.select("img.teximage"):
        alt = img.get("alt", "") or ""
        img.replace_with(alt)


def _text_with_math(node: Tag) -> str:
    """Plain text from a node, after substituting teximage <img> with their LaTeX alt."""
    clone = BeautifulSoup(str(node), "lxml")
    inner = clone.find(node.name)
    if inner is None:
        return ""
    _replace_teximages(inner)
    return _clean(inner.get_text(" ", strip=True))


# ---- field extractors ------------------------------------------------------

def _node_id(soup: BeautifulSoup) -> int | None:
    div = soup.find("div", id=re.compile(r"^node-\d+$"))
    if not div:
        return None
    m = re.match(r"node-(\d+)", div.get("id", ""))
    return int(m.group(1)) if m else None


def _title(soup: BeautifulSoup) -> str:
    h = soup.select_one("h1.title")
    return _clean(h.get_text()) if h else ""


def _breadcrumb_subjects(soup: BeautifulSoup) -> list[dict]:
    """Skip the first two anchors (Home, Subject); the rest is the subject hierarchy."""
    bc = soup.select("div.breadcrumb a")
    out: list[dict] = []
    for a in bc[2:]:
        href = a.get("href", "") or ""
        if not href.startswith("/category/"):
            continue
        out.append({"slug": href[len("/category/") :], "label": _clean(a.get_text())})
    return out


def _authsubtables(soup: BeautifulSoup) -> dict[str, list[dict]]:
    """Map label ('Author(s)', 'Subject', 'Keywords', ...) → list of {slug, label}."""
    out: dict[str, list[dict]] = {}
    for tbl in soup.select("div.authsubtable"):
        sp = tbl.find("span", class_="label")
        if not sp:
            continue
        label = _clean(sp.get_text()).rstrip(":")
        items = []
        for a in tbl.select('td a[href^="/category/"]'):
            href = a.get("href", "") or ""
            slug = href[len("/category/") :]
            if slug:
                items.append({"slug": slug, "label": _clean(a.get_text())})
        out[label] = items
    return out


def _subtable_text_excluding_auths(st: Tag) -> str:
    """Text of a subtable with any nested div.authsubtable removed (the first subtable
    on a problem page wraps Importance + nested Author/Subject/Keyword tables)."""
    clone = BeautifulSoup(str(st), "lxml").div
    if clone is None:
        return ""
    for inner in clone.select("div.authsubtable"):
        inner.decompose()
    return _clean(clone.get_text(" ", strip=True))


def _subtable_value(soup: BeautifulSoup, label: str) -> str | None:
    """Return the value text of the div.subtable whose first label-span matches `label`."""
    target = label.rstrip(":")
    for st in soup.select("div.subtable"):
        sp = st.find("span", class_="label")
        if not sp:
            continue
        if _clean(sp.get_text()).rstrip(":") != target:
            continue
        full = _subtable_text_excluding_auths(st)
        prefix = _clean(sp.get_text())
        return full[len(prefix) :].strip() if full.startswith(prefix) else full
    return None


def _importance(soup: BeautifulSoup) -> dict:
    raw = _subtable_value(soup, "Importance") or ""
    stars = raw.count("✭")
    return {"label": re.sub(r"✭+", "", raw).strip(), "stars": stars, "raw": raw}


def _accessible(soup: BeautifulSoup) -> bool | None:
    val = _subtable_value(soup, "Recomm. for undergrads")
    if val is None:
        return None
    v = val.strip().lower()
    if v.startswith("yes"):
        return True
    if v.startswith("no"):
        return False
    return None


_DATE_ORD = re.compile(r"\b(\d{1,2})(st|nd|rd|th)\b", re.IGNORECASE)


def _parse_date(s: str) -> str | None:
    s = _DATE_ORD.sub(r"\1", _clean(s))
    for fmt in ("%B %d, %Y", "%b %d, %Y"):
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def _posted(soup: BeautifulSoup) -> tuple[dict | None, str | None, str | None]:
    for st in soup.select("div.subtable"):
        ua = st.select_one('a[href^="/user/"][href$="/track"]')
        if not ua:
            continue
        href = ua.get("href", "")
        m = re.match(r"/user/([^/]+)/track", href)
        slug = m.group(1) if m else None
        name = _clean(ua.get_text())
        full = _clean(st.get_text(" ", strip=True))
        m2 = re.search(r"on:\s*(.+)$", full)
        date_raw = m2.group(1).strip() if m2 else None
        date_iso = _parse_date(date_raw) if date_raw else None
        return ({"slug": slug, "name": name} if slug else None), date_iso, date_raw
    return None, None, None


def _statements(prob_div: Tag) -> list[dict]:
    out = []
    clone = BeautifulSoup(str(prob_div), "lxml").select_one("div.problem")
    if clone is None:
        return out
    for env in clone.select("div.envtheorem"):
        b = env.find("b")
        kind = _clean(b.get_text()).rstrip(":.") if b else "Statement"
        env_clone = BeautifulSoup(str(env), "lxml").find("div", class_="envtheorem")
        _replace_teximages(env_clone)
        body = _clean(env_clone.get_text(" ", strip=True))
        body = re.sub(r"^" + re.escape(kind) + r"[:\.\s]*", "", body, count=1, flags=re.IGNORECASE)
        out.append({"kind": kind, "html": str(env), "text": body})
    return out


def _problem_block(soup: BeautifulSoup) -> tuple[str, str, list[dict]]:
    div = soup.select_one("div.problem")
    if not div:
        return "", "", []
    return str(div), _text_with_math(div), _statements(div)


def _discussion(soup: BeautifulSoup) -> tuple[str, str]:
    div = soup.select_one("div.discussion")
    if not div:
        return "", ""
    return str(div), _text_with_math(div)


def _references(soup: BeautifulSoup) -> list[dict]:
    div = soup.select_one("div.bibliography")
    if not div:
        return []
    refs = []
    for p in div.find_all("p", recursive=False):
        clone = BeautifulSoup(str(p), "lxml").p
        if clone is None:
            continue
        _replace_teximages(clone)
        text = _clean(clone.get_text(" ", strip=True))
        if not text:
            continue
        is_original = text.lstrip().startswith("*")
        m = re.match(r"\*?\s*\[([^\]]+)\]", text)
        refs.append(
            {
                "key": m.group(1) if m else None,
                "is_original": is_original,
                "raw_html": str(p),
                "raw_text": text,
                "links": [
                    {"href": a.get("href", "") or "", "text": _clean(a.get_text())}
                    for a in p.find_all("a")
                    if a.get("href")
                ],
            }
        )
    return refs


# ---- top-level -------------------------------------------------------------

def parse_problem(slug: str, html_text: str) -> dict:
    soup = BeautifulSoup(html_text, "lxml")
    auths = _authsubtables(soup)

    subjects = auths.get("Subject") or _breadcrumb_subjects(soup)
    posted_by, posted_at, posted_at_raw = _posted(soup)
    stmt_html, stmt_text, statements = _problem_block(soup)
    disc_html, disc_text = _discussion(soup)

    return {
        "slug": slug,
        "node_id": _node_id(soup),
        "canonical_url": f"{BASE}/op/{slug}",
        "title": _title(soup),
        "subject_path": subjects,
        "authors": auths.get("Author(s)", []),
        "keywords": auths.get("Keywords", []),
        "importance": _importance(soup),
        "accessible_to_undergrads": _accessible(soup),
        "posted_by": posted_by,
        "posted_at": posted_at,
        "posted_at_raw": posted_at_raw,
        "statements": statements,
        "statement_html": stmt_html,
        "statement_text": stmt_text,
        "discussion_html": disc_html,
        "discussion_text": disc_text,
        "references": _references(soup),
    }


def main(argv: list[str] | None = None) -> int:
    here = Path(__file__).resolve().parent
    project = here.parent
    p = argparse.ArgumentParser(description="Parse OPG cached HTML pages into JSON.")
    p.add_argument("--cache-dir", type=Path, default=project / "cache")
    p.add_argument("--data-dir", type=Path, default=project / "data")
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )

    op_dir = args.cache_dir / "op"
    files = sorted(op_dir.glob("*.html"))
    if args.limit:
        files = files[: args.limit]
    log.info("parsing %d file(s) from %s", len(files), op_dir)

    out_dir = args.data_dir / "problems"
    out_dir.mkdir(parents=True, exist_ok=True)

    all_records: list[dict] = []
    categories: dict[str, dict] = {}
    authors: dict[str, dict] = {}
    errors = 0
    warnings = 0

    for f in files:
        slug = f.stem
        try:
            rec = parse_problem(slug, f.read_text(encoding="utf-8"))
        except Exception as e:
            log.error("FAIL %s: %s", slug, e)
            errors += 1
            continue

        if not rec["title"]:
            log.warning("%s: missing title", slug)
            warnings += 1
        if not rec["statements"]:
            log.warning("%s: no envtheorem blocks", slug)
            warnings += 1

        (out_dir / f"{slug}.json").write_text(
            json.dumps(rec, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        all_records.append(rec)

        for kind, items in (
            ("author", rec["authors"]),
            ("subject", rec["subject_path"]),
            ("keyword", rec["keywords"]),
        ):
            for it in items:
                cat = categories.setdefault(
                    it["slug"],
                    {"slug": it["slug"], "labels": set(), "kinds": set(), "problem_slugs": []},
                )
                cat["labels"].add(it["label"])
                cat["kinds"].add(kind)
                cat["problem_slugs"].append(slug)

        for a in rec["authors"]:
            au = authors.setdefault(
                a["slug"], {"slug": a["slug"], "name": a["label"], "problem_slugs": []}
            )
            au["problem_slugs"].append(slug)

    cats_out = sorted(
        (
            {
                "slug": c["slug"],
                "labels": sorted(c["labels"]),
                "kinds": sorted(c["kinds"]),
                "problem_slugs": sorted(set(c["problem_slugs"])),
            }
            for c in categories.values()
        ),
        key=lambda x: x["slug"],
    )
    auth_out = sorted(
        (
            {"slug": a["slug"], "name": a["name"], "problem_slugs": sorted(set(a["problem_slugs"]))}
            for a in authors.values()
        ),
        key=lambda x: x["slug"],
    )

    (args.data_dir / "problems.json").write_text(
        json.dumps(all_records, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (args.data_dir / "categories.json").write_text(
        json.dumps(cats_out, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (args.data_dir / "authors.json").write_text(
        json.dumps(auth_out, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    log.info(
        "done: %d records, %d categories, %d authors, %d warning(s), %d error(s)",
        len(all_records),
        len(cats_out),
        len(auth_out),
        warnings,
        errors,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
