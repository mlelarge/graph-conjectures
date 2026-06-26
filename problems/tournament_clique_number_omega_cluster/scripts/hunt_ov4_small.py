#!/usr/bin/env python
"""SAT-guided local search for an explicit NON-circulant omega_vec=4 tournament
at small order m in [11,18] -- closing ell(4) from above (window [11,19]; P21
floor 11, P15 ceiling 19=QR_19; circulants exhausted below 19, so any witness
is GENERIC).

Decision oracle = the P21-validated no-K4 betweenness CNF
(extend_n10_ov4_census.sat_no_k4): UNSAT => omega_vec >= 4 (no order has a
K4-free backedge graph); SAT => an explicit K4-free order, exact-checked.

State = labelled tournament (out-adjacency masks).  Move = single-arc flip.
Guided: each SAT model returns a K4-free witness order; we score a tournament
by the number of distinct K4-free orders surviving up to C blocking clauses
(lower = closer to UNSAT), and flip arcs that are backedges of those witness
orders (each model points at the obstruction).  On a score-0 (UNSAT-on-first)
or low-score state we re-run the FULL no-K4 SAT; on UNSAT we VERIFY at the
P21/P22 bar:
  (1) no-K4 CNF UNSAT under BOTH Cadical153 AND Minisat22  => ov >= 4
  (2) no-K5 SAT, and the returned order's backedge graph has exact clique 4
      (core.omega_of_order)                                 => ov <= 4
  => ov(T) = 4 EXACTLY at order m < 19.  Also exact core.omega_vec_bb as a
  third independent check, and a non-circulant flag.

Seeds: uniform random; QR_11 / known structured padded by dominated vertices;
P9b stored order-9 ov=3 census classes extended.
"""
import argparse, json, os, random, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import core
from extend_n10_ov4_census import build_cnf_no_kclique, order_from_model, load_classes
from pysat.solvers import Cadical153, Minisat22

QR11_G = [1, 3, 4, 5, 9]   # quadratic residues mod 11


# --------------------------------------------------------------- arc helpers
def out_masks(n, arcs):
    out = [0] * n
    for u, v in arcs:
        out[u] |= 1 << v
    return out


def masks_to_arcs(n, out):
    return [(u, v) for u in range(n) for v in range(n) if (out[u] >> v) & 1]


def random_tournament(n, rng):
    return [(u, v) if rng.random() < 0.5 else (v, u)
            for u in range(n) for v in range(u + 1, n)]


def circulant(n, gens):
    return [(u, (u + g) % n) for u in range(n) for g in gens]


# ------------------------------------------------------- graded SAT scoring
def graded_score(n, arcs, max_blocks=50, solver_cls=Cadical153):
    """Number of distinct K4-free orders found before UNSAT or max_blocks.

    Returns (score, unsat_flag, witness_orders).  score==0 with unsat_flag True
    means no-K4 UNSAT on the FIRST solve (=> ov>=4 candidate).  Lower score =>
    closer to the UNSAT wall.  Witness orders supply guided-flip candidates.
    """
    cnf, idx = build_cnf_no_kclique(n, arcs, 4)
    witnesses = []
    with solver_cls(bootstrap_with=cnf.clauses) as m:
        blocks = 0
        while blocks <= max_blocks:
            if not m.solve():
                return len(witnesses), True, witnesses
            model = m.get_model()
            order = order_from_model(n, idx, model)
            witnesses.append(order)
            # block this exact assignment of the ordering variables
            pos = set(l for l in model if l > 0)
            block = []
            for (u, v), L in idx.items():
                block.append(-L if L in pos else L)
            m.add_clause(block)
            blocks += 1
    return len(witnesses), False, witnesses


def backedge_arcs_of_order(n, out, order):
    """Arcs (b,a) that are backedges under `order` (b later beats a earlier)."""
    pos = [0] * n
    for i, v in enumerate(order):
        pos[v] = i
    be = []
    for u in range(n):
        for v in range(n):
            if u == v:
                continue
            if (out[u] >> v) & 1 and pos[u] > pos[v]:
                be.append((u, v))
    return be


# ----------------------------------------------------------- exact verifier
def verify_hit(n, out):
    arcs = masks_to_arcs(n, out)
    # (1) no-K4 UNSAT both solvers
    s4c, _, _ = graded_score(n, arcs, max_blocks=0, solver_cls=Cadical153)
    cnf4, _ = build_cnf_no_kclique(n, arcs, 4)
    with Cadical153(bootstrap_with=cnf4.clauses) as m:
        cad4 = m.solve()
    cnf4b, _ = build_cnf_no_kclique(n, arcs, 4)
    with Minisat22(bootstrap_with=cnf4b.clauses) as m:
        min4 = m.solve()
    # (2) no-K5 SAT, model order exact clique == 4
    cnf5, idx5 = build_cnf_no_kclique(n, arcs, 5)
    with Cadical153(bootstrap_with=cnf5.clauses) as m:
        cad5 = m.solve()
        order5 = order_from_model(n, idx5, m.get_model()) if cad5 else None
    clique_of_order5 = core.omega_of_order(n, arcs, order5) if order5 else None
    # (3) exact bb
    bb = core.omega_vec_bb(n, arcs, ub=5)
    return {
        "n": n,
        "arcs": [list(a) for a in arcs],
        "noK4_cadical_sat": bool(cad4),
        "noK4_minisat_sat": bool(min4),
        "noK5_cadical_sat": bool(cad5),
        "noK5_order": order5,
        "clique_of_noK5_order": clique_of_order5,
        "omega_vec_bb": bb,
        "is_tournament": core.is_tournament(n, arcs),
        "VERIFIED_ov4": (not cad4) and (not min4) and bool(cad5)
                        and clique_of_order5 == 4 and bb == 4,
    }


