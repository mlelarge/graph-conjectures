"""Cross-check ILP vs SAT backends on a digraph.

Returns a verdict for each instance and fails fatally on disagreement.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Any

from digraph import Digraph
from verifier_ilp import verify_ilp
from verifier_sat import verify_sat


@dataclass
class CrossCheckResult:
    name: str
    ilp: dict[str, Any]
    sat: dict[str, Any]
    agree: bool
    notes: list[str]


def cross_check(D: Digraph, name: str = "<unnamed>", time_limit_s: float = 60.0) -> CrossCheckResult:
    ilp_res = verify_ilp(D, time_limit_s=time_limit_s)
    sat_res = verify_sat(D, time_limit_s=time_limit_s)

    s1, s2 = ilp_res["status"], sat_res["status"]
    notes: list[str] = []
    agree = True

    if {s1, s2} <= {"SAT", "UNSAT"}:
        if s1 != s2:
            agree = False
            notes.append(
                f"FATAL DISAGREEMENT: ILP={s1} but SAT={s2} on instance '{name}'"
            )
    elif s1 == "UNKNOWN" and s2 == "UNKNOWN":
        notes.append("Both backends returned UNKNOWN (timeout or iter cap).")
    elif s1 == "UNKNOWN" or s2 == "UNKNOWN":
        notes.append(f"One backend UNKNOWN: ILP={s1}, SAT={s2}. Not fatal.")
    else:
        notes.append(f"Unexpected status pair: ILP={s1}, SAT={s2}")
        agree = False

    return CrossCheckResult(name=name, ilp=ilp_res, sat=sat_res, agree=agree, notes=notes)


if __name__ == "__main__":
    from benchmarks import all_benchmarks

    bad = []
    for b in all_benchmarks():
        D = b.build()
        r = cross_check(D, b.name)
        flag = "OK " if r.agree else "FAIL"
        print(
            f"{flag} {b.name:18s} expected={b.expected:6s}  "
            f"ILP={r.ilp['status']:7s}  SAT={r.sat['status']:7s}  "
            f"t_ilp={r.ilp['time_s']:.2f}s  t_sat={r.sat['time_s']:.2f}s"
        )
        for note in r.notes:
            print(f"      note: {note}")
        if not r.agree:
            bad.append(b.name)

    if bad:
        print(f"\nFATAL: {len(bad)} disagreement(s): {bad}", file=sys.stderr)
        sys.exit(1)
    print("\nAll backends agree.")
