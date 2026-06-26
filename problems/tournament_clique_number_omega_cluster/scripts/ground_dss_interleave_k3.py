"""Census leg (3), MECHANISM half: for each generic ov=3 tournament H on n<=8,
find a DSS(4) optimal order sigma, build C3[H], and test the proposal's claim
that a LAG-INTERLEAVE of three copies of sigma yields an order of C3[H] whose
EXACT backedge clique (oracle) is <= 4 (= ov(H)+1).

This is the actual content that would prove ov(C3[H]) <= ov(H)+1 via DSS.
The proposal says: 'three copies of any DSS(k+1) sigma admit a lag-interleave
whose 3 pair split-sums are all <= k+1'.  We try the natural family of
lag-interleaves (slide copy boundaries) and report the BEST exact C3[H] clique.

For comparison we also report ov(C3[H]) directly (which is known/forced 4 at k=3),
so a clean PASS = some lag-interleave of the DSS order reaches clique 4.
"""
import sys, os, subprocess, time
sys.path.insert(0, 'scripts')
import core
import networkx as nx

C3_ARCS = [(0, 1), (1, 2), (2, 0)]


def gentourng_classes(n):
    out = subprocess.run(['gentourng', str(n)], capture_output=True, text=True, timeout=600)
    classes = []
    for line in out.stdout.splitlines():
        bits = ''.join(c for c in line.strip() if c in '01')
        if len(bits) != n * (n - 1) // 2:
            continue
        arcs = []; idx = 0
        for i in range(n):
            for j in range(i + 1, n):
                arcs.append((i, j) if bits[idx] == '1' else (j, i)); idx += 1
        classes.append(arcs)
    return classes


def lex_c3(nH, aH):
    bH = core.beats_matrix(nH, aH)
    bT = core.beats_matrix(3, C3_ARCS)
    arcs = [(a * nH + b, ap * nH + bp)
            for a in range(3) for b in range(nH)
            for ap in range(3) for bp in range(nH)
            if (a, b) != (ap, bp) and (bT[a][ap] or (a == ap and bH[b][bp]))]
    return 3 * nH, arcs


def omega_be_order(beats, seq):
    m = len(seq)
    if m == 0:
        return 0
    g = nx.Graph(); g.add_nodes_from(range(m))
    for i in range(m):
        for j in range(i + 1, m):
            if beats[seq[j]][seq[i]]:
                g.add_edge(i, j)
    return max((len(c) for c in nx.find_cliques(g)), default=1)


def disjoint_split_max(beats, order):
    n = len(order); best = 0
    for t in range(n + 1):
        best = max(best, omega_be_order(beats, order[:t]) + omega_be_order(beats, order[t:]))
    return best


def all_dss_orders(n, arcs, k, target, cap=200000):
    beats = core.beats_matrix(n, arcs)
    order = []; used = [False] * n; out = []

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
    """Yield C3[H] orders from lag-interleaves of 3 copies of sigma.
    Copy a uses vertices a*nH + sigma[i].  A 'lag' (la,lb,lc) shifts the START
    position of each copy in a merged timeline; we sweep the two relative lags
    over 0..n and interleave by global timeline position (ties broken by copy).
    Also include the pure-block order (copies fully separated) as a baseline.
    """
    n = len(sigma)
    # pure block orders: all 3 cyclic ways
    for rot in range(3):
        order = []
        for a in [(0 + rot) % 3, (1 + rot) % 3, (2 + rot) % 3]:
            order += [a * nH + sigma[i] for i in range(n)]
        yield ('block', rot), order
    # lag interleaves: copy a's element i appears at time i + lag[a]
    for lb in range(n + 1):
        for lc in range(n + 1):
            lag = [0, lb, lc]
            events = []  # (time, copy, i)
            for a in range(3):
                for i in range(n):
                    events.append((i + lag[a], a, i))
            events.sort(key=lambda e: (e[0], e[1]))
            order = [a * nH + sigma[i] for (_, a, i) in events]
            yield ('lag', (lb, lc)), order


def main():
    t0 = time.time()
    MAXN = 8
    if '--max-n' in sys.argv:
        MAXN = int(sys.argv[sys.argv.index('--max-n') + 1])
    fails = []
    total = 0
    for n in range(7, MAXN + 1):
        classes = gentourng_classes(n)
        ov3 = [arcs for arcs in classes if core.omega_vec(n, arcs) == 3]
        print(f"n={n}: {len(ov3)} ov=3 classes (elapsed {time.time()-t0:.1f}s)", flush=True)
        for ci, arcs in enumerate(ov3):
            dss = all_dss_orders(n, arcs, 3, 4)
            assert dss, f"no DSS order n={n} ci={ci} (should not happen, census passed)"
            N, A = lex_c3(n, arcs)
            beats3 = core.beats_matrix(N, A)
            best = None; best_tag = None
            for sigma in dss:
                for tag, order in lag_interleaves(sigma, n):
                    w = omega_be_order(beats3, order)  # == core.omega_of_order
                    if best is None or w < best:
                        best = w; best_tag = tag
                    if best <= 4:
                        break
                if best is not None and best <= 4:
                    break
            total += 1
            status = "OK" if best <= 4 else "FAIL"
            print(f"  n={n} ci={ci}: best C3[H] clique over lag-interleaves = {best} "
                  f"via {best_tag}  [{status}]", flush=True)
            if best > 4:
                fails.append((n, ci, arcs, best))
    print("=== SUMMARY ===", flush=True)
    print(f"objects tested: {total}", flush=True)
    print(f"lag-interleave failures (best clique > 4): {len(fails)}", flush=True)
    if fails:
        for f in fails[:5]:
            print("  FAIL", f, flush=True)
    print(f"DSS_INTERLEAVE_MECHANISM_HOLDS_k3: {len(fails)==0}", flush=True)
    print(f"elapsed {time.time()-t0:.1f}s", flush=True)


if __name__ == "__main__":
    main()
