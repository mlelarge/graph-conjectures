"""spine_branch2_construct.py -- CONSTRUCT-OR-REFUTE for the H8-SPINE /
O2b* branch-(2) kernel (ledger next_action).

QUESTION.  Does there exist an IN-CLASS 3-arc-strong chord-contraction
multidigraph D^bullet with a strictly rho-headless gateway in which EVERY
h-to-R path through O is LOAD-BEARING -- i.e. for every directed path
P: h=o_0 -> o_1 -> ... -> o_m -> w (o_i in O, w in R) some D_O-arc of
A_O(P), when deleted, disconnects an O-vertex from rho in D_O?  If such a
"forced single-escape spine" exists in-class then T4 (the multi-step relay
repair) is INAPPLICABLE for every choice and the repair would need a new
mechanism (T5, spine absorption).

CANDIDATE IMPOSSIBILITY (from next_action): a forced single-escape spine
needs d_O-out = 1 along the whole h->rho path; the next_action conjectures
lambda>=3 + the I/K structure may forbid this.  But the relay_free witness
already shows a single D_O-out vertex (head 7, with 7->5 its ONLY D_O-arc)
coexisting with lambda=3, because the OTHER 3 out-arcs of 7 head into the
absorbed cage X*_w and are NOT D_O-arcs.  So the lambda accounting does NOT
forbid d_O-out=1.  This script DIRECTLY builds a maximally-forced spine and
checks whether the load-bearing condition can hold while D^bullet is
in-class (3-arc-strong, (1,0)-near-split host, real failing gateway pair).

CONSTRUCTION.  Host on V1={p=0,q=1,u=2} (chord a=(0,1)) and V2 semicomplete.
D_O is engineered as a SINGLE directed induced path (the spine)

    h -> s_1 -> s_2 -> ... -> s_L -> w   (in D^bullet, after contraction)

where each spine vertex s_i carries ONLY ONE D_O-out-arc (to s_{i+1}); the
remaining out-arcs of s_i go into the cage (absorbed set), supplying
connectivity for lambda>=3 without creating a D_O alternative.  Because the
spine is a single chain with no shortcuts, deleting ANY spine arc (s_i,
s_{i+1}) leaves s_i with no path to rho through O -- every h->w path uses
the whole spine, and each of its arcs is load-bearing.  We then test:
  (1) host is (1,0)-near-split and oracle lambda == 3 (in-class);
  (2) contraction D^bullet has lambda == 3;
  (3) there is a real strictly rho-headless FAILING gateway pair at a;
  (4) the load-bearing condition holds: for the candidate w, NO h->w path P
      has D_O - A_O(P) keeping every O-vertex reachable to rho (T4 fails).
Then it reports the verdict.

This is an EXISTENTIAL construction attempt (a witness settles branch-2);
if the construction is NOT in-class (lambda<3 forced), that is the
empirical signal supporting the impossibility direction.
"""
from __future__ import annotations

import os
import sys
from collections import Counter
from itertools import combinations

