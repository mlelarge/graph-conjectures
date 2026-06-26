#!/usr/bin/env python3
"""
Independent read-only summarizer for an n*_disproof_ckpt.json checkpoint
(produced by scripts/n8_disproof.py).  Lightweight: parses JSON only, runs no
enumeration, so it is safe to call repeatedly during a live disproof run.

Reports, per the standing invariants:
  * completed edge-count buckets and the resume point;
  * per-bucket and total splits: non-planar / lemma-certified (κ'≥5) /
    searched-tested / capped / counterexamples;
  * whether the next run resumes cleanly (and from which bucket);
  * a one-line verdict (fully certified / partial-with-caps / COUNTEREXAMPLE).

Usage:
    .venv/bin/python problems/two_extremal_digraphs/scripts/disproof_checkpoint_summary.py [--n 9]
    .venv/bin/python .../disproof_checkpoint_summary.py --path <ckpt.json>
"""

import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def summarize(path):
    if not os.path.exists(path):
        print(f"[no checkpoint at {path}]")
        return 2
    try:
        with open(path) as f:
            ck = json.load(f)
    except json.JSONDecodeError:
        # could be a mid-write read; the writer uses atomic os.replace, so retry-once is cheap
        with open(path) as f:
            ck = json.load(f)

    n = ck.get("n")
    buckets = ck.get("buckets", {})
    cexs = ck.get("counterexamples", [])
    print(f"# disproof checkpoint summary  (n={n})")
    print(f"#   file: {path}")
    if ck.get("note"):
        print(f"#   note: {ck['note']}")

    done = sorted((int(k) for k, b in buckets.items() if b.get("done")))
    if not done:
        print("  no completed buckets yet.")
    else:
        print(f"  completed edge buckets |E|: {done[0]}..{done[-1]} "
              f"({len(done)} buckets)")
        gaps = [e for e in range(done[0], done[-1] + 1) if e not in done]
        if gaps:
            print(f"  !! gaps in completed range (not done): {gaps}")

    hdr = f"  {'|E|':>4} {'nonpl':>7} {'lemma':>7} {'searchd':>8} {'capped':>7} {'cex':>4}"
    print(hdr)
    tot = {"nonplanar": 0, "lemma": 0, "tested": 0, "capped": 0, "found": 0}
    for k in sorted(buckets, key=int):
        b = buckets[k]
        for f in tot:
            tot[f] += b.get(f, 0)
        print(f"  {int(k):>4} {b.get('nonplanar',0):>7} {b.get('lemma',0):>7} "
              f"{b.get('tested',0):>8} {b.get('capped',0):>7} {b.get('found',0):>4}")
    print(f"  {'TOT':>4} {tot['nonplanar']:>7} {tot['lemma']:>7} "
          f"{tot['tested']:>8} {tot['capped']:>7} {tot['found']:>4}")

    # resume point: first |E| (from 9 up) not marked done
    resume = None
    for e in range(9, 9 + 64):
        if str(e) not in buckets or not buckets[str(e)].get("done"):
            resume = e
            break
    if done and resume is not None and resume <= done[-1] + 1:
        print(f"  next run resumes cleanly from |E|={resume} "
              f"(completed buckets are skipped)")
    elif resume is not None:
        print(f"  next run starts at |E|={resume}")

    print()
    print(f"  counterexamples recorded: {len(cexs)}")
    for c in cexs[:5]:
        print(f"    n={c.get('n')} arcs={c.get('arcs')}")

    # verdict
    if cexs:
        print("\n  VERDICT: !!! COUNTEREXAMPLE present — verify with "
              "verify_counterexample.py (would refute Conjecture 9.2).")
        return 1
    if tot["capped"] > 0:
        print(f"\n  VERDICT: no counterexample so far; {tot['capped']} graph(s) "
              "budget-capped (uncertified) — raise --budget or use the "
              "forest/κ'≤4 certification on those.")
        return 0
    if done:
        print(f"\n  VERDICT: buckets |E|={done[0]}..{done[-1]} fully certified, "
              "0 capped, 0 counterexamples (no non-planar 2-extremal in that range).")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=9)
    ap.add_argument("--path", default=None)
    args = ap.parse_args()
    path = args.path or os.path.join(ROOT, "data", f"n{args.n}_disproof_ckpt.json")
    return summarize(path)


if __name__ == "__main__":
    raise SystemExit(main())
