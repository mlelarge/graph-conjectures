#!/usr/bin/env python
"""One-vertex-extension census: does an omega_vec=4 tournament exist at order 10?

Soundness of exhaustiveness: any order-10 T with ov(T)>=4 has, for every v,
ov(T-v) >= ov(T)-1 >= 3 (subadditivity) and ov(T-v) <= 3 (P9b: complete
order-9 census, max ov = 3).  So T-v is one of the 1146 stored order-9 ov=3
iso classes for EVERY v; hence T is (up to iso) H + one new vertex for some
stored H and one of 2^9 = 512 arc patterns.  Census = 1146*512 = 586752.

Per candidate T = H + vertex 9 (pattern p, bit i set <=> 9 beats i):
  FILTER (sound 'ov<=3' certificate): take precomputed orders w of H whose
  backedge graph has omega<=3 (SAT-extracted, exact-checked); insert 9 at each
  of 10 positions.  New backedge graph = old graph + vertex 9 with
  N(9) = (before & p) | (after & ~p).  omega<=3 for T-order iff N(9) is
  triangle-free in H^w (bitmask check).  Any hit => explicit order, ov(T)<=3.
  Fallback: random orders of T, exact omega_of_order <= 3 => discard.
  SURVIVORS: no-K4 SAT (Cadical153).  SAT => model order, exact-checked <=3.
  UNSAT => candidate ov>=4 hit: re-verify Minisat22 UNSAT + exact
  core.omega_vec_bb(T, ub=4) == 4.

Modes: --integrity, --calibrate, --shard K/N
"""
import argparse, json, os, random, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import core
from pysat.formula import CNF
from pysat.solvers import Cadical153, Minisat22

CLASSES_PATH = os.path.join(DIR, "data", "skeptic_o9_ov3_classes.json")


# ---------------------------------------------------------------- SAT no-K4
def transitive_ksubsets_order(n, beats, K):
    import itertools
    for sub in itertools.combinations(range(n), K):
        outdeg = {v: sum(1 for u in sub if u != v and beats[v][u]) for v in sub}
        order = sorted(sub, key=lambda v: -outdeg[v])
        if all(beats[order[a]][order[b]] for a in range(K) for b in range(a + 1, K)):
            yield order


def build_cnf_no_kclique(n, arcs, K):
    beats = core.beats_matrix(n, arcs)
    idx = {}
    nv = 0
    def lit(u, v):
        nonlocal nv
        if (u, v) in idx:
            return idx[(u, v)]
        if (v, u) in idx:
            return -idx[(v, u)]
        nv += 1
        idx[(u, v)] = nv
        return nv
    cnf = CNF()
    for u in range(n):
        for v in range(u + 1, n):
            lit(u, v)
    for u in range(n):
        for v in range(n):
            if v == u: continue
            for w in range(n):
                if w == u or w == v: continue
                cnf.append([-lit(u, v), -lit(v, w), lit(u, w)])
    for order in transitive_ksubsets_order(n, beats, K):
        cnf.append([lit(order[i], order[i + 1]) for i in range(K - 1)])
    return cnf, idx


def order_from_model(n, idx, model):
    pos = set(l for l in model if l > 0)
    def less(u, v):
        if (u, v) in idx:
            return idx[(u, v)] in pos
        return idx[(v, u)] not in pos
    import functools
    return sorted(range(n), key=functools.cmp_to_key(lambda a, b: -1 if less(a, b) else 1))


def sat_no_k4(n, arcs, solver_cls=Cadical153):
    """Returns (sat_bool, order_or_None)."""
    cnf, idx = build_cnf_no_kclique(n, arcs, 4)
    with solver_cls(bootstrap_with=cnf.clauses) as m:
        if m.solve():
            return True, order_from_model(n, idx, m.get_model())
        return False, None


