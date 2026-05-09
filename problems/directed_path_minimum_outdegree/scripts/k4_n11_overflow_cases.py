"""Run the n=11 miner with a higher cap on the overflow Shape A1 cases.

Shape A2 and Shape B cases close cleanly at n=11. Only the 12 Shape A1
cases overflow at the default 2M cap. This script runs each with a
larger cap and reports first-obstruction-found short-circuit.
"""

import sys
import time
from itertools import combinations
from k4_general_miner import (
    all_valid_st, derive_forced_arcs, has_directed_simple_path_of_length,
    DELTA,
)


def is_shape_a1(S):
    """Shape A1: S is a 4-cyclic-interval in V(C) = {1, ..., 7}."""
    S_set = set(S)
    for start in range(1, 8):
        interval = set()
        v = start
        for _ in range(4):
            interval.add(v)
            v = v + 1 if v < 7 else 1
        if interval == S_set:
            return True
    return False


def check_st_pair_with_short_circuit(S, T, n, max_completions=20000000, time_limit=600.0):
    """Like check_st_pair but stops on first obstruction."""
    PATH_V = frozenset(range(8))
    CYCLE_V = frozenset(range(1, 8))
    OUTSIDE_V = frozenset(range(8, n))
    ALL_V = frozenset(range(n))

    result = derive_forced_arcs(S, T, n)
    if result is None or (len(result) == 2 and isinstance(result[1], str)):
        return {'status': 'inconsistent', 'reason': result[1] if result is not None else 'unknown'}

    forced, forbidden = result

    free_choices = []
    for v in range(n):
        confirmed = {w for (u, w) in forced if u == v}
        excluded = {w for (u, w) in forbidden if u == v}
        need = DELTA - len(confirmed)
        if v in S:
            cand = (CYCLE_V - {v}) - excluded - confirmed
        else:
            cand = (ALL_V - {v}) - excluded - confirmed
        if need > 0:
            free_choices.append((v, need, sorted(cand)))

    free_choices.sort(key=lambda x: (len(x[2]) - x[1], x[0]))

    obstructions = []
    completions_count = [0]
    overflow = [False]
    timed_out = [False]
    short_circuit = [False]
    start_time = time.time()

    def recurse(idx, arcs):
        if overflow[0] or timed_out[0] or short_circuit[0]:
            return
        if completions_count[0] > max_completions:
            overflow[0] = True
            return
        if time.time() - start_time > time_limit:
            timed_out[0] = True
            return

        if idx == len(free_choices):
            count = [0] * n
            for (u, _) in arcs:
                count[u] += 1
            if any(c != DELTA for c in count):
                return
            completions_count[0] += 1
            if not has_directed_simple_path_of_length(arcs, n, target=8):
                obstructions.append(frozenset(arcs))
                short_circuit[0] = True  # stop on first obstruction
            return

        v, need, cand = free_choices[idx]
        valid_cand = [w for w in cand if (w, v) not in arcs]
        if len(valid_cand) < need:
            return
        for combo in combinations(valid_cand, need):
            for w in combo:
                arcs.add((v, w))
            recurse(idx + 1, arcs)
            for w in combo:
                arcs.discard((v, w))
            if short_circuit[0]:
                return

    initial = set(forced)
    recurse(0, initial)

    if short_circuit[0]:
        status = 'obstruction_found'
    elif overflow[0]:
        status = 'overflow'
    elif timed_out[0]:
        status = 'timed_out'
    else:
        status = 'closed'

    return {
        'status': status,
        'num_completions': completions_count[0],
        'num_obstructions': len(obstructions),
        'obstruction_sample': sorted(list(obstructions[0])) if obstructions else None,
        'forced_arc_count': len(forced),
        'free_choices_count': len(free_choices),
        'elapsed': time.time() - start_time,
    }


def main():
    n = 11
    max_completions = 20_000_000
    time_limit = 600.0

    if len(sys.argv) > 1:
        max_completions = int(sys.argv[1])
    if len(sys.argv) > 2:
        time_limit = float(sys.argv[2])

    pairs = all_valid_st()
    a1_pairs = [(S, T) for (S, T) in pairs if is_shape_a1(S)]

    print(f"=" * 70)
    print(f"n=11 Shape A1 cases (cap {max_completions:,}, time limit {time_limit}s):")
    print(f"=" * 70)
    print()

    closed = 0
    overflow = 0
    timed_out = 0
    obstruction_found = 0
    total_completions = 0

    for (S, T) in a1_pairs:
        result = check_st_pair_with_short_circuit(S, T, n, max_completions, time_limit)
        status = result.get('status')
        n_comp = result.get('num_completions', 0)
        elapsed = result.get('elapsed', 0)
        total_completions += n_comp

        if status == 'closed':
            closed += 1
        elif status == 'overflow':
            overflow += 1
        elif status == 'timed_out':
            timed_out += 1
        elif status == 'obstruction_found':
            obstruction_found += 1

        print(f"  S={sorted(S)} T={sorted(T)}: {status} (comp={n_comp:,}, {elapsed:.1f}s)")

        if status == 'obstruction_found':
            print(f"    Obstruction found: {result['obstruction_sample']}")
            sys.exit(1)

    print()
    print(f"Summary: {closed}/{len(a1_pairs)} closed.")
    print(f"  overflow: {overflow}")
    print(f"  timed_out: {timed_out}")
    print(f"  obstruction_found: {obstruction_found}")
    print(f"  total completions: {total_completions:,}")


if __name__ == '__main__':
    main()
