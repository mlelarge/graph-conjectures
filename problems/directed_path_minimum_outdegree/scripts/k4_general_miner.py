"""Generalized local proof miner for delta=4 at arbitrary n >= 10.

This is a parameterized version of k4_local_miner.py / k4_independent_check.py
that handles |V(D) \\ V(P)| = n - 8 outside vertices instead of just 2.

For n=10: identical to the earlier miner (3 outside vertices: x, y).
For n=11: 3 outside vertices.
For n=12: 4 outside vertices. Etc.

Vertex labelling:
  0..7 = v_0..v_7 (path vertices).
  8..(n-1) = outside vertices.

Cycle C: v_1 -> v_2 -> ... -> v_7 -> v_1 (always; assumes a=1).

Run as a script:
  uv run python scripts/k4_general_miner.py [n]

Default n=11 (the next open case after the published n=10 closure).
Outputs per-(S, T) status: closed / obstruction / overflow.
"""

from itertools import combinations
import sys
import time


DELTA = 4


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


def all_valid_st():
    out = []
    for S_tuple in combinations(range(1, 8), 4):
        if 7 not in S_tuple:
            continue
        S = frozenset(S_tuple)
        for T_tuple in combinations(S_tuple, 2):
            T = frozenset(T_tuple)
            sigma_T = frozenset(pred_C(t) for t in T)
            if sigma_T.issubset(S):
                out.append((S, T))
    return out


def derive_forced_arcs(S, T, n):
    """Derive forced/forbidden arcs for given (S, T, n).

    n >= 10. Outside vertices: 8..(n-1)."""
    if 7 not in S or len(S) != 4 or len(T) != 2 or not T.issubset(S):
        return None, "invalid (S, T)"

    PATH_V = frozenset(range(8))
    CYCLE_V = frozenset(range(1, 8))
    OUTSIDE_V = frozenset(range(8, n))
    ALL_V = frozenset(range(n))
    Vminus_S = CYCLE_V - S

    forced = set()
    forbidden = set()

    for v in range(n):
        forbidden.add((v, v))

    for i in range(7):
        forced.add((i, i + 1))

    forced.add((7, 1))

    for t in T:
        for w in Vminus_S:
            forced.add((t, w))

    B = frozenset(succ_C(s) for s in S)
    for w in B:
        forced.add((0, w))

    for s in S:
        for w in OUTSIDE_V:
            forbidden.add((s, w))

    for ext in OUTSIDE_V:
        forbidden.add((ext, 0))

    for (u, v) in list(forced):
        forbidden.add((v, u))

    if forced & forbidden:
        return None, f"forced ∩ forbidden non-empty: {forced & forbidden}"

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
                target_S = 1 if v in T else 2
                target_VCS = DELTA - target_S

                S_conf = confirmed_out & S
                S_cand = (CYCLE_V - {v}) - forbidden_out
                S_cand_in_S = S_cand & S
                S_unconf = S_cand_in_S - S_conf
                more_S = target_S - len(S_conf)

                if more_S < 0:
                    return None, f"v={v} too many S-arcs"
                if more_S > len(S_unconf):
                    return None, f"v={v} cannot meet target_S"
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
                    return None, f"v={v} cannot meet target_VCS"
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

    found = [None]

    def dfs(v, visited, length):
        if found[0] is not None:
            return
        if length >= target:
            found[0] = True
            return
        for w in adj[v]:
            if w not in visited:
                visited.add(w)
                dfs(w, visited, length + 1)
                if found[0] is not None:
                    return
                visited.discard(w)

    for start in range(n):
        if found[0] is not None:
            break
        dfs(start, {start}, 0)

    return found[0] is True


def check_st_pair(S, T, n, max_completions=2000000, time_limit=120.0):
    PATH_V = frozenset(range(8))
    CYCLE_V = frozenset(range(1, 8))
    OUTSIDE_V = frozenset(range(8, n))
    ALL_V = frozenset(range(n))

    result = derive_forced_arcs(S, T, n)
    if result is None or (len(result) == 2 and isinstance(result[1], str)):
        return {
            'S': sorted(S), 'T': sorted(T), 'n': n,
            'status': 'inconsistent',
            'reason': result[1] if result is not None else 'unknown',
        }

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

    from math import comb
    upper_bound = 1
    for v, need, cand in free_choices:
        upper_bound *= comb(len(cand), need)

    obstructions = []
    completions_count = [0]
    overflow = [False]
    timed_out = [False]
    start_time = time.time()

    def recurse(idx, arcs):
        if overflow[0] or timed_out[0]:
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

    initial = set(forced)
    recurse(0, initial)

    status = 'closed' if not obstructions else 'obstruction_found'
    if overflow[0]:
        status = 'overflow'
    if timed_out[0]:
        status = 'timed_out'

    return {
        'S': sorted(S), 'T': sorted(T), 'n': n,
        'status': status,
        'num_completions': completions_count[0],
        'num_obstructions': len(obstructions),
        'forced_arc_count': len(forced),
        'free_choices_count': len(free_choices),
        'upper_bound': upper_bound,
        'elapsed': time.time() - start_time,
    }


def main():
    n = 11
    if len(sys.argv) > 1:
        n = int(sys.argv[1])

    print(f"=" * 70)
    print(f"Generalized miner: delta=4, n={n}")
    print(f"=" * 70)
    print()

    pairs = all_valid_st()
    print(f"Valid (S, T) configurations: {len(pairs)}")
    print()

    closed = 0
    overflow = 0
    timed_out = 0
    obstruction_found = 0
    inconsistent = 0
    total_completions = 0
    total_obstructions = 0
    total_elapsed = 0.0

    for (S, T) in pairs:
        result = check_st_pair(S, T, n)
        status = result.get('status')
        n_comp = result.get('num_completions', 0)
        n_obs = result.get('num_obstructions', 0)
        elapsed = result.get('elapsed', 0)
        upper = result.get('upper_bound', 0)
        free = result.get('free_choices_count', 0)
        forced = result.get('forced_arc_count', 0)
        total_elapsed += elapsed

        if status == 'closed':
            closed += 1
            total_completions += n_comp
        elif status == 'overflow':
            overflow += 1
            total_completions += n_comp
        elif status == 'timed_out':
            timed_out += 1
            total_completions += n_comp
        elif status == 'obstruction_found':
            obstruction_found += 1
            total_obstructions += n_obs
            total_completions += n_comp
        else:
            inconsistent += 1

        msg = f"  S={result['S']} T={result['T']}: {status}"
        msg += f" (forced={forced}, free={free}, upper={upper:,}, comp={n_comp:,}"
        if n_obs > 0:
            msg += f", obs={n_obs}"
        msg += f", {elapsed:.1f}s)"
        print(msg)

    print()
    print(f"Summary at n={n}:")
    print(f"  closed: {closed}")
    print(f"  overflow: {overflow}")
    print(f"  timed_out: {timed_out}")
    print(f"  obstruction_found: {obstruction_found}")
    print(f"  inconsistent: {inconsistent}")
    print(f"  total completions: {total_completions:,}")
    print(f"  total obstructions: {total_obstructions}")
    print(f"  total elapsed: {total_elapsed:.1f}s")


if __name__ == '__main__':
    main()
