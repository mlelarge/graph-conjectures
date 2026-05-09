"""Independent checker for Lemma 4 of the delta=4, n=10 proof.

This file shares no code with scripts/k4_local_miner.py. It re-implements
from scratch:

  1. Brute-force enumeration of valid (S, T) configurations.
  2. Forced-arc derivation from a declarative rule list.
  3. Completion enumeration.
  4. Length-8 path verification.

Vertex labelling: 0..7 = v_0..v_7 (path), 8 = x, 9 = y.
n = 10. delta = 4 (4-outregular). a = 1 (V(C) = {1, ..., 7}).

Run as a script:
  uv run python scripts/k4_independent_check.py

Expected output: 24 (S, T) configurations, all closed, 0 obstructions,
matching scripts/k4_local_miner.py + scripts/k4_audit.py.
"""

from itertools import combinations
import json
import hashlib
import sys
from typing import Dict, FrozenSet, List, Set, Tuple


N = 10
ALL_V = frozenset(range(N))
PATH_V = frozenset(range(8))           # v_0..v_7
CYCLE_V = frozenset(range(1, 8))       # v_1..v_7
OUTSIDE_V = frozenset({8, 9})          # x, y
DELTA = 4


def succ_C(v: int) -> int:
    """Successor in directed cycle C: v_1 -> v_2 -> ... -> v_7 -> v_1."""
    if v == 7:
        return 1
    if 1 <= v <= 6:
        return v + 1
    raise ValueError(v)


def pred_C(v: int) -> int:
    """Predecessor in C."""
    if v == 1:
        return 7
    if 2 <= v <= 7:
        return v - 1
    raise ValueError(v)


# ---- Step 1: brute-force (S, T) enumeration ----

def all_valid_st():
    """Enumerate all (S, T) with v_7 in S, |S| = 4, |T| = 2, sigma(T) subset S."""
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


# ---- Step 2: forced-arc derivation from a declarative rule list ----

def derive_forced_arcs(S: FrozenSet[int], T: FrozenSet[int]):
    """Return (forced, forbidden) where each is a set of (u, v) ordered pairs.

    Rules applied (declarative, indexed for traceability):

      R-loop:        forbid (v, v) for all v.
      R-path:        force (i, i+1) for i in 0..6.
      R-cycle:       force (7, 1).
      R-T:           for each t in T, w in V(C)\\S, force (t, w).
      R-F3:          for each w in succ_C(S), force (0, w).
      R-Claim12:     for each s in S, w in V(D)\\V(C), forbid (s, w).
      R-LemmaA-rev:  forbid (8, 0) and (9, 0).
      R-AP:          for each forced (u, v), forbid (v, u).

    Then iterative propagation:
      P1 (force-by-need):
        for each vertex v with target T_v in some sub-target set X:
          if confirmed = T_v, exclude all unconfirmed of X.
          if unconfirmed = T_v - confirmed, force all unconfirmed of X.
      P2 (cross-vertex via R-AP): same as above.
    """
    if 7 not in S or len(S) != 4 or len(T) != 2 or not T.issubset(S):
        return None, "invalid (S, T)"

    U = S - T
    Vminus_S = CYCLE_V - S

    forced = set()
    forbidden = set()

    # R-loop
    for v in range(N):
        forbidden.add((v, v))

    # R-path
    for i in range(7):
        forced.add((i, i + 1))

    # R-cycle
    forced.add((7, 1))

    # R-T
    for t in T:
        for w in Vminus_S:
            forced.add((t, w))

    # R-F3
    B = frozenset(succ_C(s) for s in S)
    for w in B:
        forced.add((0, w))

    # R-Claim12
    for s in S:
        for w in OUTSIDE_V:
            forbidden.add((s, w))

    # R-LemmaA-rev
    forbidden.add((8, 0))
    forbidden.add((9, 0))

    # R-AP for initial forced set
    for (u, v) in list(forced):
        forbidden.add((v, u))

    # Quick sanity: forced and forbidden disjoint
    if forced & forbidden:
        return None, f"forced ∩ forbidden non-empty: {forced & forbidden}"

    # Iterative propagation P1, P2
    changed = True
    iteration_count = 0
    while changed:
        changed = False
        iteration_count += 1
        if iteration_count > 200:
            return None, "iteration count exceeded; possible inconsistency"

        for v in range(N):
            confirmed_out = {w for (u, w) in forced if u == v}
            forbidden_out = {w for (u, w) in forbidden if u == v}
            need = DELTA - len(confirmed_out)
            if need < 0:
                return None, f"vertex {v} has too many forced out-arcs"

            if v in S:
                # Score sequence
                target_S = 1 if v in T else 2
                target_VCS = DELTA - target_S

                S_conf = confirmed_out & S
                S_cand = (CYCLE_V - {v}) - forbidden_out  # candidate is in V(C)
                S_cand_in_S = S_cand & S
                S_unconf = S_cand_in_S - S_conf
                more_S = target_S - len(S_conf)

                if more_S < 0:
                    return None, f"v={v} target_S={target_S} but {len(S_conf)} confirmed"
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
                            forbidden.add((w, v))  # antiparallel
                            changed = True

                VCS_conf = confirmed_out & Vminus_S
                VCS_cand = (CYCLE_V - {v}) - forbidden_out
                VCS_cand_in_VCS = VCS_cand & Vminus_S
                VCS_unconf = VCS_cand_in_VCS - VCS_conf
                more_VCS = target_VCS - len(VCS_conf)

                if more_VCS < 0:
                    return None, f"v={v} target_VCS={target_VCS} but {len(VCS_conf)} confirmed"
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
                # Non-S: all candidates allowed (subject to forbidden)
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


