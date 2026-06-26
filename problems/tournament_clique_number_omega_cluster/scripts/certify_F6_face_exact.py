"""Certificate that the q0=1 face optimum at depth 6 is F_6 = 45.

The key lower-bound lemma is the boundary cut in every q0=1 parent.  If a depth-6
face order has heights <= (1,A,B), decompose it into depth-5 top modules
M_0,M_1,M_2.  Since q0=1, every M_0 vertex precedes every M_1 vertex.  At the
separator after M_0 and before M_1, if x M_2 vertices have appeared, the closure
formula gives

    pre_1(M_2,x)       <= A - q1(M_1)
    suf_2(M_2,3^5 - x) <= B - q2(M_0).

Also M_0 and M_1 are depth-5 face modules, so

    q2(M_0) >= ceil(F_5/A),   q1(M_1) >= ceil(F_5/B).

Thus every depth-6 face order with AB < 45 would force a depth-5 M_2 with a
simultaneous cut at the maximal slack scanned in ``data/two_cut_f6_scan.json``.
That scan is 0/52 SAT for all ordered pairs 25 <= AB < 45, A,B >= 2.  The cases
AB < 25 are excluded by F_5=25 in the M_2 child, and A=1 or B=1 are excluded by
the two-free-colours lemma.  Together with the certified construction F_6 <= 45,
this pins F_6 exactly.
"""

from __future__ import annotations

import json
import math
import os

F5 = 25
F6_UPPER = 45
MODULE_DEPTH = 5
PARENT_DEPTH = 6


def maximal_boundary_slack(A, B, floor=F5):
    """Maximal slack allowed by depth-5 face companions under caps (A,B)."""

    return A - math.ceil(floor / B), B - math.ceil(floor / A)


def relevant_sub45_targets(limit=F6_UPPER, floor=F5):
    """Ordered cap pairs that need SAT exclusion for the boundary-cut lemma."""

    rows = []
    for A in range(2, limit):
        for B in range(2, limit):
            product = A * B
            if not (floor <= product < limit):
                continue
            r1, r2 = maximal_boundary_slack(A, B, floor)
            if r1 < 0 or r2 < 0:
                continue
            rows.append((product, A, B, r1, r2))
    return tuple(sorted(rows))


def default_scan_path():
    return os.path.join(os.path.dirname(__file__), "..", "data", "two_cut_f6_scan.json")


def certify_scan(path=None):
    """Validate that the saved SAT scan excludes every relevant sub-45 target."""

    path = path or default_scan_path()
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)

    expected = relevant_sub45_targets()
    rows = data["rows"]
    actual = tuple(
        (row["product"], row["A"], row["B"], row["r1"], row["r2"])
        for row in rows
    )
    if actual != expected:
        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        raise AssertionError({"missing": missing, "extra": extra})
    sat_rows = [row for row in rows if row["sat"]]
    if sat_rows:
        raise AssertionError({"sat_rows": sat_rows})
    if data.get("target_count") != len(expected) or data.get("sat_count") != 0:
        raise AssertionError({
            "target_count": data.get("target_count"),
            "expected_count": len(expected),
            "sat_count": data.get("sat_count"),
        })

    return {
        "module_depth": MODULE_DEPTH,
        "parent_depth": PARENT_DEPTH,
        "F5": F5,
        "lower_bound": F6_UPPER,
        "upper_bound": F6_UPPER,
        "F6": F6_UPPER,
        "scan_path": path,
        "targets_excluded": len(expected),
        "sat_count": 0,
        "products_excluded": sorted({product for product, *_ in expected}),
        "notes": [
            "AB < 25 excluded by the M2 child and F5=25",
            "A=1 or B=1 excluded by the two-free-colours lemma at depth 6",
            "25 <= AB < 45, A,B >= 2 excluded by boundary-cut SAT scan",
            "F6 <= 45 supplied by the certified (1,5,9) face construction",
        ],
    }


def main():
    print(json.dumps(certify_scan(), indent=2))


if __name__ == "__main__":
    main()
