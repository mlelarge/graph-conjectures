"""Per-step loaded-edge analysis for sigma*(k) (D61).

For each step j of sigma*(k) on a V6''-negative cyclic-ladder core,
this script:

  1. Computes the forced + flexible backedges incident to sigma*(k)[j]
     that load at this step.
  2. Identifies the "old-neighbor pair" (u, v) for two-edge steps.
  3. Computes the current loaded-graph components and checks
     separation: u and v should lie in distinct components.

The output empirically characterizes the Two-Neighbor Separation
Lemma (Lemma 61.S):

  At every two-edge step of sigma*(k) on a V6''-negative cyclic-
  ladder core C without a smaller V6''-positive sub-core, the two
  old neighbors u, v lie in distinct components of the current
  loaded graph.

The empirical scan runs over every V6''-negative core at k = 4, 5, 6
and reports any violation (cycle closure that contradicts
separation).  The decider proof of C53.5 reduces to a structural
proof of this lemma.

Used by Section 61 of `docs/exchange_proof_draft.md`.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from itertools import combinations, permutations
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fork_tree_probe import fork_tree_prefix, fork_tree_tournament  # noqa: E402
from ff_signature_probe import (  # noqa: E402
    _add_flexible_vertex,
    _canonical_parent,
    valid_prefix_state_ff,
)
from lfo_forced_flexible import _find, _iter_bits, _union  # noqa: E402
from rectangle_detachability_probe import even_adjacent_blocks  # noqa: E402
from sigma_star_formula import int_to_label, sigma_star_closed  # noqa: E402
from v6pp_completion_constructor import (  # noqa: E402
    has_no_v6pp_trigger,
    is_cyclic_ladder_core,
)


# ----------------------------------------------------------------------
# 1. Per-step trace with explicit edge accounting
# ----------------------------------------------------------------------

def per_step_analysis(k: int, pi: Sequence[int], C: Sequence[int]) -> dict:
    """Run sigma*(k) step by step, recording for each step:

       - vertex placed
       - LFO position
       - flex partners that load (= flex_outmask[x] & prefix_mask before step)
       - old-neighbor count
       - separation check (component identity of pairs of partners)
    """
    bits = tuple(1 if i in set(C) else 0 for i in range(k))
    prefix = fork_tree_prefix(k, bits)
    T = fork_tree_tournament(k, pi)
    state = valid_prefix_state_ff(T, prefix)
    if state is None:
        return {"valid_prefix": False}
    prefix_mask, degree, parent, flex_outmask, windows = state
    sigma = sigma_star_closed(k)
    n = len(T)

    rows = []
    pos = len(prefix)
    failed = False
    for j, x in enumerate(sigma):
        partners = [u for u in _iter_bits(flex_outmask[x] & prefix_mask)]
        old_labels = []
        components_of_partners = []
        for u in partners:
            old_labels.append(_label(k, u))
            components_of_partners.append(_find(list(parent), u))
        all_distinct = len(set(components_of_partners)) == len(components_of_partners)
        win = windows[x]
        nxt = _add_flexible_vertex(flex_outmask, prefix_mask, degree, parent, x)
        if nxt is None:
            rows.append({
                'j': j, 'pos': pos, 'vertex_label': _label(k, x),
                'partners': old_labels, 'window': list(win),
                'in_window': win[0] <= pos <= win[1],
                'separation_ok': all_distinct,
                'failed': True,
            })
            failed = True
            break
        new_degree, new_parent = nxt
        rows.append({
            'j': j, 'pos': pos, 'vertex_label': _label(k, x),
            'partners': old_labels,
            'n_partners': len(partners),
            'window': list(win),
            'in_window': win[0] <= pos <= win[1],
            'separation_ok': all_distinct,
            'deg_after': new_degree[x],
            'failed': False,
        })
        degree, parent = new_degree, _canonical_parent(new_parent)
        prefix_mask |= 1 << x
        pos += 1
    return {
        'k': k, 'pi': list(pi), 'C': list(C),
        'rows': rows,
        'all_separated_or_isolated': not failed and all(r['separation_ok'] for r in rows),
        'failed': failed,
    }


def _label(k: int, v: int) -> str:
    """Human-readable label for a fork-tree vertex."""
    if v == 2 * k + 1:
        return 'r'
    if v == 2 * k:
        return 'p'
    if 2 * k + 2 <= v <= 3 * k + 1:
        return f'A_{v - (2 * k + 2)}'
    if 3 * k + 2 <= v <= 4 * k + 1:
        return f'B_{v - (3 * k + 2)}'
    if v % 2 == 0:
        return f'a_{v // 2}'
    return f'b_{v // 2}'


# ----------------------------------------------------------------------
# 2. Scan: which steps have 2 partners, and is separation maintained?
# ----------------------------------------------------------------------

def scan_two_edge_steps_at_k(k: int) -> dict:
    """Across all V6''-negative cyclic-ladder cores at k, scan every
    two-edge step and check separation."""
    blocks = even_adjacent_blocks(k)
    total = 0
    fails = []
    step_summaries: dict[int, dict] = defaultdict(lambda: defaultdict(int))
    for pi in permutations(range(k)):
        for size in range(1, len(blocks) + 1):
            for block_subset in combinations(blocks, size):
                C = tuple(sorted(i for blk in block_subset for i in blk))
                if not is_cyclic_ladder_core(k, pi, C):
                    continue
                if not has_no_v6pp_trigger(k, pi, C):
                    continue
                total += 1
                analysis = per_step_analysis(k, pi, C)
                if analysis['failed']:
                    if len(fails) < 5:
                        fails.append(analysis)
                    continue
                for row in analysis['rows']:
                    np_ = row.get('n_partners', 0)
                    step_summaries[row['j']]['vertex'] = row['vertex_label']
                    step_summaries[row['j']][f'n_partners={np_}'] += 1
    return {
        'k': k,
        'total_v6pp_negative_cores': total,
        'failures': len(fails),
        'first_failures': fails[:3],
        'step_summaries': {
            j: dict(d) for j, d in sorted(step_summaries.items())
        },
    }


# ----------------------------------------------------------------------
# 3. Loaded-graph component dump at each step (for one core)
# ----------------------------------------------------------------------

def component_trace(k: int, pi: Sequence[int], C: Sequence[int]) -> dict:
    """For a single (k, pi, C), trace the loaded-graph components
    visited by sigma*(k) step by step."""
    bits = tuple(1 if i in set(C) else 0 for i in range(k))
    prefix = fork_tree_prefix(k, bits)
    T = fork_tree_tournament(k, pi)
    state = valid_prefix_state_ff(T, prefix)
    if state is None:
        return {"valid_prefix": False}
    prefix_mask, degree, parent, flex_outmask, windows = state
    sigma = sigma_star_closed(k)
    n = len(T)

    trace = []
    par = list(parent)
    deg = list(degree)
    pm = prefix_mask
    pos = len(prefix)
    for j, x in enumerate(sigma):
        partners = [u for u in _iter_bits(flex_outmask[x] & pm)]
        comps = sorted({_find(list(par), u) for u in partners})
        partner_info = [{
            'label': _label(k, u),
            'component_root': _label(k, _find(list(par), u)),
            'degree_before': deg[u],
        } for u in partners]
        trace.append({
            'j': j, 'pos': pos,
            'vertex': _label(k, x),
            'partners': partner_info,
            'distinct_components': len(comps),
            'all_partner_components_distinct': len(comps) == len(partners),
        })
        nxt = _add_flexible_vertex(flex_outmask, pm, deg, par, x)
        if nxt is None:
            trace.append({'j': j, 'failed': True})
            break
        deg, par = nxt
        par = list(_canonical_parent(par))
        pm |= 1 << x
        pos += 1
    return {'k': k, 'pi': list(pi), 'C': list(C), 'trace': trace}


# ----------------------------------------------------------------------
# 4. CLI
# ----------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--k",
        type=int,
        required=True,
        help="Number of (a_i, b_i) pair levels.",
    )
    parser.add_argument(
        "--scan",
        action="store_true",
        help="Scan all V6''-negative cores at this k for separation failures.",
    )
    parser.add_argument(
        "--trace",
        type=str,
        default=None,
        help='Trace a single core as JSON: \'{"pi":[0,1,2,3,4],"C":[0,1]}\'',
    )
    args = parser.parse_args()
    if args.scan:
        print(json.dumps(scan_two_edge_steps_at_k(args.k), indent=2, default=list))
    if args.trace:
        spec = json.loads(args.trace)
        out = component_trace(args.k, spec["pi"], spec["C"])
        print(json.dumps(out, indent=2, default=list))


if __name__ == "__main__":
    main()
