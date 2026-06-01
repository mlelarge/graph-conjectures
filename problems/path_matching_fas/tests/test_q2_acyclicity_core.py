"""Q2 regression tests: D70 family lives at Delta*=2, decision correctness.

Run: python3 -m unittest tests/test_q2_acyclicity_core.py
"""
import json
import os
import random
import sys
import unittest
from itertools import combinations, permutations, product

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from degreewidth_exact import degreewidth  # noqa: E402
from reversed_matching_hardness import build_reversed_matching  # noqa: E402
from toggle_fooling_set import (  # noqa: E402
    build_toggle_family,
    build_toggle_with_probe,
    toggle_prefix,
    verify_fooling_set,
)
from q2_core_cycle_analysis import (  # noqa: E402
    back_arc_components,
    enumerate_degree2_orders,
)
from q2_apex_cut_probe import (  # noqa: E402
    all_edges,
    apex_triangle_closed,
    hits_directed_cycles,
    search_apex_csp,
)
from nonsweep_path_fas import decide_linear_forest_fas_bruteforce  # noqa: E402
from nonsweep_path_fas import arcs_of, is_acyclic, underlying_is_linear_forest  # noqa: E402


def _q2_decide(T):
    dw = degreewidth(T)
    if dw <= 1:
        return True
    if dw >= 3:
        return False
    for o in enumerate_degree2_orders(T, cap=10_000_000):
        md, cl = back_arc_components(T, o)
        if md <= 2 and not cl:
            return True
    return False


def _rand_tour(n, seed):
    r = random.Random(seed)
    T = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if r.random() < 0.5:
                T[i][j] = 1
            else:
                T[j][i] = 1
    return T


def _all_tournaments(n):
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    for bits in product((0, 1), repeat=len(pairs)):
        T = [[0] * n for _ in range(n)]
        for (i, j), bit in zip(pairs, bits):
            if bit:
                T[i][j] = 1
            else:
                T[j][i] = 1
        yield T


def _back_arc_count(T, order):
    pos = {v: i for i, v in enumerate(order)}
    n = len(T)
    return sum(
        1
        for u in range(n)
        for v in range(n)
        if u != v and T[u][v] and pos[u] > pos[v]
    )


def _directed_cycles(T, cycle_lengths):
    n = len(T)
    out = []
    seen = set()
    for cyc_len in cycle_lengths:
        for verts in combinations(range(n), cyc_len):
            # Fix the first vertex to avoid testing rotations; different
            # directed Hamilton cycles on the same vertex set remain distinct.
            first = verts[0]
            for perm_tail in permutations(verts[1:]):
                cyc = (first,) + perm_tail
                if all(T[cyc[i]][cyc[(i + 1) % cyc_len]]
                       for i in range(cyc_len)):
                    edge_set = frozenset(
                        (cyc[i], cyc[(i + 1) % cyc_len])
                        for i in range(cyc_len)
                    )
                    if edge_set not in seen:
                        seen.add(edge_set)
                        out.append(tuple(edge_set))
    return out


def _hits_directed_cycles(T, F, cycle_lengths):
    F = set(F)
    return all(any(a in F for a in C)
               for C in _directed_cycles(T, cycle_lengths))


def _static_linear_forest_hits_3_4_decide(T):
    arcs = arcs_of(T)
    cycles = _directed_cycles(T, (3, 4))
    for mask in range(1 << len(arcs)):
        if mask.bit_count() > len(T) - 1:
            continue
        F = [arcs[i] for i in range(len(arcs)) if (mask >> i) & 1]
        if underlying_is_linear_forest(F) and all(
            any(a in F for a in C) for C in cycles
        ):
            return True
    return False


def _has_directed_cycle_len_3_or_4(T, kept):
    n = len(T)
    kept = set(kept)
    for cyc_len in (3, 4):
        for verts in combinations(range(n), cyc_len):
            # Fix the first vertex to avoid testing all rotations; different
            # directed Hamilton cycles on the same vertex set remain distinct.
            first = verts[0]
            rest = list(verts[1:])

            for perm_tail in permutations(rest):
                cyc = (first,) + perm_tail
                if all((cyc[i], cyc[(i + 1) % cyc_len]) in kept
                       for i in range(cyc_len)):
                    return True
    return False


