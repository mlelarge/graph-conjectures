"""EXECUTOR (H13): search for an n-uniform vertex-order TEMPLATE of AC_n[C3]-v
whose backedge graph has clique <= 3, uniformly over odd n.

AC_n = Cay(Z/n, g={1..m-1}∪{m+1}), n=2m+1.  C3 = 0->1->2->0.
AC_n[C3] vertices = (t,h), t in Z/n, h in {0,1,2}; arc (t,h)->(t',h') iff
t->t' in AC_n (t!=t') or (t==t' and h->h' in C3).

The merged order key(t,h)=c(t)+d(h) gives clique 4 (proven, P16).  We delete a
vertex v and sweep ORDER TEMPLATES (a sort key as a function of t-residue-class,
h, and m).  For each template + each odd n in a range we compute the EXACT
backedge clique of that order (one max-clique call) on AC_n[C3]-v.  We report any
template giving clique <= 3 on ALL tested n.  Cross-check via the SAT no-K-clique
oracle that omega_vec(AC_n[C3]-v) is really 3 (>=3 automatic, <=3 from the order).

All foreground, hard timeout via signal.alarm.
"""
import sys, os, json, time, signal
sys.path.insert(0, os.path.dirname(__file__))
import core
import networkx as nx
from ground_lex_compose_c3 import ac_gen, c3, lex_compose
from search_4critical_circulant import circ_arcs, omega_vec_ge_K_via_sat, validate_sat_oracle


class Timeout(Exception):
    pass


def _alarm(sig, frm):
    raise Timeout()


# --- class function c(t) on AC_n (identity-order largest min-t backedge clique) ---
def c_of(t, m):
    if t == 0:
        return 3
    if 1 <= t <= m:
        return 2
    return 1  # m+1 <= t <= 2m


def d_of(h):
    return 2 if h == 0 else 1  # d(0)=2, d(1)=d(2)=1


def build(n):
    """AC_n[C3] as (N, arcs) with flat index t*3+h."""
    m = (n - 1) // 2
    g = ac_gen(n)
    nAC, aAC = n, circ_arcs(n, g)
    assert core.is_tournament(nAC, aAC)
    nC, aC = c3()
    N, A = lex_compose(nAC, aAC, nC, aC)
    assert core.is_tournament(N, A)
    return N, A, m


def backedge_clique_of_order(N, beats, order):
    """omega(backedge graph) for explicit order; order is a list of flat indices.
    Edge a-b (a before b) iff arc b->a present."""
    pos = {v: i for i, v in enumerate(order)}
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


# ---------------------------------------------------------------------------
# TEMPLATE FAMILY.  A template maps (t,h,m) -> a sort key tuple.  The order is
# ascending by (key_tuple, t, h).  We parameterize several candidate ideas.
# ---------------------------------------------------------------------------

def make_templates():
    """Return list of (name, keyfn) where keyfn(t,h,m)->tuple. The merged base is
    key=(c(t)+d(h), t, h). We try modifications targeted at the deleted vertex."""
    tpls = []

    # T0: the base merged order (sanity: should give clique 4 on full, maybe 4 or 3 on minus-v)
    def base(t, h, m):
        return (c_of(t, m) + d_of(h),)
    tpls.append(("base_merged", base))

    # T1: pure c(t)+d(h) but with (0,0) treated as lowest (since we delete it,
    # this is moot for v=(0,0); but try for other v). Lower the (0,*) potential.
    def t1(t, h, m):
        c = c_of(t, m)
        return (c + d_of(h),)
    tpls.append(("merged_same", t1))

    # T2: separate the K=4 class (the dangerous block-0/(t,0)-chain) by pushing
    # the C3-internal order to break the cross cliques: key = (c(t), d(h)) lexicographic
    def t2(t, h, m):
        return (c_of(t, m), d_of(h))
    tpls.append(("c_then_d", t2))

    # T3: (d(h), c(t)) — order primarily by C3-layer
    def t3(t, h, m):
        return (d_of(h), c_of(t, m))
    tpls.append(("d_then_c", t3))

    # T4: refine c(t) to a finer 'distance' potential. In AC_n identity order the
    # backedge clique grows with t; use c'(t)=0 if t==0 else (1 if t<=m else 2)+...
    # Try the *reverse* potential 2m - t style smoothing.
    def t4(t, h, m):
        # finer: position of t within its residue band
        c = c_of(t, m)
        return (c + d_of(h), c, d_of(h))
    tpls.append(("merged_refined", t4))

    # T5: shift the deleted-vertex block. If v=(0,0), the surviving (0,1),(0,2)
    # (key 4) and the (t,0) chain form the 4-clique source. Demote (0,1),(0,2)
    # by giving t==0 the SAME c as the high band (c=1) so they no longer top the
    # K=4 class.
    def t5(t, h, m):
        c = 1 if t == 0 else (2 if 1 <= t <= m else 1)
        return (c + d_of(h),)
    tpls.append(("demote_zero", t5))

    # T6: promote t==0 fully (c large) and use d to split
    def t6(t, h, m):
        c = c_of(t, m)
        # break ties within K=4 class by putting (t,0) before (0,1),(0,2)
        layer0 = 0 if h == 0 else 1
        return (c + d_of(h), layer0)
    tpls.append(("merged_h0first", t6))

    # T7: reverse tie-break: (0,1),(0,2) before (t,0)
    def t7(t, h, m):
        c = c_of(t, m)
        layer0 = 1 if h == 0 else 0
        return (c + d_of(h), layer0)
    tpls.append(("merged_h0last", t7))

    # T8: a 3-key idea: sort by t band, then within band by (h, t)
    def t8(t, h, m):
        band = 0 if t == 0 else (1 if t <= m else 2)
        return (band, h, t)
    tpls.append(("band_h_t", t8))

    # T9: finer c using exact identity-order min-t clique value per t.
    # In AC_n identity order, the unique 3-clique is {0,m,2m}. Give graded keys:
    # t in {0}:3, t in {m,2m}:special. Use c(t) plus a within-band sub-key = t.
    def t9(t, h, m):
        return (c_of(t, m) + d_of(h), t, h)
    tpls.append(("merged_t_subkey", t9))

    # T10: same with reversed sub-key t
    def t10(t, h, m):
        return (c_of(t, m) + d_of(h), -t, h)
    tpls.append(("merged_negt_subkey", t10))

    return tpls


