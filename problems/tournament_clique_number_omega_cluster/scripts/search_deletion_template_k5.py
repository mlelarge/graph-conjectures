"""EXECUTOR (H15, k=5): search for a DELETION-ORDER TEMPLATE on the two
vertex-transitive k=5 substitution candidates whose backedge graph has clique
<= 4, mirroring how d_then_c was found for k=4 (P17/P18).

Candidates (both omega_vec<=5 via the merged-key order; ledger next_action):
  (b) AC_7[AC_7]        order 49,  inner = AC_7        (vertices (a,b), a,b in Z/7)
  (a) AC_7[C3[C3]]      order 63,  inner = C3[C3]      (vertices (a,(c,d)))

For each candidate we delete v=(0,...,0) (vertex-transitive for (b); for (a) the
inner C3[C3] is itself vertex-transitive so AC_7[C3[C3]] is vertex-transitive),
and sweep a family of order TEMPLATES (sort keys built from the AC-potential
c(.) on the outer AC_7 coordinate and a layer/potential on the inner block).
We compute the EXACT backedge clique of each order on the deletion.  A template
with clique <= 4 on the deletion is the k=5 analogue of d_then_c.

Cross-check the winner (smallest order) with the no-K5 SAT oracle: deletion has
omega_vec <= 4 IFF no-K5 UNSAT.  FOREGROUND, hard signal.alarm timeout.
"""
import sys, os, json, time, signal, itertools
sys.path.insert(0, os.path.dirname(__file__))
import core
import networkx as nx
from ground_lex_compose_c3 import ac_gen, c3, lex_compose
from search_4critical_circulant import circ_arcs, omega_vec_ge_K_via_sat, validate_sat_oracle


class Timeout(Exception):
    pass


def _alarm(sig, frm):
    raise Timeout()


# AC_7 potential on a residue t (m=3): c(0)=3, c(1..3)=2, c(4..6)=1.
def c_of(t, m=3):
    if t == 0:
        return 3
    if 1 <= t <= m:
        return 2
    return 1


# d-potential on C3 layer h: d(0)=2, d(1)=d(2)=1  (P16 inner potential for C3).
def d_of(h):
    return 2 if h == 0 else 1


# --------------------------------------------------------------------------
# Build the two candidates.  Return (N, arcs, inner_decode) where inner_decode
# maps a flat block-inner index to a structured tuple for templates.
# --------------------------------------------------------------------------

