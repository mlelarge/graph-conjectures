"""Hunt for an explicit GENERIC omega_vec=4 tournament on n=18 (then 17).

Proposal (explicit-construction lens): beat the smallest-known ov=4 order
(currently 19 = QR_19, P15; proved generic interval [11,19], P21) by
simulated-annealing arc-flip search over tournaments on n=18.

Objective: maximize the EFFORT a pool of cheap heuristic orders (greedy
Copeland potential-sum + random restarts + adjacent-swap local repair with
incremental K4-count) needs to find a backedge-clique<=3 order.  A candidate
whose heuristic-order pool NEVER produces a clique<=3 order survives the gate
and is promoted to EXACT verification via the proven P15 protocol:
  no-K4 betweenness/order SAT UNSAT under BOTH Cadical153 and Minisat22
  (=> omega_vec>=4) + one explicit order with exact backedge clique 4
  (core.omega_of_order, => omega_vec<=4).

Seeds: 50% uniform random, 50% boundary-adjacent structured starts
(QR_19 minus 1-2 vertices, AC4_21 minus 3 -- all ov=3 by criticality/P15/P14
but one arc-flip away from the wall).

All EXACT statements go through core.py / the SAT model; the annealing layer
is heuristic and only ever used as a FILTER (one-sided: it can only reject
candidates by exhibiting an explicit clique<=3 order, which is exact-checked
with core.omega_of_order before rejection is trusted).
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core  # exact oracle

# ----------------------------------------------------------------- builders
QR19_G = [1, 4, 5, 6, 7, 9, 11, 16, 17]          # P15 Paley(19)
AC421_G = [1, 2, 4, 7, 8, 9, 11, 15, 16, 18]     # P14 order-21


def circulant(n, gens):
    arcs = [(u, (u + g) % n) for u in range(n) for g in gens]
    return n, arcs


def delete_vertices(n, arcs, dele):
    keep = [v for v in range(n) if v not in dele]
    idx = {v: i for i, v in enumerate(keep)}
    new = [(idx[u], idx[v]) for (u, v) in arcs if u in idx and v in idx]
    return len(keep), new


def random_tournament(n, rng):
    arcs = []
    for u in range(n):
        for v in range(u + 1, n):
            arcs.append((u, v) if rng.random() < 0.5 else (v, u))
    return n, arcs


def out_masks(n, arcs):
    out = [0] * n
    for u, v in arcs:
        out[u] |= 1 << v
    return out


def masks_to_arcs(n, out):
    return [(u, v) for u in range(n) for v in range(n) if (out[u] >> v) & 1]


# --------------------------------------------------- backedge K4 machinery
def backedge_adj(n, out, order):
    adj = [0] * n
    for i in range(n):
        a = order[i]
        for j in range(i + 1, n):
            b = order[j]
            if (out[b] >> a) & 1:           # b prec-later beats a => backedge
                adj[a] |= 1 << b
                adj[b] |= 1 << a
    return adj


def count_k4(n, adj):
    """Number of K4s, each counted once (a<b<c<d)."""
    cnt = 0
    for a in range(n):
        ma = adj[a] >> (a + 1) << (a + 1)
        while ma:
            b = (ma & -ma).bit_length() - 1
            ma &= ma - 1
            common = adj[a] & adj[b] & ~((1 << (b + 1)) - 1)
            mc = common
            while mc:
                c = (mc & -mc).bit_length() - 1
                mc &= mc - 1
                cnt += bin(adj[c] & common & ~((1 << (c + 1)) - 1)).count("1")
    return cnt


def edges_in(adj, mask):
    cnt = 0
    m = mask
    while m:
        c = (m & -m).bit_length() - 1
        m &= m - 1
        cnt += bin(adj[c] & mask & ~((1 << (c + 1)) - 1)).count("1")
    return cnt


def toggle_delta_k4(adj, a, b):
    """K4s through edge {a,b} given current adj WITHOUT counting the ab edge
    state: K4s containing edge ab = edges inside common nbhd of a,b."""
    return edges_in(adj, adj[a] & adj[b])


# --------------------------------------------- heuristic clique<=3 searcher
def greedy_copeland(n, out, rng, jitter=0.0):
    key = [bin(out[v]).count("1") + (rng.random() * jitter) for v in range(n)]
    return sorted(range(n), key=lambda v: -key[v])


def search_clique3_order(n, out, restarts, iters, rng, effort_cap=None):
    """Try to find an order whose backedge graph is K4-free.
    Returns (order_or_None, effort_steps).  One-sided heuristic filter only."""
    effort = 0
    for r in range(restarts):
        if r == 0:
            order = greedy_copeland(n, out, rng, jitter=0.0)
        elif r % 3 == 1:
            order = greedy_copeland(n, out, rng, jitter=3.0)
        else:
            order = list(range(n))
            rng.shuffle(order)
        adj = backedge_adj(n, out, order)
        cost = count_k4(n, adj)
        if cost == 0:
            return order, effort
        stall = 0
        for _ in range(iters):
            effort += 1
            if effort_cap is not None and effort > effort_cap:
                return None, effort
            if rng.random() < 0.85:
                # incremental adjacent swap: toggles exactly edge {a,b}
                i = rng.randrange(n - 1)
                a, b = order[i], order[i + 1]
                present = (adj[a] >> b) & 1
                if present:
                    adj[a] &= ~(1 << b); adj[b] &= ~(1 << a)
                    delta = -toggle_delta_k4(adj, a, b)  # removed K4s
                else:
                    delta = toggle_delta_k4(adj, a, b)   # added K4s
                    adj[a] |= 1 << b; adj[b] |= 1 << a
                if delta <= 0:
                    order[i], order[i + 1] = b, a
                    cost += delta
                    if cost == 0:
                        return order, effort
                    stall = stall + 1 if delta == 0 else 0
                else:
                    # revert toggle
                    if present:
                        adj[a] |= 1 << b; adj[b] |= 1 << a
                    else:
                        adj[a] &= ~(1 << b); adj[b] &= ~(1 << a)
                    stall += 1
            else:
                # move a random vertex to a random position (full recompute)
                i, j = rng.randrange(n), rng.randrange(n)
                if i == j:
                    continue
                cand = order[:]
                v = cand.pop(i)
                cand.insert(j, v)
                adj2 = backedge_adj(n, out, cand)
                c2 = count_k4(n, adj2)
                if c2 <= cost:
                    order, adj, cost = cand, adj2, c2
                    if cost == 0:
                        return order, effort
                    stall = stall + 1 if c2 == cost else 0
                else:
                    stall += 1
            if stall > 400:
                break
    return None, effort


# ------------------------------------------------------------- exact legs
def exact_clique_of_order(n, out, order):
    arcs = masks_to_arcs(n, out)
    return core.omega_of_order(n, arcs, order)


def enumerate_transitive_chains(n, out, K):
    """Transitive K-subsets as source-first acyclic chains s1->...->sK
    (each earlier beats all later).  Each set produced exactly once because
    the source-first acyclic order of a transitive set is unique."""
    chains = []

    def rec(chosen, cand_mask):
        if len(chosen) == K:
            chains.append(tuple(chosen))
            return
        m = cand_mask
        while m:
            v = (m & -m).bit_length() - 1
            m &= m - 1
            rec(chosen + [v], cand_mask & out[v])

    for s in range(n):
        rec([s], out[s])
    return chains


def sat_no_k4(n, out):
    """Two-solver no-K4 order-SAT (the P15/P21 protocol leg, adapted K=4).
    Returns dict with sat flags and, when SAT, a model-extracted order."""
    from pysat.formula import CNF
    from pysat.solvers import Cadical153, Minisat22

    chains = enumerate_transitive_chains(n, out, 4)
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

    for u in range(n):
        for v in range(u + 1, n):
            lit(u, v)
    cnf = CNF()
    for u in range(n):
        for v in range(n):
            if v == u:
                continue
            for w in range(n):
                if w in (u, v):
                    continue
                cnf.append([-lit(u, v), -lit(v, w), lit(u, w)])
    # backedge K4 on transitive chain s1->..->s4 occurs iff s4 prec ... prec s1;
    # forbid: require s_i prec s_{i+1} for some i.
    for ch in chains:
        cnf.append([lit(ch[i], ch[i + 1]) for i in range(3)])

    res = {"n": n, "transitive_4sets": len(chains)}
    order = None
    with Cadical153(bootstrap_with=cnf.clauses) as m:
        sat_c = m.solve()
        if sat_c:
            model = set(l for l in m.get_model() if l > 0)
            prec = {}
            for (u, v), L in idx.items():
                prec[(u, v)] = L in model
            order = sorted(range(n),
                           key=lambda v: -sum(1 for w in range(n) if w != v and
                                              (prec.get((v, w)) if (v, w) in prec
                                               else not prec.get((w, v)))))
    with Minisat22(bootstrap_with=cnf.clauses) as m:
        sat_m = m.solve()
    res["cadical_sat"] = sat_c
    res["minisat_sat"] = sat_m
    res["order_from_model"] = order
    return res


# --------------------------------------------------------------- annealing
def make_seed(kind, rng):
    if kind == "random":
        return random_tournament(18, rng)
    if kind == "qr19_minus1":
        n, arcs = circulant(19, QR19_G)
        return delete_vertices(n, arcs, {rng.randrange(19)})
    if kind == "ac421_minus3":
        n, arcs = circulant(21, AC421_G)
        dele = set(rng.sample(range(21), 3))
        return delete_vertices(n, arcs, dele)
    raise ValueError(kind)


def anneal_shard(args):
    rng = random.Random(args.seed)
    n = args.n
    t0 = time.time()
    stats = {"shard": args.shard, "seed": args.seed, "n": n,
             "seed_kind": args.seed_kind, "flips_evaluated": 0,
             "best_effort": 0, "gate_survivors": 0, "deep_gate_runs": 0,
             "restarts_of_anneal": 0, "exact3_rejects_checked": 0,
             "verified_hits": []}
    best_overall = 0
    while time.time() - t0 < args.budget:
        # fresh annealing run from a fresh seed
        stats["restarts_of_anneal"] += 1
        Tn, arcs = make_seed(args.seed_kind, rng)
        assert Tn == n
        out = out_masks(n, arcs)
        ordr, cur_eff = search_clique3_order(n, out, args.restarts,
                                             args.iters, rng)
        temp = 60.0
        steps_this_run = 0
        while time.time() - t0 < args.budget and steps_this_run < args.run_len:
            steps_this_run += 1
            temp = max(2.0, temp * 0.999)
            u = rng.randrange(n)
            v = rng.randrange(n)
            if u == v:
                continue
            # flip arc between u,v
            if (out[u] >> v) & 1:
                out[u] &= ~(1 << v); out[v] |= 1 << u
            else:
                out[v] &= ~(1 << u); out[u] |= 1 << v
            ordr2, eff2 = search_clique3_order(n, out, args.restarts,
                                               args.iters, rng)
            stats["flips_evaluated"] += 1
            if ordr2 is None:
                # GATE SURVIVOR: pool never found clique<=3. Deep gate.
                stats["gate_survivors"] += 1
                stats["deep_gate_runs"] += 1
                deep, _ = search_clique3_order(n, out, args.deep_restarts,
                                               args.deep_iters, rng)
                if deep is not None:
                    # exact-check the certificate before trusting rejection
                    ex = exact_clique_of_order(n, out, deep)
                    stats["exact3_rejects_checked"] += 1
                    assert ex <= 3, f"heuristic K4-free order has exact clique {ex}"
                    cur_eff = args.restarts * args.iters  # very hard => keep
                    continue
                # survived deep gate too -> EXACT SAT verification
                arcs_now = masks_to_arcs(n, out)
                res = sat_no_k4(n, out)
                if not res["cadical_sat"] and not res["minisat_sat"]:
                    # omega_vec >= 4 PROVEN (two solvers). Upper leg:
                    some_order = greedy_copeland(n, out, rng)
                    ub = exact_clique_of_order(n, out, some_order)
                    hit = {"arcs": arcs_now, "sat": res,
                           "upper_order": some_order, "upper_clique": ub}
                    stats["verified_hits"].append(hit)
                    return stats
                else:
                    # SAT => a K4-free order exists => ov<=3; extract+check
                    mo = res["order_from_model"]
                    if mo is not None:
                        ex = exact_clique_of_order(n, out, mo)
                        stats.setdefault("sat_model_cliques", []).append(ex)
                    cur_eff = args.restarts * args.iters
                    continue
            # plain annealing accept/reject on effort
            delta = eff2 - cur_eff
            if delta >= 0 or rng.random() < pow(2.718281828, delta / temp):
                cur_eff = eff2
                best_overall = max(best_overall, cur_eff)
            else:
                # revert flip
                if (out[u] >> v) & 1:
                    out[u] &= ~(1 << v); out[v] |= 1 << u
                else:
                    out[v] &= ~(1 << u); out[u] |= 1 << v
    stats["best_effort"] = best_overall
    stats["elapsed"] = round(time.time() - t0, 1)
    return stats


# -------------------------------------------------------------- calibration
def calibrate():
    rng = random.Random(0)
    rep = {}
    # (1) SAT-model soundness vs exact core.omega_vec at small n (K=4 analog
    #     is vacuous below 11 by P21, so calibrate the SAME encoder at K=3):
    from pysat.formula import CNF  # noqa
    ok = True
    for trial in range(20):
        n = 7
        _, arcs = random_tournament(n, rng)
        out = out_masks(n, arcs)
        # K=3 variant via same machinery
        chains = enumerate_transitive_chains(n, out, 3)
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
        for u in range(n):
            for v in range(u + 1, n):
                lit(u, v)
        from pysat.solvers import Cadical153
        cnf = []
        for u in range(n):
            for v in range(n):
                if v == u:
                    continue
                for w in range(n):
                    if w in (u, v):
                        continue
                    cnf.append([-lit(u, v), -lit(v, w), lit(u, w)])
        for ch in chains:
            cnf.append([lit(ch[i], ch[i + 1]) for i in range(2)])
        with Cadical153(bootstrap_with=cnf) as m:
            sat = m.solve()
        ov = core.omega_vec(n, arcs)
        if sat != (ov <= 2):
            ok = False
    rep["sat_encoder_sound_K3_n7_20trials"] = ok

    # (2) reproduce P15 lower leg: QR_19 no-K4 UNSAT both solvers
    n, arcs = circulant(19, QR19_G)
    out = out_masks(n, arcs)
    res = sat_no_k4(n, out)
    rep["qr19_noK4"] = {"cadical_sat": res["cadical_sat"],
                        "minisat_sat": res["minisat_sat"],
                        "transitive_4sets": res["transitive_4sets"]}

    # (3) heuristic filter finds a clique<=3 order on QR_19 - {0} (ov=3, P15)
    n18, arcs18 = delete_vertices(19, arcs, {0})
    out18 = out_masks(n18, arcs18)
    o3, eff = search_clique3_order(n18, out18, 40, 4000, random.Random(1))
    rep["qr19_minus0_found3"] = o3 is not None
    rep["qr19_minus0_effort"] = eff
    if o3 is not None:
        rep["qr19_minus0_exact_clique_of_found_order"] = \
            exact_clique_of_order(n18, out18, o3)

    # (4) heuristic filter does NOT find clique<=3 on QR_19 itself (ov=4)
    o3q, effq = search_clique3_order(19, out, 40, 4000, random.Random(2))
    rep["qr19_found3"] = o3q is not None
    rep["qr19_effort"] = effq
    return rep


def _run_one(spec):
    """Worker for the foreground multi-shard driver (multiprocessing.Pool)."""
    args = argparse.Namespace(**spec)
    return anneal_shard(args)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=18)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--seed-kind", default="random",
                    choices=["random", "qr19_minus1", "ac421_minus3"])
    ap.add_argument("--budget", type=float, default=520.0)
    ap.add_argument("--restarts", type=int, default=6)
    ap.add_argument("--iters", type=int, default=350)
    ap.add_argument("--deep-restarts", type=int, default=2000)
    ap.add_argument("--deep-iters", type=int, default=1500)
    ap.add_argument("--run-len", type=int, default=4000)
    ap.add_argument("--calibrate", action="store_true")
    ap.add_argument("--multi", default=None,
                    help="comma list of seedkind:seed shard specs; runs them "
                         "in a foreground multiprocessing.Pool and joins")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    if args.calibrate:
        rep = calibrate()
        print(json.dumps(rep, indent=1))
        return

    if args.multi:
        import multiprocessing as mp
        specs = []
        for i, item in enumerate(args.multi.split(",")):
            kind, sd = item.split(":")
            d = vars(args).copy()
            d.pop("multi"); d.pop("calibrate"); d.pop("out")
            d["seed_kind"] = kind
            d["seed"] = int(sd)
            d["shard"] = i
            specs.append(d)
        with mp.Pool(len(specs)) as pool:
            results = pool.map(_run_one, specs)
        out = {"shards": results,
               "any_verified_hit": any(r["verified_hits"] for r in results)}
        s = json.dumps(out)
        print(s)
        if args.out:
            with open(args.out, "w") as f:
                f.write(s)
        return

    stats = anneal_shard(args)
    s = json.dumps(stats)
    print(s)
    if args.out:
        with open(args.out, "w") as f:
            f.write(s)


if __name__ == "__main__":
    main()
