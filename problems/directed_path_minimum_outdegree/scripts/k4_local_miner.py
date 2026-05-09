"""Local proof miner for delta=4, n=10, score (2,2,1,1).

For each S, T configuration, derive forced arcs from:
- path arcs v_0 -> v_1 -> ... -> v_7
- cycle arc v_7 -> v_1 (a=1)
- T-arcs: t in T sends to all V(C)\\S
- F2: u-vertices' S-arcs and V(C)\\S arcs forced via antiparallel chain
- F3: v_0 -> B = succ_C(S)
- Claim 12: S-vertices' out-neighbours in V(C)
- Antiparallel exclusion
- 4-outregularity (exact count)

Then enumerate all completions, check validity (oriented, 4-outregular),
and search for a directed simple path of length >= 8.

Output per (S, T):
- "all closed": every completion has a length-8 path.
- "obstruction": at least one completion has no length-8 path.
- "inconsistent": forced arcs alone violate the constraints.
"""

import itertools
import sys

# Vertex labelling
# 0..7 = v_0..v_7
# 8 = x, 9 = y
N = 10
V_D = frozenset(range(N))
V_C = frozenset({1, 2, 3, 4, 5, 6, 7})
V_outside = frozenset({8, 9})


def succ_C(v: int) -> int:
    """Successor in cycle C: v_1 -> v_2 -> ... -> v_7 -> v_1."""
    if v == 7:
        return 1
    if 1 <= v <= 6:
        return v + 1
    raise ValueError(f"succ_C undefined for {v}")


def pred_C(v: int) -> int:
    """Predecessor in cycle C."""
    if v == 1:
        return 7
    if 2 <= v <= 7:
        return v - 1
    raise ValueError(f"pred_C undefined for {v}")


def has_path_of_length(adj: dict, target: int = 8) -> bool:
    """DFS for a directed simple path of length >= target."""
    def dfs(v, visited, length):
        if length >= target:
            return True
        for w in adj[v]:
            if w not in visited:
                visited.add(w)
                if dfs(w, visited, length + 1):
                    return True
                visited.discard(w)
        return False

    for start in adj:
        visited = {start}
        if dfs(start, visited, 0):
            return True
    return False


