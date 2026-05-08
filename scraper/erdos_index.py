#!/usr/bin/env python3
"""Index problems on erdosproblems.com/tags/graph theory.

Parses one cached HTML page (the public tag listing) and writes a JSON list
of problems with id, status, prize, statement, tags, and citation keys —
the reference set used to detect intersection with OPG.
"""

from __future__ import annotations

import argparse
import html
import json
import logging
import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

URL = "https://www.erdosproblems.com/tags/graph%20theory"
USER_AGENT = "GraphConjectures-research/0.1 (mailto:marc.lelarge@gmail.com)"

log = logging.getLogger("erdos_index")


def fetch(cache_path: Path, refresh: bool) -> str:
    if cache_path.exists() and not refresh:
        log.info("using cached %s", cache_path)
        return cache_path.read_text(encoding="utf-8")
    log.info("GET %s", URL)
    r = requests.get(URL, headers={"User-Agent": USER_AGENT}, timeout=30)
    r.raise_for_status()
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(r.text, encoding="utf-8")
    time.sleep(1)  # be polite even though we fetched only once
    return r.text


def parse(page_html: str) -> list[dict]:
    soup = BeautifulSoup(page_html, "lxml")
    problems: list[dict] = []
    for card in soup.select("div.problem-text"):
        status = card.get("id")
        if status not in ("open", "solved"):
            continue
        pid_block = card.find(id="problem_id")
        if not pid_block:
            continue

        # First <a> in problem_id is the "#N" link to /N.
        first_a = pid_block.find("a")
        if not first_a:
            continue
        m = re.match(r"#(\d+)", first_a.get_text(strip=True))
        if not m:
            continue
        number = int(m.group(1))
        rel = first_a.get("href", "") or ""
        url = "https://www.erdosproblems.com" + rel if rel.startswith("/") else rel

        # Citation keys are the remaining <a>s (e.g. "[Er76b,p.171]").
        cites_raw = [a.get_text(strip=True) for a in pid_block.find_all("a")[1:]]
        cite_keys = []
        for c in cites_raw:
            mk = re.match(r"\[([^,\]]+)", c)
            if mk:
                cite_keys.append(mk.group(1))

        prize_block = card.find(id="prize")
        prize_text = (
            html.unescape(prize_block.get_text(" ", strip=True)) if prize_block else ""
        )

        content_block = card.find(id="content")
        statement_text = (
            html.unescape(content_block.get_text(" ", strip=True)) if content_block else ""
        )

        tags_block = card.find(id="tags")
        tags: list[str] = []
        if tags_block:
            tags = [
                t.strip()
                for t in re.split(r"\s*\|\s*", tags_block.get_text(" ", strip=True))
                if t.strip()
            ]

        problems.append(
            {
                "number": number,
                "url": url,
                "status": status,
                "prize": prize_text,
                "statement": statement_text,
                "tags": tags,
                "citation_keys": sorted(set(cite_keys)),
                "citation_keys_full": cites_raw,
            }
        )
    return problems


def main(argv: list[str] | None = None) -> int:
    here = Path(__file__).resolve().parent
    project = here.parent
    p = argparse.ArgumentParser(description="Index erdosproblems.com graph-theory problems.")
    p.add_argument("--cache-dir", type=Path, default=project / "cache" / "erdos")
    p.add_argument("--data-dir", type=Path, default=project / "data")
    p.add_argument("--refresh", action="store_true", help="re-fetch even if cached")
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )

    cache_path = args.cache_dir / "graph_theory.html"
    page_html = fetch(cache_path, args.refresh)
    problems = parse(page_html)
    log.info("parsed %d problems", len(problems))

    args.data_dir.mkdir(parents=True, exist_ok=True)
    out = args.data_dir / "erdos_graph.json"
    out.write_text(json.dumps(problems, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info("wrote %s", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
