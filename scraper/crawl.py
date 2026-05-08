#!/usr/bin/env python3
"""Crawl openproblemgarden.org graph-theory category to a local cache.

Idempotent: skips already-cached pages.
Honours robots.txt Crawl-Delay (10 s; we use 12 s by default). Single-threaded.
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

BASE = "http://www.openproblemgarden.org"
LISTING_PATH = "/category/graph_theory"
USER_AGENT = "GraphConjectures-research/0.1 (mailto:marc.lelarge@gmail.com)"

log = logging.getLogger("crawl")


class TransientError(Exception):
    """Network or 5xx error worth retrying."""


def make_session() -> requests.Session:
    s = requests.Session()
    s.headers["User-Agent"] = USER_AGENT
    return s


@retry(
    retry=retry_if_exception_type(TransientError),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=4, max=30),
    reraise=True,
)
def _get(session: requests.Session, url: str) -> str:
    try:
        r = session.get(url, timeout=30)
    except (requests.ConnectionError, requests.Timeout) as e:
        raise TransientError(str(e)) from e
    if 500 <= r.status_code < 600:
        raise TransientError(f"HTTP {r.status_code} for {url}")
    r.raise_for_status()
    return r.text


def _extract_slugs(html: str, seen: set[str], slugs: list[str]) -> int:
    soup = BeautifulSoup(html, "lxml")
    new = 0
    for a in soup.select("td.view-field-node-title a"):
        href = a.get("href", "") or ""
        if href.startswith("/op/"):
            slug = href[len("/op/") :]
            if slug and slug not in seen:
                seen.add(slug)
                slugs.append(slug)
                new += 1
    return new


def _max_page(html: str) -> int:
    """Return the highest ?page=N referenced in the pager (0 if none)."""
    soup = BeautifulSoup(html, "lxml")
    nums = {0}
    for a in soup.select(".pager-list a[href*='page=']"):
        m = re.search(r"[?&]page=(\d+)", a.get("href", "") or "")
        if m:
            nums.add(int(m.group(1)))
    return max(nums)


def _fetch_listing(
    session: requests.Session, listing_dir: Path, page: int, refresh: bool
) -> tuple[str, bool]:
    """Return (html, fetched_from_network)."""
    cache_path = listing_dir / f"page-{page}.html"
    if cache_path.exists() and not refresh:
        log.info("listing page %d (cached)", page)
        return cache_path.read_text(encoding="utf-8"), False
    url = urljoin(BASE, LISTING_PATH if page == 0 else f"{LISTING_PATH}?page={page}")
    log.info("listing page %d -> GET %s", page, url)
    html = _get(session, url)
    cache_path.write_text(html, encoding="utf-8")
    return html, True


def fetch_listing_pages(
    session: requests.Session, cache_dir: Path, delay: float, refresh: bool
) -> list[str]:
    """Walk all listing pages. Return ordered, deduplicated slugs."""
    listing_dir = cache_dir / "list"
    listing_dir.mkdir(parents=True, exist_ok=True)

    slugs: list[str] = []
    seen: set[str] = set()

    html0, prev_was_network = _fetch_listing(session, listing_dir, 0, refresh)
    log.info("page 0: %d new problem link(s)", _extract_slugs(html0, seen, slugs))
    last = _max_page(html0)

    for page in range(1, last + 1):
        if prev_was_network:
            time.sleep(delay)
        html, prev_was_network = _fetch_listing(session, listing_dir, page, refresh)
        new = _extract_slugs(html, seen, slugs)
        log.info("page %d: %d new problem link(s)", page, new)

    log.info("collected %d unique slug(s) across %d listing page(s)", len(slugs), last + 1)
    return slugs


def fetch_problem_pages(
    session: requests.Session,
    slugs: list[str],
    cache_dir: Path,
    delay: float,
    refresh: bool,
    limit: int | None,
) -> int:
    op_dir = cache_dir / "op"
    op_dir.mkdir(parents=True, exist_ok=True)
    selected = slugs if limit is None else slugs[:limit]
    fetched = 0
    pending_sleep = False
    for i, slug in enumerate(selected, 1):
        cache_path = op_dir / f"{slug}.html"
        if cache_path.exists() and not refresh:
            log.info("[%d/%d] %s (cached)", i, len(selected), slug)
            continue
        if pending_sleep:
            time.sleep(delay)
        url = urljoin(BASE, f"/op/{slug}")
        log.info("[%d/%d] GET %s", i, len(selected), url)
        try:
            html = _get(session, url)
        except Exception as e:
            log.error("[%d/%d] failed %s: %s", i, len(selected), slug, e)
            pending_sleep = True
            continue
        cache_path.write_text(html, encoding="utf-8")
        fetched += 1
        pending_sleep = True
    return fetched


def main(argv: list[str] | None = None) -> int:
    here = Path(__file__).resolve().parent
    project = here.parent
    p = argparse.ArgumentParser(description="Crawl OPG graph-theory category.")
    p.add_argument("--cache-dir", type=Path, default=project / "cache")
    p.add_argument("--data-dir", type=Path, default=project / "data")
    p.add_argument(
        "--delay",
        type=float,
        default=12.0,
        help="seconds between requests (>=10 required by robots.txt)",
    )
    p.add_argument("--refresh", action="store_true", help="re-fetch even if cached")
    p.add_argument(
        "--limit",
        type=int,
        default=None,
        help="stop after N problem pages (smoke test)",
    )
    p.add_argument(
        "--listing-only",
        action="store_true",
        help="walk listings, do not fetch problem pages",
    )
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )

    if args.delay < 10:
        log.warning("delay %.1fs is below the 10s Crawl-Delay in robots.txt", args.delay)

    args.cache_dir.mkdir(parents=True, exist_ok=True)
    args.data_dir.mkdir(parents=True, exist_ok=True)

    session = make_session()
    slugs = fetch_listing_pages(session, args.cache_dir, args.delay, args.refresh)

    urls_path = args.data_dir / "urls.txt"
    urls_path.write_text("\n".join(f"/op/{s}" for s in slugs) + "\n", encoding="utf-8")
    log.info("wrote %s (%d slug(s))", urls_path, len(slugs))

    if args.listing_only:
        return 0

    fetched = fetch_problem_pages(
        session, slugs, args.cache_dir, args.delay, args.refresh, args.limit
    )
    log.info("done: %d new problem page(s); cache at %s", fetched, args.cache_dir / "op")
    return 0


if __name__ == "__main__":
    sys.exit(main())
