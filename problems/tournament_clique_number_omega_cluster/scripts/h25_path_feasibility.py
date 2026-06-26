"""H25 LATTICE-PATH REACHABILITY checker for the C3-outer VALUE leg.

By the VERIFIED H25 split-sum identity (ground_twocopy_identity.py):
  omega(C3[H]^prec) = max over the 3 cyclic copy-pairs (Y,X) in {(1,0),(2,1),(0,2)}
      of  max_p [ omega_be(Y-prefix before split p) + omega_be(X-suffix from p) ]
and every backedge clique meets at most 2 of the 3 copies.

KEY OBSERVATION (the reduction this script tests):
  Fix, for each copy c, the relative inner order sigma_c of that copy (a permutation
  of H's vertices).  Define the PREFIX backedge-clique STEP PROFILE
      f_c(a) = omega_be( first a elements of sigma_c )        (a = 0..nH)
  and the SUFFIX profile
      g_c(b) = omega_be( last b elements of sigma_c )         (b = 0..nH).
  The global interleave is recorded by the monotone lattice path
  (n_0(p), n_1(p), n_2(p)) from (0,0,0) to (nH,nH,nH): n_c(p) = #copy-c elements
  strictly before global split p.

  For a cyclic pair (Y,X), the split-sum at p uses exactly
      omega_be(Y-prefix before p) = f_Y( n_Y(p) )
      omega_be(X-suffix from p)   = g_X( nH - n_X(p) )
  so the whole identity depends on the inner orders ONLY through the profiles
  (f_c, g_c) and on the interleave ONLY through the lattice path.

  omega(C3[H]^prec) <= bound  iff  the lattice path AVOIDS, for all 3 pairs (Y,X),
  the bad set  B_{YX} = { (a, c) : f_Y(a) + g_X(nH - c) >= bound+1 }
  where a = n_Y(p), c = n_X(p) at every split p.  Because the path is monotone
  and passes through every intermediate lattice point as p sweeps 0..n, the
  feasibility question is EXACTLY a monotone-grid reachability problem in
  {0..nH}^3 with the 3 pairwise (Y,X) coordinate constraints.

This script:
  (i)  enumerates the set P(H) of distinct OPTIMAL-inner profile pairs (f,g)
       (inner orders with omega(H^sigma) = ov(H) = k), via DFS with prefix-clique
       pruning;
  (ii) for a chosen ordered profile triple, runs BFS monotone-grid reachability;
  (iii) reports per H: feasible? at bound, MIN number of distinct profiles needed
       (1 shared, else 2, else 3), and a staggering invariant.

CONTROLS (--mode controls): H25 formula==direct spot-check (orientation guard);
  an ov=2 inner H7 with omega_vec(C3[H7])=4 must be path-INFEASIBLE at bound 3;
  the G59 gold C3[QR_19] optimal-inner clique-5 order must be path-FEASIBLE at 5.

CENSUS (--mode census): exhaustive gentourng orders 7,8 filtered to ov=3, plus a
  sampled slice of order-9, each tested for a feasible optimal-inner triple at the
  given bound (default 4 = k+1 for k=3).
"""
import sys, os, json, time, subprocess, itertools, random, argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
import core
import networkx as nx

C3_ARCS = [(0, 1), (1, 2), (2, 0)]                       # 0->1->2->0
CYCLIC_PAIRS = [(1, 0), (2, 1), (0, 2)]                  # (Y,X) with arc X->Y


# --------------------------------------------------------------------------- #
#  C3[H] product (matches ground_twocopy_identity.lex_c3)
# --------------------------------------------------------------------------- #
def lex_c3(nH, aH):
    bH = core.beats_matrix(nH, aH)
    bT = core.beats_matrix(3, C3_ARCS)
    arcs = [(a * nH + b, ap * nH + bp)
            for a in range(3) for b in range(nH)
            for ap in range(3) for bp in range(nH)
            if (a, b) != (ap, bp) and (bT[a][ap] or (a == ap and bH[b][bp]))]
    return 3 * nH, arcs


def copy_of(v, nH):
    return v // nH


