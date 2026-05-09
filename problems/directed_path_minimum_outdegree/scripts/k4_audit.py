"""Audit the local proof miner for delta=4, n=10.

Checks:
1. Forced arcs in every completion: each forced arc must hold in every
   enumerated completion.
2. Score sequence of S in each completion matches the (S, T) role assignment.
3. Each completion is 4-outregular and oriented.
4. Each completion has a length-8 directed simple path (sanity check).
5. (S, T) configurations: brute-force enumerate, compare with miner.
6. Sample length-8 paths from each (S, T) for the proof table.
"""

import itertools
import sys
from k4_local_miner import (
    V_D, V_C, V_outside, succ_C, pred_C,
    derive_forced, has_path_of_length,
    shape_A1_configs, shape_A2_configs, shape_B_configs,
)


def find_path_of_length(adj: dict, target: int = 8):
    """Return one directed simple path of length target if exists, else None.
    Path is a list of vertices."""
    def dfs(v, visited, path):
        if len(path) - 1 >= target:
            return list(path)
        for w in adj[v]:
            if w not in visited:
                visited.add(w)
                path.append(w)
                result = dfs(w, visited, path)
                if result is not None:
                    return result
                path.pop()
                visited.discard(w)
        return None

    for start in adj:
        visited = {start}
        path = [start]
        result = dfs(start, visited, path)
        if result is not None:
            return result
    return None


def audit_config(S, T, max_completions=5000000):
    """Enumerate all valid completions for (S, T), validate each."""
    result = derive_forced(S, T)
    if result is None or len(result) == 2:
        return {'status': 'error_or_inconsistent', 'detail': result}

    forced, forbidden, out_confirmed, out_excluded = result
    Vminus_S = V_C - S
    U = S - T

    # Free choices
    free_choices = []
    for v in V_D:
        need = 4 - len(out_confirmed[v])
        if v in S:
            cand_set = V_C - {v} - out_excluded[v] - out_confirmed[v]
        else:
            cand_set = V_D - {v} - out_excluded[v] - out_confirmed[v]
        if need > 0:
            free_choices.append((v, need, sorted(cand_set)))

    free_choices.sort(key=lambda x: (len(x[2]) - x[1], x[0]))

    completions = []
    audit_failures = []

    def recurse(idx, arcs):
        if idx == len(free_choices):
            # Validate this completion
            # 1. Antiparallel
            for (a, b) in arcs:
                if (b, a) in arcs:
                    audit_failures.append({'reason': 'antiparallel', 'arcs': sorted(arcs)})
                    return
            # 2. 4-outregular
            out_count = {v: 0 for v in V_D}
            for (u, _) in arcs:
                out_count[u] += 1
            if any(out_count[v] != 4 for v in V_D):
                audit_failures.append({'reason': '4-outregular violation', 'out_count': out_count})
                return
            # 3. Forced arcs included
            for f_arc in forced:
                if f_arc not in arcs:
                    audit_failures.append({'reason': 'missing forced arc', 'arc': f_arc})
                    return
            # 4. Score sequence
            adj = {v: set() for v in V_D}
            for (u, w) in arcs:
                adj[u].add(w)

            for s in S:
                d_S = sum(1 for w in adj[s] if w in S)
                if s in T:
                    if d_S != 1:
                        audit_failures.append({
                            'reason': f'wrong d^+_S for T-vertex {s}',
                            'expected': 1, 'got': d_S,
                            'arcs_from_s': sorted(adj[s]),
                        })
                        return
                else:
                    if d_S != 2:
                        audit_failures.append({
                            'reason': f'wrong d^+_S for U-vertex {s}',
                            'expected': 2, 'got': d_S,
                        })
                        return
            # 5. Claim 12: S-vertex out-arcs in V(C)
            for s in S:
                for w in adj[s]:
                    if w not in V_C:
                        audit_failures.append({
                            'reason': f'S-vertex {s} sends arc to non-V(C) vertex {w}',
                        })
                        return
            # 6. Length-8 path
            path = find_path_of_length(adj, target=8)
            if path is None:
                audit_failures.append({
                    'reason': 'NO LENGTH-8 PATH (counterexample candidate!)',
                    'arcs': sorted(arcs),
                })
                return

            completions.append({'arcs': frozenset(arcs), 'length_8_path': path})
            return

        v, need, cand = free_choices[idx]
        valid_cand = [w for w in cand if (w, v) not in arcs]
        if len(valid_cand) < need:
            return

        for combo in itertools.combinations(valid_cand, need):
            for w in combo:
                arcs.add((v, w))
            recurse(idx + 1, arcs)
            for w in combo:
                arcs.discard((v, w))

    initial = set(forced)
    recurse(0, initial)

    return {
        'status': 'ok' if not audit_failures else 'audit_failed',
        'num_completions': len(completions),
        'failures': audit_failures[:5],
        'sample_paths': [c['length_8_path'] for c in completions[:3]],
        'num_forced': len(forced),
    }


