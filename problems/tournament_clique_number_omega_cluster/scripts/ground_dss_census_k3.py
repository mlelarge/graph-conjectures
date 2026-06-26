"""UNIVERSAL census leg (3) of the two-copy DSS proposal, at k=3.

Conjecture B (UNIVERSAL): every tournament H with ov(H)=k>=3 admits a DSS(k+1)
OPTIMAL order, i.e. an order sigma with omega(H^sigma)=k (optimal) AND
  max_t [ omega_be(sigma[1..t]) + omega_be(sigma[t+1..n]) ] <= k+1.

Per universal_needs_generic_census: run over the FULL GENERIC class via gentourng
(all iso classes), NOT circulants.  ONE counterexample (an ov=3 H with NO DSS(4)
optimal order) KILLS conjecture B.

For each H with ov(H)=3 we EXHAUSTIVELY search all n! orders (with prefix-clique
pruning) for a DSS(4) optimal order.  All omega values via the EXACT oracle
(core.clique_number on the backedge graph).
"""
import sys, os, subprocess, time, itertools
sys.path.insert(0, 'scripts')
import core
import networkx as nx

ARGV = sys.argv[1:]
MAXN = 8
for i, a in enumerate(ARGV):
    if a == '--max-n':
        MAXN = int(ARGV[i + 1])


def gentourng_classes(n):
    out = subprocess.run(['gentourng', str(n)], capture_output=True, text=True, timeout=600)
    if out.returncode != 0:
        raise RuntimeError("gentourng failed: " + out.stderr[:300])
    classes = []
    for line in out.stdout.splitlines():
        line = line.strip()
        bits = ''.join(c for c in line if c in '01')
        if len(bits) != n * (n - 1) // 2:
            continue
        arcs = []
        idx = 0
        for i in range(n):
            for j in range(i + 1, n):
                arcs.append((i, j) if bits[idx] == '1' else (j, i))
                idx += 1
        classes.append(arcs)
    return classes


def omega_be_prefix(beats, order, t):
    """omega of backedge graph on order[:t]."""
    if t == 0:
        return 0
    g = nx.Graph(); g.add_nodes_from(range(t))
    for i in range(t):
        a = order[i]
        for j in range(i + 1, t):
            b = order[j]
            if beats[b][a]:
                g.add_edge(i, j)
    return max((len(c) for c in nx.find_cliques(g)), default=1)


def disjoint_split_max(beats, order):
    """max_t [ omega_be(order[:t]) + omega_be(order[t:]) ]."""
    n = len(order)
    best = 0
    for t in range(n + 1):
        wl = omega_be_prefix(beats, order, t)
        # right part = order[t:] as an independent ordered subsequence
        right = order[t:]
        m = len(right)
        if m == 0:
            wr = 0
        else:
            g = nx.Graph(); g.add_nodes_from(range(m))
            for i in range(m):
                a = right[i]
                for j in range(i + 1, m):
                    b = right[j]
                    if beats[b][a]:
                        g.add_edge(i, j)
            wr = max((len(c) for c in nx.find_cliques(g)), default=1)
        if wl + wr > best:
            best = wl + wr
    return best


def find_dss_optimal_order(n, arcs, k, target):
    """DFS over all orders (prefix-clique pruned) looking for an OPTIMAL order
    (full omega == k) whose disjoint_split_max <= target.
    Returns (found_order or None, n_optimal_seen, n_dss_seen)."""
    beats = core.beats_matrix(n, arcs)
    n_opt = 0
    n_dss = 0
    found = None

    # incremental backedge-clique pruning: build order left-to-right; prune if the
    # prefix backedge clique already exceeds k (optimal needs full omega == k, so
    # any prefix with clique > k is hopeless).
    order = []
    used = [False] * n

    def prefix_clique(o):
        return omega_be_prefix(beats, o, len(o))

    def rec():
        nonlocal n_opt, n_dss, found
        if found is not None:
            return
        if len(order) == n:
            full = prefix_clique(order)
            if full == k:
                n_opt += 1
                dsm = disjoint_split_max(beats, order)
                if dsm <= target:
                    n_dss += 1
                    found = list(order)
            return
        for v in range(n):
            if used[v]:
                continue
            order.append(v)
            # prune: prefix clique must stay <= k
            if prefix_clique(order) <= k:
                used[v] = True
                rec()
                used[v] = False
            order.pop()
            if found is not None:
                return

    rec()
    return found, n_opt, n_dss


def main():
    t0 = time.time()
    overall_counterexamples = []
    for n in range(3, MAXN + 1):
        classes = gentourng_classes(n)
        ov3 = []
        for arcs in classes:
            ov = core.omega_vec(n, arcs)
            if ov == 3:
                ov3.append(arcs)
        print(f"n={n}: {len(classes)} iso classes, {len(ov3)} with ov=3 "
              f"(elapsed {time.time()-t0:.1f}s)", flush=True)
        no_dss = 0
        for ci, arcs in enumerate(ov3):
            found, n_opt, n_dss = find_dss_optimal_order(n, arcs, 3, 4)
            if found is None:
                no_dss += 1
                overall_counterexamples.append((n, ci, arcs, n_opt))
                print(f"  ** COUNTEREXAMPLE n={n} class#{ci}: ov=3, "
                      f"n_optimal_orders={n_opt}, NO DSS(4) optimal order. arcs={arcs}",
                      flush=True)
        print(f"  -> {len(ov3)-no_dss}/{len(ov3)} ov=3 classes ADMIT a DSS(4) optimal order"
              f" (no_dss={no_dss})", flush=True)

    print("=== SUMMARY ===", flush=True)
    print(f"total counterexamples (ov=3 H with NO DSS(4) optimal order): "
          f"{len(overall_counterexamples)}", flush=True)
    print(f"CONJ_B_DSS_EXISTENCE_HOLDS_k3: {len(overall_counterexamples)==0}", flush=True)
    print(f"elapsed {time.time()-t0:.1f}s", flush=True)


if __name__ == "__main__":
    main()
