"""Summarize a Phase 3 JSON log."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path


def summarize(log_path: Path) -> None:
    log = json.loads(log_path.read_text())
    entries = log["sample_entries"]
    verified = [e for e in entries if e.get("is_3_arc_strong")]
    print(f"Log: {log_path}")
    print(f"Started: {log['started_at']}, finished: {log.get('finished_at')}")
    print(f"Elapsed: {log.get('elapsed_s')}s")
    print(f"Seed: {log['seed']}")
    print(f"Templates: {log['templates']}")
    print()
    print(f"Aggregate:")
    print(f"  candidates streamed:              {log['candidates_total_streamed']}")
    print(f"  candidates skipped (not 3-arc-strong): {log['candidates_skipped_not_3_arc_strong']}")
    print(f"  candidates verified (3-arc-strong): {log['candidates_verified']}")
    print(f"  candidates UNSAT (3-arc-strong + UNSAT): {log['candidates_unsat']}")
    print(f"  publishable: {len(log['publishable_candidates'])}")
    print()
    if verified:
        print(f"3-arc-strong verified ({len(verified)}):")
        by_pair = Counter((e["template1"], e["template2"]) for e in verified)
        for k, c in sorted(by_pair.items(), key=lambda x: -x[1]):
            print(f"  ({k[0]} + {k[1]}): {c}")
        by_n = Counter(e["n"] for e in verified)
        print(f"  by n:")
        for k, c in sorted(by_n.items()):
            print(f"    n={k}: {c}")
        statuses = Counter(e["cross_check"]["ilp"] for e in verified)
        print(f"  by ILP status: {dict(statuses)}")
        sat_statuses = Counter(e["cross_check"]["sat"] for e in verified)
        print(f"  by SAT status: {dict(sat_statuses)}")
        disagreements = [e for e in verified if not e["cross_check"]["agree"]]
        if disagreements:
            print(f"  DISAGREEMENTS: {len(disagreements)}")
            for d in disagreements[:10]:
                print(f"    {d['name']}: ILP={d['cross_check']['ilp']} SAT={d['cross_check']['sat']}")
    if log["notes"]:
        print()
        print("Notes:")
        for n in log["notes"]:
            print(f"  {n}")


if __name__ == "__main__":
    paths = [Path(p) for p in sys.argv[1:]]
    if not paths:
        # find latest
        logs = sorted(Path(__file__).parent.joinpath("logs").glob("phase3_*.json"))
        if not logs:
            print("No logs found.")
            sys.exit(1)
        paths = [logs[-1]]
    for p in paths:
        summarize(p)
        print("=" * 72)