# ----------------------------------------------------------------- seeding
def make_seed(kind, n, rng, classes):
    if kind == "random":
        return out_masks(n, random_tournament(n, rng))
    if kind == "qr11_pad":
        # QR_11 (ov(QR_11)=3 dom; per G2 not 4-critical) padded with n-11
        # dominated vertices (each new vertex beaten by all earlier) then a
        # few random flips on the pad to break transitivity-domination.
        assert n >= 11
        arcs = circulant(11, QR11_G)
        for w in range(11, n):
            for u in range(w):
                arcs.append((u, w))   # u beats w: w dominated
        out = out_masks(n, arcs)
        # randomize pad arcs to make them non-dominated
        for _ in range((n - 11) * 4 + 6):
            u = rng.randrange(n); v = rng.randrange(n)
            if u == v:
                continue
            if (out[u] >> v) & 1:
                out[u] &= ~(1 << v); out[v] |= 1 << u
            else:
                out[v] &= ~(1 << u); out[u] |= 1 << v
        return out
    if kind == "p9b_extend":
        # stored order-9 ov=3 class + (n-9) appended vertices, random arcs.
        ci = rng.randrange(len(classes))
        arcs9 = [tuple(a) for a in classes[ci]["arcs"]]
        arcs = list(arcs9)
        for w in range(9, n):
            for u in range(w):
                arcs.append((u, w) if rng.random() < 0.5 else (w, u))
        return out_masks(n, arcs)
    raise ValueError(kind)


def flip(out, u, v):
    if (out[u] >> v) & 1:
        out[u] &= ~(1 << v); out[v] |= 1 << u
    else:
        out[v] &= ~(1 << u); out[u] |= 1 << v


# ------------------------------------------------------------------- driver
def hunt(n, restarts, flips, seed, deadline, classes, max_blocks=8):
    rng = random.Random(seed)
    seed_kinds = ["random", "qr11_pad", "p9b_extend"]
    best_score = 10 ** 9
    sat_calls = 0
    r = -1
    for r in range(restarts):
        if time.time() > deadline:
            break
        kind = seed_kinds[r % len(seed_kinds)]
        out = make_seed(kind, n, rng, classes)
        arcs = masks_to_arcs(n, out)
        score, unsat, wits = graded_score(n, arcs, max_blocks=max_blocks)
        sat_calls += 1
        if unsat:
            return _confirm(n, out, best_score, sat_calls, r, "seed")
        best_score = min(best_score, score)
        cur = score
        for it in range(flips):
            if time.time() > deadline:
                break
            # pick a backedge arc from a random current witness order to flip
            if wits:
                w = wits[rng.randrange(len(wits))]
                be = backedge_arcs_of_order(n, out, w)
            else:
                be = []
            if be:
                u, v = be[rng.randrange(len(be))]
            else:
                u = rng.randrange(n); v = rng.randrange(n)
                if u == v:
                    continue
            flip(out, u, v)
            arcs = masks_to_arcs(n, out)
            score, unsat, wits = graded_score(n, arcs, max_blocks=max_blocks)
            sat_calls += 1
            if unsat:
                return _confirm(n, out, best_score, sat_calls, r, "flip")
            # accept if score not worse (greedy descent toward UNSAT wall),
            # else occasionally accept to escape plateaus, else revert
            if score <= cur or rng.random() < 0.10:
                cur = score
                best_score = min(best_score, score)
            else:
                flip(out, u, v)   # revert
                # keep witnesses from the reverted (current) state for guidance
                arcs = masks_to_arcs(n, out)
                _, _, wits = graded_score(n, arcs, max_blocks=2)
    return {"n": n, "hit": False, "best_score": best_score,
            "sat_calls": sat_calls, "restarts_done": r + 1}


def _confirm(n, out, best_score, sat_calls, r, where):
    cert = verify_hit(n, out)
    return {"n": n, "hit": True, "where": where, "restart": r,
            "best_score": min(best_score, 0), "sat_calls": sat_calls,
            "certificate": cert}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--restarts", type=int, default=100)
    ap.add_argument("--flips", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--budget", type=float, default=850.0)
    ap.add_argument("--max-blocks", type=int, default=8)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    classes = load_classes()
    t0 = time.time()
    res = hunt(a.n, a.restarts, a.flips, a.seed, t0 + a.budget, classes,
               max_blocks=a.max_blocks)
    res["elapsed_s"] = round(time.time() - t0, 1)
    print(json.dumps(res))
    out = a.out or os.path.join(DIR, "data", f"hunt_ov4_n{a.n}.json")
    with open(out, "w") as f:
        json.dump(res, f, indent=1)
    if res.get("hit") and res["certificate"].get("VERIFIED_ov4"):
        hp = os.path.join(DIR, "data", "hunt_ov4_small_hit.json")
        with open(hp, "w") as f:
            json.dump(res["certificate"], f, indent=1)
        print("VERIFIED_OV4_HIT", hp, flush=True)


if __name__ == "__main__":
    main()
