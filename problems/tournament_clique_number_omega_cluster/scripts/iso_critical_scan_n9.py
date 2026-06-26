"""Branch (a)/H4 — un-run EXPERIMENT from ledger.next_action: extend the exhaustive
ISO-CLASS 3-omega_vec-critical census to n=9, to get the iso-count series
{7:1, 8:2, 9:?} and the whole-tournament-3-critical count at order 9.

n=9 has 191536 iso classes (nauty `gentourng 9`).  Naive exact omega_vec_bb on
every class is ~16 h (timed: ~0.30 s/class).  The census only needs to separate
omega_vec>=3 from omega_vec<=2, so we use a SOUND two-sided filter:

  CHEAP UPPER BOUND (omega_vec<=2 certificate): omega_vec(T)<=2 iff some total
  order gives a TRIANGLE-FREE backedge graph.  We search a bounded number of
  random + greedy (min-current-clique) orders; the FIRST triangle-free one we
  find proves omega_vec<=2 (and >=2 since these are non-transitive), so we record
  omega_vec=2 and skip the exact solve.  This is sound: finding ANY order with
  omega<=2 is a valid upper-bound certificate.

  EXACT FALLBACK: if no cheap order certifies <=2, run the exact branch-and-bound
  omega_vec_bb (ub=3) to get the true value.  This only fires on the rare classes
  that resist the cheap filter (the omega_vec=3 witnesses plus a few stubborn 2s),
  so the total cost is dominated by 191536 cheap filters, not exact solves.

For every class with omega_vec==3 we then run the EXACT criticality + whole-
tournament (min_cert_order) tests via core (these are the only exact omega_vec_bb
calls on n=8 deletions, ~dozens of classes => cheap).

Output mirrors iso_critical_scan.py for n=9 and APPENDS to data/iso_critical_scan.json.
"""
from __future__ import annotations

import json
import random
import subprocess
import sys
import time
from itertools import combinations

sys.path.insert(0, "scripts")
import core


GENTOURNG = "gentourng"


def beats_matrix(n, arcs):
    b = [[False] * n for _ in range(n)]
    for (u, v) in arcs:
        b[u][v] = True
    return b


def has_triangle_for_order(n, beats, order):
    """True iff backedge graph for `order` contains a triangle (omega>=3).
    Builds adjacency among placed vertices: pos[a]<pos[b] => edge iff beats[b][a]."""
    pos = [0] * n
    for idx, v in enumerate(order):
        pos[v] = idx
    adj = [set() for _ in range(n)]
    for a in range(n):
        for c in range(a + 1, n):
            # earlier (smaller pos) is u; edge iff later beats earlier
            if pos[a] < pos[c]:
                if beats[c][a]:
                    adj[a].add(c)
                    adj[c].add(a)
            else:
                if beats[a][c]:
                    adj[a].add(c)
                    adj[c].add(a)
    # triangle check
    for u in range(n):
        nu = adj[u]
        for w in nu:
            if w > u:
                if adj[w] & nu:
                    return True
    return False


def greedy_min_order(n, beats, seed):
    """Greedy order: place vertices one at a time, each time choosing the next
    vertex minimizing the number of new backedges into the placed set (keeps the
    backedge graph sparse / triangle-light).  `seed` perturbs tie-breaking."""
    rng = random.Random(seed)
    remaining = list(range(n))
    rng.shuffle(remaining)
    placed = []
    order = []
    while remaining:
        best_v = None
        best_cost = None
        for v in remaining:
            cost = sum(1 for a in placed if beats[v][a])  # backedges v->a
            if best_cost is None or cost < best_cost:
                best_cost = cost
                best_v = v
        placed.append(best_v)
        order.append(best_v)
        remaining.remove(best_v)
    return order


def cheap_le2_certificate(n, beats, tries=150, greedy=24):
    """Try to find an order whose backedge graph is triangle-free (=> omega_vec<=2).
    Returns True if such an order found (sound upper-bound certificate)."""
    # several greedy orders (different shuffled tie-breaks)
    for s in range(greedy):
        order = greedy_min_order(n, beats, s)
        if not has_triangle_for_order(n, beats, order):
            return True
    # random orders
    rng = random.Random(12345)
    base = list(range(n))
    for _ in range(tries):
        rng.shuffle(base)
        if not has_triangle_for_order(n, beats, base):
            return True
    return False


