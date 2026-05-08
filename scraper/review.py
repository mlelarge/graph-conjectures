#!/usr/bin/env python3
"""Per-problem literature review via `claude -p`.

Shells out to Claude Code's non-interactive mode (Max-plan auth) for each
problem in data/problems.json. Restricts tools to WebSearch + WebFetch.
Idempotent per slug; resumable on rate-limit.

Outputs:
  data/reviews/<slug>.json   (one per problem)
  data/reviews/<slug>.raw.json   (full claude session, only on parse failure — for debugging)
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import signal
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path

log = logging.getLogger("review")

SCHEMA_REQUIRED = {
    "status",
    "confidence",
    "summary",
    "since_posted",
    "search_queries",
    "verified_urls",
    "notes",
}
VALID_STATUS = {"open", "solved", "disproved", "partial", "unclear"}
VALID_CONF = {"high", "medium", "low"}
VALID_KIND = {"proof", "counterexample", "partial", "survey", "reduction"}


# ---- prompt builders -------------------------------------------------------

def build_user_prompt(p: dict) -> str:
    parts = [
        f"# Problem: {p['title']}",
        f"Slug: {p['slug']}",
        f"Canonical URL: {p['canonical_url']}",
        f"Posted: {p.get('posted_at') or p.get('posted_at_raw') or 'unknown'}",
    ]
    if p.get("subject_path"):
        parts.append("Subject path: " + " » ".join(s["label"] for s in p["subject_path"]))
    if p.get("authors"):
        parts.append("Author(s): " + ", ".join(a["label"] for a in p["authors"]))
    if p.get("keywords"):
        parts.append("Keywords: " + ", ".join(k["label"] for k in p["keywords"]))
    parts.append("")
    parts.append("## Statement(s)")
    if p.get("statements"):
        for s in p["statements"]:
            parts.append(f"**{s['kind']}.** {s['text']}")
    elif p.get("statement_text"):
        parts.append(p["statement_text"])
    if p.get("discussion_text", "").strip():
        parts.append("")
        parts.append("## Discussion (from OPG)")
        parts.append(p["discussion_text"])
    if p.get("references"):
        parts.append("")
        parts.append("## OPG bibliography (your starting point — verify post-posting follow-ups against these)")
        for r in p["references"]:
            parts.append(f"- {r['raw_text']}")
    parts.append("")
    parts.append(
        "Now perform the literature review per your instructions and return the JSON in <review_json> tags."
    )
    return "\n".join(parts)


# ---- claude invocation -----------------------------------------------------

def call_claude(
    user_prompt: str, system_prompt: str, model: str, timeout: int
) -> subprocess.CompletedProcess[str]:
    """Run `claude -p` in its own process group so a hung Node grandchild can be
    SIGKILL'd cleanly. Raises subprocess.TimeoutExpired on timeout, after the
    entire group has been killed."""
    cmd = [
        "claude",
        "-p",
        user_prompt,
        "--append-system-prompt",
        system_prompt,
        "--allowed-tools",
        "WebSearch WebFetch",
        "--model",
        model,
        "--output-format",
        "json",
        "--no-session-persistence",
    ]
    log.debug("invoking claude (model=%s, user_prompt_len=%d)", model, len(user_prompt))
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    # Watchdog: a separate thread walks the process tree at the deadline
    # and SIGKILLs every descendant. Plain os.killpg() turned out to not
    # reach claude's Node-spawned grandchildren in practice, so we recurse
    # via `pgrep -P` instead.
    killed = {"by_watchdog": False}

    def _kill_tree(pid: int) -> None:
        try:
            r = subprocess.run(
                ["pgrep", "-P", str(pid)],
                capture_output=True,
                text=True,
                timeout=2,
            )
            for tok in r.stdout.split():
                try:
                    _kill_tree(int(tok))
                except ValueError:
                    pass
        except Exception:
            pass
        try:
            os.kill(pid, signal.SIGKILL)
        except (ProcessLookupError, OSError):
            pass

    def _on_deadline() -> None:
        killed["by_watchdog"] = True
        # Try the process-group route first (cheap), then walk descendants.
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except (ProcessLookupError, OSError):
            pass
        _kill_tree(proc.pid)

    watchdog = threading.Timer(timeout, _on_deadline)
    watchdog.start()
    try:
        stdout, stderr = proc.communicate()
    finally:
        watchdog.cancel()

    if killed["by_watchdog"]:
        raise subprocess.TimeoutExpired(cmd, timeout)
    return subprocess.CompletedProcess(
        cmd, returncode=proc.returncode, stdout=stdout or "", stderr=stderr or ""
    )


_RATE_LIMIT_RE = re.compile(r"rate.?limit|usage limit|429|too many requests", re.IGNORECASE)


def looks_rate_limited(text: str) -> bool:
    return bool(_RATE_LIMIT_RE.search(text or ""))


# ---- response parsing ------------------------------------------------------

def extract_assistant_text(claude_json_str: str) -> tuple[str, dict]:
    obj = json.loads(claude_json_str)
    text = obj.get("result")
    if not text:
        # Fallback: scan the messages array for the last assistant message
        for m in reversed(obj.get("messages", []) or []):
            if isinstance(m, dict) and m.get("role") == "assistant":
                content = m.get("content")
                if isinstance(content, str):
                    text = content
                    break
                if isinstance(content, list):
                    text = "".join(
                        c.get("text", "") for c in content if isinstance(c, dict)
                    )
                    break
    return text or "", obj


_REVIEW_RE = re.compile(r"<review_json>\s*(\{.*?\})\s*</review_json>", re.DOTALL)


def extract_review(assistant_text: str) -> dict:
    m = _REVIEW_RE.search(assistant_text)
    if not m:
        raise ValueError("no <review_json> block found in assistant output")
    return json.loads(m.group(1))


# ---- validation ------------------------------------------------------------

def validate(review: dict) -> None:
    missing = SCHEMA_REQUIRED - set(review.keys())
    if missing:
        raise ValueError(f"missing required fields: {sorted(missing)}")
    if review["status"] not in VALID_STATUS:
        raise ValueError(f"invalid status: {review['status']!r}")
    if review["confidence"] not in VALID_CONF:
        raise ValueError(f"invalid confidence: {review['confidence']!r}")
    if not isinstance(review["since_posted"], list):
        raise ValueError("since_posted must be a list")
    verified = set(review.get("verified_urls") or [])
    for i, entry in enumerate(review["since_posted"]):
        if not isinstance(entry, dict):
            raise ValueError(f"since_posted[{i}] must be an object")
        url = entry.get("url")
        if url and url not in verified:
            raise ValueError(f"since_posted[{i}].url not in verified_urls: {url}")
        kind = entry.get("kind")
        if kind and kind not in VALID_KIND:
            raise ValueError(f"since_posted[{i}].kind invalid: {kind!r}")


# ---- per-problem driver ----------------------------------------------------

def review_one(
    slug: str, problem: dict, system_prompt: str, out_dir: Path, args: argparse.Namespace
) -> str:
    """Returns one of: 'ok', 'cached', 'rate_limited', 'failed', 'failed_parse', 'failed_validate'."""
    cache = out_dir / f"{slug}.json"
    if cache.exists() and not args.refresh:
        log.info("[%s] cached, skipping", slug)
        return "cached"

    user_prompt = build_user_prompt(problem)
    log.info("[%s] reviewing (prompt %d chars)…", slug, len(user_prompt))
    t0 = time.time()
    try:
        proc = call_claude(user_prompt, system_prompt, args.model, args.timeout)
    except subprocess.TimeoutExpired:
        log.error("[%s] timeout after %ds", slug, args.timeout)
        return "failed"
    elapsed = time.time() - t0

    if proc.returncode != 0 or not proc.stdout.strip():
        if looks_rate_limited(proc.stderr) or looks_rate_limited(proc.stdout):
            log.warning("[%s] rate-limited (elapsed %.0fs)", slug, elapsed)
            return "rate_limited"
        log.error(
            "[%s] claude exit=%d (elapsed %.0fs); stderr: %s",
            slug,
            proc.returncode,
            elapsed,
            (proc.stderr or "")[:500],
        )
        return "failed"

    try:
        text, full = extract_assistant_text(proc.stdout)
        review = extract_review(text)
    except Exception as e:
        log.error("[%s] parse failed (%.0fs): %s", slug, elapsed, e)
        (out_dir / f"{slug}.raw.json").write_text(proc.stdout, encoding="utf-8")
        return "failed_parse"

    try:
        validate(review)
    except Exception as e:
        log.error("[%s] validation failed: %s", slug, e)
        (out_dir / f"{slug}.raw.json").write_text(proc.stdout, encoding="utf-8")
        return "failed_validate"

    review.update(
        {
            "slug": slug,
            "reviewed_at": date.today().isoformat(),
            "model": args.model,
            "search_enabled": True,
            "elapsed_seconds": round(elapsed, 1),
        }
    )
    cache.write_text(json.dumps(review, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info(
        "[%s] %s (%s, %d cite(s), %.0fs)",
        slug,
        review["status"],
        review["confidence"],
        len(review["since_posted"]),
        elapsed,
    )
    return "ok"


# ---- main ------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    here = Path(__file__).resolve().parent
    project = here.parent
    p = argparse.ArgumentParser(description="Literature-review every OPG problem via `claude -p`.")
    p.add_argument("--data-dir", type=Path, default=project / "data")
    p.add_argument("--out-dir", type=Path, default=project / "data" / "reviews")
    p.add_argument(
        "--system-prompt-file",
        type=Path,
        default=here / "review_system_prompt.md",
    )
    p.add_argument("--model", default="claude-sonnet-4-6")
    p.add_argument(
        "--timeout",
        type=int,
        default=480,
        help="seconds per claude call (default 480 = 8 min; observed legit max ~340s)",
    )
    p.add_argument(
        "--rate-limit-sleep",
        type=int,
        default=1800,
        help="seconds to wait after a rate-limit error (default 30 min)",
    )
    p.add_argument("--slug", action="append", help="review only this slug (repeatable)")
    p.add_argument("--limit", type=int, help="stop after N successful reviews (0 disables)")
    p.add_argument("--refresh", action="store_true", help="re-review even if cached")
    p.add_argument(
        "--concurrency",
        type=int,
        default=1,
        help="parallel `claude -p` calls (default 1; bump to 3-4 if Max plan has headroom)",
    )
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )

    system_prompt = args.system_prompt_file.read_text(encoding="utf-8")
    problems = json.loads((args.data_dir / "problems.json").read_text(encoding="utf-8"))
    by_slug = {p["slug"]: p for p in problems}

    if args.slug:
        targets = [by_slug[s] for s in args.slug if s in by_slug]
        missing = [s for s in args.slug if s not in by_slug]
        if missing:
            log.error("unknown slugs: %s", missing)
            return 2
    else:
        targets = problems

    args.out_dir.mkdir(parents=True, exist_ok=True)

    counts = {"ok": 0, "cached": 0, "rate_limited": 0, "failed": 0, "failed_parse": 0, "failed_validate": 0}
    counts_lock = threading.Lock()
    rate_limit_lock = threading.Lock()
    stop_event = threading.Event()

    def worker(problem: dict) -> str:
        if stop_event.is_set():
            return "cached"
        return review_one(problem["slug"], problem, system_prompt, args.out_dir, args)

    log.info(
        "processing %d slug(s) with concurrency %d", len(targets), args.concurrency
    )
    with ThreadPoolExecutor(max_workers=max(1, args.concurrency)) as ex:
        futures = {ex.submit(worker, p): p for p in targets}
        for fut in as_completed(futures):
            try:
                result = fut.result()
            except Exception as e:
                log.error("worker exception: %s", e)
                result = "failed"
            with counts_lock:
                counts[result] = counts.get(result, 0) + 1
                done_ok = counts["ok"]

            if result == "rate_limited":
                # Serialise the back-off so concurrent workers don't all sleep separately
                acquired = rate_limit_lock.acquire(blocking=False)
                if acquired:
                    try:
                        log.warning(
                            "rate-limited; sleeping %ds (other workers will queue)",
                            args.rate_limit_sleep,
                        )
                        time.sleep(args.rate_limit_sleep)
                    finally:
                        rate_limit_lock.release()
                else:
                    # Another worker already holds the lock; just wait it out
                    rate_limit_lock.acquire()
                    rate_limit_lock.release()

            if args.limit and done_ok >= args.limit:
                log.info("reached --limit %d; cancelling pending work", args.limit)
                stop_event.set()
                for f in futures:
                    f.cancel()
                break

    log.info("done: %s", " ".join(f"{k}={v}" for k, v in counts.items() if v))
    return 0


if __name__ == "__main__":
    sys.exit(main())