def derive_forced(S: frozenset, T: frozenset):
    """Compute forced arcs and forbidden arcs for given (S, T).

    Returns (forced_arcs, forbidden_arcs) or (None, reason) if inconsistent.
    """
    if 7 not in S:
        return None, "v_7 not in S"
    if not T.issubset(S):
        return None, "T not subset of S"
    if len(S) != 4 or len(T) != 2:
        return None, f"|S|={len(S)}, |T|={len(T)}"

    U = S - T
    Vminus_S = V_C - S

    forced = set()
    forbidden = set()

    # Path arcs v_0 -> v_1 -> ... -> v_7
    for i in range(7):
        forced.add((i, i + 1))

    # Cycle arc v_7 -> v_1
    forced.add((7, 1))

    # T-arcs: each t in T sends to all V(C)\\S (and only as out-arcs in V(C))
    for t in T:
        for v in Vminus_S:
            forced.add((t, v))

    # F3: v_0 -> B = succ_C(S)
    B = frozenset(succ_C(s) for s in S)
    for v in B:
        forced.add((0, v))

    # Self-loops forbidden
    for v in V_D:
        forbidden.add((v, v))

    # Antiparallel from forced
    for (a, b) in list(forced):
        forbidden.add((b, a))

    # S-vertices: out-arcs in V(C) (Claim 12)
    for v in S:
        for w in V_outside:
            forbidden.add((v, w))

    # Lemma A: out-neighbours of v_7 (= v_L) in V(P), so not x or y
    # (Already covered by Claim 12 since v_7 in S.)

    # Lemma A reverse: in-neighbours of v_0 in V(P), so not from x or y
    forbidden.add((8, 0))
    forbidden.add((9, 0))

    # F2 forcing: iteratively derive forced and forbidden arcs based on
    # score sequence + Claim 12 + antiparallel + 4-outregularity.

    out_confirmed = {v: set() for v in V_D}
    out_excluded = {v: set() for v in V_D}

    for (u, v) in forced:
        out_confirmed[u].add(v)
    for (u, v) in forbidden:
        out_excluded[u].add(v)

    def candidates(v):
        """Set of vertices w such that (v, w) is not forbidden."""
        if v in S:
            return (V_C - {v}) - out_excluded[v]
        return (V_D - {v}) - out_excluded[v]

    def confirm_arc(u, v):
        """Mark (u, v) as forced. Returns True if newly added."""
        if v in out_confirmed[u]:
            return False
        if v in out_excluded[u]:
            raise ValueError(f"Inconsistency: ({u}, {v}) forced but already forbidden")
        out_confirmed[u].add(v)
        forced.add((u, v))
        # Antiparallel
        if u not in out_excluded[v]:
            out_excluded[v].add(u)
            forbidden.add((v, u))
        return True

    def exclude_arc(u, v):
        """Mark (u, v) as forbidden."""
        if v in out_excluded[u]:
            return False
        if v in out_confirmed[u]:
            raise ValueError(f"Inconsistency: ({u}, {v}) excluded but already forced")
        out_excluded[u].add(v)
        forbidden.add((u, v))
        return True

    # Re-add antiparallel
    for (a, b) in list(forced):
        if a not in out_excluded[b]:
            out_excluded[b].add(a)
            forbidden.add((b, a))

    changed = True
    iter_count = 0
    max_iter = 100
    while changed and iter_count < max_iter:
        changed = False
        iter_count += 1
        for v in V_D:
            confirmed = out_confirmed[v]
            cand = candidates(v) | confirmed  # candidates might exclude already-confirmed
            cand = cand - out_excluded[v] | confirmed

            need = 4 - len(confirmed)
            if need < 0:
                return None, f"vertex {v} has too many forced out-arcs ({len(confirmed)})"

            unconfirmed_cand = cand - confirmed

            if v in S:
                # Score sequence enforces d^+_S
                if v in T:
                    target_S = 1
                else:  # v in U
                    target_S = 2
                target_VCS = 4 - target_S

                # S-arcs
                S_conf = confirmed & S
                S_cand = (cand & S) - {v}
                S_unconf = S_cand - S_conf
                more_S = target_S - len(S_conf)

                if more_S < 0:
                    return None, f"vertex {v} (S) has too many S out-arcs"
                if more_S > len(S_unconf):
                    return None, f"vertex {v} (S) cannot meet d^+_S = {target_S}"
                if more_S == 0:
                    for w in list(S_unconf):
                        if exclude_arc(v, w):
                            changed = True
                if more_S == len(S_unconf) and more_S > 0:
                    for w in list(S_unconf):
                        if confirm_arc(v, w):
                            changed = True

                # V(C)\S arcs
                VCS_conf = confirmed & Vminus_S
                VCS_cand = (cand & Vminus_S)
                VCS_unconf = VCS_cand - VCS_conf
                more_VCS = target_VCS - len(VCS_conf)

                if more_VCS < 0:
                    return None, f"vertex {v} (S) has too many V(C)\\S out-arcs"
                if more_VCS > len(VCS_unconf):
                    return None, f"vertex {v} (S) cannot meet d^+_VCS = {target_VCS}"
                if more_VCS == 0:
                    for w in list(VCS_unconf):
                        if exclude_arc(v, w):
                            changed = True
                if more_VCS == len(VCS_unconf) and more_VCS > 0:
                    for w in list(VCS_unconf):
                        if confirm_arc(v, w):
                            changed = True

            else:
                # Non-S: just need 4 out-arcs total
                if need > len(unconfirmed_cand):
                    return None, f"vertex {v} cannot meet d^+ = 4"
                if need == 0:
                    for w in list(unconfirmed_cand):
                        if exclude_arc(v, w):
                            changed = True
                if need == len(unconfirmed_cand) and need > 0:
                    for w in list(unconfirmed_cand):
                        if confirm_arc(v, w):
                            changed = True

    return forced, forbidden, out_confirmed, out_excluded


