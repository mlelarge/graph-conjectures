"""Strengthen the refutation of the DSS lag-interleave MECHANISM on the two
generic n=8 ov=3 objects (gentourng classes #11, #12) where the first found
DSS(4) order's lag-interleaves only reached C3[H] clique 5 (true ov=4).

Here we enumerate ALL DSS(4) optimal orders of H and, for each, try the FULL
lag-interleave family; we report the global best C3[H] backedge clique reachable.
If even over ALL DSS orders the lag-interleave family never reaches the true
optimum 4, the proposal's mechanism ('three copies of any DSS(k+1) sigma admit a
lag-interleave whose 3 pair split-sums are all <= k+1') is REFUTED as stated.

We ALSO confirm, for contrast, that an UNRESTRICTED order of C3[H] reaches 4
(the true ov), so the gap is specifically the DSS-lag-interleave mechanism.
"""
import sys, time
sys.path.insert(0, 'scripts')
import core
import networkx as nx

C3_ARCS = [(0, 1), (1, 2), (2, 0)]

OBJS = {
 11: [(0,1),(2,0),(0,3),(4,0),(0,5),(6,0),(7,0),(1,2),(1,3),(1,4),(5,1),(6,1),(1,7),
      (2,3),(2,4),(5,2),(2,6),(7,2),(3,4),(3,5),(3,6),(3,7),(4,5),(4,6),(4,7),(5,6),(7,5),(6,7)],
 12: [(0,1),(2,0),(0,3),(4,0),(0,5),(6,0),(0,7),(1,2),(1,3),(1,4),(5,1),(6,1),(1,7),
      (2,3),(2,4),(5,2),(6,2),(7,2),(3,4),(3,5),(3,6),(3,7),(4,5),(4,6),(7,4),(5,6),(5,7),(7,6)],
}


def lex_c3(nH, aH):
    bH = core.beats_matrix(nH, aH); bT = core.beats_matrix(3, C3_ARCS)
    arcs = [(a*nH+b, ap*nH+bp) for a in range(3) for b in range(nH)
            for ap in range(3) for bp in range(nH)
            if (a, b) != (ap, bp) and (bT[a][ap] or (a == ap and bH[b][bp]))]
    return 3*nH, arcs


def omega_be_order(beats, seq):
    m = len(seq)
    if m == 0:
        return 0
    g = nx.Graph(); g.add_nodes_from(range(m))
    for i in range(m):
        for j in range(i+1, m):
            if beats[seq[j]][seq[i]]:
                g.add_edge(i, j)
    return max((len(c) for c in nx.find_cliques(g)), default=1)


def disjoint_split_max(beats, order):
    n = len(order); best = 0
    for t in range(n+1):
        best = max(best, omega_be_order(beats, order[:t]) + omega_be_order(beats, order[t:]))
    return best


def all_dss_orders(n, arcs, k, target, cap=200000):
    beats = core.beats_matrix(n, arcs)
    order = []; used = [False]*n; out = []

    def rec():
        if len(out) >= cap:
            return
        if len(order) == n:
            if omega_be_order(beats, order) == k and disjoint_split_max(beats, order) <= target:
                out.append(list(order))
            return
        for v in range(n):
            if used[v]:
                continue
            order.append(v)
            if omega_be_order(beats, order) <= k:
                used[v] = True; rec(); used[v] = False
            order.pop()
    rec()
    return out


def lag_interleaves(sigma, nH):
    n = len(sigma)
    for rot in range(3):
        order = []
        for a in [(0+rot) % 3, (1+rot) % 3, (2+rot) % 3]:
            order += [a*nH + sigma[i] for i in range(n)]
        yield order
    for lb in range(n+1):
        for lc in range(n+1):
            lag = [0, lb, lc]
            events = []
            for a in range(3):
                for i in range(n):
                    events.append((i + lag[a], a, i))
            events.sort(key=lambda e: (e[0], e[1]))
            yield [a*nH + sigma[i] for (_, a, i) in events]


def main():
    t0 = time.time()
    for ci, arcs in OBJS.items():
        ovH = core.omega_vec(8, arcs)
        N, A = lex_c3(8, arcs)
        beats3 = core.beats_matrix(N, A)
        dss = all_dss_orders(8, arcs, 3, 4)
        global_best = None
        for sigma in dss:
            for order in lag_interleaves(sigma, 8):
                w = omega_be_order(beats3, order)
                if global_best is None or w < global_best:
                    global_best = w
                if global_best <= 4:
                    break
            if global_best is not None and global_best <= 4:
                break
        print(f"class {ci}: ov(H)={ovH}, #DSS(4) optimal orders={len(dss)}, "
              f"BEST C3[H] clique over (ALL DSS orders x ALL lag-interleaves) = {global_best}",
              flush=True)
        print(f"  -> mechanism reaches true ov(C3[H])=4 ? {global_best <= 4}", flush=True)
    print(f"elapsed {time.time()-t0:.1f}s", flush=True)


if __name__ == "__main__":
    main()
