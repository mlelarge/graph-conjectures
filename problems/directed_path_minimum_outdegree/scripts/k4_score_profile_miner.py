"""Local proof miner for delta=4 at arbitrary n, parameterised by an
arbitrary internal score profile (not just the (2,2,1,1) case).

A score profile is a dict s -> target_S(s) for s in S, specifying the
forced internal out-degree of each S-vertex. Valid score profiles for
|S|=4 with delta+(S) >= 1 (oriented):

  (1,1,1,1): every vertex has d^+_S = 1.
  (2,1,1,1): one vertex has d^+_S = 2, three have d^+_S = 1.
  (2,2,1,1): two have d^+_S = 2, two have d^+_S = 1.
  (3,1,1,1): one has d^+_S = 3, three have d^+_S = 1.

For each score profile, the valid (S, T) configurations are defined by
sigma(T) subset S where T = {s in S : target_S(s) = 1}.

This script extends the previous (2,2,1,1)-only miner to all four
profiles.

Usage:
  python k4_score_profile_miner.py [n]

Default n=11.
"""

import sys
import time
from itertools import combinations
from pathlib import Path
from typing import Dict, List


DELTA = 4
PROBLEM_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROBLEM_ROOT / 'data'


def succ_C(v):
    if v == 7:
        return 1
    if 1 <= v <= 6:
        return v + 1
    raise ValueError(v)


def pred_C(v):
    if v == 1:
        return 7
    if 2 <= v <= 7:
        return v - 1
    raise ValueError(v)


def all_valid_st_for_profile(profile_name):
    """Enumerate all valid (S, target_S) configurations for the given profile.

    profile_name in {'(1,1,1,1)', '(2,1,1,1)', '(2,2,1,1)', '(3,1,1,1)'}.
    """
    out = []
    for S_tuple in combinations(range(1, 8), 4):
        if 7 not in S_tuple:
            continue
        S = frozenset(S_tuple)

        if profile_name == '(1,1,1,1)':
            target_S = {s: 1 for s in S}
            T = S  # all vertices have d^+_S = 1
            sigma_T = frozenset(pred_C(t) for t in T)
            if sigma_T.issubset(S):
                out.append((S, target_S))

        elif profile_name == '(2,1,1,1)':
            # One vertex U with d^+_S = 2, three with d^+_S = 1.
            for u in S:
                target_S = {s: 1 for s in S}
                target_S[u] = 2
                T = frozenset(s for s in S if target_S[s] == 1)
                sigma_T = frozenset(pred_C(t) for t in T)
                if sigma_T.issubset(S):
                    out.append((S, target_S))

        elif profile_name == '(2,2,1,1)':
            for u_pair in combinations(S, 2):
                target_S = {s: 1 for s in S}
                for u in u_pair:
                    target_S[u] = 2
                T = frozenset(s for s in S if target_S[s] == 1)
                sigma_T = frozenset(pred_C(t) for t in T)
                if sigma_T.issubset(S):
                    out.append((S, target_S))

        elif profile_name == '(3,1,1,1)':
            for u in S:
                target_S = {s: 1 for s in S}
                target_S[u] = 3
                T = frozenset(s for s in S if target_S[s] == 1)
                sigma_T = frozenset(pred_C(t) for t in T)
                if sigma_T.issubset(S):
                    out.append((S, target_S))

        else:
            raise ValueError(f"unknown profile: {profile_name}")

    return out


