"""!!! INVALID / SUPERSEDED (2026-06-12): this script passed build_ac_c3()'s 3rd
return value (=3, the inner C3 size) as the lattice order instead of n=21, so the
feasibility lattice and profile indexing are wrong. Its output is meaningless.
H19 for AC_7[C3] was settled INSTEAD by direct no-K6 SAT (omega_vec(C3[AC_7[C3]])=5,
H19 HOLDS); see docs/h19_cancellation_argument_sketch.md §13. Kept only for history.
!!!"""
"""Does C3[AC_7[C3]] admit a FEASIBLE (terminal-reachable) inner-order triple?

route2_append_partners only searched for CYCLE-FREE (no-deadlock) triples and found
none for AC_7[C3].  But H19 only needs the WEAKER condition: some monotone lattice path
reaches (m,m,m) through safe states (terminal_reachable), tolerating dead-ends that the
path avoids.  This probe tests exactly that, over a bounded but diverse set of optimal
orders of AC_7[C3] (the proved d_then_c append order + adjacent-swap append-escapers).

A feasible triple => omega_vec(C3[AC_7[C3]]) <= k+1 = 5 (H19 holds for this H), via H25.
Pure combinatorics on profiles; foreground.
"""
import sys, os, time, itertools
from collections import deque
sys.path.insert(0, os.path.dirname(__file__))
import core
from confirm_deletion_template_k4 import build as build_ac_c3, order_template as ac_c3_deletion_order
from h25_path_feasibility import omega_be_seq, profile_of
from route2_credit_deadlock import analyse_triple, demand_relief_map

def dsig(profile, m, k):
    dm = demand_relief_map(profile, m, k)
    return tuple(dm[t]["successor_level"] for t in sorted(dm))

def collect_profiles(max_states=8000, max_depth=6, cap_profiles=24):
    n, arcs, m = build_ac_c3(7)            # AC_7[C3], n=m=21
    k = 4
    beats = core.beats_matrix(n, arcs)
    base = tuple(ac_c3_deletion_order(m, deleted=0))
    queue = deque([(base, 0)]); seen = {base}
    profiles = {}                          # full (f,g) -> (order, demand_sig)
    while queue and len(seen) <= max_states and len(profiles) < cap_profiles:
        tau, depth = queue.popleft()
        if omega_be_seq(beats, list(tau)) != k - 1:
            continue
        sigma = list(tau) + [0]
        prof = profile_of(beats, tuple(sigma))
        if prof[0][n] == k and prof not in profiles:         # optimal append-escaper
            profiles[prof] = (sigma, dsig(prof, n, k))
        if depth < max_depth:
            for i in range(len(tau) - 1):
                nb = list(tau); nb[i], nb[i+1] = nb[i+1], nb[i]; nb = tuple(nb)
                if nb not in seen:
                    seen.add(nb); queue.append((nb, depth + 1))
    return n, arcs, k, list(profiles.keys()), [v for v in profiles.values()]

def main():
    t0 = time.time()
    n, arcs, k, profs, meta = collect_profiles()
    m = n
    print(f"AC_7[C3] (order {n}, k={k}): collected {len(profs)} distinct optimal "
          f"append-escaper profiles  [{time.time()-t0:.1f}s]", flush=True)
    sigs = sorted({tuple(d) for (_, d) in meta})
    print(f"  distinct demand-maps among them: {sigs}", flush=True)

    # test ALL ordered triples for FEASIBILITY (terminal reachable), allowing dead-ends.
    feasible = None; n_feas = 0; n_nodl = 0; tested = 0
    for trip in itertools.product(range(len(profs)), repeat=3):
        tested += 1
        r = analyse_triple([profs[trip[0]], profs[trip[1]], profs[trip[2]]], m, k,
                           record_deadlocks=False)
        if r["terminal_reachable"]:
            n_feas += 1
            if feasible is None:
                feasible = (trip, r)
        if r["feasible_no_deadlock"]:
            n_nodl += 1
    print(f"\ntested {tested} ordered triples:", flush=True)
    print(f"  FEASIBLE (terminal reachable, dead-ends allowed): {n_feas}", flush=True)
    print(f"  cycle-free (no dead-end):                         {n_nodl}", flush=True)
    if feasible:
        trip, r = feasible
        print(f"\n  *** FEASIBLE TRIPLE FOUND -> omega_vec(C3[AC_7[C3]]) <= {k+1} (H19 holds for AC_7[C3])", flush=True)
        print(f"      demand-maps: {[meta[i][1] for i in trip]}", flush=True)
        print(f"      lattice: safe={r['n_safe']} reach={r['n_reachable']} "
              f"terminal={r['terminal_reachable']} dead_ends={r['n_dead_ends']}", flush=True)
    else:
        print(f"\n  NO feasible triple among these {len(profs)} append-escaper profiles "
              f"(BOUNDED: escaper-only, local swap neighborhood). Inconclusive for H19.", flush=True)
    print(f"\nelapsed {time.time()-t0:.1f}s", flush=True)

if __name__ == "__main__":
    main()
