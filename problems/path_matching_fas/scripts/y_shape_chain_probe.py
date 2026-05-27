"""Probe a true Y-shape future interface for the confluence lemma.

The working confluence lemma (Section 18.4) hypothesizes that the
interface graph is a "disjoint union of directed paths."

- Section 16 toggle: zero interface  -> all extend.
- Section 17.6 chain-seeded: one path -> all extend.
- Section 18 branching: two disjoint paths each connecting to many
  toggled gadgets -> mixed.

This script tests an intermediate Y-shape: chain-seeded family plus one
side-branch leaf z in F_c (future-opening) with a real reversed arc
z -> y_m. The interface graph is a single tree with a degree-3 junction
at y_m. If toggle prefixes are still all extendable, the lemma's
hypothesis can be loosened to "tree" or "connected with bounded
degree." If mixed, the hypothesis is tight to disjoint paths.

Construction (vertices in base order, all reversals are flips):
  a_i = 2i, b_i = 2i+1 for 0 <= i < k     (placed pairs)
  p   = 2k                                (placed main seed)
  y_j = 2k+1+j for 0 <= j < 2k            (future chain)
  z   = 4k+1                              (future side leaf)

Reversals:
  f_i -> a_i, g_i -> b_i for f_i=y_{2i}, g_i=y_{2i+1};
  y_0 -> p   (main chain seed);
  y_j -> y_{j-1} for j >= 1 (chain links);
  z -> y_attach (side-branch leaf attaches to chain at y_attach).

Since z > y_attach in base order, the reversal z -> y_attach is a
genuine arc flip. The corresponding backedge loads when z is placed in
the suffix.

Usage:
  uv run python scripts/y_shape_chain_probe.py --max-k 5 --attach 3
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


def y_shape_toggle_tournament(k: int, attach: int) -> list[list[bool]]:
    """Chain-seeded toggle + one future side leaf z reversed into y_attach.

    Base order:
      a_0, b_0, ..., a_{k-1}, b_{k-1}, p, y_0, ..., y_{2k-1}, z.

    Reversals:
      f_i -> a_i, g_i -> b_i (toggle-forcing);
      y_0 -> p, y_j -> y_{j-1} (main chain);
      z -> y_attach (side branch).
    """
    if k <= 0:
        raise ValueError("k must be positive")
    if not (0 <= attach < 2 * k):
        raise ValueError(f"attach must be in [0, {2*k})")
    n = 4 * k + 2
    p = 2 * k
    y_base = 2 * k + 1
    z = 4 * k + 1
    T = [[False] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            T[i][j] = True
            T[j][i] = False

    # toggle-forcing
    for i in range(k):
        a = 2 * i
        b = 2 * i + 1
        f = y_base + 2 * i
        g = f + 1
        # reverse a -> f to f -> a
        T[f][a] = True
        T[a][f] = False
        T[g][b] = True
        T[b][g] = False

    # main chain seed: y_0 -> p (reversal of p -> y_0)
    y0 = y_base
    T[y0][p] = True
    T[p][y0] = False

    # main chain links: y_j -> y_{j-1} (reversal of y_{j-1} -> y_j)
    for j in range(1, 2 * k):
        y = y_base + j
        prev = y - 1
        T[y][prev] = True
        T[prev][y] = False

    # side branch: z -> y_attach (z > y_attach so this IS a reversal)
    y_attach = y_base + attach
    T[z][y_attach] = True
    T[y_attach][z] = False
    return T


def y_shape_prefix(k: int, bits: Sequence[int]) -> tuple[int, ...]:
    """Toggle prefix + main seed p (z stays unplaced)."""
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
    prefix.append(2 * k)        # p
    return tuple(prefix)


def count_y_shape_signatures(k: int, attach: int) -> dict:
    T = y_shape_toggle_tournament(k, attach)
    n = len(T)
    cut = 2 * k + 1
    extendable_count = 0
    nonextendable_count = 0
    invalid_count = 0
    sigs: dict = {}
    by_bits: list[dict] = []
    for bits in product((0, 1), repeat=k):
        prefix = y_shape_prefix(k, bits)
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
        "attach": attach,
        "expected_prefixes": 1 << k,
        "extendable": extendable_count,
        "non_extendable": nonextendable_count,
        "invalid": invalid_count,
        "distinct_sleeping_signatures": len(sigs),
        "by_bits": by_bits,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-k", type=int, default=5)
    parser.add_argument("--attach", type=int, default=None,
                        help="side-branch attach point in [0, 2k). "
                             "Default sweeps several values.")
    args = parser.parse_args()
    for k in range(1, args.max_k + 1):
        if args.attach is None:
            attaches = sorted({0, 1, max(1, k - 1), 2 * k - 1, k})
        else:
            attaches = [args.attach]
        for attach in attaches:
            if attach >= 2 * k:
                continue
            out = count_y_shape_signatures(k, attach)
            summary = {kk: vv for kk, vv in out.items() if kk != "by_bits"}
            print(f"k={k} attach={attach}: {json.dumps(summary)}")


if __name__ == "__main__":
    main()
