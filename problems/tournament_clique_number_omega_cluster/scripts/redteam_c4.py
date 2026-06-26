import sys, itertools

# Independent construction of AC_n[C3], deletion of (0,0), and direct test of the (2,2)-lemma.
# AC_n = Cay(Z/n, g), n=2m+1, g = {1..m-1} U {m+1}.
# C3 = 0->1->2->0.
# AC_n[C3]: vertex (t,h). Arc (t,h)->(t',h') iff (t!=t' and t->t' in AC_n) or (t==t' and h->h' in C3).

def make_g(m):
    n = 2*m+1
    g = set(range(1, m)) | {m+1}
    return n, g

def arc_AC(t, tp, n, g):
    # t -> tp in AC_n
    return ((tp - t) % n) in g

def arc_C3(h, hp):
    # C3: 0->1->2->0
    return (hp - h) % 3 == 1

def arc_sub(u, v, n, g):
    # u=(t,h), v=(tp,hp); does u->v in AC_n[C3]?
    t, h = u; tp, hp = v
    if t != tp:
        return arc_AC(t, tp, n, g)
    else:
        return arc_C3(h, hp)

def dominates(u, v, n, g):
    # u dominates v  ==  arc u->v
    return arc_sub(u, v, n, g)

def test_22_lemma(m, verbose=False):
    """For every a2=2 pair S2={(s,0),(s',0)} with backedge (so it's a valid 2-clique on h=0),
       compute X = {d=1 vertices (h in {1,2}) dominated by BOTH s,0 and s',0},
       and check X is backedge-independent (no backedge between any two members of X).
       d=1 vertices are those with h in {1,2}.
       Returns list of counterexamples (X has a backedge pair)."""
    n, g = make_g(m)
    counter = []
    blocks = list(range(n))
    # a2=2 clique: {(s,0),(s',0)} is a BACKEDGE clique means in the d_then_c order both are in
    # bands B4/B5 (d=2). A backedge clique = mutually a backedge under SOME order; but within
    # h=0 the pair is a clique iff there's an arc one way (tournament). The proof orders so that
    # the higher band dominates the lower. We just need: the pair forms an arc (so it CAN be a
    # 2-clique). For the lemma we consider ALL ordered pairs s != s' where one dominates the other.
    for s in range(n):
        for sp in range(n):
            if s == sp:
                continue
            # need (s,0),(s',0) to be a 2-clique: exactly one arc direction (tournament guarantees)
            # We don't restrict s in [m+1,2m] etc -- test ALL pairs to be maximally adversarial.
            u = (s, 0); up = (sp, 0)
            # X: vertices (t,h), h in {1,2}, dominated by both u and up.
            X = []
            for t in range(n):
                for h in (1, 2):
                    w = (t, h)
                    if dominates(u, w, n, g) and dominates(up, w, n, g):
                        X.append(w)
            # check backedge-independence: no pair in X has an arc between them
            for a, b in itertools.combinations(X, 2):
                if dominates(a, b, n, g) or dominates(b, a, n, g):
                    counter.append((m, s, sp, a, b))
                    if verbose:
                        print(f"  COUNTER m={m} s={s} s'={sp}: X-pair {a},{b} has a backedge")
    return counter

def test_incompat(m):
    """Directly test the arithmetic core: for all delta in g (delta = s - s'),
       NOT (1+delta in g  AND  (m+1+delta) mod n in g)."""
    n, g = make_g(m)
    bad = []
    for delta in range(n):
        c1 = ((1 + delta) % n) in g
        c2 = ((m + 1 + delta) % n) in g
        if c1 and c2:
            bad.append((m, delta, c1, c2))
    return bad

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "lemma"
    if mode == "lemma":
        lo = int(sys.argv[2]); hi = int(sys.argv[3])
        total_counter = []
        for m in range(lo, hi+1):
            c = test_22_lemma(m, verbose=True)
            if c:
                total_counter.extend(c)
            print(f"m={m} n={2*m+1}: {'OK (X backedge-independent for all a2=2 pairs)' if not c else f'{len(c)} COUNTEREXAMPLES'}")
        print(f"\nTOTAL counterexamples: {len(total_counter)}")
    elif mode == "incompat":
        lo = int(sys.argv[2]); hi = int(sys.argv[3])
        total_bad = []
        for m in range(lo, hi+1):
            b = test_incompat(m)
            if b:
                total_bad.extend(b)
                print(f"m={m}: INCOMPAT VIOLATED: {b}")
        print(f"incompat checked m={lo}..{hi}; violations: {len(total_bad)}")
