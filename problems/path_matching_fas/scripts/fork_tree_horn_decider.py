"""Horn-classification-based fork-tree Path-FAS decider.

Replaces the broken V6 decider of D30. The previous decider used the
V6 chain-end heuristic (P3, P3', P4) to predict minimal fatal toggle
supports without enumerating them; that heuristic is empirically wrong
at k>=7 (Agent (c), D30).

The Horn decider takes the structural fact from D34, D35:

  The legality relation R(pi) of every fork-tree pairing pi at k<=7
  exhaustive and k=8 sample is Horn.

A Horn relation is the solution set of a Horn CNF: every clause has at
most one positive literal.  For a 0-valid Horn relation (every R(pi) is
0-valid), the equivalent representation is a conjunction of NEGATIVE
clauses (no positive literals).  Each minimal fatal toggle support
{i1, ..., il} translates to the clause

  not(eps_{i1} and eps_{i2} and ... and eps_{il}).

The full Horn CNF for R(pi) is the conjunction of these clauses across
all minimal fatal supports.

Once R(pi) is represented as a Horn CNF, deciding eps in R(pi) is a
POLYNOMIAL-TIME unit propagation check.  However, COMPUTING the Horn
CNF (i.e., enumerating the minimal fatal supports) currently requires
brute force in time O(2^k * suffix_walk), exponential in k.

This module provides:

- `compute_minimal_fatal_supports(k, pi)`: brute force exponential.
- `horn_cnf_from_supports(supports)`: convert to clause list.
- `decide_extendability(horn_cnf, eps)`: O(|cnf| * k) unit propagation.
- `decide_path_fas_fork_tree(k, pi)`: returns YES iff R(pi) is non-empty;
  since R(pi) is 0-valid, this is always YES.
- `legality_classifier(k, pi)`: combined object exposing the Horn CNF
  and the decide method.

The polynomial-time bound is CONTINGENT on a polynomial-time fatality
oracle for individual ladder candidates.  V6 was the candidate oracle
and is now refuted; a correct oracle is an open question.  See D37.

Usage:
  uv run python scripts/fork_tree_horn_decider.py --k 5 --pi 1,2,3,4,0
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from itertools import product
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from relation_miner import extract_relation, classify_schaefer  # noqa: E402
from rectangle_detachability_probe import minimal_fatal_toggle_sets  # noqa: E402


# ---------------------------------------------------------------------------
# Horn CNF representation.

Clause = tuple[int, ...]  # tuple of variable indices, all negated.
HornCNF = list[Clause]


def compute_minimal_fatal_supports(k: int, pi: Sequence[int]) -> list[tuple[int, ...]]:
    """Brute-force enumerate inclusion-minimal non-extendable toggle supports."""
    return sorted(minimal_fatal_toggle_sets(k, pi))


def horn_cnf_from_supports(supports: list[tuple[int, ...]]) -> HornCNF:
    """Translate minimal fatal supports to negative Horn clauses.

    A support {i1, ..., il} forbids the assignment eps_{i1} = ... =
    eps_{il} = 1.  Encoded as the clause "not all eps_i true" i.e.
    "at least one eps_i is false", which is a negative clause.
    """
    return [tuple(s) for s in supports]


def decide_extendability(horn_cnf: HornCNF, eps: Sequence[int]) -> bool:
    """O(|cnf| * k) check: does eps satisfy every clause?

    For a negative Horn clause (not(eps_{i1} and ... and eps_{il})),
    eps satisfies the clause iff at least one eps_{ij} = 0.

    Equivalently, eps falsifies the clause iff every eps_{ij} = 1.
    """
    eps_tuple = tuple(int(b) for b in eps)
    for clause in horn_cnf:
        if all(eps_tuple[i] == 1 for i in clause):
            return False
    return True


def decide_path_fas_fork_tree(k: int, pi: Sequence[int]) -> dict:
    """Decide Path-FAS on the fork-tree tournament for pairing pi.

    Path-FAS(T_pi) = YES iff R(pi) is non-empty.  Since R(pi) is
    0-valid for every fork-tree pairing (verified across k<=8), the
    answer is always YES and the all-zero toggle is a witness.
    """
    supports = compute_minimal_fatal_supports(k, pi)
    horn = horn_cnf_from_supports(supports)
    all_zero = tuple([0] * k)
    yes = decide_extendability(horn, all_zero)
    return {
        "k": k,
        "pi": list(pi),
        "yes": yes,
        "witness": list(all_zero) if yes else None,
        "minimal_fatal_supports": [list(s) for s in supports],
        "horn_cnf_size": len(horn),
    }


def legality_classifier(k: int, pi: Sequence[int]) -> dict:
    """Full Horn-CNF classifier for R(pi).

    Returns:
      - horn_cnf: list of negative Horn clauses.
      - relation_size: |R(pi)|.
      - is_horn / is_bijunctive / is_affine / etc.: Schaefer classification.
      - decide: callable eps -> bool.
    """
    supports = compute_minimal_fatal_supports(k, pi)
    horn = horn_cnf_from_supports(supports)
    R = extract_relation(k, pi)
    schaefer = classify_schaefer(R)
    return {
        "k": k,
        "pi": list(pi),
        "minimal_fatal_supports": [list(s) for s in supports],
        "horn_cnf": [list(c) for c in horn],
        "horn_cnf_size": len(horn),
        "relation_size": len(R),
        "schaefer": schaefer,
    }


# ---------------------------------------------------------------------------
# Verification utilities.

def verify_decider_matches_brute_force(k: int, pi: Sequence[int]) -> dict:
    """Cross-check: decide_extendability via Horn CNF matches brute-force
    R(pi) lookup for every eps in {0,1}^k."""
    supports = compute_minimal_fatal_supports(k, pi)
    horn = horn_cnf_from_supports(supports)
    R = extract_relation(k, pi)
    mismatches: list[dict] = []
    for eps in product((0, 1), repeat=k):
        horn_says_yes = decide_extendability(horn, eps)
        brute_says_yes = eps in R
        if horn_says_yes != brute_says_yes:
            mismatches.append({
                "eps": list(eps),
                "horn": horn_says_yes,
                "brute": brute_says_yes,
            })
    return {
        "k": k,
        "pi": list(pi),
        "checked": 1 << k,
        "mismatches": mismatches,
        "all_match": not mismatches,
    }


def sweep_at_k(k: int, sample_size: int | None = None,
               seed: int = 0) -> dict:
    """Sweep all pairings (or a sample) at k and verify Horn decider."""
    from itertools import permutations
    import random

    if sample_size is None:
        pis = list(permutations(range(k)))
    else:
        rng = random.Random(seed)
        all_pis = list(permutations(range(k)))
        pis = rng.sample(all_pis, min(sample_size, len(all_pis)))

    total_mismatches = 0
    pairings_with_mismatch = 0
    first_mismatch: dict | None = None
    for pi in pis:
        out = verify_decider_matches_brute_force(k, pi)
        if not out["all_match"]:
            total_mismatches += len(out["mismatches"])
            pairings_with_mismatch += 1
            if first_mismatch is None:
                first_mismatch = out
    return {
        "k": k,
        "pairings_checked": len(pis),
        "pairings_with_mismatch": pairings_with_mismatch,
        "total_mismatches": total_mismatches,
        "first_mismatch": first_mismatch,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, required=True)
    parser.add_argument("--pi", type=str, default=None,
                        help="comma-separated permutation; if omitted, sweeps all")
    parser.add_argument("--sweep", action="store_true")
    parser.add_argument("--sample", type=int, default=None)
    parser.add_argument("--verify", action="store_true",
                        help="cross-check Horn decider vs brute force")
    args = parser.parse_args()

    if args.sweep:
        out = sweep_at_k(args.k, sample_size=args.sample)
        print(json.dumps(out, indent=2, default=list))
        return

    if args.pi is None:
        parser.error("either --pi or --sweep is required")

    pi = tuple(int(x) for x in args.pi.split(","))
    if args.verify:
        out = verify_decider_matches_brute_force(args.k, pi)
    else:
        out = legality_classifier(args.k, pi)
    print(json.dumps(out, indent=2, default=list))


if __name__ == "__main__":
    main()