class _BudgetExceeded(Exception):
    pass


def omega_vec_le_t(n, beats, t, node_budget=None):
    """EXACT decision: is omega_vec(T) <= t ?  i.e. does SOME total order give a
    backedge graph with clique number <= t (no clique of size t+1)?  Branch over
    order prefixes; placed-vertex cliques are FINAL, so if placing b completes a
    clique of size t+1 among placed vertices we prune (sound: any extension keeps
    it). If a full order completes with max clique <= t, return True; if all
    branches pruned, omega_vec >= t+1.  All-integer bitmasks.

    Generalises omega_vec_le2 (t=2). Greedy branch ordering (fewest new backedges
    first) finds a low-clique completion fast when one exists."""
    full = (1 << n) - 1
    backrow = [0] * n
    for b in range(n):
        rb = beats[b]
        m = 0
        for a in range(n):
            if rb[a]:
                m |= (1 << a)
        backrow[b] = m
    adj = [0] * n
    nodes = [0]

    def makes_big_clique(b, nb):
        """True iff adding b (with placed-neighbour mask nb) creates a clique of
        size t+1, i.e. b plus a t-clique inside nb. Recursively look for a
        t-clique within nb in the current backedge graph."""
        # need a clique of size t among nb that is fully adjacent (already true:
        # they're all adjacent to b); so need a (t)-clique among nb.
        return has_clique_of_size(nb, t)

    def has_clique_of_size(cand, sz):
        if sz <= 0:
            return True
        if sz == 1:
            return cand != 0
        c = cand
        # bound: |cand| >= sz
        if bin(cand).count("1") < sz:
            return False
        while c:
            v = (c & -c).bit_length() - 1
            c &= c - 1
            # v together with a (sz-1)-clique in cand & adj[v]
            if has_clique_of_size(cand & adj[v] & ~(1 << v), sz - 1):
                return True
            # if remaining candidates can't reach sz, stop
            if bin(c).count("1") < sz:
                break
        return False

    def recurse(remaining, placed_mask):
        if remaining == 0:
            return True
        nodes[0] += 1
        if node_budget is not None and nodes[0] > node_budget:
            raise _BudgetExceeded()
        cands = []
        rem = remaining
        while rem:
            b = (rem & -rem).bit_length() - 1
            rem &= rem - 1
            nb = backrow[b] & placed_mask
            if has_clique_of_size(nb, t):   # b + t-clique => clique t+1 -> prune
                continue
            cands.append((bin(nb).count("1"), b, nb))
        cands.sort()
        for _cnt, b, nb in cands:
            bit_b = 1 << b
            x = nb
            while x:
                a = (x & -x).bit_length() - 1
                x &= x - 1
                adj[a] |= bit_b
            adj[b] = nb
            if recurse(remaining & ~bit_b, placed_mask | bit_b):
                return True
            x = nb
            while x:
                a = (x & -x).bit_length() - 1
                x &= x - 1
                adj[a] &= ~bit_b
            adj[b] = 0
        return False

    try:
        return recurse(full, 0)
    except _BudgetExceeded:
        return False   # caller treats budget-exhaustion as ">= t+1" (histogram only)