def build_ac7_ac7():
    g = ac_gen(7)
    nAC, aAC = 7, circ_arcs(7, g)
    assert core.is_tournament(nAC, aAC)
    N, A = lex_compose(nAC, aAC, nAC, aAC)   # vertex flat = a*7 + b
    assert core.is_tournament(N, A)
    # decode flat -> (a, b)
    def decode(flat):
        return (flat // 7, flat % 7)
    return N, A, decode, 7   # inner size 7


def build_ac7_c3c3():
    g = ac_gen(7)
    nAC, aAC = 7, circ_arcs(7, g)
    assert core.is_tournament(nAC, aAC)
    nC, aC = c3()
    # inner = C3[C3], order 9, vertex flat = c*3 + d
    nIn, aIn = lex_compose(nC, aC, nC, aC)
    assert core.is_tournament(nIn, aIn)
    N, A = lex_compose(nAC, aAC, nIn, aIn)   # vertex flat = a*9 + inner
    assert core.is_tournament(N, A)
    def decode(flat):
        a = flat // 9
        inner = flat % 9
        c = inner // 3
        d = inner % 3
        return (a, c, d)
    return N, A, decode, 9


def backedge_clique_of_order(beats, order):
    g = nx.Graph()
    g.add_nodes_from(order)
    L = len(order)
    for i in range(L):
        a = order[i]
        for j in range(i + 1, L):
            b = order[j]
            if beats[b][a]:
                g.add_edge(a, b)
    if g.number_of_nodes() == 0:
        return 0
    return max((len(c) for c in nx.find_cliques(g)), default=1)


# --------------------------------------------------------------------------
# Template families.  A template maps decoded coords -> a sort key tuple.
# Order is ascending by (key, decoded...).  Two coordinate shapes:
#   (b) AC7[AC7]:  decode -> (a, b)             (both AC potentials)
#   (a) AC7[C3C3]: decode -> (a, c, d)          (AC outer, C3[C3] inner)
# --------------------------------------------------------------------------

def templates_ac7_ac7():
    tpls = []
    # base merged: key = c(a)+c(b)  (gives clique 5 on full; the upper-bound order)
    tpls.append(("base_merged", lambda a, b: (c_of(a) + c_of(b),)))
    # outer-first (the d_then_c analogue: order primarily by INNER potential, i.e.
    # deletion sits in outer block 0; mirror k=4 d_then_c which sorts by (d(h),c(t)))
    tpls.append(("inner_then_outer", lambda a, b: (c_of(b), c_of(a))))
    tpls.append(("outer_then_inner", lambda a, b: (c_of(a), c_of(b))))
    # merged with inner-first tie break
    tpls.append(("merged_innerfirst", lambda a, b: (c_of(a) + c_of(b), c_of(b), c_of(a))))
    tpls.append(("merged_outerfirst", lambda a, b: (c_of(a) + c_of(b), c_of(a), c_of(b))))
    # demote the deleted outer block-0 source: treat a==0 inner-block specially.
    # In k=4 d_then_c put all non-source C3 layers first. Analogue: put inner
    # block 0 (b==0, the inner-source row) LAST so it can't top cliques.
    tpls.append(("inner_b0_last",
                 lambda a, b: (c_of(a) + c_of(b), 1 if b == 0 else 0, c_of(a))))
    tpls.append(("inner_b0_first",
                 lambda a, b: (c_of(a) + c_of(b), 0 if b == 0 else 1, c_of(a))))
    # full lexicographic bands by (c(a), then b within) and reversed
    tpls.append(("band_a_then_b", lambda a, b: (c_of(a), b)))
    tpls.append(("band_b_then_a", lambda a, b: (c_of(b), a)))
    # the k=4 d_then_c was (d(h), c(t)); here both are AC, so try demoting outer
    # source a==0: lower its potential so the (0,*) row no longer tops the K-class
    def demote_a0(a, b):
        c = 1 if a == 0 else c_of(a)
        return (c + c_of(b),)
    tpls.append(("demote_a0", demote_a0))
    def demote_b0(a, b):
        c = 1 if b == 0 else c_of(b)
        return (c_of(a) + c,)
    tpls.append(("demote_b0", demote_b0))
    # demote both source coords
    def demote_both0(a, b):
        ca = 1 if a == 0 else c_of(a)
        cb = 1 if b == 0 else c_of(b)
        return (ca + cb,)
    tpls.append(("demote_both0", demote_both0))
    return tpls


def templates_ac7_c3c3():
    tpls = []
    # base merged: key = c(a) + d-potential of the inner C3[C3].
    # inner C3[C3] potential: merged on (c,d): c_of-like 3,2,2.. but C3 has only
    # 3 layers. Use p_in(c,d) = pc(c)+pd(d) with pc(0)=2,pc(1)=pc(2)=1 (P16 C3
    # potential applied to the OUTER C3 of the inner product) and pd same.
    def pin(c, d):
        pc = 2 if c == 0 else 1
        pd = 2 if d == 0 else 1
        return pc + pd      # in {2,3,4}; matches omega_vec(C3[C3])=3 band
    tpls.append(("base_merged", lambda a, c, d: (c_of(a) + pin(c, d),)))
    # inner-first (d_then_c analogue): primary by inner potential, secondary AC
    tpls.append(("inner_then_outer", lambda a, c, d: (pin(c, d), c_of(a))))
    tpls.append(("outer_then_inner", lambda a, c, d: (c_of(a), pin(c, d))))
    tpls.append(("merged_innerfirst",
                 lambda a, c, d: (c_of(a) + pin(c, d), pin(c, d), c_of(a))))
    tpls.append(("merged_outerfirst",
                 lambda a, c, d: (c_of(a) + pin(c, d), c_of(a), pin(c, d))))
    # demote outer source a==0
    def demote_a0(a, c, d):
        ca = 1 if a == 0 else c_of(a)
        return (ca + pin(c, d),)
    tpls.append(("demote_a0", demote_a0))
    # demote inner source (c,d)==(0,0)
    def demote_in0(a, c, d):
        p = 1 if (c == 0 and d == 0) else pin(c, d)
        return (c_of(a) + p,)
    tpls.append(("demote_in0", demote_in0))
    # full d_then_c-style 2-level on inner: (pd(d), pc(c), c_of(a))? expand:
    def layered(a, c, d):
        pc = 2 if c == 0 else 1
        pd = 2 if d == 0 else 1
        return (pd, pc, c_of(a))
    tpls.append(("inner_layered", layered))
    # all-inner-layers-first then AC (closest analogue of P18 5-band d_then_c)
    def inner_layers_first(a, c, d):
        pc = 2 if c == 0 else 1
        pd = 2 if d == 0 else 1
        return (pd + pc, c_of(a))
    tpls.append(("inner_sum_then_ac", inner_layers_first))
    return tpls


def order_from_template(decode, N, keyfn, deleted):
    items = []
    for flat in range(N):
        if flat == deleted:
            continue
        coords = decode(flat)
        key = keyfn(*coords)
        items.append((key, coords, flat))
    items.sort(key=lambda x: (x[0], x[1]))
    return [it[2] for it in items]


def run_candidate(name, builder, templates_fn, beats=None):
    N, A, decode, inner_sz = builder()
    beats = core.beats_matrix(N, A)
    deleted = 0   # (0,..,0) flat index 0; vertex-transitive
    print(f"\n=== {name}  order={N} (delete v=0) ===", flush=True)
    results = []
    for tname, keyfn in templates_fn():
        order = order_from_template(decode, N, keyfn, deleted)
        w = backedge_clique_of_order(beats, order)
        flag = "  <<< CLIQUE<=4" if w <= 4 else ""
        print(f"  [{tname}] deletion clique = {w}{flag}", flush=True)
        results.append({"template": tname, "deletion_clique": w, "le4": w <= 4})
    # also record full (no deletion) merged clique as sanity
    full_order = order_from_template(decode, N, templates_fn()[0][1], deleted=-1)
    full_w = backedge_clique_of_order(beats, full_order)
    print(f"  [full no-deletion, base_merged] clique = {full_w}", flush=True)
    return {"candidate": name, "order": N, "full_merged_clique": full_w,
            "templates": results,
            "winners": [r["template"] for r in results if r["le4"]],
            "N": N, "A": A, "decode_inner_sz": inner_sz}


def main():
    ht = int(os.environ.get("HARD_TIMEOUT", "850"))
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(ht)
    out = {}
    try:
        allok, _ = validate_sat_oracle()
        out["sat_oracle_validated"] = bool(allok)

        rb = run_candidate("AC7[AC7]", build_ac7_ac7, templates_ac7_ac7)
        ra = run_candidate("AC7[C3[C3]]", build_ac7_c3c3, templates_ac7_c3c3)

        # SAT spot-check the SMALLEST candidate's winner(s): omega_vec(.-0) <= 4 ?
        sat = {}
        for tag, rec, builder in [("AC7[AC7]", rb, build_ac7_ac7),
                                  ("AC7[C3[C3]]", ra, build_ac7_c3c3)]:
            if not rec["winners"]:
                sat[tag] = {"skipped": "no winner template"}
                continue
            N, A, decode, _ = builder()
            survivors = [i for i in range(N) if i != 0]
            relabel = {v: i for i, v in enumerate(survivors)}
            sub = [(relabel[u], relabel[v]) for (u, v) in A
                   if u in relabel and v in relabel]
            Nsub = len(survivors)
            t = time.time()
            ge5, dt5, _ = omega_vec_ge_K_via_sat(Nsub, sub, 5)  # UNSAT => >=5
            ge4, dt4, _ = omega_vec_ge_K_via_sat(Nsub, sub, 4)  # UNSAT => >=4
            sat[tag] = {"Nsub": Nsub, "ge5": bool(ge5), "ge4": bool(ge4),
                        "dt5": round(dt5, 2), "dt4": round(dt4, 2),
                        "omega_vec_deletion_le4": (not ge5)}
            print(f"  SAT {tag} (-0, N={Nsub}): >=5? {ge5} >=4? {ge4} "
                  f"=> deletion ov<=4? {not ge5} (t5={dt5:.2f}s)", flush=True)
        out["sat_check"] = sat

        # strip non-serializable arcs from candidate records
        for r in (rb, ra):
            r.pop("A", None)
        out["AC7_AC7"] = rb
        out["AC7_C3C3"] = ra
    except Timeout:
        out["status"] = "TIMEOUT"
        print("TIMEOUT", flush=True)
    finally:
        signal.alarm(0)

    dp = os.path.join(os.path.dirname(__file__), "..", "data",
                      "search_deletion_template_k5.json")
    os.makedirs(os.path.dirname(dp), exist_ok=True)
    with open(os.path.abspath(dp), "w") as f:
        json.dump(out, f, indent=1)
    print("WROTE", dp, flush=True)


if __name__ == "__main__":
    main()
