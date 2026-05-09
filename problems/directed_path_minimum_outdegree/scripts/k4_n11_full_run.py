"""Run the full n=11 miner with adequate cap for all configurations.

Outputs a summary table with per-(S, T) completion counts and obstruction
counts. This is the canonical closure run for n=11.

Reproduction: uv run python scripts/k4_n11_full_run.py
"""

import sys
import time
from itertools import combinations
from k4_general_miner import (
    all_valid_st, derive_forced_arcs, has_directed_simple_path_of_length,
    DELTA,
)
from k4_n11_overflow_cases import is_shape_a1, check_st_pair_with_short_circuit


def main():
    n = 11
    pairs = all_valid_st()

    print(f"=" * 70)
    print(f"Full n={n} miner run for delta=4 closure")
    print(f"=" * 70)
    print()
    print(f"Configurations: {len(pairs)}")
    print()

    closed = 0
    obstruction_found = 0
    overflow = 0
    timed_out = 0
    inconsistent = 0
    other = 0
    total_completions = 0
    total_elapsed = 0.0

    for (S, T) in pairs:
        # Larger cap for Shape A1, default for A2/B
        if is_shape_a1(S):
            max_comp = 50_000_000
            time_lim = 1200.0
        else:
            max_comp = 5_000_000
            time_lim = 300.0

        result = check_st_pair_with_short_circuit(S, T, n, max_comp, time_lim)
        status = result.get('status')
        n_comp = result.get('num_completions', 0)
        elapsed = result.get('elapsed', 0)
        total_completions += n_comp
        total_elapsed += elapsed

        if status == 'closed':
            closed += 1
        elif status == 'obstruction_found':
            obstruction_found += 1
        elif status == 'overflow':
            overflow += 1
        elif status == 'timed_out':
            timed_out += 1
        elif status == 'inconsistent':
            inconsistent += 1
        else:
            other += 1

        shape = 'A1' if is_shape_a1(S) else '?'
        print(f"  {shape}: S={sorted(S)} T={sorted(T)}: {status} (comp={n_comp:,}, {elapsed:.1f}s)")

        if status == 'obstruction_found':
            print(f"    Obstruction: {result.get('obstruction_sample')}")
            sys.exit(1)

    print()
    print(f"Summary at n={n}:")
    print(f"  closed: {closed}/{len(pairs)}")
    print(f"  obstruction_found: {obstruction_found}")
    print(f"  overflow: {overflow}")
    print(f"  timed_out: {timed_out}")
    print(f"  inconsistent: {inconsistent}")
    print(f"  other: {other}")
    print(f"  total completions: {total_completions:,}")
    print(f"  total elapsed: {total_elapsed:.1f}s")

    # Exit nonzero unless every config is genuinely 'closed'.
    if closed != len(pairs):
        sys.exit(1)


if __name__ == '__main__':
    main()
