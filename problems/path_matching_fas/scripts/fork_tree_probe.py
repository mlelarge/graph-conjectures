"""Probe one-tree interfaces with crossing toggle bridges.

Section 19's Y-shape data suggested that an acyclic future interface
might be enough for toggle confluence.  This script refutes that
candidate hypothesis.

The construction has one seed p, one future root r, and two future
branches A and B.  The future dependency interface is a single tree:

      p <- r <- A_0 <- A_1 <- ... <- A_{k-1}
             \
              <- B_0 <- B_1 <- ... <- B_{k-1}

Toggle gadget i connects A_i to B_{pairing[i]} when its local prefix
order is swapped.  If pairing[i] = i, all toggle prefixes are
extendable.  If pairing[i] = i+1 mod k, the interface is still one tree
but the toggle bridges cross the branch order, and the prefixes have
mixed extendability.

This says "acyclic interface graph" is too weak.  The right confluence
hypothesis must exclude crossing toggle bridges on a tree, not merely
cycles in the future-dependency interface itself.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from itertools import product
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ff_signature_probe import has_completion_ff, valid_prefix_state_ff  # noqa: E402
from sleeping_block_probe import sleeping_block_signature  # noqa: E402
from wake_signature_probe import survives_pruning  # noqa: E402


def shift_pairing(k: int, shift: int = 1) -> tuple[int, ...]:
    """Return pairing[i] = i + shift mod k."""
    if k <= 0:
        raise ValueError("k must be positive")
    return tuple((i + shift) % k for i in range(k))


def shift_one_forbidden_pairs(k: int) -> tuple[tuple[int, int], ...]:
    """Adjacent selected pairs that exactly characterize shift-1 failure.

    Empirically and structurally, for the cyclic shift pairing
    pi(i)=i+1 mod k, a toggle prefix is non-extendable iff it selects
    both bridges in one of

        (0,1), (2,3), ..., (2r-2,2r-1),

    where r=floor((k-1)/2).  The final possible adjacent pair is
    excluded because the branch-tail/window geometry leaves enough room
    to complete.
    """
    r = (k - 1) // 2
    return tuple((2 * m, 2 * m + 1) for m in range(r))


def shift_one_predicted_extendable(bits: Sequence[int]) -> bool:
    """Closed-form prediction for the shift-1 fork family."""
    return all(not (bits[i] and bits[j]) for i, j in shift_one_forbidden_pairs(len(bits)))


def shift_one_expected_counts(k: int) -> dict:
    """Expected counts under the forbidden-pair classification."""
    r = (k - 1) // 2
    extendable = (3 ** r) * (2 ** (k - 2 * r))
    return {
        "k": k,
        "forbidden_pairs": list(shift_one_forbidden_pairs(k)),
        "extendable": extendable,
        "non_extendable": (1 << k) - extendable,
    }


def fork_tree_tournament(k: int, pairing: Sequence[int]) -> list[list[bool]]:
    """Construct the fork-tree toggle tournament.

    Vertices in base order:
      a_i = 2i, b_i = 2i+1                   for 0 <= i < k
      p   = 2k                               placed seed
      r   = 2k+1                             future root
      A_i = 2k+2+i                           first branch
      B_i = 3k+2+i                           second branch

    Reversals:
      A_i -> a_i, B_pairing[i] -> b_i        toggle forcing
      r -> p                                 root seed
      A_0 -> r, A_i -> A_{i-1}               branch A
      B_0 -> r, B_i -> B_{i-1}               branch B
    """
    if k <= 0:
        raise ValueError("k must be positive")
    if sorted(pairing) != list(range(k)):
        raise ValueError("pairing must be a permutation of range(k)")

    n = 4 * k + 2
    p = 2 * k
    r = 2 * k + 1

    def A(i: int) -> int:
        return 2 * k + 2 + i

    def B(i: int) -> int:
        return 3 * k + 2 + i

    T = [[False] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            T[i][j] = True
            T[j][i] = False

    for i, bj in enumerate(pairing):
        a = 2 * i
        b = 2 * i + 1
        T[A(i)][a] = True
        T[a][A(i)] = False
        T[B(bj)][b] = True
        T[b][B(bj)] = False

    T[r][p] = True
    T[p][r] = False

    T[A(0)][r] = True
    T[r][A(0)] = False
    T[B(0)][r] = True
    T[r][B(0)] = False

    for i in range(1, k):
        T[A(i)][A(i - 1)] = True
        T[A(i - 1)][A(i)] = False
        T[B(i)][B(i - 1)] = True
        T[B(i - 1)][B(i)] = False

    return T


def fork_tree_prefix(k: int, bits: Sequence[int]) -> tuple[int, ...]:
    """Place every pair, then the seed p."""
    if len(bits) != k:
        raise ValueError("bits length must equal k")
    prefix: list[int] = []
    for i, bit in enumerate(bits):
        a = 2 * i
        b = 2 * i + 1
        if bit:
            prefix.extend((b, a))
        else:
            prefix.extend((a, b))
    prefix.append(2 * k)
    return tuple(prefix)


def count_fork_tree_signatures(k: int, pairing: Sequence[int]) -> dict:
    """Evaluate all 2^k toggle prefixes."""
    T = fork_tree_tournament(k, pairing)
    n = len(T)
    cut = 2 * k + 1
    extendable_count = 0
    nonextendable_count = 0
    invalid_count = 0
    sigs: dict = {}
    by_bits: list[dict] = []

    for bits in product((0, 1), repeat=k):
        prefix = fork_tree_prefix(k, bits)
        state = valid_prefix_state_ff(T, prefix)
        if state is None:
            invalid_count += 1
            by_bits.append({"bits": list(bits), "status": "invalid_prefix"})
            continue
        pm, deg, par, flex, win = state
        if not survives_pruning(state, cut, n):
            invalid_count += 1
            by_bits.append({"bits": list(bits), "status": "ff_pruned"})
            continue
        ext = has_completion_ff(T, cut, pm, deg, par, tuple(flex), tuple(win))
        sig = sleeping_block_signature(cut, pm, deg, par, flex, win)
        sigs.setdefault(sig, []).append(list(bits))
        by_bits.append({
            "bits": list(bits),
            "status": "ok",
            "extendable": ext,
        })
        if ext:
            extendable_count += 1
        else:
            nonextendable_count += 1

    return {
        "k": k,
        "n": n,
        "cut": cut,
        "pairing": list(pairing),
        "expected_prefixes": 1 << k,
        "extendable": extendable_count,
        "non_extendable": nonextendable_count,
        "invalid": invalid_count,
        "distinct_sleeping_signatures": len(sigs),
        "by_bits": by_bits,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-k", type=int, default=6)
    parser.add_argument("--shift", type=int, default=1)
    args = parser.parse_args()
    for k in range(1, args.max_k + 1):
        pairing = shift_pairing(k, args.shift)
        out = count_fork_tree_signatures(k, pairing)
        summary = {kk: vv for kk, vv in out.items() if kk != "by_bits"}
        print(f"k={k}: {json.dumps(summary)}")


if __name__ == "__main__":
    main()
