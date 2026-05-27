"""Relation miner for fork-tree gadgets.

For a fork-tree pairing pi in S_k, the *legality relation* is

    R(pi) = { eps in {0,1}^k : eps is an extendable toggle pattern
                               on fork_tree_tournament(k, pi) }.

This module enumerates R(pi), canonicalises it up to coordinate
permutation and per-coordinate bit flips, and classifies it under
Schaefer's Boolean dichotomy (0-valid, 1-valid, bijunctive, Horn,
dual-Horn, affine).  A relation that is in none of the six tractable
Schaefer classes is NP-hard as a constraint type.

This is Track 3 of the CSP-classification attack on Aboulker's
Problem 4.4 (Path-FAS in P?).  Tracks 1 (formal gadget-as-relation
interface) and 2 (k=6 bijunctive theorem) live elsewhere.

Usage:

    from scripts.relation_miner import (
        extract_relation,
        canonicalize_relation,
        classify_schaefer,
        is_np_hard_type,
    )

    R = extract_relation(7, (1, 2, 3, 4, 5, 6, 0))
    canon = canonicalize_relation(R)
    cls = classify_schaefer(R)
    hard = is_np_hard_type(R)
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import sys
import time
from collections import Counter
from itertools import combinations, permutations, product
from typing import Iterable, Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rectangle_detachability_probe import (  # noqa: E402
    exact_toggle_status,
    minimal_fatal_toggle_sets,
)


Relation = frozenset[tuple[int, ...]]


# ---------------------------------------------------------------------------
# M1.a Relation extraction.

def extract_relation(k: int, pi: Sequence[int]) -> Relation:
    """Return R(pi) = set of extendable toggle bit-vectors at k.

    A bit-vector eps in {0,1}^k is in R(pi) iff the fork-tree prefix
    induced by eps survives FF pruning *and* has a completing suffix.
    """
    status = exact_toggle_status(k, pi)
    out: set[tuple[int, ...]] = set()
    for bits, extendable in status.items():
        if extendable:
            out.add(tuple(int(b) for b in bits))
    return frozenset(out)


# ---------------------------------------------------------------------------
# M1.b Canonical form.

def _flip_relation(R: Relation, mask: int) -> Relation:
    """XOR every tuple in R with the binary representation of `mask`."""
    return frozenset(
        tuple(b ^ ((mask >> i) & 1) for i, b in enumerate(t))
        for t in R
    )


def _permute_relation(R: Relation, perm: Sequence[int]) -> Relation:
    """Reorder coordinates by `perm`: new tuple[i] = old tuple[perm[i]]."""
    return frozenset(
        tuple(t[perm[i]] for i in range(len(perm)))
        for t in R
    )


def _sorted_relation_key(R: Relation) -> tuple:
    """Hashable canonical representative of a set-of-tuples."""
    return tuple(sorted(R))


def _column_canonical_flip(R: Relation, k: int) -> Relation:
    """Flip each column independently so its column-weight <= |R|/2.

    Ties broken by leaving the column unflipped.  The result is
    invariant under the (Z/2Z)^k subgroup AT THE COLUMN-WEIGHT LEVEL
    but is NOT a full canonical form by itself; it is a fast normalising
    step that lets us prune the permutation search.
    """
    if not R:
        return R
    n = len(R)
    cols = [[t[i] for t in R] for i in range(k)]
    weights = [sum(c) for c in cols]
    mask = 0
    for i, w in enumerate(weights):
        if 2 * w > n:
            mask |= 1 << i
    return _flip_relation(R, mask)


def _relation_invariant(R: Relation) -> tuple:
    """Fast permutation-and-flip-invariant signature.

    Two relations with different invariants are not equivalent.
    Same invariant *almost always* means equivalent for typical inputs;
    we still verify by full canonicalisation when collisions occur.

    The signature:
      - |R|
      - arity k
      - multiset of (min(col_weight, n-col_weight)) -- since each column
        can be independently flipped, only the smaller of {w, n-w} is
        invariant.
      - multiset of per-column "row co-occurrence signatures":
        for each column, after flipping to make weight <= n/2,
        record the multiset of row weights of rows where the column
        bit is 1 (this is column-flip-aware but column-permutation
        invariant since we take the multiset across columns).
    """
    if not R:
        return (0,)
    k = len(next(iter(R)))
    n = len(R)
    if n == 0:
        return (0, k)
    cols = [[t[i] for t in R] for i in range(k)]
    col_w = [sum(c) for c in cols]
    # Flip each column to weight <= n/2 (ties: prefer the orientation
    # whose 1-rows have lex-smallest row-weight multiset).
    rows_list = list(R)
    row_w = [sum(t) for t in rows_list]
    col_sigs: list[tuple] = []
    for i in range(k):
        ones_idx = [r for r, t in enumerate(rows_list) if t[i] == 1]
        zeros_idx = [r for r in range(n) if r not in ones_idx]
        sig_ones = tuple(sorted(row_w[r] for r in ones_idx))
        sig_zeros = tuple(sorted(row_w[r] for r in zeros_idx))
        # Pick canonical orientation: smaller weight, ties by lex of sig.
        if (len(ones_idx), sig_ones) <= (len(zeros_idx), sig_zeros):
            col_sigs.append((len(ones_idx), sig_ones))
        else:
            col_sigs.append((len(zeros_idx), sig_zeros))
    col_sigs.sort()
    row_w_sorted = tuple(sorted(row_w))
    # Also include sorted "global-complement-invariant" row weight stats:
    row_w_inv = tuple(sorted(min(w, k - w) for w in row_w))
    return (n, k, tuple(col_sigs), row_w_sorted, row_w_inv)


def canonicalize_relation(R: Relation) -> tuple:
    """Return canonical form of R under (coordinate-permutation x bit-flips).

    The full symmetry group acting on relations in {0,1}^k is the
    hyperoctahedral group B_k = (Z/2Z)^k semidirect S_k of order
    k! * 2^k.  We enumerate column permutations and bit flips and
    return the lexicographically smallest sorted-tuple representative.

    For speed: we first normalise each column to weight <= |R|/2 so
    that we only need to try the residual bit-flip mask on ties.
    """
    if not R:
        return ()
    k = len(next(iter(R)))
    if k == 0:
        return ()
    n = len(R)
    best: tuple | None = None
    # For each column permutation perm, the columns of (permuted) R have
    # weights w_perm[i] = col_w[perm[i]].  Among bit-flips we must flip
    # column i iff (col_w[perm[i]] > n/2) OR (col_w[perm[i]] == n/2 AND we choose).
    cols = [[t[i] for t in R] for i in range(k)]
    col_w = [sum(c) for c in cols]
    for perm in permutations(range(k)):
        # Forced-flip mask: every column with weight > n/2 must be flipped.
        forced = 0
        tie_cols: list[int] = []
        for i in range(k):
            w = col_w[perm[i]]
            if 2 * w > n:
                forced |= 1 << i
            elif 2 * w == n:
                tie_cols.append(i)
        permuted = _permute_relation(R, perm)
        # Enumerate only the 2^|tie_cols| free flip choices.
        for tie_choice in range(1 << len(tie_cols)):
            mask = forced
            for j, c in enumerate(tie_cols):
                if (tie_choice >> j) & 1:
                    mask |= 1 << c
            flipped = _flip_relation(permuted, mask)
            key = _sorted_relation_key(flipped)
            if best is None or key < best:
                best = key
    assert best is not None
    return best


# ---------------------------------------------------------------------------
# M1.c Schaefer classification.

def _bitwise_majority(t1: tuple[int, ...], t2: tuple[int, ...], t3: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(int(a + b + c >= 2) for a, b, c in zip(t1, t2, t3))


def _bitwise_and(t1: tuple[int, ...], t2: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(a & b for a, b in zip(t1, t2))


def _bitwise_or(t1: tuple[int, ...], t2: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(a | b for a, b in zip(t1, t2))


def _bitwise_xor3(t1: tuple[int, ...], t2: tuple[int, ...], t3: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(a ^ b ^ c for a, b, c in zip(t1, t2, t3))


def _closed_under(R: Relation, ternary, pairs: bool = False) -> bool:
    if pairs:
        for a in R:
            for b in R:
                if ternary(a, b) not in R:
                    return False
        return True
    for a in R:
        for b in R:
            for c in R:
                if ternary(a, b, c) not in R:
                    return False
    return True


def is_bijunctive(R: Relation) -> bool:
    """R is bijunctive iff R is closed under coordinate-wise majority(a,b,c).

    Equivalently: R is the solution set of a 2-CNF formula.
    """
    if not R:
        return True
    return _closed_under(R, _bitwise_majority, pairs=False)


def is_horn(R: Relation) -> bool:
    """R is Horn iff R is closed under coordinate-wise AND.

    Equivalently: R is the solution set of a Horn-CNF formula.
    """
    if not R:
        return True
    return _closed_under(R, _bitwise_and, pairs=True)


def is_dual_horn(R: Relation) -> bool:
    """R is dual-Horn iff R is closed under coordinate-wise OR."""
    if not R:
        return True
    return _closed_under(R, _bitwise_or, pairs=True)


def is_affine(R: Relation) -> bool:
    """R is affine iff R is closed under a XOR b XOR c (Mal'cev).

    Equivalently: R is a coset of a linear subspace of GF(2)^k.
    """
    if not R:
        return True
    return _closed_under(R, _bitwise_xor3, pairs=False)


def classify_schaefer(R: Relation) -> dict:
    """Return Schaefer-class booleans for the relation R."""
    if not R:
        k = 0
    else:
        k = len(next(iter(R)))
    zero = tuple([0] * k)
    one = tuple([1] * k)
    return {
        "k": k,
        "size": len(R),
        "is_0_valid": (k == 0) or (zero in R),
        "is_1_valid": (k == 0) or (one in R),
        "is_bijunctive": is_bijunctive(R),
        "is_horn": is_horn(R),
        "is_dual_horn": is_dual_horn(R),
        "is_affine": is_affine(R),
    }


def is_np_hard_type(R: Relation) -> bool:
    """Schaefer NP-hardness: relation is in none of the six tractable classes.

    A constraint language consisting of {R} alone yields an NP-hard
    SAT problem iff R is not preserved by any of the six Schaefer
    polymorphisms (constant 0, constant 1, majority, AND, OR, x XOR y XOR z).
    """
    cls = classify_schaefer(R)
    if cls["size"] == 0:
        # Empty relation is unsatisfiable; CSP is trivially in P.
        return False
    return not (
        cls["is_0_valid"]
        or cls["is_1_valid"]
        or cls["is_bijunctive"]
        or cls["is_horn"]
        or cls["is_dual_horn"]
        or cls["is_affine"]
    )


# ---------------------------------------------------------------------------
# Structural features (M5).

def structural_features(k: int, pi: Sequence[int]) -> dict:
    """Return minimal-fatal-support statistics for the pairing pi."""
    minimal = minimal_fatal_toggle_sets(k, pi)
    sizes = Counter(len(s) for s in minimal)
    return {
        "num_minimal_fatal": len(minimal),
        "minimal_fatal_size_histogram": dict(sorted(sizes.items())),
        "minimal_fatal_supports": [list(s) for s in minimal],
    }


# ---------------------------------------------------------------------------
# M2/M3 enumerator.

def enumerate_pairings(k: int, sample: int | None = None,
                       seed: int = 0) -> Iterable[tuple[int, ...]]:
    """Yield pairings in S_k.

    If `sample` is None, iterate exhaustively (k! pairings).
    Otherwise, take a deterministic pseudorandom sample of `sample`
    pairings (with replacement-free Fisher-Yates).
    """
    if sample is None:
        for perm in permutations(range(k)):
            yield perm
        return

    import random
    rng = random.Random(seed)
    seen: set[tuple[int, ...]] = set()
    while len(seen) < sample:
        # Random permutation via shuffle.
        a = list(range(k))
        rng.shuffle(a)
        t = tuple(a)
        if t not in seen:
            seen.add(t)
            yield t


def build_catalogue(k: int, sample: int | None = None,
                    verbose: bool = False,
                    progress_every: int = 200,
                    seed: int = 0,
                    verify_canonical: bool = True) -> dict:
    """Enumerate pairings, compute R(pi), and bucket by equivalence.

    Two-stage strategy:

      Stage 1 (fast).  For each pairing, compute R(pi) and the
        permutation-and-flip-invariant signature `_relation_invariant`.
        Bucket pairings by this invariant.  For typical inputs the
        invariant is exact (different invariants => inequivalent
        relations; same invariant => almost always equivalent).

      Stage 2 (slow, optional).  Within each invariant bucket,
        run `canonicalize_relation` on one representative per
        *distinct* raw relation (frozenset); if all representatives
        give the same canonical form, the bucket is collapsed; if not,
        the bucket is split.

    `verify_canonical=True` runs Stage 2.  For very large sweeps with
    expensive canonicalisation, set it to False (the invariant alone is
    usually enough to count distinct relations).
    """
    # Stage 1: bucket by invariant.
    invariant_buckets: dict[tuple, dict] = {}
    pairings_iter = list(enumerate_pairings(k, sample=sample, seed=seed))
    n_total = len(pairings_iter)
    start = time.time()

    for idx, pi in enumerate(pairings_iter):
        R = extract_relation(k, pi)
        inv = _relation_invariant(R)
        if inv not in invariant_buckets:
            cls = classify_schaefer(R)
            invariant_buckets[inv] = {
                "canonical_size": len(R),
                "schaefer": cls,
                "np_hard_type": is_np_hard_type(R),
                "count": 1,
                "witness_pairings": [list(pi)],
                "first_witness_R": sorted(R),
                "first_R": R,
                "all_R_samples": {R},
            }
        else:
            entry = invariant_buckets[inv]
            entry["count"] += 1
            if len(entry["witness_pairings"]) < 5:
                entry["witness_pairings"].append(list(pi))
            entry["all_R_samples"].add(R)
            # If a different concrete R appears under the same
            # invariant, also re-classify (the Schaefer class is the
            # same up to relabeling but distinct R's may give different
            # specific class labels).  We keep the class of the first
            # representative as canonical for reporting.

        if verbose and (idx + 1) % progress_every == 0:
            elapsed = time.time() - start
            eta = elapsed * (n_total - idx - 1) / max(idx + 1, 1)
            print(
                f"  k={k}: scanned {idx + 1}/{n_total}, "
                f"invariant-buckets={len(invariant_buckets)}, "
                f"elapsed={elapsed:.1f}s, eta={eta:.1f}s",
                file=sys.stderr,
                flush=True,
            )

    # Stage 2: canonicalisation pass.  For each invariant bucket,
    # canonicalise every distinct R-sample and group by canonical
    # form.  Split buckets accordingly.
    catalogue: dict[tuple, dict] = {}
    if verify_canonical:
        for inv, entry in invariant_buckets.items():
            samples = entry["all_R_samples"]
            canon_for_R: dict[Relation, tuple] = {}
            for R in samples:
                canon_for_R[R] = canonicalize_relation(R)
            # Collapse: distinct canonical forms inside this bucket.
            distinct_canons = set(canon_for_R.values())
            if len(distinct_canons) == 1:
                canon = next(iter(distinct_canons))
                catalogue[canon] = {
                    "canonical_size": entry["canonical_size"],
                    "schaefer": entry["schaefer"],
                    "np_hard_type": entry["np_hard_type"],
                    "count": entry["count"],
                    "witness_pairings": entry["witness_pairings"],
                    "first_witness_R": entry["first_witness_R"],
                    "invariant_bucket_collisions": 0,
                }
            else:
                # Bucket-split: rare; need to re-bin pairings by
                # canonical form.  But we lost the per-pairing R
                # mapping; we have only the set of distinct R's.  In
                # practice all pairings with same invariant produce
                # equivalent R; record the split as a warning.
                if verbose:
                    print(
                        f"  WARNING: invariant bucket split into "
                        f"{len(distinct_canons)} canonical classes "
                        f"at k={k}, inv={inv}",
                        file=sys.stderr,
                    )
                for canon in distinct_canons:
                    if canon in catalogue:
                        continue
                    repr_R = next(R for R, c in canon_for_R.items() if c == canon)
                    cls = classify_schaefer(repr_R)
                    catalogue[canon] = {
                        "canonical_size": len(repr_R),
                        "schaefer": cls,
                        "np_hard_type": is_np_hard_type(repr_R),
                        "count": -1,  # split; counts not exact
                        "witness_pairings": entry["witness_pairings"][:1],
                        "first_witness_R": sorted(repr_R),
                        "invariant_bucket_collisions": len(distinct_canons),
                    }
    else:
        for inv, entry in invariant_buckets.items():
            # Use invariant tuple itself as the canonical key.
            canon = ("inv", inv)
            catalogue[canon] = {
                "canonical_size": entry["canonical_size"],
                "schaefer": entry["schaefer"],
                "np_hard_type": entry["np_hard_type"],
                "count": entry["count"],
                "witness_pairings": entry["witness_pairings"],
                "first_witness_R": entry["first_witness_R"],
                "invariant_bucket_collisions": 0,
            }

    return {
        "k": k,
        "scanned": n_total,
        "distinct_canonical": len(catalogue),
        "invariant_buckets": len(invariant_buckets),
        "catalogue": catalogue,
        "elapsed_sec": time.time() - start,
    }


def catalogue_summary(cat: dict) -> dict:
    """Return a JSON-serialisable summary of a catalogue."""
    entries = []
    for canon, entry in cat["catalogue"].items():
        cls = entry["schaefer"]
        entries.append({
            "canonical_repr": [list(t) for t in canon],
            "canonical_size": entry["canonical_size"],
            "count": entry["count"],
            "is_0_valid": cls["is_0_valid"],
            "is_1_valid": cls["is_1_valid"],
            "is_bijunctive": cls["is_bijunctive"],
            "is_horn": cls["is_horn"],
            "is_dual_horn": cls["is_dual_horn"],
            "is_affine": cls["is_affine"],
            "np_hard_type": entry["np_hard_type"],
            "example_pairing": entry["witness_pairings"][0],
        })
    n_bij = sum(1 for e in entries if e["is_bijunctive"])
    n_horn = sum(1 for e in entries if e["is_horn"])
    n_dual = sum(1 for e in entries if e["is_dual_horn"])
    n_aff = sum(1 for e in entries if e["is_affine"])
    n_0v = sum(1 for e in entries if e["is_0_valid"])
    n_1v = sum(1 for e in entries if e["is_1_valid"])
    n_hard = sum(1 for e in entries if e["np_hard_type"])
    return {
        "k": cat["k"],
        "scanned": cat["scanned"],
        "distinct_canonical": cat["distinct_canonical"],
        "elapsed_sec": cat["elapsed_sec"],
        "schaefer_breakdown": {
            "0_valid": n_0v,
            "1_valid": n_1v,
            "bijunctive": n_bij,
            "horn": n_horn,
            "dual_horn": n_dual,
            "affine": n_aff,
            "np_hard_type": n_hard,
        },
        "entries": entries,
    }


# ---------------------------------------------------------------------------
# CLI.

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--k", type=int, required=True,
                        help="number of toggles (relation arity)")
    parser.add_argument("--sample", type=int, default=None,
                        help="sample size (omit for full S_k sweep)")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out", type=str, default=None,
                        help="path to write catalogue JSON")
    parser.add_argument("--summary-out", type=str, default=None,
                        help="path to write summary JSON")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    cat = build_catalogue(
        args.k,
        sample=args.sample,
        verbose=args.verbose,
        seed=args.seed,
    )
    summary = catalogue_summary(cat)
    print(json.dumps(summary["schaefer_breakdown"], indent=2))
    print(
        f"k={args.k} scanned={cat['scanned']} "
        f"distinct={cat['distinct_canonical']} "
        f"elapsed={cat['elapsed_sec']:.1f}s"
    )

    if args.out is not None:
        with open(args.out, "w") as f:
            json.dump(
                {
                    "k": cat["k"],
                    "scanned": cat["scanned"],
                    "distinct_canonical": cat["distinct_canonical"],
                    "elapsed_sec": cat["elapsed_sec"],
                    "catalogue": [
                        {
                            "canonical_repr": [list(t) for t in canon],
                            **entry,
                            "first_witness_R": [list(t) for t in entry["first_witness_R"]],
                        }
                        for canon, entry in cat["catalogue"].items()
                    ],
                },
                f,
                indent=2,
            )

    if args.summary_out is not None:
        with open(args.summary_out, "w") as f:
            json.dump(summary, f, indent=2)


if __name__ == "__main__":
    main()
