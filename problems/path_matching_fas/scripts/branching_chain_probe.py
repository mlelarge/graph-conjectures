"""Test the necessity of the single-chain hypothesis in the confluence lemma.

The user's chain-seeded refutation shows that any quotient based on
"future query reachability" still preserves all 2^k toggle bits. The
proposed next target is a confluence lemma:

  If a sleeping-block component difference is confined to a degree-2
  path segment whose future dependency interface is a SINGLE directed
  chain, then internal toggle choices are extension-equivalent.

The single-chain hypothesis is critical. This script probes what
happens if the future interface is BRANCHED:

  - Two independent chains, with f_i in chain A and g_i in chain B.
  - Toggle bit ϵ_i = 1 loads a_i-b_i flex backedge, merging f_i's
    component with g_i's component, hence merging chain A with chain B
    at gadget i.
  - If multiple ϵ_i = 1, the two chains get merged at multiple places —
    creating cycles in the back-arc graph.

If the construction produces a mix of extendable / non-extendable
toggle prefixes, sleeping-block correctly distinguishes them. This
justifies the single-chain hypothesis of the confluence lemma.

Usage:
  uv run python scripts/branching_chain_probe.py --max-k 5
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


def branching_toggle_tournament(k: int) -> list[list[bool]]:
    """Construct a two-chain branching toggle tournament.

    Vertices: a_i, b_i (placed pairs), p_A, p_B (two seeds), f_i, g_i
    (chain A and chain B leaves). Linear order:

      a_0, b_0, ..., a_{k-1}, b_{k-1}, p_A, p_B, f_0, f_1, ..., f_{k-1},
      g_0, g_1, ..., g_{k-1}

    Indices:
      a_i = 2i
      b_i = 2i + 1
      p_A = 2k
      p_B = 2k + 1
      f_i = 2k + 2 + i
      g_i = 2k + 2 + k + i = 3k + 2 + i

    Reversed arcs (these become backedges in the LFO):
      f_i -> a_i, g_i -> b_i (forced for k large enough);
      f_0 -> p_A, g_0 -> p_B (chain seeds, flex);
      f_j -> f_{j-1}, g_j -> g_{j-1} for j >= 1 (chain links, flex).

    At the cut after placing the pairs + p_A + p_B, the future has
    two separate chains. Toggle bit ϵ_i = 1 connects f_i (in chain A)
    with g_i (in chain B) via gadget i.
    """
    if k <= 0:
        raise ValueError("k must be positive")
    n = 4 * k + 2
    p_A = 2 * k
    p_B = 2 * k + 1
    # Base transitive
    T = [[False] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            T[i][j] = True
            T[j][i] = False

    def f(i):
        return 2 * k + 2 + i

    def g(i):
        return 3 * k + 2 + i

    # Toggle-forcing reversals
    for i in range(k):
        T[f(i)][2 * i] = True
        T[2 * i][f(i)] = False
        T[g(i)][2 * i + 1] = True
        T[2 * i + 1][g(i)] = False

    # Chain A seed: f_0 -> p_A
    T[f(0)][p_A] = True
    T[p_A][f(0)] = False
    # Chain A links: f_j -> f_{j-1}
    for j in range(1, k):
        T[f(j)][f(j - 1)] = True
        T[f(j - 1)][f(j)] = False

    # Chain B seed: g_0 -> p_B
    T[g(0)][p_B] = True
    T[p_B][g(0)] = False
    # Chain B links: g_j -> g_{j-1}
    for j in range(1, k):
        T[g(j)][g(j - 1)] = True
        T[g(j - 1)][g(j)] = False

    return T


def branching_toggle_prefix(k: int, bits: Sequence[int]) -> tuple[int, ...]:
    """Toggle prefix placing both seeds after the pairs."""
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
    prefix.extend((2 * k, 2 * k + 1))  # p_A, p_B
    return tuple(prefix)


def count_branching_signatures(k: int) -> dict:
    T = branching_toggle_tournament(k)
    n = len(T)
    cut = 2 * k + 2
    extendable_count = 0
    nonextendable_count = 0
    invalid_count = 0
    sigs: dict = {}
    by_bits: list[dict] = []
    for bits in product((0, 1), repeat=k):
        prefix = branching_toggle_prefix(k, bits)
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
    args = parser.parse_args()
    for k in range(1, args.max_k + 1):
        out = count_branching_signatures(k)
        summary = {kk: vv for kk, vv in out.items() if kk != "by_bits"}
        print(f"k={k}: {json.dumps(summary)}")


if __name__ == "__main__":
    main()