def derive_forced_arcs_with_profile(S, target_S_map, n):
    """Derive forced/forbidden arcs with arbitrary score profile.

    target_S_map: dict s -> target d^+_S value for s in S.
    """
    PATH_V = frozenset(range(8))
    CYCLE_V = frozenset(range(1, 8))
    OUTSIDE_V = frozenset(range(8, n))
    ALL_V = frozenset(range(n))
    Vminus_S = CYCLE_V - S

    if 7 not in S or len(S) != 4:
        return None, "invalid S"
    if set(target_S_map.keys()) != set(S):
        return None, "target_S_map keys != S"

    T = frozenset(s for s in S if target_S_map[s] == 1)

    forced = set()
    forbidden = set()

    for v in range(n):
        forbidden.add((v, v))

    # Path arcs
    for i in range(7):
        forced.add((i, i + 1))

    # Cycle arc
    forced.add((7, 1))

    # T-arcs (vertices with d^+_S = 1)
    for t in T:
        for w in Vminus_S:
            forced.add((t, w))

    # F3
    B = frozenset(succ_C(s) for s in S)
    for w in B:
        forced.add((0, w))

    # Claim 12
    for s in S:
        for w in OUTSIDE_V:
            forbidden.add((s, w))

    # Lemma A reverse
    for ext in OUTSIDE_V:
        forbidden.add((ext, 0))

    # Antiparallel from forced
    for (u, v) in list(forced):
        forbidden.add((v, u))

    if forced & forbidden:
        return None, "forced ∩ forbidden non-empty"

    iteration_count = 0
    changed = True
    while changed:
        changed = False
        iteration_count += 1
        if iteration_count > 200:
            return None, "iteration count exceeded"

        for v in range(n):
            confirmed_out = {w for (u, w) in forced if u == v}
            forbidden_out = {w for (u, w) in forbidden if u == v}
            need = DELTA - len(confirmed_out)
            if need < 0:
                return None, f"vertex {v} too many forced"

            if v in S:
                target_S = target_S_map[v]
                target_VCS = DELTA - target_S

                S_conf = confirmed_out & S
                S_cand_in_S = ((CYCLE_V - {v}) - forbidden_out) & S
                S_unconf = S_cand_in_S - S_conf
                more_S = target_S - len(S_conf)

                if more_S < 0:
                    return None, f"v={v} too many S-arcs"
                if more_S > len(S_unconf):
                    return None, f"v={v} cannot meet target_S={target_S}"
                if more_S == 0 and S_unconf:
                    for w in S_unconf:
                        if (v, w) not in forbidden:
                            forbidden.add((v, w))
                            changed = True
                if more_S == len(S_unconf) and more_S > 0:
                    for w in list(S_unconf):
                        if (v, w) not in forced:
                            forced.add((v, w))
                            forbidden.add((w, v))
                            changed = True

                VCS_conf = confirmed_out & Vminus_S
                VCS_cand_in_VCS = ((CYCLE_V - {v}) - forbidden_out) & Vminus_S
                VCS_unconf = VCS_cand_in_VCS - VCS_conf
                more_VCS = target_VCS - len(VCS_conf)

                if more_VCS < 0:
                    return None, f"v={v} too many VCS-arcs"
                if more_VCS > len(VCS_unconf):
                    return None, f"v={v} cannot meet target_VCS={target_VCS}"
                if more_VCS == 0 and VCS_unconf:
                    for w in VCS_unconf:
                        if (v, w) not in forbidden:
                            forbidden.add((v, w))
                            changed = True
                if more_VCS == len(VCS_unconf) and more_VCS > 0:
                    for w in list(VCS_unconf):
                        if (v, w) not in forced:
                            forced.add((v, w))
                            forbidden.add((w, v))
                            changed = True
            else:
                cand = (ALL_V - {v}) - forbidden_out
                unconf = cand - confirmed_out
                if need > len(unconf):
                    return None, f"v={v} cannot meet d^+ = {DELTA}"
                if need == 0 and unconf:
                    for w in unconf:
                        if (v, w) not in forbidden:
                            forbidden.add((v, w))
                            changed = True
                if need == len(unconf) and need > 0:
                    for w in list(unconf):
                        if (v, w) not in forced:
                            forced.add((v, w))
                            forbidden.add((w, v))
                            changed = True

    return forced, forbidden


def has_directed_simple_path_of_length(arcs, n, target=8):
    adj = {v: set() for v in range(n)}
    for (u, w) in arcs:
        adj[u].add(w)
    found = [False]

    def dfs(v, visited, length):
        if found[0]:
            return
        if length >= target:
            found[0] = True
            return
        for w in adj[v]:
            if w not in visited:
                visited.add(w)
                dfs(w, visited, length + 1)
                if found[0]:
                    return
                visited.discard(w)

    for start in range(n):
        if found[0]:
            break
        dfs(start, {start}, 0)

    return found[0]


