"""STEP 2 (the real deliverable): minimum RESOLUTION REFUTATION WIDTH W(p) of
phi_{C_p(g)} for the almost-consecutive family, and a test of cyclic-shift
uniformity of the clauses used.

Width-w resolution saturation (Ben-Sasson--Wigderson, sound & complete for the
EXISTENCE of a width-w refutation): repeatedly resolve pairs of clauses; keep a
resolvent only if its width <= w; if the empty clause appears, a width-w
refutation exists.  W(p) = smallest w for which the empty clause is derivable.

This is EXACT (no heuristic): width-w saturation derives the empty clause iff a
width-w refutation exists.  We also subsume (drop a clause if a subset clause is
present) to keep the set small -- subsumption is sound and does not change
derivability of the empty clause.

phi_{C_p(g)}: variables x_{u,v} (u<v).  Clauses:
  - transitivity:  (-uv | -vw | uw)  for all ordered triples (3-clauses)
  - forbidden:     (b<a | c<b)        for each transitive triple (a,b,c) (2-clauses)
We also need totality/antisymmetry, which is BUILT IN by using one variable per
unordered pair with sign = direction (x_{v,u} = -x_{u,v}); there are no separate
totality clauses, exactly as in Step 1 (validated == oracle).

We measure W(7), W(11), W(13).  We ALSO record, at the minimum width, whether the
multiset of clauses ACTUALLY USED in a derivation of the empty clause is closed
under the cyclic shift sigma: v -> v+1 mod p (acting on variable indices).
"""
import os
import sys, time, json, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core


def circ_arcs(p, g):
    return [(i, (i + d) % p) for i in range(p) for d in g]

