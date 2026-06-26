"""Fast bitset Tomita-style max-clique (and capped variant) for backedge graphs.

Much faster than the networkx-based core.omega_of_order for checking a SPECIFIC order's
backedge clique (on S~_6, order 243: ~0.002s for a well-structured order vs ~7s via
networkx find_cliques; verified to agree).  Adjacency is bitsets (Python ints).

NOTE on limits (2026-06-12): this DID NOT crack w_6 = omega_vec(S~_6) via local search.
Reason: rejecting a clique-increasing move is cheap (cap prunes once a (cap+1)-clique is
found), but every ACCEPTED move keeping the clique at its current value K requires a
near-full search to VERIFY max = K on the dense order-243 backedge graph -- intrinsically
slow.  So order-243 local search does not converge to a useful w_6 upper bound, and w_6
stays in [6,9].  Kept for fast specific-order clique checks and future use.
"""

def backedge_adj(n, beats, order):
    """adjacency bitsets of the backedge graph of `order` (edge iff later beats earlier)."""
    adj = [0]*n
    for i in range(n):
        a = order[i]
        for j in range(i+1, n):
            b = order[j]
            if beats[b][a]:
                adj[a] |= (1 << b); adj[b] |= (1 << a)
    return adj

def max_clique(adj, n):
    """exact max-clique number via Tomita BB with greedy-colouring bound."""
    best = [0]
    def expand(R, P):
        order = []; col = []; unc = P; c = 0
        while unc:                                   # greedy colouring of P
            c += 1; avail = unc
            while avail:
                v = (avail & -avail).bit_length()-1; vb = 1 << v
                order.append(v); col.append(c)
                unc &= ~vb; avail &= ~vb; avail &= ~adj[v]
        for i in range(len(order)-1, -1, -1):        # high colour first
            if R + col[i] <= best[0]: return
            v = order[i]; vb = 1 << v; nP = P & adj[v]
            if nP: expand(R+1, nP)
            elif R+1 > best[0]: best[0] = R+1
            P &= ~vb
    expand(0, (1 << n) - 1)
    return best[0]

def capped_clique(adj, n, cap):
    """min(max_clique, cap+1): stops early once the clique exceeds cap (cheap rejection)."""
    best = [0]
    def expand(R, P):
        if best[0] > cap: return
        order = []; col = []; unc = P; c = 0
        while unc:
            c += 1; avail = unc
            while avail:
                v = (avail & -avail).bit_length()-1; vb = 1 << v
                order.append(v); col.append(c)
                unc &= ~vb; avail &= ~vb; avail &= ~adj[v]
        for i in range(len(order)-1, -1, -1):
            if R + col[i] <= best[0] or best[0] > cap: return
            v = order[i]; vb = 1 << v; nP = P & adj[v]
            if nP: expand(R+1, nP)
            elif R+1 > best[0]: best[0] = R+1
            P &= ~vb
    expand(0, (1 << n) - 1)
    return best[0]

def omega_of_order(n, beats, order):
    """drop-in fast replacement for core.omega_of_order (specific-order backedge clique)."""
    return max_clique(backedge_adj(n, beats, order), n)