# --------------------------------------------------------------------------- #
#  backedge clique of an ordered subsequence (positions = order)
# --------------------------------------------------------------------------- #
def omega_be_seq(beats, seq):
    m = len(seq)
    if m == 0:
        return 0
    g = nx.Graph(); g.add_nodes_from(range(m))
    for i in range(m):
        a = seq[i]
        for j in range(i + 1, m):
            b = seq[j]
            if beats[b][a]:
                g.add_edge(i, j)
    return max((len(c) for c in nx.find_cliques(g)), default=1)


# --------------------------------------------------------------------------- #
#  H25 direct split-sum formula (re-implemented, used as the orientation guard)
# --------------------------------------------------------------------------- #
def split_sum_formula(n, beats, order, nH):
    best = 0
    pos_index = {v: i for i, v in enumerate(order)}
    for (Y, X) in CYCLIC_PAIRS:
        Ypos = [v for v in order if copy_of(v, nH) == Y]
        Xpos = [v for v in order if copy_of(v, nH) == X]
        for p in range(n + 1):
            left = [v for v in Ypos if pos_index[v] < p]
            right = [v for v in Xpos if pos_index[v] >= p]
            wl = omega_be_seq(beats, left)
            wr = omega_be_seq(beats, right)
            if wl + wr > best:
                best = wl + wr
    return best


# --------------------------------------------------------------------------- #
#  Profile (f,g) for one inner order sigma (a permutation of H's vertices)
#  f(a) = omega_be(first a elements of sigma);  g(b) = omega_be(last b elements)
# --------------------------------------------------------------------------- #
def profile_of(beatsH, sigma):
    nH = len(sigma)
    f = [0] * (nH + 1)
    for a in range(1, nH + 1):
        f[a] = omega_be_seq(beatsH, list(sigma[:a]))
    g = [0] * (nH + 1)
    for b in range(1, nH + 1):
        g[b] = omega_be_seq(beatsH, list(sigma[nH - b:]))
    return tuple(f), tuple(g)


# --------------------------------------------------------------------------- #
#  Enumerate distinct OPTIMAL-inner profile pairs P(H)
#  Optimal = omega(H^sigma) == k.  DFS over orders, prune when prefix clique > k.
# --------------------------------------------------------------------------- #
def optimal_profiles(nH, aH, k, cap=None):
    """Return set of distinct (f,g) profile pairs over OPTIMAL inner orders sigma
    (full backedge clique == k).  cap: stop after collecting `cap` distinct pairs."""
    beatsH = core.beats_matrix(nH, aH)
    profiles = {}                 # (f,g) -> one witnessing sigma
    placed = []
    # incremental backedge graph among placed inner vertices
    adj = {}                      # v -> set of placed neighbours

    def cur_clique():
        g = nx.Graph(); g.add_nodes_from(placed)
        for v in placed:
            for u in adj[v]:
                g.add_edge(u, v)
        return max((len(c) for c in nx.find_cliques(g)), default=(0 if not placed else 1))

    def recurse(remaining):
        if cap is not None and len(profiles) >= cap:
            return
        if not remaining:
            sigma = tuple(placed)
            fg = profile_of(beatsH, sigma)
            # FIX (2026-06-12): enforce OPTIMAL full clique == k.  The prefix prune
            # below rejects any PROPER prefix with clique > k, but a full order can
            # first reach clique k+1 only on placing its LAST vertex (remaining empty),
            # reaching here unpruned.  Without this guard the function silently emits
            # width-(k+1) orders mislabeled as optimal.
            if fg[0][nH] == k and fg not in profiles:
                profiles[fg] = sigma
            return
        # prune: prefix clique already exceeds k => cannot be an optimal order
        if cur_clique() > k:
            return
        for b in list(remaining):
            nb = {a for a in placed if beatsH[b][a]}
            placed.append(b); adj[b] = nb
            for a in nb:
                adj[a].add(b)
            recurse(remaining - {b})
            placed.pop()
            for a in nb:
                adj[a].discard(b)
            del adj[b]

    recurse(frozenset(range(nH)))
    return profiles


