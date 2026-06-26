"""H5 HUB-BARRIER refutation search (the un-run experiment in ledger.next_action).

H5 claims: a 3-connected, uniformly-4-edge-connected M that decomposes as
(digon-forest F_D) + (balanced single arcs) with k(F_D) >= 2 components CANNOT
exist, because uniform-4-edge-connectivity forces a high-capacity-degree HUB
which forces F_D connected (k=1).

The PRIOR search (xu_reduction_check.py step B) was GRAVEYARDED (G8) as VACUOUS:
it hard-coded target single-degree = 4 - 2*digon_deg[v], i.e. capacity-degree
EXACTLY 4 at every vertex (M 4-regular). That regime EXCLUDES every genuine
3-connected 2-extremal member, whose hub has cap-degree 8/10/12. So '0 breakers'
there was construction-bias, not evidence.

THIS SCRIPT fixes the vacuity: it PERMITS hub vertices (single-degree allowed
ABOVE the deficit, so total capacity-degree may exceed 4), while still requiring:
  - F_D a disconnected forest (k(F_D) >= 2)   [the Step-1 break candidate]
  - M uniformly 4-edge-connected (all pairwise cap maxflow == 4)
  - underlying simple graph 3-connected
  - single edges admit a balanced (Eulerian) orientation
and tests is_2extremal on each balanced orientation.

A single is_2extremal=True witness with k(F_D)>=2 REFUTES H5 and reopens Step 1.
0 witnesses across the hub-permitting regime is POSITIVE structural evidence for
H5 (still empirical, not a proof; per discipline_gates.empirical_not_proof).

Output is a JSON summary on stdout.
"""
import os
import sys, json, itertools, signal, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import h2_oracle as H
import xu_reduction_check as X

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

_RESULTS = None


def run(nmin, nmax, max_single, hub_cap):
    """hub_cap = max allowed single-degree at any vertex (permits cap-degree up to
    2*digon_deg + hub_cap). max_single = max number of single edges in M.
    A vertex is a 'hub' if its capacity-degree exceeds 4."""
    global _RESULTS
    results = {
        'params': {'nmin': nmin, 'nmax': nmax, 'max_single': max_single,
                   'hub_cap': hub_cap},
        'examined_M': 0,
        'disconnected_FD_uniform4_3conn': 0,
        'with_hub': 0,
        'witness_2extremal': [],
        'examples': [],
        'by_n': {},
    }
    _RESULTS = results

    for n in range(nmin, nmax + 1):
        all_edges = [(i, j) for i in range(n) for j in range(i + 1, n)]
        cnt_examined = 0
        cnt_qual = 0
        cnt_hub = 0
        # disconnected digon forests (paths-style ok; general forest also ok).
        # Use general forests but we want DISCONNECTED (>=2 comps).
        for fd in X.gen_forests(n, all_edges):
            ncomp = X.fd_components(n, fd)
            if ncomp < 2:
                continue
            fd_set = set(fd)
            digon_deg = [0] * n
            for (u, v) in fd:
                digon_deg[u] += 1
                digon_deg[v] += 1
            remaining = [e for e in all_edges if e not in fd_set]
            # Each vertex needs total cap-degree >= 4 for uniform-4 to be possible:
            #   2*digon_deg[v] + single_deg[v] >= 4  => single_deg[v] >= 4-2*digon_deg[v].
            # We PERMIT single_deg[v] to be ANY even value in
            #   [max(0, 4-2*digon_deg[v]) ... hub_cap], i.e. hubs allowed.
            # Enumerate single-edge subsets up to size max_single; filter by:
            #   single_deg even everywhere, cap-deg>=4 everywhere.
            L = len(remaining)
            for r in range(1, min(max_single, L) + 1):
                for singles in itertools.combinations(remaining, r):
                    sd = [0] * n
                    for (u, v) in singles:
                        sd[u] += 1
                        sd[v] += 1
                    ok = True
                    for v in range(n):
                        if sd[v] % 2 != 0:
                            ok = False
                            break
                        capdeg = 2 * digon_deg[v] + sd[v]
                        if capdeg < 4 or sd[v] > hub_cap:
                            ok = False
                            break
                    if not ok:
                        continue
                    simple = fd_set | set(singles)
                    if len(simple) < n:  # must span all vertices
                        # a vertex with no incident edge cannot be in a strong digraph
                        # (it would be isolated). Reject.
                        verts = set()
                        for (a, b) in simple:
                            verts.add(a); verts.add(b)
                        if len(verts) < n:
                            continue
                    cnt_examined += 1
                    results['examined_M'] += 1
                    if cnt_examined % 100000 == 0:
                        print(f"    [n={n}] examined={cnt_examined} qual={cnt_qual} "
                              f"hub={cnt_hub}", file=sys.stderr, flush=True)
                    cap = {}
                    for e in fd_set:
                        cap[e] = 2
                    for e in singles:
                        cap[e] = 1
                    vals = X.all_pairwise_cap(n, cap)
                    if vals != {4}:
                        continue
                    nc = X.node_connectivity_simple(n, simple)
                    if nc < 3:
                        continue
                    cnt_qual += 1
                    results['disconnected_FD_uniform4_3conn'] += 1
                    has_hub = any(2 * digon_deg[v] + sd[v] > 4 for v in range(n))
                    if has_hub:
                        cnt_hub += 1
                        results['with_hub'] += 1
                    is2e = False
                    chosen = None
                    for orient in X._all_balanced_orientations(n, list(singles)):
                        arcs = X.arcs_from_M(list(fd_set), orient)
                        if H.is_2extremal(n, arcs):
                            is2e = True
                            chosen = orient
                            break
                    rec = {
                        'n': n,
                        'fd': [list(e) for e in sorted(fd_set)],
                        'singles': [list(e) for e in sorted(singles)],
                        'ncomp_FD': ncomp,
                        'node_conn': nc,
                        'capdeg': [2 * digon_deg[v] + sd[v] for v in range(n)],
                        'has_hub': has_hub,
                        'is_2extremal': is2e,
                    }
                    if chosen is not None:
                        rec['orientation'] = [list(a) for a in chosen]
                    if len(results['examples']) < 30:
                        results['examples'].append(rec)
                    if is2e:
                        results['witness_2extremal'].append(rec)
                        print(f"  *** WITNESS n={n} k(F_D)={ncomp} REFUTES H5 ***",
                              file=sys.stderr, flush=True)
        results['by_n'][n] = {'examined': cnt_examined,
                              'qualifying': cnt_qual, 'with_hub': cnt_hub}
        print(f"  n={n}: examined={cnt_examined} disc_FD_uniform4_3conn={cnt_qual} "
              f"with_hub={cnt_hub} witnesses={len(results['witness_2extremal'])}",
              file=sys.stderr, flush=True)
    return results


if __name__ == '__main__':
    import os
    nmin = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    nmax = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    max_single = int(sys.argv[3]) if len(sys.argv) > 3 else 9
    hub_cap = int(sys.argv[4]) if len(sys.argv) > 4 else 8
    tlimit = int(sys.argv[5]) if len(sys.argv) > 5 else 840

    def handler(signum, frame):
        if _RESULTS is not None:
            r = dict(_RESULTS)
            r['TIMEOUT'] = True
            print(json.dumps(r, indent=2))
        os._exit(0)

    signal.signal(signal.SIGALRM, handler)
    signal.alarm(tlimit)
    t0 = time.time()
    res = run(nmin, nmax, max_single, hub_cap)
    res['elapsed_sec'] = round(time.time() - t0, 1)
    print(json.dumps(res, indent=2))