def enumerate_and_check(S: frozenset, T: frozenset, max_completions: int = 5000000, time_limit: float = 120.0):
    """Enumerate all valid completions and check for length-8 paths.

    Smarter enumeration: order free choices by smallest cand first to constrain
    early; also propagate antiparallel during recursion (which we already do).

    Returns dict with status info and any obstructions found.
    """
    import time
    start = time.time()

    result = derive_forced(S, T)
    if result is None or len(result) == 2:
        if result is None:
            return {'status': 'error'}
        return {'status': 'inconsistent', 'reason': result[1]}

    forced, forbidden, out_confirmed, out_excluded = result
    Vminus_S = V_C - S

    # For each vertex, compute remaining choices
    free_choices = []
    for v in V_D:
        need = 4 - len(out_confirmed[v])
        if v in S:
            cand_set = V_C - {v} - out_excluded[v] - out_confirmed[v]
        else:
            cand_set = V_D - {v} - out_excluded[v] - out_confirmed[v]

        if need > 0:
            free_choices.append((v, need, sorted(cand_set)))

    # Order: smallest cand first (more constraining)
    free_choices.sort(key=lambda x: (len(x[2]) - x[1], x[0]))

    # Estimate (worst-case upper bound, not accounting for cross-vertex antiparallel)
    from math import comb
    total = 1
    for v, need, cand in free_choices:
        total *= comb(len(cand), need)

    obstructions = []
    completions_checked = 0
    timed_out = False

    def recurse(idx, arcs):
        nonlocal completions_checked, timed_out
        if timed_out:
            return
        if time.time() - start > time_limit:
            timed_out = True
            return
        if completions_checked > max_completions:
            timed_out = True
            return

        if idx == len(free_choices):
            # All assignments made; verify 4-outregular
            out_count = {v: 0 for v in V_D}
            for (u, _) in arcs:
                out_count[u] += 1
            if any(out_count[v] != 4 for v in V_D):
                return

            # Build adj
            adj = {v: set() for v in V_D}
            for (u, w) in arcs:
                adj[u].add(w)

            completions_checked += 1

            if not has_path_of_length(adj, target=8):
                obstructions.append(frozenset(arcs))
            return

        v, need, cand = free_choices[idx]
        # Filter cand: skip those that would conflict with existing arcs
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

    status = 'closed' if not obstructions else 'obstruction_found'
    if timed_out:
        status = 'timed_out'

    return {
        'status': status,
        'num_completions': completions_checked,
        'num_obstructions': len(obstructions),
        'obstructions': [sorted(arcs) for arcs in obstructions[:3]],
        'free_choices_count': len(free_choices),
        'forced_count': len(forced),
        'estimated_upper_bound': total,
        'elapsed': time.time() - start,
    }


# ---- Configurations ----

def shape_A1_configs():
    """All (S, T) for Shape A1: S a 4-cyclic-interval containing v_7,
    T a valid 2-subset (sigma(T) subset S)."""
    configs = []
    # Cyclic intervals containing v_7: starting at v_4, v_5, v_6, v_7.
    for start in [4, 5, 6, 7]:
        S = frozenset((start - 1 + i) % 7 + 1 for i in range(4))
        if 7 not in S:
            continue
        # Vertices in S in C-order: a, b, c, d.
        S_ordered = []
        v = start
        for _ in range(4):
            S_ordered.append(v)
            v = succ_C(v)
        a, b, c, d = S_ordered
        # Valid T placements: {b,c}, {b,d}, {c,d}
        for T_pair in [(b, c), (b, d), (c, d)]:
            T = frozenset(T_pair)
            configs.append(('A1', S, T, S_ordered, T_pair))
    return configs


def shape_A2_configs():
    """All (S, T) for Shape A2: 3-block + isolated u'.
    Block at positions (p, p+1, p+2) cyclically. u, t_1, t_0 = v_p, v_{p+1}, v_{p+2}.
    T = {t_0, t_1}. u' not adjacent to block (u' != v_{p-1}, u' != v_{p+3}).
    v_7 in S means v_7 in block OR u' = v_7."""
    configs = []

    # v_7 in block: block contains 7.
    # v_7 = u (p = 7): block (7, 1, 2). u' in {4, 5}.
    # v_7 = t_1 (p+1 = 7, p = 6): block (6, 7, 1). u' in {3, 4}.
    # v_7 = t_0 (p+2 = 7, p = 5): block (5, 6, 7). u' in {2, 3}.
    # v_7 = u' (isolated): block at p such that 7 not in {p, p+1, p+2}
    #   AND v_7 != v_{p-1} AND v_7 != v_{p+3}.
    # That means p in {2, 3} (since p=1 gives p-1=7 adjacency, p=4 gives p+3=7 adjacency,
    # p=5,6,7 contain v_7 in block).

    cases = [
        # (block, T = last 2 of block, valid u' positions, label)
        ((7, 1, 2), (1, 2), [4, 5], 'A2.1'),
        ((6, 7, 1), (7, 1), [3, 4], 'A2.2'),
        ((5, 6, 7), (6, 7), [2, 3], 'A2.3'),
        # v_7 as isolated u':
        ((2, 3, 4), (3, 4), [7], 'A2.4'),  # block (2,3,4), u' = 7
        ((3, 4, 5), (4, 5), [7], 'A2.5'),  # block (3,4,5), u' = 7
    ]

    for block, T_pair, u_primes, label in cases:
        for u_prime in u_primes:
            S = frozenset(block) | {u_prime}
            T = frozenset(T_pair)
            configs.append((label, S, T, list(block) + [u_prime], T_pair))
    return configs