# ------------------------------------------------------- witness orders of H
def witness_orders(n, arcs, want=12, rng=None):
    """Distinct orders of H with backedge omega <= 3 (exact-checked)."""
    rng = rng or random.Random(0)
    found = []
    seen = set()
    # SAT with random relabelings for diversity
    for _ in range(want * 2):
        perm = list(range(n)); rng.shuffle(perm)
        rarcs = [(perm[u], perm[v]) for (u, v) in arcs]
        ok, order = sat_no_k4(n, rarcs)
        if not ok:
            raise AssertionError("class claimed ov=3 but no-K4 UNSAT at n=9")
        inv = [0] * n
        for i, p in enumerate(perm):
            inv[p] = i
        worder = tuple(inv[v] for v in order)
        assert core.omega_of_order(n, arcs, list(worder)) <= 3
        if worder not in seen:
            seen.add(worder); found.append(list(worder))
        if len(found) >= want:
            break
    return found


# --------------------------------------------------------------- the filter
def precompute_order_data(arcs9, orders):
    """For each witness order w of H: backedge adjacency bitmasks + prefix masks."""
    beats = core.beats_matrix(9, arcs9)
    data = []
    for w in orders:
        adj = [0] * 9
        for i in range(9):
            a = w[i]
            for j in range(i + 1, 9):
                b = w[j]
                if beats[b][a]:           # b after a in order, b->a : backedge
                    adj[a] |= 1 << b
                    adj[b] |= 1 << a
        prefix = [0] * 11
        for i in range(9):
            prefix[i + 1] = prefix[i] | (1 << w[i])
        data.append((adj, prefix))
    return data


FULL9 = (1 << 9) - 1


def filter_pattern(odata, p):
    """True iff some (order,pos) certifies ov(T)<=3 for pattern p (sound)."""
    notp = (~p) & FULL9
    for adj, prefix in odata:
        for pos in range(10):
            before = prefix[pos]
            N = (before & p) | (((~before) & FULL9) & notp)
            # triangle-free check of H^w restricted to N
            m = N
            tri = False
            while m:
                a = (m & -m).bit_length() - 1
                m &= m - 1
                na = adj[a] & N
                mm = na & ~((1 << (a + 1)) - 1)   # b > a only
                while mm:
                    b = (mm & -mm).bit_length() - 1
                    mm &= mm - 1
                    if adj[a] & adj[b] & N:
                        tri = True; break
                if tri:
                    break
            if not tri:
                return True
    return False


def extension_arcs(arcs9, p):
    arcs = list(arcs9)
    for i in range(9):
        arcs.append((9, i) if (p >> i) & 1 else (i, 9))
    return arcs


def decide_extension(arcs9, odata, p, rng):
    """Returns ('le3', None) or ('ge4', certdict)."""
    if filter_pattern(odata, p):
        return 'le3', None
    arcs10 = extension_arcs(arcs9, p)
    # fallback random exact orders
    for _ in range(60):
        w = list(range(10)); rng.shuffle(w)
        if core.omega_of_order(10, arcs10, w) <= 3:
            return 'le3', None
    sat, order = sat_no_k4(10, arcs10, Cadical153)
    if sat:
        assert core.omega_of_order(10, arcs10, order) <= 3
        return 'le3', None
    # UNSAT: ov>=4 candidate -- double solver + exact bb
    sat2, _ = sat_no_k4(10, arcs10, Minisat22)
    bb = core.omega_vec_bb(10, arcs10, ub=4)
    return 'ge4', {"pattern": p, "minisat_unsat": (not sat2), "bb_ub4": bb}


# ------------------------------------------------------------------- modes
def load_classes():
    with open(CLASSES_PATH) as f:
        d = json.load(f)
    assert d["n_ov3"] == 1146 and len(d["classes"]) == 1146
    return d["classes"]


def mode_integrity():
    classes = load_classes()
    rng = random.Random(20260610)
    sample = rng.sample(range(1146), 20)
    bad = []
    for i in sample:
        arcs = [tuple(a) for a in classes[i]["arcs"]]
        ist = core.is_tournament(9, arcs)
        ov = core.omega_vec_bb(9, arcs)
        if not ist or ov != 3:
            bad.append((i, ist, ov))
        print(f"class {i}: is_tournament={ist} omega_vec_bb={ov}", flush=True)
    print("INTEGRITY", "PASS" if not bad else f"FAIL {bad}")
    return not bad