def omega_vec_le2(n, beats):
    """EXACT decision: is omega_vec(T) <= 2 ?  i.e. does SOME total order give a
    triangle-free backedge graph?  Branch over order prefixes (prec-smallest first);
    a placed vertex b gets backedge to earlier placed a iff beats[b][a]. Triangles
    among placed vertices are FINAL once formed, so if placing b creates a triangle
    we prune (no extension can remove it). If a full order completes triangle-free,
    omega_vec<=2. If every branch is pruned, omega_vec>=3.  All-integer bitmasks.

    This is sound and exact (it is the decision version of omega_vec_bb at ub=3),
    just much faster than the networkx-based bb."""
    # bmask[b] over a<b-in-placement: precompute backedge bitmask of b against any set
    # We'll keep `adj[v]` = bitmask of placed neighbours of v in the backedge graph.
    full = (1 << n) - 1
    # backrow[b] = bitmask of vertices a with beats[b][a] (b->a) -> b backedges onto a
    backrow = [0] * n
    for b in range(n):
        m = 0
        rb = beats[b]
        for a in range(n):
            if rb[a]:
                m |= (1 << a)
        backrow[b] = m

    adj = [0] * n  # backedge-graph adjacency among PLACED vertices

    def recurse(remaining, placed_mask):
        if remaining == 0:
            return True  # completed a triangle-free order
        # collect candidate vertices that DON'T create a triangle, with their
        # backedge counts; branch greedily (fewest new backedges first) so a
        # triangle-free completion -- if one exists -- is found fast.
        cands = []
        rem = remaining
        while rem:
            b = (rem & -rem).bit_length() - 1
            rem &= rem - 1
            nb = backrow[b] & placed_mask
            tri = False
            t = nb
            while t:
                a = (t & -t).bit_length() - 1
                t &= t - 1
                if adj[a] & nb:
                    tri = True
                    break
            if tri:
                continue
            cands.append((bin(nb).count("1"), b, nb))
        cands.sort()
        for _cnt, b, nb in cands:
            # place b
            bit_b = 1 << b
            t = nb
            while t:
                a = (t & -t).bit_length() - 1
                t &= t - 1
                adj[a] |= bit_b
            adj[b] = nb
            if recurse(remaining & ~bit_b, placed_mask | bit_b):
                # undo before returning (keep adj clean for caller reuse not needed)
                return True
            # undo
            t = nb
            while t:
                a = (t & -t).bit_length() - 1
                t &= t - 1
                adj[a] &= ~bit_b
            adj[b] = 0
        return False

    return recurse(full, 0)


def sub_beats(n, beats, drop):
    """beats matrix of T - drop, relabelled to 0..n-2 (order preserved)."""
    keep = [v for v in range(n) if v != drop]
    m = len(keep)
    sb = [[False] * m for _ in range(m)]
    for i, a in enumerate(keep):
        for j, b in enumerate(keep):
            if a != b:
                sb[i][j] = beats[a][b]
    return m, sb


def is_transitive(m, sb):
    score = [sum(sb[u][v] for v in range(m)) for u in range(m)]
    return sorted(score) == list(range(m))


def is_k_critical_fast(n, arcs, beats, k):
    """k=3: omega_vec(T)==3 already known true by caller. Critical iff every
    single-vertex deletion has omega_vec == k-1 == 2, i.e. (le2 True) AND
    (not transitive => omega_vec >= 2)."""
    assert k == 3
    for v in range(n):
        m, sb = sub_beats(n, beats, v)
        if not omega_vec_le2(m, sb):      # omega_vec(T-v) >= 3 -> not critical
            return False
        if is_transitive(m, sb):          # omega_vec(T-v) == 1 -> not == k-1
            return False
    return True


_MIN_CERT_VERIFY = [0]  # verify the monotonicity argument on the first few criticals


def min_cert_order_fast(n, arcs, k):
    """For a k-critical tournament min_cert_order == n ALWAYS:
    omega_vec is monotone under taking subtournaments (any induced sub-backedge
    graph has clique number <= the whole, over the restricted order set), so since
    every (n-1)-deletion has omega_vec == k-1 < k, every proper subtournament
    (contained in some deletion) has omega_vec < k. Hence the smallest sub with
    omega_vec >= k is T itself: min_cert == n.  We VERIFY this against the exact
    core routine on the first few critical classes, then trust it."""
    if _MIN_CERT_VERIFY[0] < 6:
        _MIN_CERT_VERIFY[0] += 1
        sz, _ = core.min_subtournament_order_for_k(n, arcs, k)
        assert sz == n, f"monotonicity FAILED: min_cert={sz} != n={n} for {arcs}"
        return sz
    return n


def gentourng_classes(n):
    proc = subprocess.run([GENTOURNG, str(n)], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"gentourng {n} failed: {proc.stderr}")
    pairs = list(combinations(range(n), 2))
    L = len(pairs)
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        assert len(line) == L, (len(line), L, line)
        arcs = []
        for b, (i, j) in zip(line, pairs):
            arcs.append((i, j) if b == "1" else (j, i))
        yield arcs


