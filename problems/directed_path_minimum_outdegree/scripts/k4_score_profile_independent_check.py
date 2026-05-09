"""Independent score-profile checker for delta=4 at arbitrary n >= 10.

This file shares no code with scripts/k4_score_profile_miner.py
(or any other miner). It re-implements from scratch:

  1. Brute-force enumeration of (S, T, score profile) configurations
     for all four score sequences (1,1,1,1), (2,1,1,1), (2,2,1,1),
     (3,1,1,1).
  2. Forced-arc derivation from a declarative rule list.
  3. Completion enumeration.
  4. Length-8 path verification.
  5. Per-configuration completion counts and obstruction tracking.

Vertex labelling: 0..7 = v_0..v_7 (path), 8..(n-1) = outside vertices.
n >= 10. delta = 4 (4-outregular). a = 1 (V(C) = {1, ..., 7}).

Usage:
  uv run python scripts/k4_score_profile_independent_check.py [n]

Default n=11. The script exits 0 iff every configuration closes;
nonzero on obstruction, overflow, timeout, or inconsistency.
"""

from itertools import combinations
import sys
import time


N_DEGREE = 4  # delta value


def cycle_succ(v):
    """Successor in cycle C: 1 -> 2 -> ... -> 7 -> 1."""
    if v == 7:
        return 1
    if 1 <= v <= 6:
        return v + 1
    raise ValueError(v)


def cycle_pred(v):
    """Predecessor in cycle C."""
    if v == 1:
        return 7
    if 2 <= v <= 7:
        return v - 1
    raise ValueError(v)


# ---- Step 1: enumerate configurations ----

def enumerate_score_profile_configs(profile_label):
    """Enumerate all (S, profile_map) pairs valid for the given profile.

    profile_map is a dict from S-vertex to its forced internal out-degree.
    The valid configurations satisfy v_7 in S, |S| = 4, and the cyclic-
    closure constraint that vertices with profile_map[s] = 1 (= the
    T-vertices) have their predecessors in S.
    """
    out = []
    for S_tuple in combinations(range(1, 8), 4):
        if 7 not in S_tuple:
            continue
        S = frozenset(S_tuple)

        if profile_label == '(1,1,1,1)':
            score_map = {s: 1 for s in S}
            T = S
            sigma_T = frozenset(cycle_pred(t) for t in T)
            if sigma_T.issubset(S):
                out.append((S, score_map))
        elif profile_label == '(2,1,1,1)':
            for u in S:
                score_map = {s: (2 if s == u else 1) for s in S}
                T = frozenset(s for s in S if score_map[s] == 1)
                sigma_T = frozenset(cycle_pred(t) for t in T)
                if sigma_T.issubset(S):
                    out.append((S, score_map))
        elif profile_label == '(2,2,1,1)':
            for u_pair in combinations(S, 2):
                u_set = frozenset(u_pair)
                score_map = {s: (2 if s in u_set else 1) for s in S}
                T = frozenset(s for s in S if score_map[s] == 1)
                sigma_T = frozenset(cycle_pred(t) for t in T)
                if sigma_T.issubset(S):
                    out.append((S, score_map))
        elif profile_label == '(3,1,1,1)':
            for u in S:
                score_map = {s: (3 if s == u else 1) for s in S}
                T = frozenset(s for s in S if score_map[s] == 1)
                sigma_T = frozenset(cycle_pred(t) for t in T)
                if sigma_T.issubset(S):
                    out.append((S, score_map))
        else:
            raise ValueError(f"unknown profile: {profile_label}")
    return out


# ---- Step 2: forced/forbidden arc derivation ----

