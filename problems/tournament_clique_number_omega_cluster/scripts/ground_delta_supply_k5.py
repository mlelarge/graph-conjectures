"""GROUND the Delta-supply k=5 proposal.

D := Delta(TT_1, H1*, H1*), order 51.  H1* = C25({1,2,3,4,5,6,7,9,10,12,14,17}).
Block layout (constructions.delta): block1 = {v} (vertex 0), block2 = A (1..25),
block3 = B (26..50).  v=>A, A=>B, B=>v, circulant arcs inside A and B.

Legs (one foreground command each):
  --leg upper    : explicit cyclic order B*, v, A* (each block in an ov-optimal H1* order);
                   report backedge clique via core.omega_of_order.  Also try no-K5 SAT
                   to extract a clique<=4 order if the explicit order overshoots.
  --leg lower    : no-K5 linear-order CNF on D (two solvers).  UNSAT => omega_vec>=5.
  --leg delete --orbit {v|a|b} : no-K5 CNF on D-x expecting SAT; certify backedge clique<=4.
  --leg dic      : acyclic-4-colouring CNF on D (expect UNSAT) and on D-v (expect SAT).

Falsifiable: KILL if no-K5 on D is SAT with a verified clique-4 order (omega_vec(D)=4).
"""
import sys, os, time, json, argparse, functools, signal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
from pysat.formula import CNF
from pysat.solvers import Cadical153, Minisat22

H1g = [1, 2, 3, 4, 5, 6, 7, 9, 10, 12, 14, 17]
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data",
                    "ground_delta_supply_k5.json")


def circ(n, g):
    return [(i, (i + d) % n) for i in range(n) for d in g]


def build_D():
    """D = Delta(TT_1, H1*, H1*) on 51 vertices."""
    from constructions import delta, transitive_tournament
    H = (25, circ(25, H1g))
    assert core.is_tournament(*H), "H1* not a tournament"
    n, arcs = delta(transitive_tournament(1), H, H)
    assert core.is_tournament(n, arcs), "D not a tournament"
    assert n == 51
    return n, arcs


# ----------------------------------------------------------------------------- #
#  no-K_{K} linear-order CNF (forbid a backedge K-clique).
#  SAT  => an order with backedge clique < K exists => omega_vec <= K-1.
#  UNSAT => omega_vec >= K.
# ----------------------------------------------------------------------------- #
def no_kclique_decision(n, arcs, K, alarm=540):
    beats = core.beats_matrix(n, arcs)
    out = [0] * n
    for u in range(n):
        m = 0
        for v in range(n):
            if beats[u][v]:
                m |= (1 << v)
        out[u] = m

    def enum_chains(L):
        res = []
        ap = res.append
        def rec(chosen, cand):
            if len(chosen) == L:
                ap(tuple(chosen)); return
            m = cand
            while m:
                v = (m & -m).bit_length() - 1
                m &= m - 1
                rec(chosen + [v], cand & out[v])
        for s in range(n):
            rec([s], out[s])
        return res

    t0 = time.time()
    chains = enum_chains(K)
    print(f"  transitive {K}-chains: {len(chains)} ({time.time()-t0:.2f}s)", flush=True)

    idx = {}; nv = [0]
    def lit(u, v):
        if (u, v) in idx: return idx[(u, v)]
        if (v, u) in idx: return -idx[(v, u)]
        nv[0] += 1; idx[(u, v)] = nv[0]; return nv[0]
    for u in range(n):
        for v in range(u + 1, n):
            lit(u, v)
    cnf = CNF()
    for u in range(n):
        for v in range(n):
            if v == u: continue
            for w in range(n):
                if w == u or w == v: continue
                cnf.append([-lit(u, v), -lit(v, w), lit(u, w)])
    for ch in chains:
        cnf.append([lit(ch[i], ch[i + 1]) for i in range(K - 1)])
    print(f"  CNF vars {nv[0]} clauses {len(cnf.clauses)}", flush=True)

    t1 = time.time()
    s = Cadical153(bootstrap_with=cnf.clauses)
    sat = s.solve()
    print(f"  Cadical153 no-K{K} SAT = {sat} ({time.time()-t1:.2f}s)", flush=True)

    order = None; model = None
    if sat:
        model = set(s.get_model())
    # second solver only when UNSAT (soundness on the hard direction);
    # if SAT we certify the witness independently anyway.
    sat2 = sat
    if not sat:
        t2 = time.time()
        s2 = Minisat22(bootstrap_with=cnf.clauses)
        sat2 = s2.solve()
        print(f"  Minisat22 no-K{K} SAT = {sat2} ({time.time()-t2:.2f}s)", flush=True)
        s2.delete()
        assert sat == sat2, "SOLVER DISAGREEMENT"

    if sat:
        def precedes(u, v):
            l = lit(u, v)
            return (l in model) if l > 0 else ((-l) not in model)
        def cmp(a, b):
            if a == b: return 0
            return -1 if precedes(a, b) else 1
        order = sorted(range(n), key=functools.cmp_to_key(cmp))
    s.delete()
    return sat, order