def check_pair(S, target_S_map, n, max_completions, time_limit, progress_every=None):
    PATH_V = frozenset(range(8))
    CYCLE_V = frozenset(range(1, 8))
    OUTSIDE_V = frozenset(range(8, n))
    ALL_V = frozenset(range(n))

    result = derive_forced_arcs_with_profile(S, target_S_map, n)
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
    last_progress = [start_time]

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
                short_circuit[0] = True
            # Progress output
            if progress_every is not None and completions_count[0] % progress_every == 0:
                now = time.time()
                rate = progress_every / max(1e-9, now - last_progress[0])
                print(f"    [progress] {completions_count[0]:,} completions, "
                      f"{now - start_time:.1f}s elapsed, {rate:.0f}/s",
                      flush=True)
                last_progress[0] = now
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


def run_profile(profile_name, n, max_completions, time_limit, progress_every=None,
                checkpoint_path=None):
    pairs = all_valid_st_for_profile(profile_name)
    print()
    print(f"=== Score profile {profile_name} at n={n}: {len(pairs)} configurations ===",
          flush=True)

    closed = 0
    other = 0
    total_completions = 0
    total_elapsed = 0.0

    for (S, target_S_map) in pairs:
        result = check_pair(S, target_S_map, n, max_completions, time_limit,
                            progress_every=progress_every)
        status = result.get('status')
        n_comp = result.get('num_completions', 0)
        elapsed = result.get('elapsed', 0)
        total_completions += n_comp
        total_elapsed += elapsed

        if status == 'closed':
            closed += 1
        else:
            other += 1

        # Identify u-vertices for display
        u_set = sorted(s for s in S if target_S_map[s] != 1)
        line = (f"  S={sorted(S)} u={u_set}: {status} "
                f"(forced={result.get('forced_arc_count', 0)}, "
                f"free={result.get('free_choices_count', 0)}, "
                f"comp={n_comp:,}, {elapsed:.1f}s)")
        print(line, flush=True)

        # Checkpoint: append per-config result to file
        if checkpoint_path:
            with open(checkpoint_path, 'a') as f:
                f.write(f"{profile_name}\t{sorted(S)}\t{u_set}\t{status}\t"
                        f"{result.get('forced_arc_count', 0)}\t"
                        f"{result.get('free_choices_count', 0)}\t"
                        f"{n_comp}\t{elapsed:.2f}\n")

        if status == 'obstruction_found':
            print(f"    Obstruction: {result.get('obstruction_sample')}", flush=True)
            return False, total_completions, closed, other

    return closed == len(pairs), total_completions, closed, other


def main():
    n = 11
    if len(sys.argv) > 1:
        n = int(sys.argv[1])

    max_completions = 100_000_000
    time_limit = 3600.0
    progress_every = None
    checkpoint_path = None

    # For larger n, automatically enable progress and checkpoint output.
    if n >= 12:
        progress_every = 5_000_000
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        checkpoint_path = DATA_DIR / f"k4_n{n}_checkpoint.tsv"
        # Initialise checkpoint file
        with open(checkpoint_path, 'w') as f:
            f.write("# profile\tS\tu_set\tstatus\tforced\tfree\tcompletions\telapsed_s\n")

    print(f"Score-profile-aware miner: delta=4, n={n}", flush=True)
    print(f"max_completions={max_completions:,}, time_limit={time_limit}s per (S, profile)",
          flush=True)
    if progress_every:
        print(f"progress every {progress_every:,} completions", flush=True)
    if checkpoint_path:
        print(f"per-config checkpoint -> {checkpoint_path.relative_to(PROBLEM_ROOT)}", flush=True)

    grand_total = 0
    grand_closed = 0
    grand_other = 0
    all_ok = True

    for profile in ['(1,1,1,1)', '(2,1,1,1)', '(2,2,1,1)', '(3,1,1,1)']:
        ok, total, closed, other = run_profile(
            profile, n, max_completions, time_limit,
            progress_every=progress_every,
            checkpoint_path=checkpoint_path,
        )
        grand_total += total
        grand_closed += closed
        grand_other += other
        if not ok:
            all_ok = False

    print()
    print(f"Grand summary at n={n}:")
    print(f"  total configurations closed: {grand_closed}")
    print(f"  total configurations not closed: {grand_other}")
    print(f"  total completions: {grand_total:,}")
    if not all_ok:
        sys.exit(1)


if __name__ == '__main__':
    main()
