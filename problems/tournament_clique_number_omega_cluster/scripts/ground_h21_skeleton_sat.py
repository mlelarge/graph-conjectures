"""GROUND the H21 first-moment skeleton SAT test on C3[QR_19] (order 57, ov=5 by P23).

QUESTION (structural): does there EXIST a total order of C3[QR_19] whose backedge
graph has NO 6-clique (product clique <= 5) AND whose three induced inner QR_19
suborders each have backedge clique <= 4 (inner no-K5)?

  SAT   => an OPTIMAL-INNER clique-5 order exists: H21 first-moment skeleton survives.
  UNSAT => every clique-5 order of C3[QR_19] uses a non-optimal inner copy
           (induced inner clique 5 = ov+1) => first-moment 'pick optimal inner
           sigmas then merge' mechanism class is unreachable on this proven object.

Encoding = EXACT same audited shape as decide_ov_c3_qr19.py (P23):
  bool x_{uv}='u precedes v'; transitivity 3-clauses;
  one clause per transitive 6-chain of C3[QR_19] (no product K6);
  PLUS one clause per transitive 5-chain WITHIN each inner copy B_i (no inner K5).

Pre-step: re-solve the UNCONSTRAINED P23 no-K6 CNF, reconstruct its witness order,
and report the induced backedge clique of each of the 3 inner copies (peek at which
branch is true).
"""
import sys, os, time, signal, functools, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
from lexlib import lex_substitute, C3, is_tournament
from pysat.formula import CNF
from pysat.solvers import Cadical153, Minisat22


def _alarm(sig, frm):
    print("SELF-ALARM TIMEOUT", flush=True)
    sys.exit(2)
signal.signal(signal.SIGALRM, _alarm)
signal.alarm(560)

OUT = {"object": "C3[QR_19]", "order": 57}

# ---- build C3[QR_19] (outer C3, inner QR_19); copies B0={0..18},B1={19..37},B2={38..56} ----
QR = sorted({(x * x) % 19 for x in range(1, 19)})
arcs19 = [(i, (i + d) % 19) for i in range(19) for d in QR]
assert core.is_tournament(19, arcs19), "QR_19 not a tournament"
QR19 = (19, arcs19)
n, arcs = lex_substitute(C3, QR19)
assert is_tournament(n, arcs)
copies = [list(range(0, 19)), list(range(19, 38)), list(range(38, 57))]
print("object C3[QR_19] order", n, "QR=", QR, "copies", [(c[0], c[-1]) for c in copies], flush=True)
OUT["QR"] = QR

beats = [[False] * n for _ in range(n)]
for (u, v) in arcs:
    beats[u][v] = True
out = [0] * n
for u in range(n):
    m = 0
    for v in range(n):
        if beats[u][v]:
            m |= (1 << v)
    out[u] = m


def enum_chains(K, universe_mask=None):
    """All transitive K-subsets as source->...->sink chains. If universe_mask
    given (a bitmask of allowed vertices), restrict chains to that vertex set."""
    res = []
    ap = res.append
    full = (1 << n) - 1 if universe_mask is None else universe_mask
    def rec(chosen, cand):
        if len(chosen) == K:
            ap(tuple(chosen)); return
        m = cand
        while m:
            v = (m & -m).bit_length() - 1
            m &= m - 1
            rec(chosen + [v], cand & out[v])
    s_iter = range(n) if universe_mask is None else [i for i in range(n) if (full >> i) & 1]
    for s in s_iter:
        if universe_mask is not None:
            rec([s], out[s] & full)
        else:
            rec([s], out[s])
    return res


t0 = time.time()
chains6 = enum_chains(6)
print("product transitive 6-chains:", len(chains6), "(%.2fs)" % (time.time() - t0), flush=True)
OUT["n_chains6"] = len(chains6)

# inner transitive 5-chains, one batch per copy (restricted to that copy's vertices)
inner5 = []
for ci, c in enumerate(copies):
    mask = 0
    for v in c:
        mask |= (1 << v)
    ch = enum_chains(5, universe_mask=mask)
    inner5.append(ch)
    print("copy", ci, "inner transitive 5-chains:", len(ch), flush=True)
OUT["n_inner5_per_copy"] = [len(x) for x in inner5]

# ---- shared literal table ----
idx = {}; nv = [0]
def lit(u, v):
    if (u, v) in idx:
        return idx[(u, v)]
    if (v, u) in idx:
        return -idx[(v, u)]
    nv[0] += 1; idx[(u, v)] = nv[0]; return nv[0]
for u in range(n):
    for v in range(u + 1, n):
        lit(u, v)

def base_transitivity():
    cl = []
    for u in range(n):
        for v in range(n):
            if v == u: continue
            for w in range(n):
                if w == u or w == v: continue
                cl.append([-lit(u, v), -lit(v, w), lit(u, w)])
    return cl

TRANS = base_transitivity()
print("transitivity clauses", len(TRANS), "vars", nv[0], flush=True)