class TestD70Diagnostic(unittest.TestCase):
    def test_base_families_are_degreewidth_one(self):
        for m in range(2, 9):
            self.assertEqual(degreewidth(build_reversed_matching(m)), 1)
        for k in range(1, 5):
            self.assertEqual(degreewidth(build_toggle_family(k)), 1)

    def test_probe_family_is_degreewidth_two(self):
        # The genuine fooling instances live in the Q2 layer.
        for k in range(1, 4):
            for j in range(k):
                self.assertEqual(degreewidth(build_toggle_with_probe(k, j)), 2)

    def test_fooling_failures_are_cycles_not_degree(self):
        # When a toggle prefix fails to complete, it is a back-arc CYCLE,
        # never a degree-3 vertex.
        for k in (2, 3):
            for j in range(k):
                T = build_toggle_with_probe(k, j)
                n = len(T)
                for x in range(1 << k):
                    eps = tuple((x >> i) & 1 for i in range(k))
                    pref = toggle_prefix(k, eps)
                    rest = [v for v in range(n) if v not in set(pref)]
                    md, cl = back_arc_components(T, pref + rest)
                    # canonical completion never overshoots degree budget
                    self.assertLessEqual(md, 2)

    def test_fooling_set_holds(self):
        for k in (1, 2, 3):
            self.assertTrue(verify_fooling_set(k)["fooling_set_holds"])

    def test_toggle_explosion_is_history_not_prefix_set_count(self):
        # All 2^k toggle prefixes have the same placed vertex set; the
        # exponential D70 obstruction is component history, not Q1's prefix-set
        # count.  This is why the Q1 polynomial recognizer does not decide Q2.
        for k in (2, 3, 4):
            masks = set()
            for x in range(1 << k):
                eps = tuple((x >> i) & 1 for i in range(k))
                mask = sum(1 << v for v in toggle_prefix(k, eps))
                masks.add(mask)
            self.assertEqual(len(masks), 1)

    def test_degree2_orders_blow_up_on_probe_family(self):
        # Witness that #degree-2 orders is super-polynomial on D70.
        c1 = len(enumerate_degree2_orders(build_toggle_with_probe(1, 0)))
        c2 = len(enumerate_degree2_orders(build_toggle_with_probe(2, 0)))
        c3 = len(enumerate_degree2_orders(build_toggle_with_probe(3, 0)))
        self.assertGreater(c1, 100)
        self.assertGreater(c2, c1)
        self.assertGreater(c3, c2)


