"""Clean 2-cut recursion for the q_0=1 face (docs sec. 18).

With the clean 2-cut schedule  M_2[:s] | M_0 | M_1 | M_2[s:]  (q_0=1 is automatic,
sec.17), the parent layer heights reduce to EXACT formulas in which M_0, M_1 enter
only as scalars and ONLY M_2 carries two staircases (pre_1, suf_2):

    Q1 = max( q1(M_0), q1(M_2), q1(M_1) + pre_1(M_2, s) )
    Q2 = max( q2(M_1), q2(M_2), q2(M_0) + suf_2(M_2, m-s) )

Validated against closure_heights (0 mismatches).  The recursion reproduces
F_4 = 15, but the (pre_1, suf_2) Pareto frontier grows ~x5.2 per level
(10, 54, 274, ...), i.e. exponentially -- so the construction does not close
computationally; the obstruction is exactly that frontier growth.
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass

from stilde_profile_closure import step_profile


@dataclass(frozen=True)
class PortfolioCutCertificate:
    """Certificate that a clean 2-cut preserves chosen endpoint heights."""

    cut: int
    target_q1: int
    target_q2: int
    need_pre1: int
    need_suf2: int
    pre1_at_cut: int
    suf2_after_cut: int
    parent_q1: int
    parent_q2: int


def parent_heights_2cut(m0, m1, m2, s):
    """Exact (Q1, Q2) for the 2-cut M_2[:s]|M_0|M_1|M_2[s:] (StepProfiles in)."""
    m = 3 ** m2.depth
    q1 = max(m0.heights[1], m2.heights[1], m1.heights[1] + m2.prefix[1][s])
    q2 = max(m1.heights[2], m2.heights[2], m0.heights[2] + m2.suffix[2][m - s])
    return q1, q2


def parent_heights_3piece(m0, m1, m2, s, t):
    """Exact (Q1, Q2) for M_2[:s]|M_0|M_2[s:t]|M_1|M_2[t:].

    This is the two-cut extension of the clean 2-cut.  The middle M_2 block lies
    after M_0 but before M_1, so it contributes to both the colour-2 suffix read
    from the first cut and the colour-1 prefix read from the second cut.
    """

    m = 3 ** m2.depth
    if not 0 <= s <= t <= m:
        raise ValueError(f"cuts must satisfy 0 <= s <= t <= {m}")
    q1 = max(m0.heights[1], m2.heights[1], m1.heights[1] + m2.prefix[1][t])
    q2 = max(m1.heights[2], m2.heights[2], m0.heights[2] + m2.suffix[2][m - s])
    return q1, q2


def endpoint_targets(m0, m1, m2):
    """Endpoint heights before the two crossing terms are paid."""

    return max(m0.heights[1], m2.heights[1]), max(m1.heights[2], m2.heights[2])


def portfolio_cut_certificates(m0, m1, m2, target=None):
    """All cuts whose crossing terms do not increase the endpoint target.

    For a portfolio step, M_0 supplies the q_1 endpoint, M_1 supplies the q_2
    endpoint, and M_2 supplies the floating staircase.  With target (A,B), the
    exact formulas reduce feasibility to one cut satisfying

        pre_1(M_2,s) <= A - q_1(M_1)
        suf_2(M_2,m-s) <= B - q_2(M_0).

    If target is omitted, use the smallest endpoint pair visible before the
    crossing terms: (max(q_1(M_0),q_1(M_2)), max(q_2(M_1),q_2(M_2))).
    """

    if target is None:
        target = endpoint_targets(m0, m1, m2)
    target_q1, target_q2 = target
    need_pre1 = target_q1 - m1.heights[1]
    need_suf2 = target_q2 - m0.heights[2]
    if need_pre1 < 0 or need_suf2 < 0:
        return []

    m = 3 ** m2.depth
    out = []
    for cut in range(m + 1):
        pre1 = m2.prefix[1][cut]
        suf2 = m2.suffix[2][m - cut]
        if pre1 > need_pre1 or suf2 > need_suf2:
            continue
        parent_q1, parent_q2 = parent_heights_2cut(m0, m1, m2, cut)
        if parent_q1 <= target_q1 and parent_q2 <= target_q2:
            out.append(
                PortfolioCutCertificate(
                    cut=cut,
                    target_q1=target_q1,
                    target_q2=target_q2,
                    need_pre1=need_pre1,
                    need_suf2=need_suf2,
                    pre1_at_cut=pre1,
                    suf2_after_cut=suf2,
                    parent_q1=parent_q1,
                    parent_q2=parent_q2,
                )
            )
    return out


def order_2cut(m0, m1, m2, s):
    m = 3 ** m2.depth
    return ([2 * m + v for v in m2.order[:s]] + [v for v in m0.order]
            + [m + v for v in m1.order] + [2 * m + v for v in m2.order[s:]])


def order_3piece(m0, m1, m2, s, t):
    """Order for M_2[:s]|M_0|M_2[s:t]|M_1|M_2[t:]."""

    m = 3 ** m2.depth
    if not 0 <= s <= t <= m:
        raise ValueError(f"cuts must satisfy 0 <= s <= t <= {m}")
    return (
        [2 * m + v for v in m2.order[:s]]
        + [v for v in m0.order]
        + [2 * m + v for v in m2.order[s:t]]
        + [m + v for v in m1.order]
        + [2 * m + v for v in m2.order[t:]]
    )


def parent_state_2cut(m0, m1, m2, s):
    """Exact (pre_1, suf_2) state for the 2-cut parent.

    The parent order is M_2[:s] | M_0 | M_1 | M_2[s:].  These formulas show that
    the reduced two-staircase state is closed under the clean 2-cut: no full
    interval profile is needed to compute the next (pre_1, suf_2).
    """
    m = 3 ** m2.depth
    if not 0 <= s <= m:
        raise ValueError(f"s must be in [0,{m}]")

    pre1 = []
    for t in range(3 * m + 1):
        if t <= s:
            value = m2.prefix[1][t]
        elif t <= s + m:
            n0 = t - s
            value = max(m2.prefix[1][s], m0.prefix[1][n0])
        elif t <= s + 2 * m:
            n1 = t - s - m
            value = max(m0.heights[1], m1.prefix[1][n1] + m2.prefix[1][s])
        else:
            n2 = t - 2 * m
            value = max(
                m0.heights[1],
                m1.heights[1] + m2.prefix[1][s],
                m2.prefix[1][n2],
            )
        pre1.append(value)

    suf2_by_start = []
    for t in range(3 * m + 1):
        if t < s:
            value = max(
                m2.suffix[2][m - t],
                m1.heights[2],
                m0.heights[2] + m2.suffix[2][m - s],
            )
        elif t <= s + m:
            n0 = t - s
            value = max(
                m1.heights[2],
                m0.suffix[2][m - n0] + m2.suffix[2][m - s],
            )
        elif t <= s + 2 * m:
            n1 = t - s - m
            value = max(m1.suffix[2][m - n1], m2.suffix[2][m - s])
        else:
            n2 = t - 2 * m
            value = m2.suffix[2][m - n2]
        suf2_by_start.append(value)
    suf2 = tuple(suf2_by_start[3 * m - length] for length in range(3 * m + 1))
    return tuple(pre1), suf2


def _key(p):
    return (p.prefix[1], p.suffix[2])


def _dom(a, b):
    return all(all(x <= y for x, y in zip(sa, sb)) for sa, sb in zip(a, b))


def _pareto(profiles, cap):
    by = {}
    for p in profiles:
        by.setdefault(_key(p), p)
    items = list(by.items())
    keep = [p for k, p in items if not any(k2 != k and _dom(k2, k) for k2, _ in items)]
    keep.sort(key=lambda p: p.heights[1] * p.heights[2])
    return keep[:cap]


def run(max_depth, cap=400, sample_triples=4000, seed=0, verbose=True):
    """Reduced 2-cut recursion. Returns {depth: (F_k, frontier_size)}."""
    import random
    rng = random.Random(seed)
    lvl = [step_profile(list(o), 2) for o in itertools.permutations(range(9))]
    front = _pareto([p for p in lvl if p.heights[0] == 1], cap)
    out = {2: (min(p.heights[1] * p.heights[2] for p in front), len(front))}
    if verbose:
        print(f"depth 2: F={out[2][0]}  frontier={out[2][1]}", flush=True)
    for depth in range(3, max_depth + 1):
        m = 3 ** (depth - 1)
        bestF = 10 ** 9
        by_shape = {}
        for _ in range(sample_triples):
            m0, m1, m2 = (rng.choice(front), rng.choice(front), rng.choice(front))
            for s in range(m + 1):
                q1, q2 = parent_heights_2cut(m0, m1, m2, s)
                if q1 * q2 < bestF:
                    bestF = q1 * q2
                by_shape.setdefault((q1, q2), []).append((m0, m1, m2, s))
        profs = []
        for cands in by_shape.values():
            for (m0, m1, m2, s) in cands[:6]:
                p = step_profile(order_2cut(m0, m1, m2, s), depth)
                if p.heights[0] == 1:
                    profs.append(p)
        front = _pareto(profs, cap)
        out[depth] = (bestF, len(front))
        if verbose:
            print(f"depth {depth}: F={bestF}  frontier={len(front)}", flush=True)
    return out


if __name__ == "__main__":
    run(5, cap=400, sample_triples=4000)