# --------------------------------------------------------------------------- #
#  Monotone-grid reachability with the 3 cyclic-pair constraints.
#
#  Profiles assigned per copy: prof[c] = (f_c, g_c).  Bad sets per pair (Y,X):
#     a lattice point (n0,n1,n2) is BAD if for some pair (Y,X),
#       f_{prof[Y]}(n_Y) + g_{prof[X]}(nH - n_X) >= bound+1.
#  A path from (0,0,0) to (nH,nH,nH) takes unit steps in one coordinate.
#  Feasible iff there is a monotone path through only NON-bad points.
#  (Endpoints (0,..) and (..,nH) are forced; f(0)=g(0)=0 so corners are fine
#   unless ov already > bound, which never happens since bound>=k.)
# --------------------------------------------------------------------------- #
def point_ok(pt, nH, fY, gY, fX_by, bound):
    pass  # placeholder, real check inline below


def reachable(nH, profY, bound):
    """profY: list [prof0, prof1, prof2] each = (f,g).  Returns (feasible, stagger)
    where stagger = max over reachable points of the number of cyclic pairs that
    are 'tight' (split-sum == bound) at that point -- the staggering invariant the
    symbolic counting proof must bound."""
    f = [profY[c][0] for c in range(3)]
    g = [profY[c][1] for c in range(3)]

    def bad(n0, n1, n2):
        nc = (n0, n1, n2)
        for (Y, X) in CYCLIC_PAIRS:
            if f[Y][nc[Y]] + g[X][nH - nc[X]] >= bound + 1:
                return True
        return False

    def tightcount(n0, n1, n2):
        nc = (n0, n1, n2); t = 0
        for (Y, X) in CYCLIC_PAIRS:
            if f[Y][nc[Y]] + g[X][nH - nc[X]] == bound:
                t += 1
        return t

    if bad(0, 0, 0):
        return False, 0
    # BFS/DP over the grid; reachable[pt] true if a clean monotone path reaches pt
    from collections import deque
    seen = set([(0, 0, 0)])
    dq = deque([(0, 0, 0)])
    max_tight = tightcount(0, 0, 0)
    target = (nH, nH, nH)
    while dq:
        (a, b, c) = dq.popleft()
        for (da, db, dc) in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
            na, nb, nc = a + da, b + db, c + dc
            if na > nH or nb > nH or nc > nH:
                continue
            if (na, nb, nc) in seen:
                continue
            if bad(na, nb, nc):
                continue
            seen.add((na, nb, nc))
            tc = tightcount(na, nb, nc)
            if tc > max_tight:
                max_tight = tc
            dq.append((na, nb, nc))
    return (target in seen), max_tight


# --------------------------------------------------------------------------- #
#  Per-H feasibility: try shared single profile, then pairs, then triples.
#  Returns dict with feasible?, min_distinct, stagger.
# --------------------------------------------------------------------------- #
def feasible_H(nH, aH, k, bound, profile_cap=400):
    profs = optimal_profiles(nH, aH, k, cap=profile_cap)
    P = list(profs.keys())
    truncated = (len(P) >= profile_cap)
    # 1 distinct (all copies share one profile)
    for p in P:
        ok, stag = reachable(nH, [p, p, p], bound)
        if ok:
            return {"feasible": True, "min_distinct": 1, "stagger": stag,
                    "n_profiles": len(P), "profiles_truncated": truncated}
    # 2 distinct: assign 2 distinct profiles to the 3 copies (one repeated).
    # Try all ordered placements using exactly 2 of the profiles.
    best_stag = None
    for p, q in itertools.permutations(P, 2):
        for assign in [(p, p, q), (p, q, p), (q, p, p)]:
            ok, stag = reachable(nH, list(assign), bound)
            if ok:
                return {"feasible": True, "min_distinct": 2, "stagger": stag,
                        "n_profiles": len(P), "profiles_truncated": truncated}
    # 3 distinct
    for trip in itertools.permutations(P, 3):
        ok, stag = reachable(nH, list(trip), bound)
        if ok:
            return {"feasible": True, "min_distinct": 3, "stagger": stag,
                    "n_profiles": len(P), "profiles_truncated": truncated}
    return {"feasible": False, "min_distinct": None, "stagger": None,
            "n_profiles": len(P), "profiles_truncated": truncated}


