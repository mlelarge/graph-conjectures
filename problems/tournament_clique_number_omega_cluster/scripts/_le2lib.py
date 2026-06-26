"""Independent LOWER-BOUND verification for AC_17 via a fast bitmask
triangle-free-order search, plus VALIDATION of that reformulation against
the canonical core.omega_vec_bb on small circulants.

Reformulation (independently justified):
  omega_vec(T) = min over total orders prec of omega(backedge graph).
  omega(G) <= 2  iff  G is triangle-free.
  So omega_vec(T) <= 2  iff  SOME total order yields a triangle-free backedge graph.
  Hence: no triangle-free order exists  =>  omega_vec(T) >= 3.
Combined with an explicit order giving omega=3 (upper bound), omega_vec(T)=3.

Soundness of incremental triangle test: when placing b after prefix `placed`
in prec order, b's backedge neighbours are exactly {a in placed : b->a}.
Adjacency among already-placed vertices is FINAL (an edge a-c with a,c placed is
fixed once both are placed). So a new triangle can only be {b, x, y} with x,y in
nb(b) and x~y already. Checking that is exact.
"""
import os
import sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core

def has_le2_order_bitmask(n, arcs, fixed_first=None, all_starts=False, time_budget=None):
    bm = core.beats_matrix(n, arcs)
    # backedge-down sets: bdown[b] = bitmask of a with b->a  (potential backedge nbrs)
    bdown = [0]*n
    for b in range(n):
        for a in range(n):
            if bm[b][a]:
                bdown[b] |= (1 << a)
    full = (1 << n) - 1
    adj = [0]*n          # current backedge adjacency among placed (bitmask)
    start = time.time()
    timed_out = [False]

    def dfs(placed_mask):
        if time_budget and time.time()-start > time_budget:
            timed_out[0] = True
            return False
        if placed_mask == full:
            return True
        remaining = full & ~placed_mask
        r = remaining
        while r:
            b = (r & -r).bit_length() - 1
            r &= r - 1
            nb = bdown[b] & placed_mask          # backedge nbrs among placed
            # triangle iff two placed nbrs are adjacent: any x in nb with adj[x]&nb != x-bit
            tri = False
            m = nb
            while m:
                x = (m & -m).bit_length() - 1
                m &= m - 1
                if adj[x] & nb:                  # x adjacent to another placed nbr of b
                    tri = True
                    break
            if tri:
                continue
            # place b
            bbit = 1 << b
            mm = nb
            while mm:
                a = (mm & -mm).bit_length() - 1
                mm &= mm - 1
                adj[a] |= bbit
            adj[b] = nb
            if dfs(placed_mask | bbit):
                return True
            # undo
            mm = nb
            while mm:
                a = (mm & -mm).bit_length() - 1
                mm &= mm - 1
                adj[a] &= ~bbit
            adj[b] = 0
        return False

    if all_starts:
        for s in range(n):
            for i in range(n): adj[i] = 0
            adj[s] = 0
            if dfs(1 << s):
                return True, timed_out[0]
        return False, timed_out[0]
    else:
        s = 0 if fixed_first is None else fixed_first
        adj[s] = 0
        res = dfs(1 << s)
        return res, timed_out[0]

def circ(p, gen):
    return [(i, (i + d) % p) for i in range(p) for d in gen]

