"""Empirical verification of the fork-tree monotonicity theorem (D37).

The theorem (Section 48 of exchange_proof_draft.md):

  If eps <= eps' coordinate-wise and eps' is extendable on
  fork-tree(k, pi), then eps is extendable.

Equivalently, R(pi) is downward-closed in the lattice {0,1}^k.

The proof is by direct subset-of-linear-forest argument; see Section 48.
This module empirically verifies the claim on every R(pi) at small k
to catch any subtle interaction I might have missed in the proof
sketch.

Usage:
  uv run python scripts/monotonicity_probe.py --k 5 --all
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from itertools import permutations
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from relation_miner import extract_relation  # noqa: E402


def is_downward_closed(R: frozenset[tuple[int, ...]], k: int) -> tuple[bool, list[tuple]]:
    """Check R is downward-closed: for every eps in R and every
    eps' <= eps, eps' in R.

    Returns (verdict, list of violating (eps_higher, eps_lower) pairs).
    """
    violations = []
    R_set = set(R)
    for eps in R:
        # Enumerate eps' <= eps by flipping any subset of 1-bits to 0.
        ones = [i for i, b in enumerate(eps) if b == 1]
        for mask in range(1 << len(ones)):
            new_eps = list(eps)
            for j, i in enumerate(ones):
                if mask & (1 << j):
                    new_eps[i] = 0
            new_eps_t = tuple(new_eps)
            if new_eps_t not in R_set:
                violations.append((eps, new_eps_t))
                if len(violations) >= 5:
                    return False, violations
    return len(violations) == 0, violations


def verify_pairing(k: int, pi: Sequence[int]) -> dict:
    """Check monotonicity for one pairing."""
    R = extract_relation(k, pi)
    ok, violations = is_downward_closed(R, k)
    return {
        "k": k,
        "pi": list(pi),
        "relation_size": len(R),
        "downward_closed": ok,
        "violations": [{"eps_above": list(a), "eps_below": list(b)}
                       for a, b in violations[:3]],
    }


def sweep_all(k: int) -> dict:
    """Verify monotonicity across all k! pairings at k."""
    violations = []
    checked = 0
    for pi in permutations(range(k)):
        out = verify_pairing(k, pi)
        checked += 1
        if not out["downward_closed"]:
            violations.append(out)
    return {
        "k": k,
        "pairings_checked": checked,
        "violations": len(violations),
        "first_violations": violations[:3],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, required=True)
    parser.add_argument("--pi", type=str, default=None)
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    if args.all:
        out = sweep_all(args.k)
    elif args.pi:
        pi = tuple(int(x) for x in args.pi.split(","))
        out = verify_pairing(args.k, pi)
    else:
        parser.error("either --pi or --all required")

    print(json.dumps(out, indent=2, default=list))


if __name__ == "__main__":
    main()