# --------------------------------------------------------------------------- #
#  Controls
# --------------------------------------------------------------------------- #
def mode_controls():
    print("=== H25 PATH-FEASIBILITY CONTROLS ===", flush=True)
    rng = random.Random(7)

    # (A) orientation guard: formula==direct on random small C3[H] orders
    print("[A] H25 formula==direct orientation guard ...", flush=True)
    mism = 0; checked = 0
    for _ in range(5):
        nH = rng.choice([4, 5, 6])
        aH = []
        for i in range(nH):
            for j in range(i + 1, nH):
                aH.append((i, j) if rng.random() < 0.5 else (j, i))
        n, arcs = lex_c3(nH, aH)
        beats = core.beats_matrix(n, arcs)
        for _ in range(40):
            order = list(range(n)); rng.shuffle(order)
            direct = core.omega_of_order(n, arcs, order)
            formula = split_sum_formula(n, beats, order, nH)
            checked += 1
            if direct != formula:
                mism += 1
    print(f"    orientation guard: {checked} orders, {mism} mismatches "
          f"({'OK' if mism == 0 else 'FAIL'})", flush=True)

    # (B) NEGATIVE control: an inner H7 with ov=2 and omega_vec(C3[H7])=4.
    #     Such an H7 exists (H16 counterexample family). Find one, verify
    #     omega_vec(C3[H7])=4>3, and assert path-INFEASIBLE at bound 3.
    print("[B] negative control: ov=2 inner H7, omega_vec(C3[H7])=4 => "
          "INFEASIBLE at bound 3 ...", flush=True)
    h7 = None
    ovC3_known = None
    # H16 counterexample stored? (H7 nested under d['H7']['arcs'];
    # exact omega_vec(C3[H7]) stored under d['C3_of_H7']['exact_omega_vec'])
    try:
        cert = json.load(open('data/h16_counterexample.json'))
        if isinstance(cert, dict) and 'H7' in cert and 'arcs' in cert['H7']:
            h7 = (7, [tuple(a) for a in cert['H7']['arcs']])
            ovC3_known = cert.get('C3_of_H7', {}).get('exact_omega_vec')
    except Exception as e:
        print("    (no h16_counterexample.json usable:", e, ")", flush=True)
    if h7 is None:
        # search a random ov=2 H7 whose C3[H7] has omega_vec 4
        print("    searching a random ov=2 H7 with omega_vec(C3[H7])=4 ...", flush=True)
        found = False
        for _ in range(2000):
            nH = 7
            aH = []
            for i in range(nH):
                for j in range(i + 1, nH):
                    aH.append((i, j) if rng.random() < 0.5 else (j, i))
            if core.omega_vec(nH, aH) != 2:
                continue
            n, arcs = lex_c3(nH, aH)
            if core.omega_vec(n, arcs, method='bb') == 4:
                h7 = (nH, aH); found = True; break
        if not found:
            print("    COULD NOT FIND negative-control H7 (control inconclusive)", flush=True)
    negative_ok = None
    if h7 is not None:
        nH, aH = h7
        ovH = core.omega_vec(nH, aH)
        n, arcs = lex_c3(nH, aH)
        # omega_vec(C3[H7]) on order 21: use the stored EXACT value if present
        # (recomputing via bb on order 21 is slow); else compute.
        ovC3 = ovC3_known if ovC3_known is not None else core.omega_vec(n, arcs, method='bb')
        # path feasibility uses OPTIMAL inner orders at k=ovH; check INFEASIBLE at bound 3
        res = feasible_H(nH, aH, ovH, bound=3)
        print(f"    H7 ov={ovH}, omega_vec(C3[H7])={ovC3}, "
              f"path-feasible@bound3={res['feasible']} (expect infeasible)", flush=True)
        # The checker is sound only if it does NOT claim feasible@3 when the true
        # value is 4. (Optimal-inner restriction at k=2.)
        negative_ok = (ovC3 == 4 and res['feasible'] is False)
        print(f"    negative control {'OK' if negative_ok else 'FAIL/INCONCLUSIVE'}", flush=True)

    # (C) POSITIVE control: G59 gold C3[QR_19] optimal-inner clique-5 order.
    #     Reconstruct the per-copy inner orders from the gold witness, build the
    #     profile triple, and assert path-FEASIBLE at bound 5.
    print("[C] positive control: G59 gold C3[QR_19] optimal-inner clique-5 order "
          "=> FEASIBLE at bound 5 ...", flush=True)
    gold = json.load(open('data/ground_h21_skeleton_sat.json'))
    qr = gold['QR']
    nH = 19
    aH = [(i, (i + d) % 19) for i in range(19) for d in qr]
    assert core.is_tournament(19, aH)
    beatsH = core.beats_matrix(nH, aH)
    n, arcs = lex_c3(nH, aH)
    wo = gold['witness_order']
    beats = core.beats_matrix(n, arcs)
    direct = core.omega_of_order(n, arcs, wo)
    formula = split_sum_formula(n, beats, wo, nH)
    print(f"    gold order: direct={direct} formula={formula} "
          f"(both expect 5)", flush=True)
    # extract per-copy inner orders (relative order of each copy in wo) and their profiles
    inner_seq = {0: [], 1: [], 2: []}
    for v in wo:
        c = copy_of(v, nH)
        inner_seq[c].append(v % nH)          # inner label
    profs = []
    inner_clq = []
    for c in range(3):
        sigma = inner_seq[c]
        fg = profile_of(beatsH, sigma)
        profs.append(fg)
        inner_clq.append(omega_be_seq(beatsH, sigma))
    print(f"    inner cliques per copy (from gold) = {inner_clq} (expect [4,4,4])", flush=True)
    # build the lattice path from wo directly and verify NO bad point at bound 5
    # then confirm reachable() with these exact profiles returns feasible.
    ok5, stag5 = reachable(nH, profs, bound=5)
    print(f"    gold profile triple path-feasible@bound5={ok5} stagger={stag5} "
          f"(expect True)", flush=True)
    positive_ok = (direct == 5 and formula == 5 and inner_clq == [4, 4, 4] and ok5)
    print(f"    positive control {'OK' if positive_ok else 'FAIL'}", flush=True)

    print("=== CONTROLS SUMMARY ===", flush=True)
    print(f"    orientation_guard_ok = {mism == 0}", flush=True)
    print(f"    negative_control_ok  = {negative_ok}", flush=True)
    print(f"    positive_control_ok  = {positive_ok}", flush=True)
    allok = (mism == 0) and (negative_ok is True) and positive_ok
    print(f"CONTROLS_ALL_OK: {allok}", flush=True)