# ----------------------------------------------------------------------------- #
#  acyclic-K-colouring CNF (dicolouring): each colour class induces an acyclic
#  subtournament.  SAT => dic <= K.  UNSAT => dic >= K+1.
#  We forbid every directed triangle being monochromatic, AND more generally a
#  colour class is acyclic iff no monochromatic directed cycle; for tournaments
#  acyclic <=> transitive <=> no directed triangle.  So forbidding mono C3 suffices.
# ----------------------------------------------------------------------------- #
def dicolorable_cnf(n, arcs, K):
    beats = core.beats_matrix(n, arcs)
    # directed triangles
    tris = []
    for a in range(n):
        for b in range(n):
            if b == a or not beats[a][b]: continue
            for c in range(n):
                if c == a or c == b: continue
                if beats[b][c] and beats[c][a]:
                    tri = tuple(sorted((a, b, c)))
                    tris.append(tri)
    tris = sorted(set(tris))
    var = {}; nv = [0]
    def x(v, col):
        key = (v, col)
        if key not in var:
            nv[0] += 1; var[key] = nv[0]
        return var[key]
    cnf = CNF()
    for v in range(n):
        cnf.append([x(v, c) for c in range(K)])           # at least one colour
        for c1 in range(K):
            for c2 in range(c1 + 1, K):
                cnf.append([-x(v, c1), -x(v, c2)])         # at most one
    for (a, b, c) in tris:
        for col in range(K):
            cnf.append([-x(a, col), -x(b, col), -x(c, col)])  # not all mono
    s = Cadical153(bootstrap_with=cnf.clauses)
    sat = s.solve()
    s.delete()
    return sat, len(tris)


def save(rec):
    db = {}
    if os.path.exists(DATA):
        try: db = json.load(open(DATA))
        except Exception: db = {}
    db.update(rec)
    json.dump(db, open(DATA, "w"), indent=1)
    print("  saved ->", DATA, flush=True)