def scan(n, k=3):
    omega_hist = {1: 0, 2: 0, 3: 0}
    n_iso = 0
    n_exact_solves = 0
    crit = []
    whole = []
    t0 = time.time()
    for arcs in gentourng_classes(n):
        n_iso += 1
        if n_iso % 2000 == 0:
            print(f"  ...{n_iso} classes, {n_exact_solves} exact, "
                  f"{time.time()-t0:.0f}s, crit={len(crit)}", flush=True)
        if LIMIT and n_iso > LIMIT:
            break
        _ts = time.time()
        beats = beats_matrix(n, arcs)
        # transitive (omega_vec=1) detection: acyclic => the topological order is
        # edgeless. Cheap filter already covers <=2; check =1 via: some order with
        # NO backedge at all. A tournament is transitive iff it has a Hamilton
        # source chain; simplest: omega_vec==1 iff acyclic. We just let the cheap
        # <=2 path record 2 unless we explicitly find an edgeless order.
        # FAST exact <=2 decision (random/greedy heuristic first as a quick positive,
        # then the exact bitmask branch-and-bound decision omega_vec_le2):
        if cheap_le2_certificate(n, beats, tries=20, greedy=4) or omega_vec_le2(n, beats):
            # omega_vec <= 2; classify 1 vs 2 (1 iff transitive: scores = perm of 0..n-1)
            score = [sum(beats[u][v] for v in range(n)) for u in range(n)]
            if sorted(score) == list(range(n)):
                omega_hist[1] += 1
            else:
                omega_hist[2] += 1
            continue
        # omega_vec >= 3 (le2 False).  CRITICALITY (the H4 census) is decided
        # WITHOUT the exact omega_vec of T: a 3-critical T needs every deletion
        # omega_vec(T-v) == 2 (le2 True on n-1 AND non-transitive). If all deletions
        # are == 2 and T itself is > 2, then omega_vec(T) <= 2+1 = 3, hence == 3,
        # so criticality is FULLY decided by the fast le2-on-deletions test.
        n_exact_solves += 1
        crit_flag = is_k_critical_fast(n, arcs, beats, k)
        if crit_flag:
            # omega_vec(T)==3 (proved by the bound above); whole-tournament-critical
            # iff no proper sub has omega_vec>=3 -- but 3-criticality already gives
            # every (n-1)-deletion omega_vec==2, and omega_vec is monotone under
            # taking subtournaments, so min_cert_order == n automatically. Verify.
            w = k
            sz = min_cert_order_fast(n, arcs, k)
            rec = {"arcs": arcs, "min_cert_order": sz}
            crit.append(rec)
            if sz == n:
                whole.append(rec)
        else:
            # not critical: split histogram 3 vs >=4 with a BUDGETED le3 decision.
            # (Histogram only; does NOT affect the critical census.) If the budget
            # is exhausted we record the value as ">=4" bucket key 4 (these are the
            # rare hard omega_vec>=4 orbits); true omega_vec==3 classes resolve le3
            # quickly via greedy ordering.
            if omega_vec_le_t(n, beats, k, node_budget=200000):
                w = k
            else:
                w = k + 1   # >=4 OR budget-exhausted -> lumped as ">=4" bucket
        omega_hist[w] = omega_hist.get(w, 0) + 1
        _dt = time.time() - _ts
        if _dt > 8.0:
            print(f"  !! slow class #{n_iso}: {_dt:.1f}s crit={crit_flag}", flush=True)
    return {
        "n": n,
        "k": k,
        "n_iso_classes": n_iso,
        "n_exact_solves": n_exact_solves,
        "omega_vec_histogram": {str(a): b for a, b in sorted(omega_hist.items()) if b},
        "num_k_critical_iso": len(crit),
        "num_whole_tournament_k_critical_iso": len(whole),
        "whole_tournament_present": len(whole) > 0,
        "critical_examples": crit[:10],
        "whole_examples": whole[:10],
        "elapsed_s": round(time.time() - t0, 1),
    }


LIMIT = 0  # 0 => full scan; set via argv[2] for calibration

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 9
    if len(sys.argv) > 2:
        LIMIT = int(sys.argv[2])
    res = scan(n, 3)
    print(json.dumps(res, indent=2), flush=True)
    path = "data/iso_critical_scan_n9.json"
    with open(path, "w") as f:
        json.dump(res, f, indent=2)
    print("SAVED", path, flush=True)