class TestQ2DecisionCorrectness(unittest.TestCase):
    def test_matches_bruteforce_random(self):
        bad = 0
        for n in (4, 5, 6, 7):
            for s in range(60):
                T = _rand_tour(n, s * 13 + n)
                if _q2_decide(T) != decide_linear_forest_fas_bruteforce(T):
                    bad += 1
        self.assertEqual(bad, 0)

    def test_min_degree2_edge_count_shortcut_is_false(self):
        # There is a degree-2 order with n-1 back-arcs, but its back-arc graph
        # has a 5-cycle and no acyclic degree-2 order exists.  Thus Q2 cannot
        # be reduced to minimizing the number of degree-2 back-arcs.
        T = [
            [0, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 0, 1, 1, 0],
            [0, 1, 0, 1, 0, 0, 1],
            [0, 1, 0, 0, 0, 1, 1],
            [0, 0, 1, 1, 0, 1, 0],
            [1, 0, 1, 0, 0, 0, 1],
            [1, 1, 0, 0, 1, 0, 0],
        ]
        orders = enumerate_degree2_orders(T)
        self.assertEqual(len(orders), 1)
        order = orders[0]
        self.assertEqual(_back_arc_count(T, order), len(T) - 1)
        self.assertEqual(back_arc_components(T, order), (2, [5]))
        self.assertFalse(_q2_decide(T))

    def test_static_3_4_linear_forest_formulation_matches_bruteforce(self):
        # Exact non-forward formulation: Path-FAS iff some linear forest F
        # hits every directed 3-cycle and directed 4-cycle.  This is stronger
        # than the sampled fixed-F lemma below: it tests the decision problem.
        for n in range(2, 6):
            for T in _all_tournaments(n):
                self.assertEqual(
                    _static_linear_forest_hits_3_4_decide(T),
                    decide_linear_forest_fas_bruteforce(T),
                )

    def test_triangle_only_static_formulation_is_false(self):
        # Directed 4-cycle 0->1->2->3->0 with both diagonals deleted.  The
        # selected diagonal matching hits every cyclic triangle, but T-F keeps
        # the directed 4-cycle, so 4-cycle constraints are genuinely needed.
        T = [[0] * 4 for _ in range(4)]
        for u, v in ((0, 1), (1, 2), (2, 3), (3, 0), (0, 2), (1, 3)):
            T[u][v] = 1
        F = {(0, 2), (1, 3)}
        self.assertTrue(underlying_is_linear_forest(F))
        self.assertTrue(_hits_directed_cycles(T, F, (3,)))
        self.assertFalse(_hits_directed_cycles(T, F, (3, 4)))
        self.assertFalse(is_acyclic(4, set(arcs_of(T)) - F))

    def test_degree2_fas_without_forest_topology_is_false(self):
        # Even full directed acyclicity plus max selected-degree <=2 is not
        # enough: this certified NO has a degree-2 FAS S, but S contains an
        # undirected 4-cycle.  Q2's remaining content is exactly this selected
        # forest topology, not another directed-cycle constraint.
        data = os.path.join(
            os.path.dirname(__file__),
            "..",
            "data",
            "minimal_no_obstruction_catalogue_n7.json",
        )
        with open(data) as fh:
            T = json.load(fh)["records"][0]["T"]
        S = {(0, 6), (3, 1), (3, 2), (4, 1), (4, 2), (6, 5)}
        deg = [0] * len(T)
        for u, v in S:
            deg[u] += 1
            deg[v] += 1
        self.assertFalse(decide_linear_forest_fas_bruteforce(T))
        self.assertLessEqual(max(deg), 2)
        self.assertTrue(is_acyclic(len(T), set(arcs_of(T)) - S))
        self.assertTrue(_hits_directed_cycles(T, S, (3, 4)))
        self.assertFalse(underlying_is_linear_forest(S))

    def test_linear_forest_fas_needs_only_directed_3_and_4_cycles(self):
        # If F is already a linear forest, any shortest directed cycle in T-F
        # has length at most 4: all chords of a longer shortest cycle would
        # have to lie in F, forcing degree >=3 for length >=6 or a 5-cycle in F.
        rng = random.Random(2404)
        for n in range(4, 10):
            for s in range(80):
                T = _rand_tour(n, 1000 * n + s)
                perm = list(range(n))
                rng.shuffle(perm)
                F = set()
                for i in range(n - 1):
                    if rng.random() < 0.45:
                        u, v = perm[i], perm[i + 1]
                        F.add((u, v) if T[u][v] else (v, u))
                kept = set(arcs_of(T)) - F
                self.assertEqual(
                    is_acyclic(n, kept),
                    not _has_directed_cycle_len_3_or_4(T, kept),
                )