def brute_force_st_configs():
    """Enumerate all (S, T) with v_7 in S, |S|=4, |T|=2, sigma(T) subset S."""
    configs = []
    for S_tuple in itertools.combinations(range(1, 8), 4):
        if 7 not in S_tuple:
            continue
        S = frozenset(S_tuple)
        for T_tuple in itertools.combinations(S_tuple, 2):
            T = frozenset(T_tuple)
            sigma_T = frozenset(pred_C(t) for t in T)
            if sigma_T.issubset(S):
                configs.append((S, T))
    return configs


def audit_st_completeness():
    """Verify miner's (S, T) enumeration matches brute force."""
    bf = set(brute_force_st_configs())
    miner = set()
    for label, S, T, _, _ in shape_A1_configs():
        miner.add((S, T))
    for label, S, T, _, _ in shape_A2_configs():
        miner.add((S, T))
    for label, S, T, _, _ in shape_B_configs():
        miner.add((S, T))

    missing_from_miner = bf - miner
    extra_in_miner = miner - bf

    return {
        'brute_force_count': len(bf),
        'miner_count': len(miner),
        'missing_from_miner': [(sorted(S), sorted(T)) for S, T in missing_from_miner],
        'extra_in_miner': [(sorted(S), sorted(T)) for S, T in extra_in_miner],
        'match': len(missing_from_miner) == 0 and len(extra_in_miner) == 0,
    }


def main():
    # Audit (S, T) completeness
    print("=" * 70)
    print("Audit: (S, T) configuration completeness")
    print("=" * 70)
    completeness = audit_st_completeness()
    print(f"Brute force: {completeness['brute_force_count']} configs")
    print(f"Miner enumerates: {completeness['miner_count']} configs")
    print(f"Match: {completeness['match']}")
    if completeness['missing_from_miner']:
        print(f"  MISSING: {completeness['missing_from_miner']}")
    if completeness['extra_in_miner']:
        print(f"  EXTRA: {completeness['extra_in_miner']}")

    # Audit each (S, T)
    print()
    print("=" * 70)
    print("Audit: per-(S, T) validation")
    print("=" * 70)

    all_configs = []
    for label, S, T, _, _ in shape_A1_configs():
        all_configs.append((label, S, T))
    for label, S, T, _, _ in shape_A2_configs():
        all_configs.append((label, S, T))
    for label, S, T, _, _ in shape_B_configs():
        all_configs.append((label, S, T))

    total_pass = 0
    total_fail = 0
    sample_paths_per_config = {}
    for label, S, T in all_configs:
        result = audit_config(S, T)
        status = result.get('status')
        n_comp = result.get('num_completions', 0)
        if status == 'ok':
            total_pass += 1
            print(f"  {label} S={sorted(S)} T={sorted(T)}: OK ({n_comp} completions)")
            sample_paths_per_config[(tuple(sorted(S)), tuple(sorted(T)))] = result['sample_paths'][0] if result['sample_paths'] else None
        else:
            total_fail += 1
            print(f"  {label} S={sorted(S)} T={sorted(T)}: FAIL")
            for f in result.get('failures', []):
                print(f"    {f}")

    print()
    print(f"Total: {total_pass} passed, {total_fail} failed.")

    # Print sample paths
    print()
    print("=" * 70)
    print("Sample length-8 paths per (S, T):")
    print("=" * 70)
    for (S, T), path in sorted(sample_paths_per_config.items()):
        print(f"  S={list(S)} T={list(T)}: path = {path}")


if __name__ == '__main__':
    main()