def ac_g(p):
    return set(range(1, (p - 3) // 2 + 1)) | {(p + 1) // 2}


# ---- literal encoding: a literal is an ordered pair (u,v) meaning u<v.
# canonical var = frozenset? we use signed int: id(u,v) = +/- of a canonical pair var.
def make_varmap(p):
    pair_id = {}
    nid = 0
    for u in range(p):
        for v in range(u + 1, p):
            nid += 1
            pair_id[(u, v)] = nid
    def lit(u, v):
        if u < v:
            return pair_id[(u, v)]
        else:
            return -pair_id[(v, u)]
    return lit


def build_clauses(p, arcs):
    beats = core.beats_matrix(p, arcs)
    lit = make_varmap(p)
    clauses = set()
    # transitivity 3-clauses
    for u in range(p):
        for v in range(p):
            if v == u: continue
            for w in range(p):
                if w == u or w == v: continue
                cl = frozenset([-lit(u, v), -lit(v, w), lit(u, w)])
                # tautology check: contains x and -x
                if any(-x in cl for x in cl):
                    continue
                clauses.add(cl)
    # forbidden 2-clauses: (b<a | c<b)
    for a in range(p):
        for b in range(p):
            if b == a: continue
            for c in range(p):
                if c == a or c == b: continue
                if beats[c][a] and beats[c][b] and beats[b][a]:
                    cl = frozenset([lit(b, a), lit(c, b)])
                    if any(-x in cl for x in cl):
                        continue
                    clauses.add(cl)
    return clauses


def resolve(c1, c2):
    """All resolvents of c1,c2 on a unique clashing literal. Returns list of
    frozenset resolvents (skip tautologies)."""
    out = []
    for x in c1:
        if -x in c2:
            r = (c1 - {x}) | (c2 - {-x})
            if any(-y in r for y in r):
                continue  # tautology
            out.append(frozenset(r))
    return out


def width_w_refutable(clauses, w, time_budget):
    """Width-w saturation. Returns (refuted: bool, used_clause_set or None,
    n_clauses_at_saturation, timed_out: bool).

    Sound & complete: derives empty clause iff a width-w refutation exists,
    PROVIDED we run to fixpoint within the time budget. If we time out before
    fixpoint WITHOUT deriving empty, result is INCONCLUSIVE (timed_out=True).
    """
    t0 = time.time()
    # keep only clauses of width <= w (wider input clauses cannot appear in a
    # width-w refutation derivation -- but ALL our input clauses have width<=3,
    # so for w>=3 they all qualify; for w<3 only the 2-clauses qualify).
    S = set(c for c in clauses if len(c) <= w)
    # subsumption: drop c if a proper subset is in S
    def subsumed(c, against):
        for d in against:
            if d <= c and d != c:
                return True
        return False
    # parent tracking for the empty-clause derivation cone
    parents = {}  # clause -> (p1,p2) or None for axioms
    for c in S:
        parents[c] = None
    frontier = list(S)
    empty = frozenset()
    while frontier:
        if time.time() - t0 > time_budget:
            return (False, None, len(S), True)
        newf = []
        cur = list(S)
        # resolve frontier x all
        for c1 in frontier:
            for c2 in cur:
                if time.time() - t0 > time_budget:
                    return (False, None, len(S), True)
                for r in resolve(c1, c2):
                    if len(r) > w:
                        continue
                    if r in S:
                        continue
                    # subsumption: skip if already covered
                    if subsumed(r, S):
                        continue
                    S.add(r)
                    parents[r] = (c1, c2)
                    newf.append(r)
                    if r == empty:
                        used = collect_cone(empty, parents)
                        return (True, used, len(S), False)
        frontier = newf
    return (False, None, len(S), False)


def collect_cone(c, parents):
    """All AXIOM (input) clauses in the derivation cone of clause c."""
    seen = set()
    axioms = set()
    stack = [c]
    while stack:
        x = stack.pop()
        if x in seen: continue
        seen.add(x)
        pr = parents.get(x)
        if pr is None:
            axioms.add(x)
        else:
            stack.append(pr[0]); stack.append(pr[1])
    return axioms


def shift_clause(c, p):
    """Apply sigma: v->v+1 mod p to a clause (set of signed pair-vars)."""
    lit = make_varmap(p)
    out = []
    # invert: need vertex pair from var id. rebuild inverse map
    inv = {}
    nid = 0
    for u in range(p):
        for v in range(u + 1, p):
            nid += 1
            inv[nid] = (u, v)
    for x in c:
        sign = 1 if x > 0 else -1
        (u, v) = inv[abs(x)]
        # literal meaning: if x>0 means u<v ; if x<0 means v<u
        if sign > 0:
            uu, vv = u, v          # u<v
        else:
            uu, vv = v, u          # v<u
        uu2, vv2 = (uu + 1) % p, (vv + 1) % p
        out.append(lit(uu2, vv2))
    return frozenset(out)


def is_sigma_invariant(clause_set, p):
    shifted = set(shift_clause(c, p) for c in clause_set)
    return shifted == set(clause_set)


def main():
    out = {"results": []}
    for p in [7, 11, 13]:
        g = ac_g(p)
        arcs = circ_arcs(p, g)
        clauses = build_clauses(p, arcs)
        n2 = sum(1 for c in clauses if len(c) == 2)
        n3 = sum(1 for c in clauses if len(c) == 3)
        rec = {"p": p, "g": sorted(g), "n_clauses": len(clauses),
               "n_2clauses": n2, "n_3clauses": n3, "W": None, "widths": {}}
        print(f"\n=== p={p} g={sorted(g)}  clauses={len(clauses)} (2cl={n2},3cl={n3}) ===")
        Wp = None
        used_at_W = None
        # try increasing width. cap at some w_max; per-width budget.
        for w in range(2, 9):
            t0 = time.time()
            refuted, used, ssz, timed = width_w_refutable(clauses, w, time_budget=120)
            dt = time.time() - t0
            rec["widths"][str(w)] = {"refuted": refuted, "sat_set_size": ssz,
                                     "timed_out": timed, "time_s": round(dt, 1)}
            status = "REFUTED" if refuted else ("TIMEOUT" if timed else "no-empty(saturated)")
            print(f"  width w={w}: {status}  |S|={ssz}  ({dt:.1f}s)")
            if refuted:
                Wp = w
                used_at_W = used
                break
            if timed:
                # cannot conclude this width; but a higher width is even harder.
                # record and stop climbing (inconclusive above).
                rec["climb_stopped_timeout"] = w
                break
        rec["W"] = Wp
        if used_at_W is not None:
            sig = is_sigma_invariant(used_at_W, p)
            rec["n_axioms_in_refutation"] = len(used_at_W)
            rec["refutation_cone_sigma_invariant"] = sig
            print(f"  => W({p}) = {Wp}; axioms used = {len(used_at_W)}; "
                  f"cone sigma-invariant = {sig}")
        out["results"].append(rec)
    Ws = [(r["p"], r["W"]) for r in out["results"]]
    out["W_sequence"] = Ws
    print("\nW sequence (p, W):", Ws)
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'sat_refutation_width.json'), "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out))


if __name__ == "__main__":
    main()
