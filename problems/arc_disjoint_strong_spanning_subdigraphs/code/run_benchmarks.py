"""Run the full benchmark validation set and print a pass/fail table."""

from __future__ import annotations

import sys
import time

from benchmarks import all_benchmarks
from cross_check import cross_check


def main() -> int:
    print(
        f"{'name':<18s}  {'n':>2s}  {'m':>3s}  "
        f"{'kappa':>5s}  {'expect':>6s}  "
        f"{'ILP':>6s}  {'SAT':>6s}  {'tILP':>7s}  {'tSAT':>7s}  agree"
    )
    print("-" * 92)
    fail_count = 0
    total_t = 0.0
    for b in all_benchmarks():
        D = b.build()
        t0 = time.time()
        r = cross_check(D, b.name, time_limit_s=120.0)
        total_t += time.time() - t0
        ilp_ok = r.ilp["status"] == b.expected
        sat_ok = r.sat["status"] == b.expected
        both_match_expected = ilp_ok and sat_ok
        agree_flag = "OK " if r.agree and both_match_expected else "FAIL"
        if agree_flag == "FAIL":
            fail_count += 1
        print(
            f"{b.name:<18s}  "
            f"{b.n:>2d}  {D.m():>3d}  "
            f"{D.arc_connectivity():>5d}  {b.expected:>6s}  "
            f"{r.ilp['status']:>6s}  {r.sat['status']:>6s}  "
            f"{r.ilp['time_s']:>6.2f}s  {r.sat['time_s']:>6.2f}s  {agree_flag}"
        )
        for note in r.notes:
            print(f"   note: {note}")
        # If either backend disagreed with the expected literature answer,
        # print the witness validation status (sanity log).
        if not both_match_expected:
            print(
                f"   ILP got {r.ilp['status']} (expected {b.expected}); "
                f"SAT got {r.sat['status']}"
            )
            if r.ilp.get("reason"):
                print(f"   ILP reason: {r.ilp['reason']}")
            if r.sat.get("reason"):
                print(f"   SAT reason: {r.sat['reason']}")

    print("-" * 92)
    if fail_count == 0:
        print(f"All {len(all_benchmarks())} benchmarks passed in {total_t:.1f}s.")
        return 0
    print(f"{fail_count} benchmark(s) FAILED in {total_t:.1f}s.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