def shape_B_configs():
    """All (S, T) for true Shape B: 2 separated pairs of consecutive vertices,
    with at least one V(C)\\S vertex between the pairs in BOTH cyclic gaps.
    v_7 in S. T = 'second' of each pair (forced by sigma-image analysis).
    Gap pattern (1, 2) or (2, 1).
    """
    configs = []
    seen = set()

    # Iterate over the start of pair_1, then the gap to pair_2.
    # Pair_1 = (p, p+1), pair_2 = (p + 2 + g1, p + 3 + g1) with gap_1 = g1 >= 1.
    # Then gap_2 = 7 - 4 - g1 = 3 - g1, must be >= 1.
    # So g1 in {1, 2}.

    for p in range(1, 8):
        for g1 in [1, 2]:
            g2 = 3 - g1
            if g2 < 1:
                continue
            p1 = p
            p2 = ((p) % 7) + 1   # p + 1 mod 7
            q1 = ((p + 1 + g1) % 7) + 1   # p + 2 + g1 mod 7 (1-indexed)
            # actually let me just compute directly
            def shift(x, k):
                return ((x - 1 + k) % 7) + 1
            p1 = shift(p, 0)
            p2 = shift(p, 1)
            q1 = shift(p, 2 + g1)
            q2 = shift(p, 3 + g1)
            S = frozenset({p1, p2, q1, q2})
            if len(S) != 4:
                continue
            if 7 not in S:
                continue
            key = tuple(sorted(S))
            if key in seen:
                continue
            # Verify true Shape B: not 4 cyclically consecutive
            S_sorted_cyclic = sorted(S)
            # Check if S is 4 cyclically consecutive
            is_consecutive = False
            for start in range(1, 8):
                interval = {((start - 1 + i) % 7) + 1 for i in range(4)}
                if interval == set(S):
                    is_consecutive = True
                    break
            if is_consecutive:
                continue
            seen.add(key)
            T = frozenset({p2, q2})
            configs.append(('B', S, T, [p1, p2, q1, q2], (p2, q2)))
    return configs


def main():
    print("=" * 70)
    print("Shape A1 (sanity check, should all close):")
    print("=" * 70)
    for label, S, T, S_ord, T_pair in shape_A1_configs():
        print(f"\n{label}: S = {sorted(S)} (C-order {S_ord}), T = {sorted(T)}")
        result = enumerate_and_check(S, T)
        print(f"  status: {result.get('status')}")
        if 'num_completions' in result:
            print(f"  completions checked: {result['num_completions']}, "
                  f"obstructions: {result.get('num_obstructions', 0)}")
        if result.get('status') == 'too_many_completions':
            print(f"  estimated completions: {result.get('estimated')}")
        if result.get('status') == 'inconsistent':
            print(f"  reason: {result.get('reason')}")
        if 'forced_count' in result:
            print(f"  forced arcs: {result['forced_count']}, free choices: {result['free_choices_count']}")
        if result.get('obstructions'):
            print(f"  example obstruction: {result['obstructions'][0]}")

    print()
    print("=" * 70)
    print("Shape B (priority):")
    print("=" * 70)
    for label, S, T, S_ord, T_pair in shape_B_configs():
        print(f"\n{label}: S = {sorted(S)}, T = {sorted(T)}")
        result = enumerate_and_check(S, T)
        print(f"  status: {result.get('status')}")
        if 'num_completions' in result:
            print(f"  completions checked: {result['num_completions']}, "
                  f"obstructions: {result.get('num_obstructions', 0)}")
        if result.get('status') == 'too_many_completions':
            print(f"  estimated completions: {result.get('estimated')}")
        if result.get('status') == 'inconsistent':
            print(f"  reason: {result.get('reason')}")
        if 'forced_count' in result:
            print(f"  forced arcs: {result['forced_count']}, free choices: {result['free_choices_count']}")
        if result.get('obstructions'):
            print(f"  example obstruction: {result['obstructions'][0]}")

    print()
    print("=" * 70)
    print("Shape A2:")
    print("=" * 70)
    for label, S, T, S_ord, T_pair in shape_A2_configs():
        print(f"\n{label}: S = {sorted(S)}, T = {sorted(T)}")
        result = enumerate_and_check(S, T)
        print(f"  status: {result.get('status')}")
        if 'num_completions' in result:
            print(f"  completions checked: {result['num_completions']}, "
                  f"obstructions: {result.get('num_obstructions', 0)}")
        if result.get('status') == 'too_many_completions':
            print(f"  estimated completions: {result.get('estimated')}")
        if result.get('status') == 'inconsistent':
            print(f"  reason: {result.get('reason')}")
        if 'forced_count' in result:
            print(f"  forced arcs: {result['forced_count']}, free choices: {result['free_choices_count']}")
        if result.get('obstructions'):
            print(f"  example obstruction: {result['obstructions'][0]}")


if __name__ == '__main__':
    main()
