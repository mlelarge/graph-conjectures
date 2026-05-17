"""Canonical benchmark instances for the SAD verifier.

Each entry records:
 - name: short identifier;
 - n, arcs: vertex set (implicitly 0..n-1) and arc multiset;
 - expected: "SAT" or "UNSAT";
 - source: citation for the expected answer;
 - notes: any caveats.

Conventions:
 - vertices are integers 0..n-1;
 - arcs are tuples (u, v) and the list may contain duplicates (multiarcs).

S_4 note. In Bang-Jensen & Wang (2025, arXiv:2309.06904) the digraph S_4 is
defined as "the square of the directed 4-cycle". So S_4 = C_4^2. The
benchmarks below therefore use C_2k^2 for k = 2, 3, 4 and list S_4 separately
under the name `S4` purely for traceability; they share the same arc set when
k = 2. We assert this equivalence at construction time.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from digraph import Digraph


@dataclass
class Benchmark:
    name: str
    n: int
    arcs: list[tuple[int, int]]
    expected: Literal["SAT", "UNSAT"]
    source: str
    notes: str = ""

    def build(self) -> Digraph:
        return Digraph.from_arcs(range(self.n), self.arcs)


# ----------------------------------------------------------------------------
# UNSAT benchmarks
# ----------------------------------------------------------------------------


def _C_2k_square_arcs(k: int) -> tuple[int, list[tuple[int, int]]]:
    """Arc set of C_{2k}^2: arcs i -> i+1 and i -> i+2 for every i, mod n."""
    n = 2 * k
    arcs: list[tuple[int, int]] = []
    for i in range(n):
        arcs.append((i, (i + 1) % n))
        arcs.append((i, (i + 2) % n))
    return n, arcs


def _S4() -> Benchmark:
    """S_4 := C_4^2, the square of the directed 4-cycle.

    Per Bang-Jensen & Wang (2025, p.~2, paragraph after Thm 1.2):
        "Note that S_4 above is the square of a 4-cycle."
    Per Bang-Jensen & Yeo (Combinatorica 24, 2004): S_4 is the unique
    2-arc-strong semicomplete digraph with no strong arc decomposition.

    Vertices: 0..3. Arcs: (i, i+1 mod 4) and (i, i+2 mod 4), i = 0..3.
    Total arcs = 8. Strongly connected, semicomplete (between 0 and 2 we
    have both 0->2 and 2->0; same for 1 and 3), arc-connectivity 2.
    """
    n, arcs = _C_2k_square_arcs(2)
    return Benchmark(
        name="S4",
        n=n,
        arcs=arcs,
        expected="UNSAT",
        source=(
            "Bang-Jensen & Yeo, Combinatorica 24 (2004); "
            "Bang-Jensen & Wang, J. Graph Theory 108 (2025) note S_4 = C_4^2."
        ),
        notes="S_4 is the unique 2-arc-strong semicomplete obstruction; equals C_4^2.",
    )


def _C_2k_square(k: int) -> Benchmark:
    """Square of the directed cycle on n = 2k vertices, k >= 2.

    For k >= 2 these are 2-arc-strong locally semicomplete digraphs that do
    NOT have a strong arc decomposition. The case k = 2 coincides with S_4
    (a semicomplete digraph). For k >= 3 the digraph is locally semicomplete
    but not semicomplete.

    Reference: Bang-Jensen & Huang, "Decomposing locally semicomplete digraphs
    into strong spanning subdigraphs", JCTB 102 (2012), 701-714.
    """
    n, arcs = _C_2k_square_arcs(k)
    return Benchmark(
        name=f"C{n}_square",
        n=n,
        arcs=arcs,
        expected="UNSAT",
        source="Bang-Jensen & Huang, JCTB 102 (2012).",
        notes=f"Square of the directed cycle on {n} vertices (= S_4 when k = 2).",
    )


# ----------------------------------------------------------------------------
# BJG–Yeo 2020 composition exceptions (Theorem 1.4 of arXiv:1903.12225).
# The four 2-arc-strong strong-semicomplete-composition obstructions are
# S_4, C_3[K2bar,K2bar,K2bar], C_3[K2bar,K2bar,P2bar], C_3[K2bar,K2bar,K3bar].
# S_4 is encoded above; the other three are below.
#
# Composition convention. C_3 is the directed 3-cycle on layers {1,2,3} with
# arcs 1->2, 2->3, 3->1. The composition C_3[H_1,H_2,H_3] has vertex set the
# disjoint union of V(H_1), V(H_2), V(H_3); arcs are A(H_1) cup A(H_2) cup
# A(H_3) plus, for every arc i->i' of C_3, all arcs u->v with u in V(H_i) and
# v in V(H_{i'}). Here K2bar = empty digraph on 2 vertices, K3bar = empty
# digraph on 3 vertices, P2bar = digraph on 2 vertices with the single arc
# from vertex 1 to vertex 2 (per Auditor's reading of BJG–Yeo 2020 Figure 2).
# ----------------------------------------------------------------------------


def _compose_C3(sizes: tuple[int, int, int], inner_arcs: list[tuple[int, int]]) -> tuple[int, list[tuple[int, int]]]:
    """Return (n, arcs) for C_3[H_1, H_2, H_3] where H_i is on vertices of
    `sizes[i]` and `inner_arcs` is the union of A(H_i) given in the GLOBAL
    vertex numbering 0..n-1.

    Vertex layout: layer 1 = [0, s_1), layer 2 = [s_1, s_1 + s_2),
    layer 3 = [s_1 + s_2, n).
    """
    s1, s2, s3 = sizes
    n = s1 + s2 + s3
    layer1 = list(range(0, s1))
    layer2 = list(range(s1, s1 + s2))
    layer3 = list(range(s1 + s2, n))
    arcs: list[tuple[int, int]] = []
    # Inter-layer arcs from C_3: 1 -> 2, 2 -> 3, 3 -> 1.
    for u in layer1:
        for v in layer2:
            arcs.append((u, v))
    for u in layer2:
        for v in layer3:
            arcs.append((u, v))
    for u in layer3:
        for v in layer1:
            arcs.append((u, v))
    # Intra-layer arcs (only non-empty for non-K_t-bar inner digraphs).
    arcs.extend(inner_arcs)
    return n, arcs


def _C3_K2_K2_K2() -> Benchmark:
    """C_3[K2bar, K2bar, K2bar]. 6 vertices, 12 arcs, 2-arc-strong, UNSAT.

    Second of the four BJG–Yeo 2020 composition exceptions (Theorem 1.4 of
    arXiv:1903.12225).
    """
    n, arcs = _compose_C3((2, 2, 2), inner_arcs=[])
    return Benchmark(
        name="C3_K2K2K2",
        n=n,
        arcs=arcs,
        expected="UNSAT",
        source="Bang-Jensen–Gutin–Yeo, J. Graph Theory 95 (2020), Theorem 1.4 (arXiv:1903.12225).",
        notes="C_3[K2bar, K2bar, K2bar]; 2nd of the four BJG–Yeo 2020 exceptions.",
    )


def _C3_K2_K2_P2() -> Benchmark:
    """C_3[K2bar, K2bar, P2bar]. 6 vertices, 13 arcs, 2-arc-strong, UNSAT.

    Third of the four BJG–Yeo 2020 composition exceptions. P2bar is the
    digraph on 2 vertices with the single arc (1, 2) — the auditor reads
    this from BJG–Yeo 2020 Figure 2.
    """
    # Layer 3 occupies vertices {4, 5}; internal arc 4 -> 5.
    inner_arcs = [(4, 5)]
    n, arcs = _compose_C3((2, 2, 2), inner_arcs=inner_arcs)
    return Benchmark(
        name="C3_K2K2P2",
        n=n,
        arcs=arcs,
        expected="UNSAT",
        source="Bang-Jensen–Gutin–Yeo, J. Graph Theory 95 (2020), Theorem 1.4 (arXiv:1903.12225).",
        notes="C_3[K2bar, K2bar, P2bar]; 3rd of the four BJG–Yeo 2020 exceptions.",
    )


def _C3_K2_K2_K3() -> Benchmark:
    """C_3[K2bar, K2bar, K3bar]. 7 vertices, 16 arcs, 2-arc-strong, UNSAT.

    Fourth of the four BJG–Yeo 2020 composition exceptions.
    """
    n, arcs = _compose_C3((2, 2, 3), inner_arcs=[])
    return Benchmark(
        name="C3_K2K2K3",
        n=n,
        arcs=arcs,
        expected="UNSAT",
        source="Bang-Jensen–Gutin–Yeo, J. Graph Theory 95 (2020), Theorem 1.4 (arXiv:1903.12225).",
        notes="C_3[K2bar, K2bar, K3bar]; 4th of the four BJG–Yeo 2020 exceptions.",
    )


# ----------------------------------------------------------------------------
# Ai–He–Li–Qin–Wang 2024 (arXiv:2408.02260) Lemma 2.11 smallest case.
# ----------------------------------------------------------------------------


def _AiEtAl_Lemma211_smallest() -> Benchmark:
    """Smallest 2-arc-strong split digraph containing the Lemma 2.11 (case 1)
    substructure of Ai, He, Li, Qin, Wang 2024 (arXiv:2408.02260). Vertices
    labelled u = 4 in V_1, and V_2 = {x_1, x_2, x_3, v} = {0, 1, 2, 3}.

    The lemma fixes:
        N^+(u)  = {x_1, x_3}     N^-(u)  = {x_1, x_2}
        N^+(x_1) = {x_2, u}      N^+(x_2) = {v, u}
    with x_3, v in V \\ {x_1, x_2, u}; for the smallest |V_2| = 4 instance
    take v != x_3 (the case x_3 = v collapses to S_4).

    The fixed neighborhoods force 6 arcs. Semicompleteness of V_2 forces a
    further 3 (x_3 -> x_1, v -> x_1, x_3 -> x_2) since x_1's outgoing
    neighborhood excludes x_3, v and x_2's excludes x_3. The vertices x_3
    and v then each have in-degree 1; the only candidates for additional
    in-arcs are each other, so 2-arc-strongness forces x_3 <-> v (both
    arcs). Total = 11 arcs.

    The whole digraph is split (V_1 = {u} trivially independent; V_2 is
    semicomplete) but is NOT a semicomplete digraph: the pair {u, v} is
    non-adjacent. So this instance is genuinely outside the BJ-Yeo 2004 and
    BJ-Huang 2012 obstruction lists, and is the smallest member of the
    Ai et al. 2024 split exception family with |V_2| > 3.
    """
    # Label u = 4, x_1 = 0, x_2 = 1, x_3 = 2, v = 3.
    arcs = [
        (4, 0), (4, 2),       # u -> x_1, u -> x_3                  (N^+(u))
        (0, 4), (1, 4),       # x_1 -> u, x_2 -> u                  (N^-(u))
        (0, 1),               # x_1 -> x_2                          (N^+(x_1))
        (1, 3),               # x_2 -> v                            (N^+(x_2))
        (2, 0), (3, 0),       # x_3 -> x_1, v -> x_1                (semicomplete)
        (2, 1),               # x_3 -> x_2                          (semicomplete)
        (2, 3), (3, 2),       # x_3 <-> v                           (2-arc-strong)
    ]
    return Benchmark(
        name="AiEtAl_L211_min",
        n=5,
        arcs=arcs,
        expected="UNSAT",
        source="Ai, He, Li, Qin, Wang, arXiv:2408.02260, Lemma 2.11 (case 1).",
        notes="Smallest 2-arc-strong split digraph with the L2.11 case-1 substructure (|V_2|=4).",
    )


# ----------------------------------------------------------------------------
# Ai–He–Li–Qin–Wang 2024 (arXiv:2408.02260) Lemma 3.12 smallest case.
# ----------------------------------------------------------------------------


def _AiEtAl_Lemma312_smallest() -> Benchmark:
    """Smallest 2-arc-strong split digraph containing the Lemma 3.12 (case 1)
    substructure of Ai, He, Li, Qin, Wang 2024 (arXiv:2408.02260, p. 25).

    Verbatim from the lemma:
        Let D = (V_1, V_2; A) be a 2-arc-strong split digraph with |V_2| >= 4
        and D[V_2] is not strong. Acyclic ordering of strong components
        C_1, ..., C_p (p >= 2). If D[C_p] is a 3-cycle abca with vertices
        u, v in V_1 satisfying
            N_D^+(b) = {u, v, c},  N_D^+(c) = {v, a},  N_D^+(a) = {u, b},
            N_D^+(u) = {a, u^+},   N_D^+(v) = {b, v^+},
            N_D^-(u) = {a, b},     N_D^-(v) = {b, c},
        where u^+, v^+ in V_2 \\ C_p (possibly equal),
        then D has no strong arc decomposition.

    Smallest realization: take u^+ = v^+ = w as a single vertex, giving
    V_2 = {a, b, c, w}, V_1 = {u, v}, n = 6.

    Semicompleteness of V_2 combined with C_p = {a, b, c} being the terminal
    strong component (so no arcs from C_p to {w}) forces w -> a, w -> b,
    w -> c. The fixed N^+ neighborhoods preclude any other arcs out of
    a, b, c, u, v. Total = 14 arcs.

    Labels: a = 0, b = 1, c = 2, w = 3, u = 4, v = 5.
    """
    arcs = [
        # 3-cycle in C_p:
        (0, 1), (1, 2), (2, 0),         # a -> b, b -> c, c -> a
        # N^+(b) = {u, v, c}: c -> b already in cycle? no; b -> c is in cycle.
        # so add b -> u, b -> v:
        (1, 4), (1, 5),
        # N^+(c) = {v, a}: c -> a already in cycle; add c -> v:
        (2, 5),
        # N^+(a) = {u, b}: a -> b already in cycle; add a -> u:
        (0, 4),
        # N^+(u) = {a, u^+ = w}:
        (4, 0), (4, 3),
        # N^+(v) = {b, v^+ = w}:
        (5, 1), (5, 3),
        # V_2 semicomplete + C_p terminal => w forces:
        (3, 0), (3, 1), (3, 2),
    ]
    return Benchmark(
        name="AiEtAl_L312_min",
        n=6,
        arcs=arcs,
        expected="UNSAT",
        source="Ai, He, Li, Qin, Wang, arXiv:2408.02260, Lemma 3.12 (case 1).",
        notes="Smallest 2-arc-strong split digraph with the L3.12 case-1 substructure (|V_2|=4, D[V_2] not strong, u^+ = v^+).",
    )


# ----------------------------------------------------------------------------
# Ai-He-Li-Qin-Wang 2024 (arXiv:2408.02260) Appendix B.2.
# ----------------------------------------------------------------------------


def _aietal_s4_minus_1_arcs() -> list[tuple[int, int]]:
    """S_{4,-1} on v_1=0, v_2=1, v_3=2, v_4=3.

    Audit source: team/05_audit.md Appendix A.9.2. This is the canonical
    template T1: the 4-cycle, both directions on diagonal v_1-v_3, and only
    v_4 -> v_2 on the other diagonal.
    """
    return [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (0, 2), (2, 0),
        (3, 1),
    ]


def _aietal_b2_arcs(case: str) -> list[tuple[int, int]]:
    """Verified UNSAT B.2 iso-class representative for case i/ii/iii."""
    base = _aietal_s4_minus_1_arcs()
    common_at_a = [
        (3, 4),  # v_4 -> a
        (4, 1),  # a -> v_2
        (1, 4),  # v_2 -> a
        (4, 3),  # a -> v_4
    ]
    extra = {
        "i": [],
        "ii": [(4, 0)],  # a -> v_1
        "iii": [(0, 4)],  # v_1 -> a
    }
    if case not in extra:
        raise ValueError(f"unverified B.2 case: {case}")
    return base + common_at_a + extra[case]


def _AiEtAl_B2_case_i() -> Benchmark:
    return Benchmark(
        name="AiEtAl_B2_case_i",
        n=5,
        arcs=_aietal_b2_arcs("i"),
        expected="UNSAT",
        source="Ai, He, Li, Qin, Wang, arXiv:2408.02260, Appendix B.2 case (i); see team/05_audit.md A.9.2.",
        notes="Verified B.2-alpha iso-class; D[V_2]=S_{4,-1}; hash e19fcf9b6d693745...",
    )


def _AiEtAl_B2_case_ii() -> Benchmark:
    return Benchmark(
        name="AiEtAl_B2_case_ii",
        n=5,
        arcs=_aietal_b2_arcs("ii"),
        expected="UNSAT",
        source="Ai, He, Li, Qin, Wang, arXiv:2408.02260, Appendix B.2 case (ii); see team/05_audit.md A.9.2.",
        notes="Verified B.2-beta iso-class; D[V_2]=S_{4,-1}; hash c5524d22d2aba648...",
    )


def _AiEtAl_B2_case_iii() -> Benchmark:
    return Benchmark(
        name="AiEtAl_B2_case_iii",
        n=5,
        arcs=_aietal_b2_arcs("iii"),
        expected="UNSAT",
        source="Ai, He, Li, Qin, Wang, arXiv:2408.02260, Appendix B.2 case (iii); see team/05_audit.md A.9.2.",
        notes="Verified B.2-gamma iso-class; D[V_2]=S_{4,-1}; hash 52e5e47f3f76137e...",
    )


# ----------------------------------------------------------------------------
# Ai-He-Li-Qin-Wang 2024 (arXiv:2408.02260) Appendix B.3.
# ----------------------------------------------------------------------------


def _aietal_s4_minus_2_arcs() -> list[tuple[int, int]]:
    """S_{4,-2} on v_1=0, v_2=1, v_3=2, v_4=3."""
    return [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (0, 2),
        (1, 3),
    ]


def _aietal_b3_extras_at_a(case: str) -> list[tuple[int, int]]:
    """Reliable B.3 extras at a=4 beyond v_4->a and a->v_2.

    The corrected solid-core reading is from team/24_appendix_b3_figure_audit.md.
    In particular cases iii and v do *not* include v_2 -> a; the old
    transcription's extra v_2 -> a was precisely what made the five mismatch
    cases SAT.
    """
    if case == "i":
        return [(1, 4), (4, 3)]  # v_2 -> a, a -> v_4
    if case == "ii":
        return [(1, 4), (4, 0)]  # v_2 -> a, a -> v_1
    if case == "iii":
        return [(0, 4), (4, 3)]  # v_1 -> a, a -> v_4
    if case == "iv":
        return [(1, 4), (4, 2)]  # v_2 -> a, a -> v_3
    if case == "v":
        return [(2, 4), (4, 3)]  # v_3 -> a, a -> v_4
    raise ValueError(f"unverified B.3 component case: {case}")


def _aietal_b3_star_arc(arc: tuple[int, int]) -> tuple[int, int]:
    """Apply the B.3 star operation from a=4 to b=5."""
    sigma = {0: 3, 3: 0, 1: 2, 2: 1}

    def image(v: int) -> int:
        if v == 4:
            return 5
        return sigma.get(v, v)

    x, y = arc
    return (image(y), image(x))


def _aietal_b3_arcs(star_case: str, a_case: str) -> list[tuple[int, int]]:
    """Arcs for B.3 product (star_case)* x (a_case).

    Encoding follows /tmp/check_b3_minimal.py as cited by team/05_audit.md
    A.9.4 and only covers verifier-confirmed UNSAT products with reliable
    arc lists.
    """
    base = _aietal_s4_minus_2_arcs()
    common = [
        (3, 4),  # v_4 -> a
        (4, 1),  # a -> v_2
        (2, 5),  # v_3 -> b
        (5, 0),  # b -> v_1
    ]
    a_extras = _aietal_b3_extras_at_a(a_case)
    b_extras = [_aietal_b3_star_arc(arc) for arc in _aietal_b3_extras_at_a(star_case)]

    seen: set[tuple[int, int]] = set()
    out: list[tuple[int, int]] = []
    for arc in base + common + a_extras + b_extras:
        if arc not in seen:
            seen.add(arc)
            out.append(arc)
    return out


def _AiEtAl_B3_i_star_i() -> Benchmark:
    return Benchmark(
        name="AiEtAl_B3_i_star_i",
        n=6,
        arcs=_aietal_b3_arcs("i", "i"),
        expected="UNSAT",
        source="Ai, He, Li, Qin, Wang, arXiv:2408.02260, Appendix B.3 case (i)*x(i); see team/05_audit.md A.9.4.",
        notes="Verified B.3-alpha iso-class; hash 92edbcb1560d099f...",
    )


def _AiEtAl_B3_i_star_ii() -> Benchmark:
    return Benchmark(
        name="AiEtAl_B3_i_star_ii",
        n=6,
        arcs=_aietal_b3_arcs("i", "ii"),
        expected="UNSAT",
        source="Ai, He, Li, Qin, Wang, arXiv:2408.02260, Appendix B.3 case (i)*x(ii); see team/05_audit.md A.9.4.",
        notes="Verified B.3-beta representative; arc-reverse covers the symmetric (ii)*x(i) hash.",
    )


def _AiEtAl_B3_i_star_iii() -> Benchmark:
    return Benchmark(
        name="AiEtAl_B3_i_star_iii",
        n=6,
        arcs=_aietal_b3_arcs("i", "iii"),
        expected="UNSAT",
        source="Ai, He, Li, Qin, Wang, arXiv:2408.02260, Appendix B.3 case (i)*x(iii); see team/24_appendix_b3_figure_audit.md.",
        notes="Corrected 14-arc B.3 core; old 15-arc transcription with extra v_2->a is SAT.",
    )


def _AiEtAl_B3_i_star_iv() -> Benchmark:
    return Benchmark(
        name="AiEtAl_B3_i_star_iv",
        n=6,
        arcs=_aietal_b3_arcs("i", "iv"),
        expected="UNSAT",
        source="Ai, He, Li, Qin, Wang, arXiv:2408.02260, Appendix B.3 case (i)*x(iv); see team/05_audit.md A.9.4.",
        notes="Verified B.3-gamma iso-class; hash e6e7a2494bfa5cd4...",
    )


def _AiEtAl_B3_ii_star_ii() -> Benchmark:
    return Benchmark(
        name="AiEtAl_B3_ii_star_ii",
        n=6,
        arcs=_aietal_b3_arcs("ii", "ii"),
        expected="UNSAT",
        source="Ai, He, Li, Qin, Wang, arXiv:2408.02260, Appendix B.3 case (ii)*x(ii); see team/05_audit.md A.9.4.",
        notes="Verified B.3-delta iso-class; hash 10fae725561067fd...",
    )


def _AiEtAl_B3_ii_star_iii() -> Benchmark:
    return Benchmark(
        name="AiEtAl_B3_ii_star_iii",
        n=6,
        arcs=_aietal_b3_arcs("ii", "iii"),
        expected="UNSAT",
        source="Ai, He, Li, Qin, Wang, arXiv:2408.02260, Appendix B.3 case (ii)*x(iii); see team/24_appendix_b3_figure_audit.md.",
        notes="Corrected 14-arc B.3 core; old 15-arc transcription with extra v_2->a is SAT.",
    )


def _AiEtAl_B3_ii_star_iv() -> Benchmark:
    return Benchmark(
        name="AiEtAl_B3_ii_star_iv",
        n=6,
        arcs=_aietal_b3_arcs("ii", "iv"),
        expected="UNSAT",
        source="Ai, He, Li, Qin, Wang, arXiv:2408.02260, Appendix B.3 case (ii)*x(iv); see team/05_audit.md A.9.4.",
        notes="Verified B.3-epsilon iso-class; hash 0cab4a53e5e81027...",
    )


def _AiEtAl_B3_iii_star_iii() -> Benchmark:
    return Benchmark(
        name="AiEtAl_B3_iii_star_iii",
        n=6,
        arcs=_aietal_b3_arcs("iii", "iii"),
        expected="UNSAT",
        source="Ai, He, Li, Qin, Wang, arXiv:2408.02260, Appendix B.3 case (iii)*x(iii); see team/24_appendix_b3_figure_audit.md.",
        notes="Corrected 14-arc B.3 core; old 16-arc transcription with extra v_2->a and b->v_3 is SAT.",
    )


def _AiEtAl_B3_iii_star_iv() -> Benchmark:
    return Benchmark(
        name="AiEtAl_B3_iii_star_iv",
        n=6,
        arcs=_aietal_b3_arcs("iii", "iv"),
        expected="UNSAT",
        source="Ai, He, Li, Qin, Wang, arXiv:2408.02260, Appendix B.3 case (iii)*x(iv); see team/24_appendix_b3_figure_audit.md.",
        notes="Corrected 14-arc B.3 core; old 15-arc transcription with extra b->v_3 is SAT.",
    )


def _AiEtAl_B3_iii_star_v() -> Benchmark:
    return Benchmark(
        name="AiEtAl_B3_iii_star_v",
        n=6,
        arcs=_aietal_b3_arcs("iii", "v"),
        expected="UNSAT",
        source="Ai, He, Li, Qin, Wang, arXiv:2408.02260, Appendix B.3 case (iii)*x(v); see team/24_appendix_b3_figure_audit.md.",
        notes="Corrected 14-arc B.3 core; old 16-arc transcription with extra v_2->a and b->v_3 is SAT.",
    )


# ----------------------------------------------------------------------------
# Ai–He–Li–Qin–Wang 2024 (arXiv:2408.02260) Appendix B.3: (iv)* x (iv).
# The unique counterexample to Problem 1.6 of Bang-Jensen–Wang 2025, named
# explicitly on p. 3 of arXiv:2408.02260. 6 vertices, 14 arcs, 2-arc-strong
# split, no strong arc decomposition.
#
# Per-arc transcription audit: see team/05_audit.md, Appendix A.4. Every
# arc is text-forced from the proof of the (iv)*x(iv) case (p. 34) and the
# definition of the * operation (p. 31), plus structural-degree arguments
# matching the p. 34 proof's N^+/N^- counts. No figure-only ambiguity.
# ----------------------------------------------------------------------------


def _AiEtAl_iv_star_iv() -> Benchmark:
    """The 6-vertex digraph (iv)* x (iv) from Appendix B.3 of Ai, He, Li, Qin,
    Wang 2024 (arXiv:2408.02260).

    Base D[V_2] = S_{4,-2} on {v_1, v_2, v_3, v_4} (the 4-cycle
    v_1 -> v_2 -> v_3 -> v_4 -> v_1 plus diagonals v_1 -> v_3 and v_2 -> v_4).
    Configuration (iv) at vertex a:    arcs {v_4->a, a->v_2, v_2->a, a->v_3}.
    Configuration (iv)* at vertex b:   arcs {b->v_1, v_3->b, b->v_3, v_2->b}.

    Encoded with vertex map v_1=0, v_2=1, v_3=2, v_4=3, a=4, b=5.

    Properties (proof: see team/05_audit.md Appendix A.4):
        n = 6, m = 14, strongly connected, lambda^arc = 2.
        V_1 = {a, b} independent, V_2 semicomplete (S_{4,-2}).
        Split digraph, NOT semicomplete ({a, b} non-adjacent).
        *-self-symmetric (the whole digraph is isomorphic to its arc-reverse).

    The paper's Theorem 1.8 lists this as the only Appendix-B obstruction
    that is also referenced by name in the introduction ("the unique
    counterexample to Problem 1.6 of Bang-Jensen–Wang 2025").
    """
    arcs = [
        # D[V_2] = S_{4,-2}: 4-cycle v_1 v_2 v_3 v_4 v_1 + diagonals v_1->v_3, v_2->v_4
        (0, 1), (1, 2), (2, 3), (3, 0),  # 4-cycle
        (0, 2),                          # v_1 -> v_3 (diagonal)
        (1, 3),                          # v_2 -> v_4 (diagonal)
        # Configuration (iv) at a = 4:
        (3, 4),                          # v_4 -> a   (forced by p.31: "v_4 a in D")
        (4, 1),                          # a -> v_2   (forced by p.31: "av_2 in D")
        (1, 4),                          # v_2 -> a   (forced by d^-(a) >= 2)
        (4, 2),                          # a -> v_3   (forced by p.30 case-(iv) def)
        # Configuration (iv)* at b = 5 (image of (iv) under * = reverse + 180-rotate):
        (5, 0),                          # b -> v_1   (* image of v_4 -> a)
        (2, 5),                          # v_3 -> b   (* image of a -> v_2)
        (5, 2),                          # b -> v_3   (* image of v_2 -> a)
        (1, 5),                          # v_2 -> b   (* image of a -> v_3)
    ]
    return Benchmark(
        name="AiEtAl_iv_star_iv",
        n=6,
        arcs=arcs,
        expected="UNSAT",
        source="Ai, He, Li, Qin, Wang, arXiv:2408.02260, Appendix B.3 case (iv)*x(iv); see team/05_audit.md A.4.",
        notes="Unique counterexample to Problem 1.6 of Bang-Jensen–Wang 2025; D[V_2]=S_{4,-2}.",
    )


# ----------------------------------------------------------------------------
# SAT benchmarks
# ----------------------------------------------------------------------------


def _QR7_tournament() -> Benchmark:
    """The Paley tournament QR(7): vertices Z/7, arcs i -> j iff (j - i) mod 7
    is a nonzero quadratic residue. QRs mod 7 are {1, 2, 4}.

    A doubly regular 2-arc-strong tournament on 7 vertices. Arc-connectivity 3
    in fact: every vertex has in-degree 3 and out-degree 3, and the tournament
    is doubly regular, hence 3-arc-strong.

    By Bang-Jensen & Yeo 2004, every 2-arc-strong tournament != S_4 has a
    strong arc decomposition. QR(7) is a tournament on 7 vertices, not S_4, so
    SAT.
    """
    n = 7
    qr = {1, 2, 4}
    arcs: list[tuple[int, int]] = []
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            if (j - i) % n in qr:
                arcs.append((i, j))
    return Benchmark(
        name="QR7_tournament",
        n=n,
        arcs=arcs,
        expected="SAT",
        source="Bang-Jensen & Yeo 2004; QR(7) is 2-arc-strong, != S_4.",
        notes="Paley tournament on 7 vertices; in fact 3-arc-strong.",
    )


def _K5_bidirected() -> Benchmark:
    """K_5^*: complete bidirected digraph on 5 vertices. Arcs i -> j and j -> i
    for every i != j.

    Arc count: 20. Arc-connectivity: 4. Hence 4-arc-strong, so by any positive
    K >= 3 theorem (already by Bang-Jensen-Yeo 2004 for semicomplete digraphs)
    it has a strong arc decomposition.
    """
    n = 5
    arcs = [(i, j) for i in range(n) for j in range(n) if i != j]
    return Benchmark(
        name="K5_bidirected",
        n=n,
        arcs=arcs,
        expected="SAT",
        source="Bang-Jensen & Yeo 2004; K_5^* is 4-arc-strong semicomplete.",
        notes="Complete bidirected digraph on 5 vertices.",
    )


def _C5_doubled() -> Benchmark:
    """Directed cycle on 5 vertices doubled: every cycle arc has multiplicity 2.

    Arc-connectivity 2; Eulerian; trivially decomposable by giving each color
    one of the two copies of each arc.
    """
    n = 5
    arcs: list[tuple[int, int]] = []
    for i in range(n):
        arcs.append((i, (i + 1) % n))
        arcs.append((i, (i + 1) % n))
    return Benchmark(
        name="C5_doubled",
        n=n,
        arcs=arcs,
        expected="SAT",
        source="Trivial: split parallel arcs.",
        notes="Multigraph sanity instance; 2-arc-strong.",
    )


# ----------------------------------------------------------------------------
# Aggregate
# ----------------------------------------------------------------------------


def strict_split_unsat_benchmarks() -> list[Benchmark]:
    """Strict-split UNSAT catalogue entries currently safe for indexing.

    This includes the verified Appendix B.2 iso-classes and all verified B.3
    UNSAT products with reliable 14-arc core lists. The B.3 cases involving
    iii/v follow team/24_appendix_b3_figure_audit.md, which resolved the old
    mismatch as extra-arc transcription errors.
    """
    return [
        _S4(),
        _AiEtAl_Lemma211_smallest(),
        _AiEtAl_Lemma312_smallest(),
        _AiEtAl_B2_case_i(),
        _AiEtAl_B2_case_ii(),
        _AiEtAl_B2_case_iii(),
        _AiEtAl_B3_i_star_i(),
        _AiEtAl_B3_i_star_ii(),
        _AiEtAl_B3_i_star_iii(),
        _AiEtAl_B3_i_star_iv(),
        _AiEtAl_B3_ii_star_ii(),
        _AiEtAl_B3_ii_star_iii(),
        _AiEtAl_B3_ii_star_iv(),
        _AiEtAl_B3_iii_star_iii(),
        _AiEtAl_B3_iii_star_iv(),
        _AiEtAl_B3_iii_star_v(),
        _AiEtAl_iv_star_iv(),
    ]


def all_benchmarks() -> list[Benchmark]:
    return [
        _S4(),
        _C_2k_square(3),
        _C_2k_square(4),
        _C3_K2_K2_K2(),
        _C3_K2_K2_P2(),
        _C3_K2_K2_K3(),
        _AiEtAl_Lemma211_smallest(),
        _AiEtAl_Lemma312_smallest(),
        _AiEtAl_B2_case_i(),
        _AiEtAl_B2_case_ii(),
        _AiEtAl_B2_case_iii(),
        _AiEtAl_B3_i_star_i(),
        _AiEtAl_B3_i_star_ii(),
        _AiEtAl_B3_i_star_iii(),
        _AiEtAl_B3_i_star_iv(),
        _AiEtAl_B3_ii_star_ii(),
        _AiEtAl_B3_ii_star_iii(),
        _AiEtAl_B3_ii_star_iv(),
        _AiEtAl_B3_iii_star_iii(),
        _AiEtAl_B3_iii_star_iv(),
        _AiEtAl_B3_iii_star_v(),
        _AiEtAl_iv_star_iv(),
        _QR7_tournament(),
        _K5_bidirected(),
        _C5_doubled(),
    ]


if __name__ == "__main__":
    for b in all_benchmarks():
        D = b.build()
        print(
            f"{b.name:20s}  n={b.n:2d}  m={D.m():3d}  "
            f"strong={D.is_strongly_connected()}  "
            f"kappa'={D.arc_connectivity()}  "
            f"expected={b.expected}"
        )
