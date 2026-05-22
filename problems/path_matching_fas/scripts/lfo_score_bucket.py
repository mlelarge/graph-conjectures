"""Exact LFO enumeration inside selected score-sequence buckets.

The full non-isomorphic n=7 sweep is slow because naive canonicalization
tries every relabeling for every labeled tournament. For a fixed score
sequence, isomorphisms preserve out-degrees, so we only need to permute
vertices inside equal-score classes. This makes the empirically relevant
n=7 buckets feasible.
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import sys
import time
from collections import defaultdict
from typing import Iterable

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verify import verify  # noqa: E402


DEFAULT_TARGETS = [
    (3, 3, 3, 3, 3, 3, 3),
    (2, 3, 3, 3, 3, 3, 4),
    (2, 2, 3, 3, 3, 4, 4),
]


PERMS_BY_N: dict[int, list[tuple[int, ...]]] = {}


def order_perms(n: int) -> list[tuple[int, ...]]:
    if n not in PERMS_BY_N:
        PERMS_BY_N[n] = list(itertools.permutations(range(n)))
    return PERMS_BY_N[n]


def parse_scores(raw: str | None) -> list[tuple[int, ...]]:
    if not raw:
        return DEFAULT_TARGETS
    out = []
    for chunk in raw.split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        out.append(tuple(sorted(int(x) for x in chunk.split(","))))
    return out


def score_sequence(T: list[list[int]]) -> tuple[int, ...]:
    return tuple(sorted(sum(row) for row in T))


def score_vector(T: list[list[int]]) -> list[int]:
    return [sum(row) for row in T]


def all_tournaments_with_scores(n: int) -> Iterable[tuple[list[list[int]], tuple[int, ...]]]:
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    for bits in itertools.product((0, 1), repeat=len(pairs)):
        T = [[0] * n for _ in range(n)]
        scores = [0] * n
        for (i, j), b in zip(pairs, bits):
            if b == 1:
                T[i][j] = 1
                scores[i] += 1
            else:
                T[j][i] = 1
                scores[j] += 1
        yield T, tuple(sorted(scores))


def score_respecting_permutations(scores: list[int]) -> Iterable[tuple[int, ...]]:
    groups: dict[int, list[int]] = defaultdict(list)
    for v, s in enumerate(scores):
        groups[s].append(v)

    blocks = [
        list(itertools.permutations(groups[s]))
        for s in sorted(groups)
    ]
    for choice in itertools.product(*blocks):
        yield tuple(v for block in choice for v in block)


def canonical_key_with_scores(T: list[list[int]]) -> tuple[int, ...]:
    """Canonical key using only relabelings that preserve score classes."""
    n = len(T)
    best = None
    scores = score_vector(T)
    for P in score_respecting_permutations(scores):
        key = tuple(T[P[i]][P[j]] for i in range(n) for j in range(n))
        if best is None or key < best:
            best = key
    assert best is not None
    return best


def analyze_lfo(T: list[list[int]]) -> dict:
    n = len(T)
    min_fas = None
    has_lfo = False
    has_degree2 = False
    has_forest = False
    has_matching = False
    has_exact_path = False
    lfo_order = None
    degree2_order = None
    forest_order = None

    for P in order_perms(n):
        info = verify(T, list(P))
        if min_fas is None or info["count"] < min_fas:
            min_fas = info["count"]
        if info["max_degree"] <= 2:
            has_degree2 = True
            if degree2_order is None:
                degree2_order = list(P)
        if info["is_forest"]:
            has_forest = True
            if forest_order is None:
                forest_order = list(P)
        if info["is_linear_forest"]:
            has_lfo = True
            if lfo_order is None:
                lfo_order = list(P)
        has_matching = has_matching or info["is_matching"]
        has_exact_path = has_exact_path or info["is_path"]

    return {
        "min_fas": min_fas,
        "has_lfo": has_lfo,
        "has_degree2_relaxation": has_degree2,
        "has_forest_ordering": has_forest,
        "has_matching_fas": has_matching,
        "has_exact_path_backarcs": has_exact_path,
        "lfo_order": lfo_order,
        "degree2_order": degree2_order,
        "forest_order": forest_order,
        "no_kind": (
            None if has_lfo else
            "size" if min_fas is not None and min_fas > n - 1 else
            "combinatorial"
        ),
    }


def summarize_bucket(records: list[dict]) -> dict:
    return {
        "non_iso_total": len(records),
        "lfo_yes": sum(1 for r in records if r["has_lfo"]),
        "lfo_no": sum(1 for r in records if not r["has_lfo"]),
        "size_no": sum(1 for r in records if r["no_kind"] == "size"),
        "combinatorial_no": sum(1 for r in records if r["no_kind"] == "combinatorial"),
        "degree2_relaxation_yes": sum(1 for r in records if r["has_degree2_relaxation"]),
        "forest_ordering_yes": sum(1 for r in records if r["has_forest_ordering"]),
        "matching_fas_yes": sum(1 for r in records if r["has_matching_fas"]),
        "exact_path_backarcs_yes": sum(1 for r in records if r["has_exact_path_backarcs"]),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=7)
    p.add_argument("--all-scores", action="store_true",
                   help="Enumerate every score sequence instead of the default target buckets.")
    p.add_argument("--scores", default=None,
                   help="Semicolon-separated score sequences, e.g. '3,3,3,3,3,3,3;2,3,3,3,3,3,4'.")
    p.add_argument("--out", default=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "data",
        "lfo_score_buckets_n7.json"))
    p.add_argument("--progress", type=int, default=250000)
    args = p.parse_args()

    targets = None if args.all_scores else set(parse_scores(args.scores))
    t0 = time.time()
    buckets: dict[tuple[int, ...], dict[tuple[int, ...], list[list[int]]]] = (
        defaultdict(dict) if targets is None else {target: {} for target in targets}
    )
    labeled_counts: dict[tuple[int, ...], int] = (
        defaultdict(int) if targets is None else {target: 0 for target in targets}
    )

    for idx, (T, seq) in enumerate(all_tournaments_with_scores(args.n), start=1):
        if targets is not None and seq not in targets:
            continue
        labeled_counts[seq] += 1
        key = canonical_key_with_scores(T)
        buckets[seq].setdefault(key, T)
        if args.progress and idx % args.progress == 0:
            print(f"processed {idx} labeled tournaments; "
                  f"bucket sizes = { {str(k): len(v) for k, v in buckets.items()} }",
                  flush=True)

    results = []
    result_sequences = sorted(buckets if targets is None else targets)
    for seq in result_sequences:
        records = []
        for iso_idx, T in enumerate(buckets[seq].values()):
            record = {
                "iso_index": iso_idx,
                "score_sequence": list(seq),
                "T": T,
                **analyze_lfo(T),
            }
            records.append(record)
        summary = {
            "score_sequence": list(seq),
            "labeled_total": labeled_counts[seq],
            **summarize_bucket(records),
        }
        results.append({
            "summary": summary,
            "records": records,
        })
        print(summary, flush=True)

    out = {
        "n": args.n,
        "all_scores": args.all_scores,
        "targets": [list(t) for t in result_sequences],
        "seconds": round(time.time() - t0, 2),
        "buckets": results,
    }
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(out, f, indent=2)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