_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE = os.path.join(os.path.dirname(_HERE), "code")
for _p in (_CODE, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def build_host(spine_len: int = 3):
    """Return host arcs on V1={0,1,2}, V2={3..}, with a forced single-escape
    spine of length `spine_len` between the escaped head and the rho-tail w.

    Labels (host, before contraction):
      p=0, q=1, u=2          (V1; chord a=(0,1))
      cage = 3,4,5           (the C_u kernel; semicomplete triangle into u)
      h0, h1 = 6, 7          (the two escaped AV_u heads; h0 enters the spine)
      spine s_1..s_L         (forced chain; here L = spine_len)
      w0, w1, w2             (the R-layer / rho-tails)
    All outside K-vertices dominate the cage (gives them cage hooks and
    feeds lambda from the absorbed side).
    """
    cage = (3, 4, 5)
    h0, h1 = 6, 7
    base = 8
    spine = tuple(range(base, base + spine_len))      # s_1..s_L
    wbase = base + spine_len
    rho_tails = (wbase, wbase + 1, wbase + 2)          # w0=wbase is candidate w
    n = wbase + 3

    arcs = [(0, 1)]                                    # chord a
    # cage semicomplete triangle, cage -> u
    arcs += [(x, y) for x in cage for y in cage if x != y]
    arcs += [(x, 2) for x in cage]
    # u -> escaped heads
    arcs += [(2, h0), (2, h1)]
    # h1 helper arc so it is a genuine second escaped head (points at h0)
    arcs += [(7, 6)]

    # THE SPINE in D_O: h0 -> s_1 -> ... -> s_L -> w0, single chain.
    chain = (h0,) + spine + (rho_tails[0],)
    for a_, b_ in zip(chain, chain[1:]):
        arcs.append((a_, b_))

    # Each spine vertex's OTHER out-arcs go into the cage only (no D_O alt).
    # (cage domination below already adds spine -> cage.)
    # rho-tails are semicomplete among themselves and reach rho via contraction
    arcs += [(x, y) for x in rho_tails for y in rho_tails if x != y]
    # rho-tails dominate the escaped heads (full domination, rho-headless)
    arcs += [(r, hh) for r in rho_tails for hh in (h0, h1)]
    # rho-tails dominate the spine (so spine vertices are reached / semicomplete)
    arcs += [(r, s) for r in rho_tails for s in spine]

    # rho-tail -> rho (i.e. -> p,q) after contraction: give each w a p/q arc
    arcs += [(rho_tails[0], 0), (rho_tails[1], 0), (rho_tails[2], 1)]
    arcs += [(rho_tails[1], 1), (rho_tails[2], 0)]
    # rho (p,q) feeds back into V2 so the host is strongly connected
    arcs += [(0, spine[0]), (1, spine[-1] if spine else rho_tails[0])]
    arcs += [(0, 4), (1, 5)]

    # Every outside K-vertex dominates the cage (cage hooks + lambda supply).
    outside = (h0, h1) + spine + rho_tails
    arcs += [(x, c) for x in outside for c in cage]

    # Make V2 semicomplete: add any missing pair among V2 with a single dir.
    V2 = list(cage) + [h0, h1] + list(spine) + list(rho_tails)
    have = set(arcs)
    for x, y in combinations(V2, 2):
        if (x, y) not in have and (y, x) not in have:
            arcs.append((x, y))
            have.add((x, y))
    # dedup, keep simple
    seen = set()
    out = []
    for e in arcs:
        if e[0] != e[1] and e not in seen:
            seen.add(e)
            out.append(e)
    return n, out, dict(cage=cage, h0=h0, h1=h1, spine=spine,
                        rho_tails=rho_tails)


def contract(host_n, host_arcs):
    """Contract V1={0,1,2}: identify p=0,q=1 -> rho=0, u=2 -> 1; relabel."""
    relabel = {0: 0, 1: 0, 2: 1}
    nxt = 2
    for v in range(3, host_n):
        relabel[v] = nxt
        nxt += 1
    out = []
    for x, y in host_arcs:
        rx, ry = relabel[x], relabel[y]
        if rx != ry:
            out.append((rx, ry))
    return nxt, out, relabel


def main():
    import networkx as nx
    import oracle
    from digraph import Digraph
    from generators.near_split import is_one_zero_near_split

    verdicts = {}
    for spine_len in (2, 3, 4):
        n_h, host, meta = build_host(spine_len)
        host = [e for e in host if e[0] != e[1]]
        assert len(host) == len(set(host)), "host not simple"

        # (in-class check 1) (1,0)-near-split with V1={0,1,2}
        ok, why = is_one_zero_near_split(
            Digraph.from_arcs(range(n_h), host), [0, 1, 2],
            list(range(3, n_h)))
        lam = oracle.arc_connectivity(n_h, host)
        sad = oracle.check_construction(n_h, host, name=f"spine{spine_len}")
        in_class = ok and lam == 3

        # contraction
        n, arcs, relabel = contract(n_h, host)
        mult = Counter(arcs)
        lam_b = oracle.arc_connectivity(n, arcs)
        root, u = 0, 1

        # identify cage in contraction
        g = nx.MultiDiGraph(); g.add_nodes_from(range(n)); g.add_edges_from(arcs)
        wo = g.copy(); wo.remove_node(u)
        cage = {u} | {x for x in range(n)
                      if x not in (root, u) and not nx.has_path(wo, x, root)}

        # candidate w = contraction of rho_tails[0]
        w = relabel[meta["rho_tails"][0]]
        h0c = relabel[meta["h0"]]
        spine_c = [relabel[s] for s in meta["spine"]]
        Xst = cage | {w}
        O = set(range(n)) - Xst - {root}

        # load-bearing test: for EVERY directed h0->w path P in D^bullet,
        # check whether D_O - A_O(P) keeps every O-vertex reaching rho.
        # If NO path is sparable -> load-bearing (T4 fails). We enumerate
        # simple h0->w paths (graph is tiny).
        simple = nx.DiGraph()
        simple.add_nodes_from(range(n))
        simple.add_edges_from(set(arcs))
        DO_nodes = O | {root}

        def reach_all_O(deleted):
            H = nx.DiGraph(); H.add_nodes_from(DO_nodes)
            for (x, y) in set(arcs):
                if x in O and y in DO_nodes and (x, y) not in deleted:
                    H.add_edge(x, y)
            return all(nx.has_path(H, z, root) for z in O)

        sparable_path = None
        n_paths = 0
        for path in nx.all_simple_paths(simple, h0c, w, cutoff=n):
            # all interior in O? (h0 in O, w in Xst boundary)
            if any(p == root for p in path):
                continue
            if any(p in Xst for p in path[:-1]):
                continue
            n_paths += 1
            A_O = {(path[i], path[i + 1]) for i in range(len(path) - 1)
                   if path[i + 1] in O}  # arcs with head in O
            if reach_all_O(A_O):
                sparable_path = path
                break
        load_bearing = (sparable_path is None) and (n_paths > 0)

        # measure d_O-out of spine vertices (the forced-chain signature)
        do_out = {}
        for s in spine_c:
            heads = set(y for (x, y) in set(arcs) if x == s and y in DO_nodes)
            do_out[s] = sorted(heads)

        verdicts[spine_len] = dict(
            n_host=n_h, n=n, in_class=in_class, near_split=ok,
            host_lambda=lam, contract_lambda=lam_b,
            sad=sad["sad"],
            cross=(sad["cross_check"]["agree"]
                   if sad["cross_check"] else None),
            cage=sorted(cage), w=w, h0=h0c, spine=spine_c,
            O=sorted(O), Xst=sorted(Xst),
            n_hw_paths=n_paths, load_bearing=load_bearing,
            sparable_path=sparable_path, do_out_spine=do_out,
        )

    print("=== SPINE BRANCH-2 CONSTRUCTION ATTEMPT ===")
    for L, v in verdicts.items():
        print(f"\n-- spine_len={L} (n_host={v['n_host']}, n_contract={v['n']}) --")
        print(f"  near_split={v['near_split']} host_lambda={v['host_lambda']} "
              f"contract_lambda={v['contract_lambda']} IN_CLASS={v['in_class']}")
        print(f"  host SAD={v['sad']} cross_agree={v['cross']}")
        print(f"  cage={v['cage']} w={v['w']} h0={v['h0']} spine={v['spine']}")
        print(f"  X*_w={v['Xst']} O={v['O']}")
        print(f"  d_O_out(spine)={v['do_out_spine']}")
        print(f"  #(h0->w paths in O)={v['n_hw_paths']} "
              f"LOAD_BEARING(no sparable path)={v['load_bearing']}")
        if v['sparable_path']:
            print(f"  sparable path (T4 applies) = {v['sparable_path']}")

    # SUMMARY verdict
    print("\n=== VERDICT ===")
    any_inclass_lb = any(v['in_class'] and v['load_bearing']
                         for v in verdicts.values())
    print(f"in-class load-bearing spine found: {any_inclass_lb}")
    for L, v in verdicts.items():
        tag = ("IN-CLASS+LOAD-BEARING (branch-2 WITNESS)"
               if v['in_class'] and v['load_bearing']
               else ("load-bearing but NOT in-class (lambda<3 -> supports "
                     "impossibility)" if v['load_bearing'] and not v['in_class']
                     else ("in-class but T4 applies (sparable path exists)"
                           if v['in_class'] else "neither")))
        print(f"  spine_len={L}: {tag}")


if __name__ == "__main__":
    main()
