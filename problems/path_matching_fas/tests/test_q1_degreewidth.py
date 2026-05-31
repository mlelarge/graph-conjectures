"""Pin the Q1 forward-DP facts (degreewidth ≤ 2 recognition).

Run: python3 -m unittest tests/test_q1_degreewidth.py
"""
import itertools
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from degreewidth_exact import _masks, degreewidth, is_degreewidth_le2  # noqa: E402


def all_tournaments(n):
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    for bits in itertools.product((0, 1), repeat=len(pairs)):
        T = [[0] * n for _ in range(n)]
        for (i, j), b in zip(pairs, bits):
            if b:
                T[i][j] = 1
            else:
                T[j][i] = 1
        yield T


def rand_tournament(n, rng):
    T = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < 0.5:
                T[i][j] = 1
            else:
                T[j][i] = 1
    return T


def forward_dp_le2(T):
    """Δ*≤2 via the Q1 forward placement DP: append u to prefix-set S iff
    bd(u|S)=2·|N⁺(u)∩S|+d⁻(u)−|S| ≤ 2.  Reachability over subsets."""
    n = len(T)
    if n <= 1:
        return True
    outmask, _, dminus = _masks(T)
    reach = bytearray(1 << n)
    reach[0] = 1
    for S in range(1, 1 << n):
        p = bin(S).count("1") - 1  # position at which the added vertex sits
        ok = 0
        rem = S
        while rem:
            vb = rem & (-rem)
            u = vb.bit_length() - 1
            rem ^= vb
            prev = S ^ vb
            if not reach[prev]:
                continue
            c = bin(outmask[u] & prev).count("1")
            if 2 * c + dminus[u] - p <= 2:
                ok = 1
                break
        reach[S] = ok
    return bool(reach[(1 << n) - 1])


class TestQ1(unittest.TestCase):
    def test_placement_identity(self):
        """bd(u|S) = 2·|N⁺(u)∩S| + d⁻(u) − |S| equals the masks back-degree."""
        rng = random.Random(1)
        for n in range(2, 11):
            for _ in range(50):
                T = rand_tournament(n, rng)
                outmask, inmask, dminus = _masks(T)
                verts = list(range(n))
                rng.shuffle(verts)
                cut = rng.randint(0, n - 1)
                S = 0
                for w in verts[:cut]:
                    S |= 1 << w
                rest = [w for w in range(n) if not (S >> w) & 1]
                if not rest:
                    continue
                u = rng.choice(rest)
                bd_solver = (bin(outmask[u] & S).count("1")
                             + (dminus[u] - bin(inmask[u] & S).count("1")))
                bd_formula = 2 * bin(outmask[u] & S).count("1") + dminus[u] - bin(S).count("1")
                self.assertEqual(bd_solver, bd_formula)

    def test_forward_dp_matches_exact_exhaustive_n_le_6(self):
        """The Q1 forward placement DP decides Δ*≤2 correctly on all n≤6."""
        for n in range(2, 7):
            for T in all_tournaments(n):
                self.assertEqual(forward_dp_le2(T), degreewidth(T) <= 2)

    def test_forward_dp_matches_exact_random(self):
        rng = random.Random(7)
        for n in range(7, 12):
            for _ in range(300):
                T = rand_tournament(n, rng)
                self.assertEqual(forward_dp_le2(T), is_degreewidth_le2(T))

    def test_all_small_tournaments_are_dw_le_2(self):
        """First Δ*≥3 tournament appears at n=7: every n≤6 tournament is Δ*≤2."""
        for n in range(2, 7):
            for T in all_tournaments(n):
                self.assertLessEqual(degreewidth(T), 2)
        # and Δ*≥3 instances DO exist at n=7
        rng = random.Random(3)
        found = any(degreewidth(rand_tournament(7, rng)) >= 3 for _ in range(5000))
        self.assertTrue(found)

    def test_reachable_recognizer_exact(self):
        """The reachable-prefix BFS (full set reachable?) decides Δ*≤2 exactly."""
        from q1_reachable_count import reachable_stats

        for n in range(2, 7):
            for T in all_tournaments(n):
                _, _, full = reachable_stats(T)
                self.assertEqual(full, degreewidth(T) <= 2)

    def test_one_sided_window_lemma(self):
        """Reachable size-p prefix S ⟹ every v∈S has d⁻(v) ≤ p+1 (S ⊆ A_p)."""
        rng = random.Random(9)
        for n in range(2, 11):
            for _ in range(200):
                T = rand_tournament(n, rng)
                om = [0] * n
                dm = [0] * n
                for u in range(n):
                    for v in range(n):
                        if u != v and T[u][v]:
                            om[u] |= 1 << v
                for v in range(n):
                    dm[v] = sum(1 for u in range(n) if u != v and T[u][v])
                frontier = {0}
                for p in range(n):
                    nxt = set()
                    for S in frontier:
                        for u in range(n):
                            if (S >> u) & 1:
                                continue
                            c = bin(om[u] & S).count("1")
                            if 2 * c + dm[u] - p <= 2:
                                nxt.add(S | (1 << u))
                    for S in nxt:  # size p+1
                        for v in range(n):
                            if (S >> v) & 1:
                                self.assertLessEqual(dm[v], (p + 1) + 1)
                    frontier = nxt

    def test_transitive_reachable_count_formula(self):
        """Transitive: #reachable size-p prefixes = C(p+2,2) for p ≤ n−2."""
        from math import comb

        from q1_reachable_count import masks

        n = 9
        T = [[1 if i > j else 0 for j in range(n)] for i in range(n)]
        om, dm = masks(T)
        frontier = {0}
        per_size = {0: 1}
        for p in range(n):
            nxt = set()
            for S in frontier:
                for u in range(n):
                    if (S >> u) & 1:
                        continue
                    c = bin(om[u] & S).count("1")
                    if 2 * c + dm[u] - p <= 2:
                        nxt.add(S | (1 << u))
            per_size[p + 1] = len(nxt)
            frontier = nxt
        for p in range(1, n - 1):
            self.assertEqual(per_size[p], comb(p + 2, 2))


if __name__ == "__main__":
    unittest.main()