# ---- Step 3: completion enumeration ----

def enumerate_completions(S, T, forced, forbidden, max_completions=100000):
    """Enumerate every 4-outregular oriented completion satisfying forced/forbidden."""
    free_choices = []
    for v in range(N):
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

    completions = []
    overflow = [False]

    def recurse(idx, arcs):
        if overflow[0]:
            return
        if len(completions) > max_completions:
            overflow[0] = True
            return
        if idx == len(free_choices):
            # Check 4-outregular
            count = [0] * N
            for (u, _) in arcs:
                count[u] += 1
            if any(c != DELTA for c in count):
                return
            completions.append(frozenset(arcs))
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
    return completions, overflow[0]


# ---- Step 4: length-8 path search ----

def has_directed_simple_path_of_length(arcs, target=8):
    """Check whether `arcs` has a directed simple path of length >= target.
    Returns (bool, witness_path or None)."""
    adj = {v: set() for v in range(N)}
    for (u, w) in arcs:
        adj[u].add(w)

    found = [None]

    def dfs(v, visited, path):
        if found[0] is not None:
            return
        if len(path) - 1 >= target:
            found[0] = list(path)
            return
        for w in adj[v]:
            if w not in visited:
                visited.add(w)
                path.append(w)
                dfs(w, visited, path)
                if found[0] is not None:
                    return
                path.pop()
                visited.discard(w)

    for start in range(N):
        if found[0] is not None:
            break
        dfs(start, {start}, [start])

    if found[0] is None:
        return False, None
    return True, found[0]


# ---- Step 5: certificate generation ----

def hash_arcs(arcs):
    """Stable hash of an arc set (sorted, sha256)."""
    h = hashlib.sha256()
    for (u, w) in sorted(arcs):
        h.update(f"{u},{w};".encode())
    return h.hexdigest()


def check_st_pair(S, T):
    """For (S, T): derive forced arcs, enumerate completions, check each.

    Returns dict with full info for certificate.
    """
    result = derive_forced_arcs(S, T)
    if result is None or len(result) == 2 and isinstance(result[1], str):
        return {
            'S': sorted(S),
            'T': sorted(T),
            'status': 'inconsistent',
            'reason': result[1] if result is not None else 'unknown',
            'forced_arcs': [],
            'completions': [],
        }

    forced, forbidden = result
    completions, overflow = enumerate_completions(S, T, forced, forbidden)
    if overflow:
        return {
            'S': sorted(S),
            'T': sorted(T),
            'status': 'overflow',
            'forced_arcs': sorted(forced),
            'num_completions_seen': len(completions),
        }

    obstructions = []
    completion_records = []
    for arcs in completions:
        ok, path = has_directed_simple_path_of_length(arcs, target=8)
        rec = {
            'arcs': sorted([list(a) for a in arcs]),  # full arc list
            'arcs_hash': hash_arcs(arcs),
            'has_length_8_path': ok,
        }
        if ok:
            rec['path'] = path
        else:
            obstructions.append(arcs)
        completion_records.append(rec)

    return {
        'S': sorted(S),
        'T': sorted(T),
        'status': 'closed' if not obstructions else 'obstruction_found',
        'num_completions': len(completions),
        'num_obstructions': len(obstructions),
        'forced_arcs': sorted(forced),
        'forced_arc_count': len(forced),
        'completions': completion_records,
    }


def main():
    print("Independent checker for Lemma 4 (delta=4, n=10).")
    print("This file shares NO code with k4_local_miner.py.")
    print()
    pairs = all_valid_st()
    print(f"Brute-force valid (S, T) configurations: {len(pairs)}")

    results = []
    total_completions = 0
    total_obstructions = 0
    failed = 0
    for (S, T) in pairs:
        rec = check_st_pair(S, T)
        results.append(rec)
        status = rec.get('status')
        if status == 'closed':
            total_completions += rec['num_completions']
            print(f"  S={rec['S']} T={rec['T']}: closed ({rec['num_completions']} completions)")
        else:
            failed += 1
            total_obstructions += rec.get('num_obstructions', 0)
            print(f"  S={rec['S']} T={rec['T']}: {status}")

    print()
    print(f"Summary: {len(results) - failed}/{len(results)} closed, "
          f"{total_completions} total completions, {total_obstructions} obstructions.")

    if failed == 0 and total_obstructions == 0:
        print("AGREES with k4_local_miner.py + k4_audit.py.")
        sys.exit(0)
    else:
        print("DISAGREES with miner. Check obstructions and inconsistencies.")
        sys.exit(1)


if __name__ == '__main__':
    main()
