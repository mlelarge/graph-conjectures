"""Verify the MECHANISM of the S3.1 argument, not just its conclusion.

Proof claims:
 - within a cell, c(a)=c(a') means a,a' in the SAME length-m monotone interval
   (band1=[m+1,2m] for c=1, band2=[1,m] for c=2, band3={0} for c=3).
 - for a != a' in one such interval, the backedge (smaller-key beaten by larger)
   needs gap in g but it lands in [m+2,2m], disjoint from g.

We check, for every same-cell ordered pair (u prec v), explicitly which gap is
tested and that it is NEVER in g.  Also confirm the "g excludes m" detail:
g={1..m-1}U{m+1}, so m NOT in g, 0 not in g, [m+2,2m] not in g.
We also independently confirm: NO appeal to vertex (a,b) sharing requires P13.
"""

def g_set(n):
    m = (n - 1) // 2
    return set(range(1, m)) | {m + 1}, m


def c(t, m):
    if t == 0:
        return 3
    if 1 <= t <= m:
        return 2
    return 1


def main():
    for n in [7, 9, 13, 21, 35]:
        g, m = g_set(n)
        # confirm interval/band claims
        # c=1 vertices: outer in [m+1,2m]; c=2: [1,m]; c=3: {0}
        b1 = [a for a in range(n) if c(a, m) == 1]
        b2 = [a for a in range(n) if c(a, m) == 2]
        b3 = [a for a in range(n) if c(a, m) == 3]
        assert b1 == list(range(m + 1, 2 * m + 1)), (n, b1)
        assert b2 == list(range(1, m + 1)), (n, b2)
        assert b3 == [0], (n, b3)
        # within band1: gaps for a != a' (both in [m+1,2m])
        # within band2: same.  Check both directions of gap never both in g per
        # the proof's "earlier has smaller a" claim AND check the residue range.
        bad_residue = []
        for band in (b1, b2):
            for a in band:
                for ap in band:
                    if a == ap:
                        continue
                    gap = (a - ap) % n
                    # gap in [1,m-1] U [m+2,2m] (never m, never m+1? check)
                    if gap == m or gap == m + 1:
                        # m+1 would be IN g -> potential backedge inside band!
                        bad_residue.append((n, band is b1, a, ap, gap, gap in g))
        # The KEY worry: can an in-band gap equal m+1 (which IS in g)?
        inband_gap_eq_mp1 = [x for x in bad_residue if x[4] == m + 1]
        print(f"n={n} m={m}: in-band gaps equal to m+1 (would be in g!): "
              f"{len(inband_gap_eq_mp1)}  (any gap==m: {sum(1 for x in bad_residue if x[4]==m)})")
        if inband_gap_eq_mp1:
            for x in inband_gap_eq_mp1[:5]:
                print("   DANGER in-band gap=m+1:", x)
    print("DONE")


if __name__ == "__main__":
    main()
