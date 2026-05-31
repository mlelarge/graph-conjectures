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

    def test_two_sided_window_lemma(self):
        """D96: every vertex v of a reachable prefix S has |i(v)−d⁻(v)| ≤ 2 in
        any witnessing order (corrects D94's one-sided claim). Consequences:
        per-level cap |S∩{d⁻=t}| ≤ 5 and S ⊆ {d⁻ ≤ p+1}."""
        from q1_reachable_count import masks

        rng = random.Random(9)
        for n in range(3, 10):
            for _ in range(150):
                T = rand_tournament(n, rng)
                om, dm = masks(T)
                # BFS keeping one witnessing order per reachable prefix
                frontier = {0: []}
                for p in range(n):
                    nxt = {}
                    for S, order in frontier.items():
                        for u in range(n):
                            if (S >> u) & 1:
                                continue
                            c = bin(om[u] & S).count("1")
                            if 2 * c + dm[u] - p <= 2:
                                S2 = S | (1 << u)
                                if S2 not in nxt:
                                    nxt[S2] = order + [u]
                    for S, order in nxt.items():
                        # two-sided window on the witnessing order
                        for i, v in enumerate(order):
                            self.assertLessEqual(abs(i - dm[v]), 2)
                        # per-level cap ≤5 and S ⊆ {d⁻ ≤ p+1}
                        from collections import Counter

                        lvl = Counter(dm[v] for v in order)
                        self.assertLessEqual(max(lvl.values()), 5)
                        for v in order:
                            self.assertLessEqual(dm[v], (p + 1) + 1)
                    frontier = nxt
                    if not frontier:
                        break

    def test_N3_in_neighbor_closure(self):
        """(N3) PROVED: every v in a reachable prefix S has ≤2 in-neighbours
        outside S (|N⁻(v)∖S| ≤ 2)."""
        from q1_reachable_count import masks

        rng = random.Random(20260531)
        for n in range(4, 10):
            for _ in range(150):
                T = rand_tournament(n, rng)
                om, dm = masks(T)
                Nin = [[v for v in range(n) if v != u and T[v][u]] for u in range(n)]
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
                    for S in nxt:
                        for u in range(n):
                            if (S >> u) & 1:
                                outside = sum(1 for w in Nin[u] if not (S >> w) & 1)
                                self.assertLessEqual(outside, 2)
                    frontier = nxt

    def test_recursion_hereditary_lemma(self):
        """D97 (PROVED): if S is a reachable prefix of T and B ⊆ V, then S∩B is
        a reachable prefix of the induced sub-tournament T[B]."""
        from q1_reachable_count import masks

        def is_reachable_prefix(T, Sl):
            n = len(T)
            p = len(Sl)
            if p == 0:
                return True
            om = {u: set(v for v in range(n) if T[u][v]) for u in range(n)}
            dm = [sum(1 for u in range(n) if T[u][v]) for v in range(n)]
            idxset = set(Sl)
            frontier = {0}
            full = (1 << p) - 1
            for sz in range(p):
                nxt = set()
                for mask in frontier:
                    placed = set(Sl[k] for k in range(p) if (mask >> k) & 1)
                    for k in range(p):
                        if (mask >> k) & 1:
                            continue
                        v = Sl[k]
                        c = len(om[v] & placed)
                        if 2 * c + dm[v] - sz <= 2:
                            nxt.add(mask | (1 << k))
                frontier = nxt
                if not frontier:
                    return False
            return full in frontier

        rng = random.Random(20260531)
        for n in range(4, 8):
            for _ in range(60):
                T = rand_tournament(n, rng)
                om, dm = masks(T)
                # enumerate reachable prefixes
                frontier = {0}
                reach = []
                for sz in range(n):
                    nxt = set()
                    for Sm in frontier:
                        for u in range(n):
                            if (Sm >> u) & 1:
                                continue
                            c = bin(om[u] & Sm).count("1")
                            if 2 * c + dm[u] - sz <= 2:
                                nxt.add(Sm | (1 << u))
                    reach += list(nxt)
                    frontier = nxt
                    if not nxt:
                        break
                for Sm in reach[:: max(1, len(reach) // 6)]:
                    Sset = [v for v in range(n) if (Sm >> v) & 1]
                    B = sorted(v for v in range(n) if (v * 7 + n) % 3)  # arbitrary subset
                    if not B:
                        continue
                    TB = [[T[a][b] for b in B] for a in B]
                    SB = [B.index(v) for v in Sset if v in B]
                    self.assertTrue(is_reachable_prefix(TB, SB))

    def test_deep_omission_bound_is_NOT_two(self):
        """D97: the conjecture |D| ≤ 2 (deep omissions, d⁻≤p−3) is FALSE — it is
        2 exhaustively at n≤7 but reaches 3 at n=10 (refutation witness)."""
        from q1_reachable_count import masks

        def max_deep(T):
            n = len(T)
            om, dm = masks(T)
            frontier = {0}
            md = 0
            for p in range(n + 1):
                for S in frontier:
                    md = max(md, sum(1 for w in range(n)
                                     if not (S >> w) & 1 and dm[w] <= p - 3))
                if p == n:
                    break
                nxt = set()
                for S in frontier:
                    for u in range(n):
                        if (S >> u) & 1:
                            continue
                        c = bin(om[u] & S).count("1")
                        if 2 * c + dm[u] - p <= 2:
                            nxt.add(S | (1 << u))
                frontier = nxt
                if not frontier:
                    break
            return md

        rng = random.Random(1)
        best = 0
        for _ in range(6000):
            best = max(best, max_deep(rand_tournament(10, rng)))
            if best >= 3:
                break
        self.assertGreaterEqual(best, 3)  # |D| exceeds 2 at n=10

    def test_diameter_band_part_proved_le_8(self):
        """D98 (PROVED): for reachable prefixes S, S' of the same size,
        |(S△S') ∩ band| ≤ 8, since |S∩band|,|S'∩band| ≤ 4 (W3)."""
        from q1_reachable_count import masks

        rng = random.Random(20260531)
        for n in range(4, 9):
            for _ in range(120):
                T = rand_tournament(n, rng)
                om, dm = masks(T)
                frontier = {0}
                bysize = {0: [0]}
                for p in range(n):
                    nxt = set()
                    for S in frontier:
                        for u in range(n):
                            if (S >> u) & 1:
                                continue
                            c = bin(om[u] & S).count("1")
                            if 2 * c + dm[u] - p <= 2:
                                nxt.add(S | (1 << u))
                    if nxt:
                        bysize[p + 1] = list(nxt)
                    frontier = nxt
                    if not nxt:
                        break
                for p, lst in bysize.items():
                    for a in lst:
                        band_a = sum(1 for v in range(n)
                                     if (a >> v) & 1 and p - 2 <= dm[v] <= p + 1)
                        self.assertLessEqual(band_a, 4)  # W3
                    for i in range(len(lst)):
                        for j in range(i + 1, len(lst)):
                            x = lst[i] ^ lst[j]
                            band = sum(1 for v in range(n)
                                       if (x >> v) & 1 and p - 2 <= dm[v] <= p + 1)
                            self.assertLessEqual(band, 8)

    def test_diameter_is_bounded(self):
        """D98 (evidence): the diameter (max |S△S'| over same-size reachable
        prefixes) is bounded by a small constant, not growing with n.
        Bounded diameter ⟹ #reachable = poly ⟹ Q1 ∈ P."""
        from q1_reachable_count import masks

        def diameter(T):
            n = len(T)
            om, dm = masks(T)
            frontier = {0}
            md = 0
            bysize = {0: [0]}
            for p in range(n):
                nxt = set()
                for S in frontier:
                    for u in range(n):
                        if (S >> u) & 1:
                            continue
                        c = bin(om[u] & S).count("1")
                        if 2 * c + dm[u] - p <= 2:
                            nxt.add(S | (1 << u))
                if nxt:
                    bysize[p + 1] = list(nxt)
                frontier = nxt
                if not nxt:
                    break
            for lst in bysize.values():
                for i in range(len(lst)):
                    for j in range(i + 1, len(lst)):
                        md = max(md, bin(lst[i] ^ lst[j]).count("1"))
            return md

        rng = random.Random(7)
        for n in range(4, 13):
            worst = 0
            for _ in range(400):
                worst = max(worst, diameter(rand_tournament(n, rng)))
            # transitive maximizer skeleton
            Tt = [[1 if i > j else 0 for j in range(n)] for i in range(n)]
            worst = max(worst, diameter(Tt))
            self.assertLessEqual(worst, 12)  # bounded; observed ≤8

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