class TestApexCutProbe(unittest.TestCase):
    def test_apex_triangle_closure_is_exact(self):
        # For any selected edge set F, "F hits all directed triangles" is
        # exactly the apex-cut closure condition C_v - N_F(v) subset F.
        for T in _all_tournaments(4):
            edges = all_edges(4)
            for mask in range(1 << len(edges)):
                F = {edges[i] for i in range(len(edges)) if (mask >> i) & 1}
                self.assertEqual(
                    apex_triangle_closed(T, F),
                    hits_directed_cycles(T, F, 3),
                )

    def test_apex_csp_matches_bruteforce_exhaustive_n_le_5(self):
        # The apex CSP is an exact reformulation plus global linear-forest
        # and 4-cycle checks.  Exhaustive n<=5 keeps this pinned.
        for n in range(2, 6):
            for T in _all_tournaments(n):
                out = search_apex_csp(T, node_cap=100_000)
                self.assertTrue(out["exhausted"])
                self.assertEqual(out["found"], decide_linear_forest_fas_bruteforce(T))

    def test_apex_csp_refutes_certified_n7_no_catalogue(self):
        data = os.path.join(
            os.path.dirname(__file__),
            "..",
            "data",
            "minimal_no_obstruction_catalogue_n7.json",
        )
        with open(data) as fh:
            recs = json.load(fh)["records"]
        max_nodes = 0
        ac_empty = 0
        for rec in recs:
            out = search_apex_csp(rec["T"], node_cap=100_000)
            self.assertTrue(out["exhausted"])
            self.assertFalse(out["found"])
            max_nodes = max(max_nodes, out["nodes"])
            ac_empty += int(out["initial_ac"]["consistent"] is False)
        self.assertLessEqual(max_nodes, 100)
        self.assertGreaterEqual(ac_empty, 4)


if __name__ == "__main__":
    unittest.main()


def _count_directed_3cycles(T):
    import itertools
    n=len(T); c=0
    for a,b,d in itertools.combinations(range(n),3):
        for x,y,z in ((a,b,d),(a,d,b)):
            if T[x][y] and T[y][z] and T[z][x]: c+=1
    return c


class TestCycleCountCondition(unittest.TestCase):
    def test_cycle_count_necessary_condition(self):
        """Q2 §9 (PROVED poly NO-certificate): Path-FAS YES => #directed-3-cycles
        <= (n-1)(n-2). Verified 0 violations exhaustive n<=6; and it is necessary
        NOT sufficient (minimal-NO instances have few 3-cycles, below the bound)."""
        import itertools
        import json
        import os

        from nonsweep_path_fas import decide_linear_forest_fas_bruteforce as brute

        def all_T(n):
            pr = [(i, j) for i in range(n) for j in range(i + 1, n)]
            for bits in itertools.product((0, 1), repeat=len(pr)):
                T = [[0] * n for _ in range(n)]
                for (i, j), b in zip(pr, bits):
                    T[i][j] = 1 if b else 0
                    T[j][i] = 0 if b else 1
                yield T

        for n in range(3, 7):
            bound = (n - 1) * (n - 2)
            for T in all_T(n):
                if brute(T):
                    self.assertLessEqual(_count_directed_3cycles(T), bound)
        # necessary-not-sufficient: n=7 minimal-NOs are all below the bound yet NO
        here = os.path.dirname(__file__)
        path = os.path.join(here, "..", "data",
                            "minimal_no_obstruction_catalogue_n7.json")
        with open(path) as fh:
            recs = json.load(fh)["records"]
        bound = (7 - 1) * (7 - 2)
        self.assertTrue(all(_count_directed_3cycles(r["T"]) < bound for r in recs))


class TestExpressiveness(unittest.TestCase):
    def test_4set_cyclic_triangle_sparsity(self):
        """Q2 §10 (PROVED): every 4-subset of a tournament spans <=2 cyclic
        triangles (exhaustive n<=5)."""
        import itertools
        def all_T(n):
            pr=[(i,j) for i in range(n) for j in range(i+1,n)]
            for bits in itertools.product((0,1),repeat=len(pr)):
                T=[[0]*n for _ in range(n)]
                for (i,j),b in zip(pr,bits):
                    T[i][j]=1 if b else 0; T[j][i]=0 if b else 1
                yield T
        for n in range(4,6):
            for T in all_T(n):
                for S in itertools.combinations(range(n),4):
                    ct=sum(1 for tri in itertools.combinations(S,3)
                           for x,y,z in (tri,(tri[0],tri[2],tri[1]))
                           if T[x][y] and T[y][z] and T[z][x])
                    self.assertLessEqual(ct,2)