def derive_forced(S, score_map, n):
    """Derive forced and forbidden arcs from a declarative rule list.

    Rules:
      R-loop: (v, v) forbidden for all v.
      R-path: (i, i+1) forced for i = 0..6.
      R-cycle: (7, 1) forced.
      R-T: t -> w forced for t in T (= score_map^{-1}(1)),
           w in V(C) \\ S.
      R-F3: (0, w) forced for w in succ_C(S).
      R-Claim12: (s, w) forbidden for s in S, w outside V(C).
      R-LemmaA-rev: (ext, 0) forbidden for ext outside V(P).
      R-AP: forced (u, v) implies forbidden (v, u).
      R-out: every vertex has out-degree 4 (used in propagation).
      R-score: each s in S has out-degree-in-S = score_map[s].
      R-VCS: each s in S has out-degree-in-(V(C)\\S) = 4 - score_map[s].

    Iterative propagation P1, P2:
      For each vertex v with target T_v in some sub-target set X:
        if confirmed = T_v, exclude all unconfirmed of X.
        if unconfirmed = T_v - confirmed, force all unconfirmed of X.
    """
    PATH_VERTICES = frozenset(range(8))
    CYCLE_VERTICES = frozenset(range(1, 8))
    OUTSIDE_VERTICES = frozenset(range(8, n))
    ALL_VERTICES = frozenset(range(n))
    NON_S_IN_CYCLE = CYCLE_VERTICES - S

    if 7 not in S or len(S) != 4:
        return None, "invalid S"
    if set(score_map.keys()) != set(S):
        return None, "score_map keys != S"

    T_vertices = frozenset(s for s in S if score_map[s] == 1)

    forced = set()
    forbidden = set()

    # R-loop
    for v in range(n):
        forbidden.add((v, v))

    # R-path
    for i in range(7):
        forced.add((i, i + 1))

    # R-cycle
    forced.add((7, 1))

    # R-T
    for t in T_vertices:
        for w in NON_S_IN_CYCLE:
            forced.add((t, w))

    # R-F3
    B = frozenset(cycle_succ(s) for s in S)
    for w in B:
        forced.add((0, w))

    # R-Claim12
    for s in S:
        for w in OUTSIDE_VERTICES:
            forbidden.add((s, w))

    # R-LemmaA-rev
    for ext in OUTSIDE_VERTICES:
        forbidden.add((ext, 0))

    # R-AP for the initial forced set
    for (u, v) in list(forced):
        forbidden.add((v, u))

    if forced & forbidden:
        return None, "forced ∩ forbidden non-empty after initial rules"

    # Iterative P1 / P2
    iters = 0
    while True:
        iters += 1
        if iters > 200:
            return None, "iteration limit exceeded"
        progressed = False

        for v in range(n):
            confirmed_out = {w for (u, w) in forced if u == v}
            forbidden_out = {w for (u, w) in forbidden if u == v}
            need = N_DEGREE - len(confirmed_out)
            if need < 0:
                return None, f"vertex {v} has too many forced out-arcs"

            if v in S:
                target_internal = score_map[v]
                target_external = N_DEGREE - target_internal

                # Internal (S \\ {v})
                S_conf = confirmed_out & S
                S_cand = ((CYCLE_VERTICES - {v}) - forbidden_out) & S
                S_unconf = S_cand - S_conf
                more_internal = target_internal - len(S_conf)

                if more_internal < 0:
                    return None, f"v={v}: too many internal S-arcs"
                if more_internal > len(S_unconf):
                    return None, f"v={v}: cannot meet target_S = {target_internal}"
                if more_internal == 0 and S_unconf:
                    for w in S_unconf:
                        if (v, w) not in forbidden:
                            forbidden.add((v, w))
                            progressed = True
                if more_internal == len(S_unconf) and more_internal > 0:
                    for w in list(S_unconf):
                        if (v, w) not in forced:
                            forced.add((v, w))
                            forbidden.add((w, v))
                            progressed = True

                # External (V(C) \\ S)
                X_conf = confirmed_out & NON_S_IN_CYCLE
                X_cand = ((CYCLE_VERTICES - {v}) - forbidden_out) & NON_S_IN_CYCLE
                X_unconf = X_cand - X_conf
                more_external = target_external - len(X_conf)

                if more_external < 0:
                    return None, f"v={v}: too many external V(C)\\S arcs"
                if more_external > len(X_unconf):
                    return None, f"v={v}: cannot meet target_VCS = {target_external}"
                if more_external == 0 and X_unconf:
                    for w in X_unconf:
                        if (v, w) not in forbidden:
                            forbidden.add((v, w))
                            progressed = True
                if more_external == len(X_unconf) and more_external > 0:
                    for w in list(X_unconf):
                        if (v, w) not in forced:
                            forced.add((v, w))
                            forbidden.add((w, v))
                            progressed = True
            else:
                cand = (ALL_VERTICES - {v}) - forbidden_out
                unconf = cand - confirmed_out
                if need > len(unconf):
                    return None, f"v={v}: cannot meet d^+ = {N_DEGREE}"
                if need == 0 and unconf:
                    for w in unconf:
                        if (v, w) not in forbidden:
                            forbidden.add((v, w))
                            progressed = True
                if need == len(unconf) and need > 0:
                    for w in list(unconf):
                        if (v, w) not in forced:
                            forced.add((v, w))
                            forbidden.add((w, v))
                            progressed = True

        if not progressed:
            break

    return forced, forbidden


# ---- Step 3: completion enumeration ----