def random_tournament(n, rng):
    arcs = []
    for u in range(n):
        for v in range(u + 1, n):
            arcs.append((u, v) if rng.random() < 0.5 else (v, u))
    return arcs


def mode_calibrate():
    rng = random.Random(424242)
    mism = 0
    ge4_count = 0
    for t in range(200):
        arcs = random_tournament(10, rng)
        sat, order = sat_no_k4(10, arcs, Cadical153)
        verdict_ge4 = not sat
        if sat:
            assert core.omega_of_order(10, arcs, order) <= 3
        bb = core.omega_vec_bb(10, arcs, ub=4)
        exact_ge4 = (bb >= 4)
        if verdict_ge4 != exact_ge4:
            mism += 1
            print(f"MISMATCH t={t} sat_ge4={verdict_ge4} bb={bb}")
        ge4_count += int(exact_ge4)
    print(f"CALIBRATION: 200 random n=10, mismatches={mism}, exact_ge4_count={ge4_count}")
    return mism == 0


def mode_shard(k, nsh, out):
    classes = load_classes()
    lo = (1146 * k) // nsh
    hi = (1146 * (k + 1)) // nsh
    rng = random.Random(1000 + k)
    t0 = time.time()
    n_cand = 0
    survivors = []
    sat_calls = 0
    for ci in range(lo, hi):
        arcs9 = [tuple(a) for a in classes[ci]["arcs"]]
        orders = witness_orders(9, arcs9, want=12, rng=rng)
        odata = precompute_order_data(arcs9, orders)
        for p in range(512):
            n_cand += 1
            if filter_pattern(odata, p):
                continue
            arcs10 = extension_arcs(arcs9, p)
            done = False
            for _ in range(60):
                w = list(range(10)); rng.shuffle(w)
                if core.omega_of_order(10, arcs10, w) <= 3:
                    done = True; break
            if done:
                continue
            sat_calls += 1
            sat, order = sat_no_k4(10, arcs10, Cadical153)
            if sat:
                assert core.omega_of_order(10, arcs10, order) <= 3
                continue
            sat2, _ = sat_no_k4(10, arcs10, Minisat22)
            bb = core.omega_vec_bb(10, arcs10, ub=4)
            survivors.append({"class_index_in_file": ci, "pattern": p,
                              "minisat_unsat": (not sat2), "bb_ub4": bb,
                              "arcs10": [list(a) for a in arcs10]})
            print(f"SURVIVOR ci={ci} p={p} minisat_unsat={not sat2} bb={bb}", flush=True)
        if (ci - lo) % 25 == 0:
            print(f"shard {k}/{nsh} class {ci} ({ci-lo+1}/{hi-lo}) cand={n_cand} "
                  f"satcalls={sat_calls} surv={len(survivors)} t={time.time()-t0:.1f}s", flush=True)
    res = {"shard": k, "nshards": nsh, "class_range": [lo, hi],
           "n_candidates": n_cand, "sat_fallback_calls": sat_calls,
           "n_survivors": len(survivors), "survivors": survivors,
           "elapsed_s": round(time.time() - t0, 1)}
    with open(out, "w") as f:
        json.dump(res, f, indent=1)
    print(f"SHARD {k}/{nsh} DONE candidates={n_cand} survivors={len(survivors)} "
          f"satcalls={sat_calls} elapsed={res['elapsed_s']}s -> {out}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--integrity", action="store_true")
    ap.add_argument("--calibrate", action="store_true")
    ap.add_argument("--shard", type=str, default=None)   # "k/N"
    ap.add_argument("--out", type=str, default=None)
    a = ap.parse_args()
    if a.integrity:
        sys.exit(0 if mode_integrity() else 1)
    if a.calibrate:
        sys.exit(0 if mode_calibrate() else 1)
    if a.shard:
        k, nsh = map(int, a.shard.split("/"))
        mode_shard(k, nsh, a.out or os.path.join(DIR, "data", f"extend_n10_shard_{k}.json"))


if __name__ == "__main__":
    main()
