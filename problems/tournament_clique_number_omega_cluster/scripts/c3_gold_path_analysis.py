"""Checkpoint C3 (docs/h19_cancellation_argument_sketch.md): does the proven
clique-5 gold order of C3[QR_19] realise the predicted CANCELLATION structure --
(i) three DISTINCT optimal inner orders, (ii) STAGGERED clique ramps, (iii) a
ROTATING-LEADER interleaving path?

Pure analysis of the verified gold witness order (data/ground_h21_skeleton_sat.json)
against the proved H25 split-sum identity. Foreground, no oracle search.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import core
import networkx as nx

NH = 19
QR = sorted({(x * x) % 19 for x in range(1, 19)})          # quadratic residues mod 19
ARCS = [(i, (i + d) % 19) for i in range(19) for d in QR]  # i -> i+d
BEATS = core.beats_matrix(NH, ARCS)
CYCLIC_PAIRS = [(1, 0), (2, 1), (0, 2)]                    # (Y,X) with arc X->Y in C3


def omega_be_seq(seq):
    """backedge clique number of an ordered list of inner indices (later beats earlier)."""
    m = len(seq)
    if m == 0:
        return 0
    g = nx.Graph(); g.add_nodes_from(range(m))
    for i in range(m):
        for j in range(i + 1, m):
            if BEATS[seq[j]][seq[i]]:
                g.add_edge(i, j)
    return max((len(c) for c in nx.find_cliques(g)), default=1)


def prefix_profile(sigma):
    return [omega_be_seq(sigma[:a]) for a in range(len(sigma) + 1)]   # f(a), a=0..m


def suffix_profile(sigma):
    m = len(sigma)
    return [omega_be_seq(sigma[m - b:]) if b > 0 else 0 for b in range(m + 1)]  # g(b)


def ramp_positions(profile, k):
    """first index a at which profile reaches level t, for t=1..k. profile[a]=f(a)."""
    pos = {}
    for t in range(1, k + 1):
        pos[t] = next((a for a, val in enumerate(profile) if val >= t), None)
    return pos


def main():
    gold = json.load(open(os.path.join(os.path.dirname(__file__),
                                       "..", "data", "ground_h21_skeleton_sat.json")))
    wo = gold["witness_order"]
    assert len(wo) == 57
    copy = lambda v: v // NH
    inner = lambda v: v % NH

    # (i) inner orders per copy, in order of appearance
    sigma = {c: [inner(v) for v in wo if copy(v) == c] for c in range(3)}
    for c in range(3):
        assert sorted(sigma[c]) == list(range(NH)), f"copy {c} not a permutation"

    print("=== (i) INNER ORDERS ===", flush=True)
    distinct = len({tuple(sigma[c]) for c in range(3)})
    for c in range(3):
        print(f"  sigma_{c} = {sigma[c]}", flush=True)
    print(f"  distinct inner orders among the 3 copies: {distinct}  "
          f"(prediction: 3)", flush=True)

    # per-copy full backedge clique (optimal-inner check: should be k=4)
    k = 4
    f = {c: prefix_profile(sigma[c]) for c in range(3)}
    g = {c: suffix_profile(sigma[c]) for c in range(3)}
    inner_clique = {c: f[c][NH] for c in range(3)}
    print(f"  full inner backedge clique per copy = "
          f"{[inner_clique[c] for c in range(3)]}  (optimal-inner = {[k]*3})", flush=True)

    # internal tension: does some copy violate the single-order 'tight' slack f+g<=k+1 ?
    print("\n=== internal slack  max_a [ f_c(a) + g_c(m-a) ]  (tight order <= k+1=5) ===",
          flush=True)
    for c in range(3):
        worst = max(f[c][a] + g[c][NH - a] for a in range(NH + 1))
        print(f"  copy {c}: max internal split-sum = {worst}  "
              f"({'TIGHT' if worst <= k + 1 else 'OVER (needs cancellation)'})", flush=True)

    # (ii) staggered ramps
    print("\n=== (ii) PREFIX-CLIQUE RAMPS (first a reaching level t), m=19 ===", flush=True)
    centers = {}
    for c in range(3):
        rp = ramp_positions(f[c], k)
        centers[c] = rp[k]                       # a at which copy first reaches full clique k
        frac = {t: (None if rp[t] is None else round(rp[t] / NH, 2)) for t in rp}
        print(f"  copy {c}: reach levels {dict(rp)}   (as fraction of m: {frac})", flush=True)
    order_by_center = sorted(range(3), key=lambda c: centers[c])
    print(f"  copies ordered by full-clique position: {order_by_center} "
          f"at a={[centers[c] for c in order_by_center]} "
          f"(/{NH} = {[round(centers[c]/NH,2) for c in order_by_center]})", flush=True)
    spread = max(centers.values()) - min(centers.values())
    print(f"  ramp spread = {spread}/{NH} = {round(spread/NH,2)}  "
          f"(staggered if ~ phases 0, 1/3, 2/3)", flush=True)

    # (iii) reconstruct the path and trace the rotating leader
    print("\n=== (iii) PATH TRACE: H25 value, binding pair, advancing copy per step ===",
          flush=True)
    N = 57
    # j_c(p) = # copy-c vertices among first p of wo
    def jvec(p):
        js = [0, 0, 0]
        for v in wo[:p]:
            js[copy(v)] += 1
        return js

    def split_sums(js):
        out = {}
        for (Y, X) in CYCLIC_PAIRS:
            out[(Y, X)] = f[Y][js[Y]] + g[X][NH - js[X]]
        return out

    max_val = 0
    binding_seq = []     # (advancing_copy, binding_pair) per step
    over = 0
    for p in range(N + 1):
        js = jvec(p)
        ss = split_sums(js)
        val = max(ss.values())
        max_val = max(max_val, val)
        if val > k + 1:
            over += 1
        if p < N:
            adv = copy(wo[p])
            binding = max(ss, key=ss.get)
            binding_seq.append((adv, binding, val))

    print(f"  max H25 value along path = {max_val}  (must be 5 = k+1; "
          f"points over budget = {over})", flush=True)

    # rotating-leader summary: at the steps where the binding value is AT budget (==5),
    # which pair is binding, and is the advancing copy the HEAD of that pair?
    print("\n  steps where path is AT budget (value==5): (advancing_copy -> binding_pair)",
          flush=True)
    at_budget = [(adv, bind) for (adv, bind, val) in binding_seq if val == k + 1]
    # compress consecutive identical binding pairs into phases
    phases = []
    for adv, bind in at_budget:
        if not phases or phases[-1][0] != bind:
            phases.append([bind, [adv], 1])
        else:
            phases[-1][1].append(adv); phases[-1][2] += 1
    for bind, advs, cnt in phases:
        Y, X = bind
        heads = sum(1 for a in advs if a == Y)
        print(f"    pair (Y={Y},X={X}) binding for {cnt} steps; "
              f"advancing copy was HEAD(Y) in {heads}/{cnt}", flush=True)
    pair_phase_order = [tuple(p[0]) for p in phases]
    print(f"\n  binding-pair phase sequence = {pair_phase_order}", flush=True)
    distinct_pairs = len(set(pair_phase_order))
    print(f"  distinct binding pairs across phases = {distinct_pairs}/3  "
          f"(rotating leader => all 3 appear)", flush=True)

    # verdict
    print("\n=== C3 VERDICT ===", flush=True)
    print(f"  (i)   distinct inner orders = {distinct}        [predict 3]", flush=True)
    needs_cancel = any(max(f[c][a] + g[c][NH - a] for a in range(NH + 1)) > k + 1
                       for c in range(3))
    print(f"  (i')  some copy internally over-budget (cancellation used) = {needs_cancel}",
          flush=True)
    print(f"  (ii)  ramp spread = {round(spread/NH,2)} of m   [staggered ~0.33-0.66]",
          flush=True)
    print(f"  (iii) binding pair rotates through {distinct_pairs}/3 cyclic pairs", flush=True)


if __name__ == "__main__":
    main()