def enumerate_completions(S, score_map, n, forced, forbidden,
                          max_completions=200_000_000, time_limit=3600.0):
    """Enumerate every 4-outregular oriented completion satisfying the
    forced/forbidden constraints. Short-circuits on first obstruction."""
    PATH_VERTICES = frozenset(range(8))
    CYCLE_VERTICES = frozenset(range(1, 8))
    ALL_VERTICES = frozenset(range(n))

    free_choices = []
    for v in range(n):
        confirmed = {w for (u, w) in forced if u == v}
        excluded = {w for (u, w) in forbidden if u == v}
        need = N_DEGREE - len(confirmed)
        if v in S:
            cand = (CYCLE_VERTICES - {v}) - excluded - confirmed
        else:
            cand = (ALL_VERTICES - {v}) - excluded - confirmed
        if need > 0:
            free_choices.append((v, need, sorted(cand)))

    free_choices.sort(key=lambda x: (len(x[2]) - x[1], x[0]))

    obstructions = []
    completions_count = [0]
    overflow_flag = [False]
    timed_out_flag = [False]
    short_circuit_flag = [False]
    start_time = time.time()

    def recurse(idx, arcs):
        if overflow_flag[0] or timed_out_flag[0] or short_circuit_flag[0]:
            return
        if completions_count[0] > max_completions:
            overflow_flag[0] = True
            return
        if time.time() - start_time > time_limit:
            timed_out_flag[0] = True
            return

        if idx == len(free_choices):
            count = [0] * n
            for (u, _) in arcs:
                count[u] += 1
            if any(c != N_DEGREE for c in count):
                return
            completions_count[0] += 1
            if not has_path_of_length_at_least_8(arcs, n):
                obstructions.append(frozenset(arcs))
                short_circuit_flag[0] = True
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
            if short_circuit_flag[0]:
                return

    initial = set(forced)
    recurse(0, initial)

    if short_circuit_flag[0]:
        status = 'obstruction_found'
    elif overflow_flag[0]:
        status = 'overflow'
    elif timed_out_flag[0]:
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


# ---- Step 4: length-8 path search ----

def has_path_of_length_at_least_8(arcs, n):
    """DFS for a directed simple path of length >= 8."""
    adj = {v: set() for v in range(n)}
    for (u, w) in arcs:
        adj[u].add(w)

    found = [False]

    def dfs(v, visited, length):
        if found[0]:
            return
        if length >= 8:
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


# ---- Top-level driver ----

def run_profile(profile_label, n, max_comp, time_lim):
    configs = enumerate_score_profile_configs(profile_label)
    print()
    print(f"=== Profile {profile_label} at n={n}: {len(configs)} configurations ===")

    profile_completions = 0
    profile_closed = 0

    for (S, score_map) in configs:
        result = derive_forced(S, score_map, n)
        if result is None or len(result) == 2 and isinstance(result[1], str):
            reason = result[1] if result is not None else 'unknown'
            print(f"  S={sorted(S)} score={score_map}: inconsistent ({reason})")
            return False, profile_completions, profile_closed, len(configs)

        forced, forbidden = result
        check = enumerate_completions(S, score_map, n, forced, forbidden, max_comp, time_lim)
        status = check.get('status')
        n_comp = check.get('num_completions', 0)
        elapsed = check.get('elapsed', 0)
        profile_completions += n_comp

        if status == 'closed':
            profile_closed += 1

        u_set = sorted(s for s in S if score_map[s] != 1)
        print(f"  S={sorted(S)} u={u_set}: {status} "
              f"(forced={check.get('forced_arc_count', 0)}, "
              f"free={check.get('free_choices_count', 0)}, "
              f"comp={n_comp:,}, {elapsed:.1f}s)")

        if status != 'closed':
            return False, profile_completions, profile_closed, len(configs)

    return True, profile_completions, profile_closed, len(configs)


def main():
    n = 11
    if len(sys.argv) > 1:
        n = int(sys.argv[1])

    max_comp = 200_000_000
    time_lim = 3600.0

    print(f"Independent score-profile checker: delta=4, n={n}")
    print(f"This file shares NO code with k4_score_profile_miner.py.")
    print(f"max_completions={max_comp:,}, time_limit={time_lim}s per (S, profile)")

    expected_counts = {
        '(1,1,1,1)': 0,
        '(2,1,1,1)': 4,
        '(2,2,1,1)': 24,
        '(3,1,1,1)': 4,
    }

    grand_total = 0
    all_ok = True

    for profile in ['(1,1,1,1)', '(2,1,1,1)', '(2,2,1,1)', '(3,1,1,1)']:
        ok, total, closed, n_configs = run_profile(profile, n, max_comp, time_lim)
        grand_total += total
        if n_configs != expected_counts[profile]:
            print(f"  WARNING: profile {profile} has {n_configs} configs, expected {expected_counts[profile]}")
            all_ok = False
        if not ok:
            all_ok = False

    print()
    print(f"Independent check at n={n}:")
    print(f"  total completions: {grand_total:,}")
    if all_ok:
        print("  RESULT: Independent closure check passed. All 32 configurations")
        print("    in the configuration universe (0 + 4 + 24 + 4) closed.")
        print("  Note: this script does not import or compare against")
        print("    k4_score_profile_miner.py. To verify agreement with the miner,")
        print("    run both scripts and compare per-(S, T) completion counts.")
        sys.exit(0)
    else:
        print("  RESULT: Closure FAILED. See output above.")
        sys.exit(1)


if __name__ == '__main__':
    main()