def order_from_template(N, m, keyfn, deleted):
    """Build the order (list of surviving flat indices) by sorting (t,h) by
    (keyfn(t,h,m), t, h)."""
    items = []
    n = 2 * m + 1
    for t in range(n):
        for h in range(3):
            flat = t * 3 + h
            if flat == deleted:
                continue
            items.append((keyfn(t, h, m), t, h, flat))
    items.sort(key=lambda x: (x[0], x[1], x[2]))
    return [it[3] for it in items]


def main():
    ap_timeout = int(os.environ.get("HARD_TIMEOUT", "850"))
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(ap_timeout)

    out = {"templates": [], "ns": []}
    try:
        # validate SAT oracle once
        allok, _ = validate_sat_oracle()
        out["sat_oracle_validated"] = bool(allok)
        if not allok:
            print("SAT ORACLE FAILED VALIDATION", flush=True)

        ns = list(range(7, 32, 2))  # 7,9,...,31
        out["ns"] = ns
        templates = make_templates()

        # Precompute graphs/beats per n
        graph_cache = {}
        for n in ns:
            N, A, m = build(n)
            beats = core.beats_matrix(N, A)
            graph_cache[n] = (N, A, m, beats)

        # By vertex transitivity delete v=(0,0) flat index 0.
        deleted = 0

        results = []
        for name, keyfn in templates:
            per_n = {}
            worst = 0
            for n in ns:
                N, A, m, beats = graph_cache[n]
                order = order_from_template(N, m, keyfn, deleted)
                w = backedge_clique_of_order(N, beats, order)
                per_n[n] = w
                worst = max(worst, w)
            rec = {"name": name, "worst_clique": worst, "per_n": per_n,
                   "uniform_le3": worst <= 3}
            results.append(rec)
            flag = "  <<< CLIQUE<=3 UNIFORM" if worst <= 3 else ""
            print(f"[{name}] worst={worst} per_n={per_n}{flag}", flush=True)
        out["templates"] = results

        winners = [r for r in results if r["uniform_le3"]]
        out["winners"] = [r["name"] for r in winners]

        # Cross-check the winners (or the best) via SAT no-K-clique oracle:
        # omega_vec(AC_n[C3]-0) >= 4 ?  (UNSAT => >=4 => template can't beat it)
        # We want >=4 to be FALSE (i.e. SAT => omega_vec<=3) and >=3 TRUE.
        sat_check = {}
        for n in [7, 9, 11]:
            N, A, m, beats = graph_cache[n]
            # delete vertex 0: build subtournament on survivors
            survivors = [i for i in range(N) if i != deleted]
            relabel = {v: i for i, v in enumerate(survivors)}
            subarcs = [(relabel[u], relabel[v]) for (u, v) in A
                       if u in relabel and v in relabel]
            Nsub = len(survivors)
            ge4, dt4, _ = omega_vec_ge_K_via_sat(Nsub, subarcs, 4)
            ge3, dt3, _ = omega_vec_ge_K_via_sat(Nsub, subarcs, 3)
            sat_check[n] = {"ge4": bool(ge4), "ge3": bool(ge3),
                            "Nsub": Nsub, "dt4": round(dt4, 3), "dt3": round(dt3, 3)}
            print(f"  SAT check n={n} (AC_n[C3]-0, N={Nsub}): >=4? {ge4}  >=3? {ge3}",
                  flush=True)
        out["sat_check_deletion"] = sat_check

    except Timeout:
        out["status"] = "TIMEOUT"
        print("TIMEOUT", flush=True)
    finally:
        signal.alarm(0)

    dp = os.path.join(os.path.dirname(__file__), "..", "data",
                      "search_deletion_template_k4.json")
    os.makedirs(os.path.dirname(dp), exist_ok=True)
    with open(dp, "w") as f:
        json.dump(out, f, indent=1)
    print("WROTE", dp, flush=True)


if __name__ == "__main__":
    main()