# --------------------------------------------------------------------------- #
#  gentourng iso-class enumeration
# --------------------------------------------------------------------------- #
def gentourng_classes(n):
    out = subprocess.run(['gentourng', str(n)], capture_output=True, text=True, timeout=600)
    if out.returncode != 0:
        raise RuntimeError("gentourng failed: " + out.stderr[:300])
    classes = []
    for line in out.stdout.splitlines():
        bits = ''.join(c for c in line.strip() if c in '01')
        if len(bits) != n * (n - 1) // 2:
            continue
        arcs = []; idx = 0
        for i in range(n):
            for j in range(i + 1, n):
                arcs.append((i, j) if bits[idx] == '1' else (j, i))
                idx += 1
        classes.append(arcs)
    return classes


def random_tournament(nH, rng):
    aH = []
    for i in range(nH):
        for j in range(i + 1, nH):
            aH.append((i, j) if rng.random() < 0.5 else (j, i))
    return aH


def mode_census(orders, order9_sample, seed, bound, time_budget=560):
    t0 = time.time()
    rng = random.Random(seed)
    out = {"bound": bound, "orders": orders, "order9_sample": order9_sample,
           "seed": seed, "per_order": {}, "examples_infeasible": []}
    n_infeasible_total = 0

    for nH in orders:
        if time.time() - t0 > time_budget:
            out["per_order"][str(nH)] = {"aborted_time": True}
            print(f"[order {nH}] ABORTED (time budget) before start", flush=True)
            break
        classes = gentourng_classes(nH)
        ov3 = []
        for aH in classes:
            if core.omega_vec(nH, aH) == 3:
                ov3.append(aH)
        print(f"[order {nH}] {len(classes)} iso classes, {len(ov3)} with ov=3", flush=True)
        rec = {"n_classes": len(classes), "n_ov3": len(ov3),
               "n_feasible": 0, "n_infeasible": 0,
               "min_distinct_dist": {1: 0, 2: 0, 3: 0},
               "stagger_max": 0, "aborted_time": False, "n_tested": 0}
        for idx, aH in enumerate(ov3):
            if time.time() - t0 > time_budget:
                rec["aborted_time"] = True
                print(f"[order {nH}] ABORTED at ov3 index {idx}/{len(ov3)} "
                      f"(time budget)", flush=True)
                break
            res = feasible_H(nH, aH, 3, bound)
            rec["n_tested"] += 1
            if res["feasible"]:
                rec["n_feasible"] += 1
                rec["min_distinct_dist"][res["min_distinct"]] += 1
                if res["stagger"] is not None:
                    rec["stagger_max"] = max(rec["stagger_max"], res["stagger"])
            else:
                rec["n_infeasible"] += 1
                n_infeasible_total += 1
                if len(out["examples_infeasible"]) < 10:
                    out["examples_infeasible"].append(
                        {"nH": nH, "arcs": [list(a) for a in aH],
                         "n_profiles": res["n_profiles"],
                         "profiles_truncated": res["profiles_truncated"]})
        out["per_order"][str(nH)] = rec
        print(f"[order {nH}] tested={rec['n_tested']} feasible={rec['n_feasible']} "
              f"INFEASIBLE={rec['n_infeasible']} "
              f"min_distinct={rec['min_distinct_dist']} "
              f"stagger_max={rec['stagger_max']}", flush=True)

    # order-9 sampled slice
    if order9_sample > 0 and time.time() - t0 < time_budget:
        rec9 = {"n_tested": 0, "n_feasible": 0, "n_infeasible": 0,
                "min_distinct_dist": {1: 0, 2: 0, 3: 0}, "stagger_max": 0,
                "n_sampled_ov3": 0, "n_drawn": 0, "aborted_time": False}
        drawn = 0
        while rec9["n_sampled_ov3"] < order9_sample:
            if time.time() - t0 > time_budget:
                rec9["aborted_time"] = True
                print(f"[order 9] ABORTED (time budget) after "
                      f"{rec9['n_sampled_ov3']} ov=3 drawn", flush=True)
                break
            aH = random_tournament(9, rng)
            drawn += 1
            if core.omega_vec(9, aH) != 3:
                continue
            rec9["n_sampled_ov3"] += 1
            res = feasible_H(9, aH, 3, bound)
            rec9["n_tested"] += 1
            if res["feasible"]:
                rec9["n_feasible"] += 1
                rec9["min_distinct_dist"][res["min_distinct"]] += 1
                if res["stagger"] is not None:
                    rec9["stagger_max"] = max(rec9["stagger_max"], res["stagger"])
            else:
                rec9["n_infeasible"] += 1
                n_infeasible_total += 1
                if len(out["examples_infeasible"]) < 10:
                    out["examples_infeasible"].append(
                        {"nH": 9, "arcs": [list(a) for a in aH],
                         "n_profiles": res["n_profiles"],
                         "profiles_truncated": res["profiles_truncated"]})
        rec9["n_drawn"] = drawn
        out["per_order"]["9_sample"] = rec9
        print(f"[order 9 sample] ov3 tested={rec9['n_tested']} "
              f"feasible={rec9['n_feasible']} INFEASIBLE={rec9['n_infeasible']} "
              f"min_distinct={rec9['min_distinct_dist']} "
              f"stagger_max={rec9['stagger_max']}", flush=True)

    out["n_infeasible_total"] = n_infeasible_total
    out["elapsed_s"] = round(time.time() - t0, 1)
    os.makedirs('data', exist_ok=True)
    json.dump(out, open('data/h25_path_census.json', 'w'), indent=1)
    print("=== CENSUS SUMMARY ===", flush=True)
    print(f"    total INFEASIBLE (ov=3, bound={bound}) = {n_infeasible_total}", flush=True)
    print(f"    elapsed {out['elapsed_s']}s ; wrote data/h25_path_census.json", flush=True)
    print(f"CENSUS_ALL_FEASIBLE: {n_infeasible_total == 0}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', required=True, choices=['controls', 'census'])
    ap.add_argument('--orders', default='7,8')
    ap.add_argument('--order9-sample', type=int, default=0)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--bound', type=int, default=4)
    a = ap.parse_args()
    if a.mode == 'controls':
        mode_controls()
    else:
        orders = [int(x) for x in a.orders.split(',') if x.strip()]
        mode_census(orders, a.order9_sample, a.seed, a.bound)


if __name__ == '__main__':
    main()
