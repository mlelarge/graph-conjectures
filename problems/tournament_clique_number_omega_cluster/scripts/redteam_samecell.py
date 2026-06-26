"""INDEPENDENT red-team of CLAIM (proof S3.1): under inner_then_outer order
key=(c(b),c(a),a,b), there is NO backedge between two vertices in the SAME cell
(c(b),c(a)).

I re-derive EVERYTHING from the proof text definitions. No repo imports.

n = 2m+1, g = {1..m-1} U {m+1}  (subset of Z/n).
Vertex (a,b), a,b in Z/n.
Arc (a,b) -> (a',b') iff
   [a != a' and (a'-a) mod n in g]   OR
   [a == a'  and (b'-b) mod n in g].
c(t) = 3 if t==0 ; 2 if 1<=t<=m ; 1 if m+1<=t<=2m.
key(a,b) = (c(b), c(a), a, b)   (ascending order = the inner_then_outer order).

Backedge graph for order: vertices u,v with u prec v (key(u) < key(v)) and the
arc v->u present (backward arc) => edge.  A "backedge between two same-cell
vertices" means: two vertices u,v in the same cell with an edge in the backedge
graph, i.e. (smaller-key one is beaten by the larger-key one).

We brute-force ALL ordered pairs within each cell for many n and report any
same-cell backedge.
"""

def g_set(n):
    assert n % 2 == 1 and n >= 7
    m = (n - 1) // 2
    return set(range(1, m)) | {m + 1}, m


def c(t, m):
    if t == 0:
        return 3
    if 1 <= t <= m:
        return 2
    return 1  # m+1 .. 2m


def beats(u, v, g, n):
    """arc u->v present?  u=(a,b), v=(a',b')."""
    a, b = u
    ap, bp = v
    if a != ap:
        return ((ap - a) % n) in g
    else:
        return ((bp - b) % n) in g


def key(u, m):
    a, b = u
    return (c(b, m), c(a, m), a, b)


def cell(u, m):
    a, b = u
    return (c(b, m), c(a, m))


def check_n(n):
    g, m = g_set(n)
    verts = [(a, b) for a in range(n) for b in range(n)]
    # sanity: it IS a tournament (exactly one arc per pair)
    bad_tour = 0
    # group by cell
    from collections import defaultdict
    cells = defaultdict(list)
    for u in verts:
        cells[cell(u, m)].append(u)

    violations = []
    for cl, members in cells.items():
        for i in range(len(members)):
            for j in range(len(members)):
                if i == j:
                    continue
                u = members[i]
                v = members[j]
                # require u prec v
                if key(u, m) < key(v, m):
                    # backedge iff v beats u (backward arc v->u)
                    if beats(v, u, g, n):
                        violations.append((cl, u, v))
    return violations, len(verts)


def tournament_sanity(n):
    g, m = g_set(n)
    verts = [(a, b) for a in range(n) for b in range(n)]
    bad = 0
    for i in range(len(verts)):
        for j in range(i + 1, len(verts)):
            u, v = verts[i], verts[j]
            f = beats(u, v, g, n)
            r = beats(v, u, g, n)
            if f == r:  # both or neither => not a tournament
                bad += 1
    return bad


def main():
    for n in [7, 9, 11, 13, 15, 17, 19, 21, 25, 31, 39, 49]:
        viol, nv = check_n(n)
        bad_tour = tournament_sanity(n) if n <= 21 else "skip"
        print(f"n={n} (m={(n-1)//2}) verts={nv} not-tournament-pairs={bad_tour} "
              f"SAME-CELL BACKEDGES={len(viol)}")
        if viol:
            for v in viol[:20]:
                print("   VIOLATION:", v)
    print("DONE")


if __name__ == "__main__":
    main()