def reconstruct(model):
    mset = set(model)
    def precedes(u, v):
        l = lit(u, v)
        return (l in mset) if l > 0 else ((-l) not in mset)
    def cmp(a, b):
        if a == b: return 0
        return -1 if precedes(a, b) else 1
    return sorted(range(n), key=functools.cmp_to_key(cmp))


def inner_suborder_clique(order):
    """For each copy, backedge clique of the induced QR_19 suborder."""
    res = []
    for c in copies:
        cset = set(c)
        sub_order = [v for v in order if v in cset]
        nn, sub = core.subtournament(n, arcs, c)
        # relabel order to subtournament indices
        relabel = {v: i for i, v in enumerate(c)}
        sub_ord = [relabel[v] for v in sub_order]
        res.append(core.omega_of_order(nn, sub, sub_ord))
    return res


# ============ PRE-STEP: unconstrained P23 no-K6 witness, peek inner cliques ============
print("\n=== PRE-STEP: unconstrained P23 no-K6 witness ===", flush=True)
cnf0 = CNF()
cnf0.extend(TRANS)
for ch in chains6:
    cnf0.append([lit(ch[i], ch[i + 1]) for i in range(5)])
t = time.time()
s0 = Cadical153(bootstrap_with=cnf0.clauses)
sat0 = s0.solve()
print("unconstrained no-K6 SAT =", sat0, "(%.2fs)" % (time.time() - t), flush=True)
OUT["prestep_noK6_sat"] = bool(sat0)
if sat0:
    o0 = reconstruct(s0.get_model())
    w0 = core.omega_of_order(n, arcs, o0)
    inner0 = inner_suborder_clique(o0)
    print("  product backedge clique =", w0, "| induced inner cliques per copy =", inner0, flush=True)
    OUT["prestep_product_clique"] = w0
    OUT["prestep_inner_cliques"] = inner0
s0.delete()


# ============ MAIN: no-K6 product AND no-K5 inner ============
print("\n=== MAIN: no product-K6 + no inner-K5 (all 3 copies) ===", flush=True)
cnf = CNF()
cnf.extend(TRANS)
for ch in chains6:
    cnf.append([lit(ch[i], ch[i + 1]) for i in range(5)])
for ci, ch_list in enumerate(inner5):
    for ch in ch_list:
        cnf.append([lit(ch[i], ch[i + 1]) for i in range(4)])
print("MAIN CNF vars", nv[0], "clauses", len(cnf.clauses), flush=True)
OUT["main_n_clauses"] = len(cnf.clauses)

t1 = time.time()
s1 = Cadical153(bootstrap_with=cnf.clauses)
sat1 = s1.solve()
dt1 = time.time() - t1
print("Cadical153 (noK6 + inner-noK5) SAT =", sat1, "(%.2fs)" % dt1, flush=True)

t2 = time.time()
s2 = Minisat22(bootstrap_with=cnf.clauses)
sat2 = s2.solve()
dt2 = time.time() - t2
print("Minisat22  (noK6 + inner-noK5) SAT =", sat2, "(%.2fs)" % dt2, flush=True)
assert sat1 == sat2, "SOLVER DISAGREEMENT %s vs %s" % (sat1, sat2)
OUT["main_sat_cadical"] = bool(sat1)
OUT["main_sat_minisat"] = bool(sat2)
OUT["main_time_cadical_s"] = round(dt1, 2)
OUT["main_time_minisat_s"] = round(dt2, 2)

if sat1:
    order = reconstruct(s1.get_model())
    w = core.omega_of_order(n, arcs, order)
    inner = inner_suborder_clique(order)
    print("INDEPENDENT CHECK: product backedge clique =", w, "| inner cliques =", inner, flush=True)
    assert w <= 5, "product clique %d > 5 -- encoding bug" % w
    assert all(x <= 4 for x in inner), "inner clique > 4 -- encoding bug %s" % inner
    OUT["witness_product_clique"] = w
    OUT["witness_inner_cliques"] = inner
    OUT["witness_order"] = order
    # copy-label interleaving signature
    label = {}
    for ci, c in enumerate(copies):
        for v in c:
            label[v] = ci
    sig = [label[v] for v in order]
    OUT["witness_copy_signature"] = sig
    # per-copy d-profile (backedge in-count within copy along the order)
    print("RESULT: SAT -> optimal-inner clique-5 order EXISTS. H21 skeleton SURVIVES.", flush=True)
    print("VERDICT MAIN=SAT", flush=True)
else:
    print("RESULT: UNSAT -> every clique-5 order of C3[QR_19] forces a non-optimal inner copy.", flush=True)
    print("        First-moment 'optimal inner + merge' mechanism class is UNREACHABLE here.", flush=True)
    print("VERDICT MAIN=UNSAT", flush=True)
s1.delete(); s2.delete()

os.makedirs("data", exist_ok=True)
with open("data/ground_h21_skeleton_sat.json", "w") as f:
    json.dump(OUT, f, indent=1)
print("\nDONE; wrote data/ground_h21_skeleton_sat.json", flush=True)