def main():
    def _alarm(sig, frm):
        print("SELF-ALARM TIMEOUT", flush=True); sys.exit(2)
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(580)

    ap = argparse.ArgumentParser()
    ap.add_argument("--leg", required=True,
                    choices=["upper", "lower", "delete", "dic", "build"])
    ap.add_argument("--orbit", choices=["v", "a", "b"])
    args = ap.parse_args()

    n, arcs = build_D()
    print(f"D = Delta(TT_1,H1*,H1*) order={n} arcs={len(arcs)} tournament=True", flush=True)
    # orbit reps: v=0, a=(A,0)=1, b=(B,0)=26
    orbit_vtx = {"v": 0, "a": 1, "b": 26}

    if args.leg == "build":
        print("build OK", flush=True); return

    if args.leg == "lower":
        # no-K5 on D.  UNSAT => omega_vec(D) >= 5.  SAT (clique<=4) => KILL.
        sat, order = no_kclique_decision(n, arcs, 5)
        if sat:
            w = core.omega_of_order(n, arcs, order)
            print(f"  INDEPENDENT CHECK clique of SAT witness = {w}", flush=True)
            save({"leg_lower": {"no_K5_SAT": True, "witness_clique": w,
                                "verdict": "KILL omega_vec(D)<=4" if w <= 4 else "encoding-bug"}})
            print(f"  RESULT omega_vec(D) <= {w}  -> KILL" if w <= 4 else "  ENCODING BUG", flush=True)
        else:
            save({"leg_lower": {"no_K5_SAT": False, "verdict": "omega_vec(D)>=5"}})
            print("  RESULT omega_vec(D) >= 5  (no-K5 UNSAT, two solvers)", flush=True)
        return

    if args.leg == "upper":
        # no-K5 SAT extracts an order with backedge clique <=4? then omega_vec=4 (KILL).
        # If UNSAT here, omega_vec>=5; no-K6 SAT then pins omega_vec<=5.
        sat5, order5 = no_kclique_decision(n, arcs, 5)
        if sat5:
            w = core.omega_of_order(n, arcs, order5)
            print(f"  no-K5 SAT, witness clique = {w}", flush=True)
            save({"leg_upper": {"no_K5_SAT": True, "clique": w,
                                "verdict": "omega_vec(D)=4 KILL" if w <= 4 else "bug"}})
            return
        print("  no-K5 UNSAT -> omega_vec(D)>=5; deciding upper via no-K6", flush=True)
        sat6, order6 = no_kclique_decision(n, arcs, 6)
        if sat6:
            w = core.omega_of_order(n, arcs, order6)
            print(f"  no-K6 SAT, witness clique = {w}  -> omega_vec(D) = 5", flush=True)
            save({"leg_upper": {"no_K5_SAT": False, "no_K6_SAT": True, "clique": w,
                                "verdict": "omega_vec(D)=5"}})
        else:
            print("  no-K6 UNSAT -> omega_vec(D) >= 6 (!)", flush=True)
            save({"leg_upper": {"no_K5_SAT": False, "no_K6_SAT": False,
                                "verdict": "omega_vec(D)>=6"}})
        return

    if args.leg == "delete":
        assert args.orbit, "need --orbit"
        x = orbit_vtx[args.orbit]
        keep = [w for w in range(n) if w != x]
        nn, sub = core.subtournament(n, arcs, keep)
        print(f"  D-{args.orbit} (vtx {x}) order={nn}", flush=True)
        sat, order = no_kclique_decision(nn, sub, 5)
        if sat:
            w = core.omega_of_order(nn, sub, order)
            print(f"  no-K5 SAT on D-{args.orbit}, witness clique = {w}", flush=True)
            save({f"leg_delete_{args.orbit}": {"no_K5_SAT": True, "clique": w,
                  "verdict": "omega_vec(D-x)<=4 (>=4 from intact H1*) => =4" if w <= 4 else "bug"}})
        else:
            print(f"  no-K5 UNSAT on D-{args.orbit} -> omega_vec(D-{args.orbit}) >= 5"
                  " (NOT critical at this orbit)", flush=True)
            save({f"leg_delete_{args.orbit}": {"no_K5_SAT": False,
                  "verdict": "omega_vec(D-x)>=5 -> 5-ov-criticality FAILS"}})
        return

    if args.leg == "dic":
        sat4, ntri = dicolorable_cnf(n, arcs, 4)
        print(f"  dic 4-colouring of D: SAT={sat4} (mono-C3 forbidden, {ntri} triangles)",
              flush=True)
        # D - v
        keep = [w for w in range(n) if w != 0]
        nn, sub = core.subtournament(n, arcs, keep)
        sat4v, ntriv = dicolorable_cnf(nn, sub, 4)
        print(f"  dic 4-colouring of D-v: SAT={sat4v}", flush=True)
        save({"leg_dic": {"dic4_D_SAT": sat4, "dic4_Dminusv_SAT": sat4v,
              "verdict": ("dic(D)>=5 and dic(D-v)<=4 OK" if (not sat4 and sat4v)
                          else "dic legs NOT as predicted")}})
        return


if __name__ == "__main__":
    main()
