"""Route-B residuals: exhaustive verifier sweep over the two finite residuals
of `team/27_r3star_hard_case_edmonds.md` §7.

Residuals:

  1. (H1b) at |V_2| = 3 -- 3-arc-strong (1,0)-near-split digraphs where
     D^bullet[V_2] is strong with arc-connectivity 1 (a cut-arc).  On
     3 vertices, the strong semicomplete digraphs with lambda = 1 are
     exactly the directed 3-cycle and the 5 "3-cycle + extra arcs"
     orientations that retain a cut-arc (14 labelled kernels in total
     over the 6 labelled vertex orders, fewer when canonicalised --
     pynauty will collapse them).

  2. (H2) at |V_2| = 4 -- 3-arc-strong (1,0)-near-split digraphs where
     D^bullet[V_2] is isomorphic to S_4 = double-cycle on 4 vertices
     (Hamilton cycle plus the two 2-cycles on diagonals; 8 arcs).

For each generated instance we:

  - independently verify the (1,0)-near-split predicate;
  - compute lambda^arc and skip unless it equals 3;
  - canonicalise via `generators/canonicalize.py` and dedup;
  - call cross_check (ILP + SAT) and assert agreement;
  - log the SAT witness;
  - perform the alignment checks against the Specialist's
    §4 (H1b) / §4 (H2) construction:
      (a) each colour class is spanning strong (already implicit in
          the SAD definition; we double-check by Tarjan on the witness);
      (b) the colour containing e_0 (= internal arc) contains >= 1
          arc from R_q^+ and >= 1 arc from R_p^- (the "q-reaching"
          colour, satisfying Q_i where i is that colour);
      (c) the OTHER colour contains >= 1 arc from each of
          R_p^+, R_q^+, R_p^-, R_q^- (the "good" colour, satisfying
          P_{3-i} and Q_{3-i});
      (d) the colour containing the cut-arc e^* (for H1b) is the
          "good" colour in (c).

Output:

  - code/logs/route_b_residuals_<ts>.json with full instance log,
    witnesses, and alignment booleans per instance.
  - stdout summary table.

Hard rules enforced:

  - exhaustive enumeration (no sampling) over canonically distinct
    kernels and over all bridge configurations;
  - witness logged for every SAT instance;
  - independent (1,0)-near-split predicate check;
  - stop on any lambda = 3 UNSAT (extremely unlikely; record).
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
import time
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterator

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from cross_check import cross_check  # noqa: E402
from digraph import Digraph  # noqa: E402
from generators.canonicalize import canonical_key  # noqa: E402
from generators.near_split import (  # noqa: E402
    NSInstance,
    is_one_zero_near_split,
)


# ---------------------------------------------------------------------------
# Residual-kernel enumerators
# ---------------------------------------------------------------------------


def _enumerate_3vertex_semicomplete_lambda1() -> list[tuple[tuple[int, int], ...]]:
    """Return all labelled semicomplete orientations on V_2 = {0, 1, 2}
    that are strongly connected with arc-connectivity 1.

    For each unordered pair {u, v} with u < v in {0, 1, 2}, the
    orientation is one of: only u->v, only v->u, both (i.e. 2-cycle).
    So 3^3 = 27 orientations. We filter for strong and lambda = 1.
    """
    V = [0, 1, 2]
    pairs = [(0, 1), (0, 2), (1, 2)]
    results: list[tuple[tuple[int, int], ...]] = []
    for choices in itertools.product([0, 1, 2], repeat=3):
        arcs: list[tuple[int, int]] = []
        for (u, v), c in zip(pairs, choices):
            if c == 0:
                arcs.append((u, v))
            elif c == 1:
                arcs.append((v, u))
            else:
                arcs.extend([(u, v), (v, u)])
        D = Digraph.from_arcs(V, arcs)
        if not D.is_strongly_connected():
            continue
        if D.arc_connectivity() != 1:
            continue
        results.append(tuple(sorted(arcs)))
    return results


def _S4_arcs(V2: list[int]) -> tuple[tuple[int, int], ...]:
    """The arc-set of S_4 on V_2 = [v_a, v_b, v_c, v_d] (length 4).

    S_4 = double-cycle: Hamilton cycle v_0 -> v_1 -> v_2 -> v_3 -> v_0
    PLUS two diagonal 2-cycles v_0 <-> v_2 and v_1 <-> v_3.  Total 8
    arcs.
    """
    assert len(V2) == 4
    v0, v1, v2, v3 = V2
    arcs = [
        (v0, v1), (v1, v2), (v2, v3), (v3, v0),  # Hamilton cycle
        (v0, v2), (v2, v0),                       # diagonal 2-cycle 1
        (v1, v3), (v3, v1),                       # diagonal 2-cycle 2
    ]
    return tuple(arcs)


# ---------------------------------------------------------------------------
# Instance enumeration for a residual
# ---------------------------------------------------------------------------


def _all_bridge_arcs(V1: list[int], V2: list[int]) -> list[tuple[int, int]]:
    """All 2 * |V_1| * |V_2| candidate bridge arcs (both directions)."""
    out: list[tuple[int, int]] = []
    for a in V1:
        for b in V2:
            out.append((a, b))
            out.append((b, a))
    return out


def _bridge_subset_iter(
    bridges: list[tuple[int, int]],
    cap: int | None = None,
    seed: int = 20260517,
) -> Iterator[tuple[tuple[int, int], ...]]:
    """Yield subsets of `bridges` as tuples.

    Exhaustive (deterministic order) if cap is None or 2^|bridges| <= cap.
    Otherwise, deterministic random sampling biased toward moderate
    densities (p in {0.4, 0.5, 0.6, 0.7}), which is where 3-arc-strong
    instances live.
    """
    import random
    nB = len(bridges)
    total = 1 << nB
    if cap is None or total <= cap:
        for mask in range(total):
            yield tuple(bridges[i] for i in range(nB) if (mask >> i) & 1)
        return
    rng = random.Random(seed)
    densities = (0.4, 0.5, 0.6, 0.7)
    emitted: set[int] = set()
    # Try sampling up to 4 * cap candidates to fill the cap with unique subsets.
    attempts = 0
    while len(emitted) < cap and attempts < 4 * cap:
        attempts += 1
        p = rng.choice(densities)
        mask = 0
        for i in range(nB):
            if rng.random() < p:
                mask |= 1 << i
        if mask in emitted:
            continue
        emitted.add(mask)
        yield tuple(bridges[i] for i in range(nB) if (mask >> i) & 1)


def enumerate_h1b(
    v1_sizes: tuple[int, ...] = (2, 3, 4),
    bridge_cap_per_kernel: int | None = None,
) -> Iterator[NSInstance]:
    """Generate (1,0)-near-split candidates for residual (H1b).

    V_1 = [0, v1_size), V_2 = [v1_size, v1_size + 3).  D[V_2] is one of
    the 14 strong-lambda-1 semicomplete kernels on 3 vertices.  Every
    ordered V_1-internal pair is tried as the chord e_0.  Every bridge
    subset is enumerated.

    Note: many emitted instances will fail the lambda(D) = 3 gate;
    that's expected and filtered downstream.
    """
    kernels = _enumerate_3vertex_semicomplete_lambda1()
    counter = 0
    for v1_size in v1_sizes:
        V1 = list(range(v1_size))
        V2_local = [v1_size, v1_size + 1, v1_size + 2]
        # Shift kernel labels into V_2 coordinates.
        offset = v1_size
        bridges = _all_bridge_arcs(V1, V2_local)
        for kernel in kernels:
            # Re-label kernel arcs from {0,1,2} -> V_2_local.
            v2_arcs = tuple((u + offset, v + offset) for (u, v) in kernel)
            # Enumerate all V_1-internal ordered pairs.
            internal_candidates = [(a, b) for a in V1 for b in V1 if a != b]
            for internal in internal_candidates:
                for bridge_subset in _bridge_subset_iter(bridges, cap=bridge_cap_per_kernel):
                    arcs = list(v2_arcs) + [internal] + list(bridge_subset)
                    yield NSInstance(
                        name=f"H1b[|V1|={v1_size},int={internal},kern#={kernels.index(kernel)},k={counter}]",
                        n=v1_size + 3,
                        arcs=tuple(arcs),
                        V1=tuple(V1),
                        V2=tuple(V2_local),
                        internal_arc=internal,
                        construction="H1b_exhaustive",
                    )
                    counter += 1


def enumerate_h2(
    v1_sizes: tuple[int, ...] = (2, 3),
    bridge_cap_per_kernel: int | None = None,
) -> Iterator[NSInstance]:
    """Generate (1,0)-near-split candidates for residual (H2).

    V_1 = [0, v1_size), V_2 = [v1_size, v1_size + 4).  D[V_2] = S_4.
    Every ordered V_1-internal pair is tried.  Every bridge subset is
    enumerated.
    """
    counter = 0
    for v1_size in v1_sizes:
        V1 = list(range(v1_size))
        V2_local = [v1_size + i for i in range(4)]
        bridges = _all_bridge_arcs(V1, V2_local)
        v2_arcs = _S4_arcs(V2_local)
        internal_candidates = [(a, b) for a in V1 for b in V1 if a != b]
        for internal in internal_candidates:
            for bridge_subset in _bridge_subset_iter(bridges, cap=bridge_cap_per_kernel):
                arcs = list(v2_arcs) + [internal] + list(bridge_subset)
                yield NSInstance(
                    name=f"H2[|V1|={v1_size},int={internal},k={counter}]",
                    n=v1_size + 4,
                    arcs=tuple(arcs),
                    V1=tuple(V1),
                    V2=tuple(V2_local),
                    internal_arc=internal,
                    construction="H2_exhaustive",
                )
                counter += 1


# ---------------------------------------------------------------------------
# Side-label classification of a witness
# ---------------------------------------------------------------------------


def _classify_arc_side(
    arc: tuple[int, int, int],
    p: int,
    q: int,
    V2: set[int],
) -> str | None:
    """Return one of {'Rp+', 'Rq+', 'Rp-', 'Rq-'} or None.

    Definitions (verbatim from team/22_*: side labels at the contracted
    vertex r = p_bullet):

      R_p^+ : arcs r -> y in D^bullet with preimage (p, y), y in V_2.
              In the un-contracted D: this is (p, y) with y in V_2.
      R_q^+ : (q, y) with y in V_2.
      R_p^- : (x, p) with x in V_2.
      R_q^- : (x, q) with x in V_2.
    """
    u, v, _k = arc
    if u == p and v in V2:
        return "Rp+"
    if u == q and v in V2:
        return "Rq+"
    if v == p and u in V2:
        return "Rp-"
    if v == q and u in V2:
        return "Rq-"
    return None


def _witness_strong(arcs: list[tuple[int, int, int]], V: list[int]) -> bool:
    """True iff the (V, arcs) sub-digraph is spanning strong."""
    from digraph import is_strongly_connected_arcs
    return is_strongly_connected_arcs(V, arcs)


def _find_v2_cutarc(
    D_V2_arcs: list[tuple[int, int]], V2: list[int]
) -> tuple[int, int] | None:
    """Return a cut-arc of D[V_2] (any arc whose removal breaks strong
    connectivity), or None if none exists / not strong / multiple cut-arcs
    indistinguishable: returns the first found.

    For H1b kernels, exactly one cut-arc is the structural reference; if
    there are multiple, we return one (the witness check is robust to
    multiplicity since we only assert containment in the "good" colour).
    """
    if not D_V2_arcs:
        return None
    from digraph import is_strongly_connected_arcs

    # Build keyed arcs for is_strongly_connected_arcs.
    base = [(u, v, 0) for (u, v) in D_V2_arcs]
    if not is_strongly_connected_arcs(V2, base):
        return None
    for i, (u, v) in enumerate(D_V2_arcs):
        rest = [arc for j, arc in enumerate(base) if j != i]
        if not is_strongly_connected_arcs(V2, rest):
            return (u, v)
    return None


@dataclass
class AlignmentRecord:
    """Result of the §27 alignment check on a SAT witness."""

    # Both colour classes spanning strong on V(D)?  (must be True for SAD.)
    red_strong: bool = False
    blue_strong: bool = False

    # Colour of e_0 (the internal arc).  "R" or "B".  This is the colour
    # i in §4's notation (the colour that "absorbs" e_0).
    e0_colour: str = "?"

    # Counts of side-class arcs per colour.
    Rp_plus_R: int = 0
    Rq_plus_R: int = 0
    Rp_minus_R: int = 0
    Rq_minus_R: int = 0
    Rp_plus_B: int = 0
    Rq_plus_B: int = 0
    Rp_minus_B: int = 0
    Rq_minus_B: int = 0

    # "Good" colour (= 3 - i in §4 notation), the one NOT absorbing e_0:
    # must contain >= 1 of each side class.  We populate good_has_all and
    # bad_has_qreaching (the absorbing colour must have R_q^+ and R_p^-).
    good_colour: str = "?"
    good_has_all: bool = False  # all 4 classes present in good colour
    bad_has_qreaching: bool = False  # bad colour has R_q^+ and R_p^- (for Q_i)
    bad_has_preaching: bool = True  # P_i not required; placeholder

    # (H1b only) cut-arc colour: should be the good colour.
    cutarc_in_v2: tuple[int, int] | None = None
    cutarc_colour: str | None = None
    cutarc_in_good_colour: bool | None = None

    # Overall alignment verdict: all three §27 alignment conditions hold.
    aligned: bool = False


def _alignment_check(
    inst: NSInstance,
    witness: tuple[list[tuple[int, int, int]], list[tuple[int, int, int]]],
    is_h1b: bool,
) -> AlignmentRecord:
    """Check whether the SAT witness is compatible with the Specialist's
    §4 construction.

    The witness is a SAD (A_R, A_B) of D.  Side labels are at r = p_bullet,
    i.e. arcs touching p or q.  We verify:

      (1) both colour classes spanning strong on V(D);
      (2) the colour i = colour of e_0 has >= 1 R_q^+ arc and >= 1 R_p^-
          arc (so Q_i holds: a q -> p witness via the q_bullet out-arc
          and the p_bullet in-arc);
      (3) the other colour 3-i has >= 1 of each of R_p^+, R_q^+, R_p^-,
          R_q^- (so P_{3-i} AND Q_{3-i} hold: both p->q and q->p
          witnesses).

    For (H1b), we additionally check whether the cut-arc of D[V_2] lies
    in the "good" colour 3-i.  This is the alignment with the §4.2
    handling of the cut-arc.
    """
    red, blue = witness
    p, q = inst.internal_arc
    V2 = set(inst.V2)
    rec = AlignmentRecord()
    V = list(range(inst.n))
    rec.red_strong = _witness_strong(red, V)
    rec.blue_strong = _witness_strong(blue, V)

    # Find colour of e_0.
    e0_in_red = any((u == p and v == q) for (u, v, _k) in red)
    e0_in_blue = any((u == p and v == q) for (u, v, _k) in blue)
    if e0_in_red and not e0_in_blue:
        rec.e0_colour = "R"
        rec.good_colour = "B"
    elif e0_in_blue and not e0_in_red:
        rec.e0_colour = "B"
        rec.good_colour = "R"
    else:
        rec.e0_colour = "?"
        rec.good_colour = "?"

    # Classify witness arcs by side label.
    for arc in red:
        s = _classify_arc_side(arc, p, q, V2)
        if s == "Rp+":
            rec.Rp_plus_R += 1
        elif s == "Rq+":
            rec.Rq_plus_R += 1
        elif s == "Rp-":
            rec.Rp_minus_R += 1
        elif s == "Rq-":
            rec.Rq_minus_R += 1
    for arc in blue:
        s = _classify_arc_side(arc, p, q, V2)
        if s == "Rp+":
            rec.Rp_plus_B += 1
        elif s == "Rq+":
            rec.Rq_plus_B += 1
        elif s == "Rp-":
            rec.Rp_minus_B += 1
        elif s == "Rq-":
            rec.Rq_minus_B += 1

    # good_has_all: good colour has >= 1 of each side class.
    if rec.good_colour == "R":
        rec.good_has_all = (
            rec.Rp_plus_R >= 1 and rec.Rq_plus_R >= 1
            and rec.Rp_minus_R >= 1 and rec.Rq_minus_R >= 1
        )
        rec.bad_has_qreaching = (rec.Rq_plus_B >= 1 and rec.Rp_minus_B >= 1)
    elif rec.good_colour == "B":
        rec.good_has_all = (
            rec.Rp_plus_B >= 1 and rec.Rq_plus_B >= 1
            and rec.Rp_minus_B >= 1 and rec.Rq_minus_B >= 1
        )
        rec.bad_has_qreaching = (rec.Rq_plus_R >= 1 and rec.Rp_minus_R >= 1)
    else:
        rec.good_has_all = False
        rec.bad_has_qreaching = False

    # (H1b) cut-arc check: find cut-arc of D[V_2] and check its colour.
    if is_h1b:
        # Collect D[V_2] arcs from inst.arcs.
        v2_internal_arcs: list[tuple[int, int]] = []
        for (u, v) in inst.arcs:
            if u in V2 and v in V2:
                v2_internal_arcs.append((u, v))
        cutarc = _find_v2_cutarc(v2_internal_arcs, list(inst.V2))
        rec.cutarc_in_v2 = cutarc
        if cutarc is not None:
            in_red = any(
                (u == cutarc[0] and v == cutarc[1]) for (u, v, _k) in red
            )
            in_blue = any(
                (u == cutarc[0] and v == cutarc[1]) for (u, v, _k) in blue
            )
            if in_red and not in_blue:
                rec.cutarc_colour = "R"
            elif in_blue and not in_red:
                rec.cutarc_colour = "B"
            else:
                rec.cutarc_colour = "?"
            rec.cutarc_in_good_colour = (rec.cutarc_colour == rec.good_colour)

    # Overall: aligned iff red & blue strong; good_has_all; bad_has_qreaching.
    rec.aligned = (
        rec.red_strong
        and rec.blue_strong
        and rec.good_has_all
        and rec.bad_has_qreaching
        and rec.e0_colour in ("R", "B")
    )
    return rec


# ---------------------------------------------------------------------------
# Sweep
# ---------------------------------------------------------------------------


@dataclass
class ResidualStats:
    name: str
    streamed: int = 0
    ns_confirmed: int = 0
    strong: int = 0
    lambda_eq_3: int = 0
    lambda_other: int = 0
    canonical_distinct: int = 0
    verified_sat: int = 0
    verified_unsat: int = 0
    disagreements: int = 0
    aligned: int = 0
    not_aligned: int = 0
    cutarc_in_good: int = 0
    cutarc_in_bad: int = 0
    cutarc_undefined: int = 0
    elapsed_s: float = 0.0


@dataclass
class ResidualLog:
    started_at: str
    config: dict[str, Any] = field(default_factory=dict)
    h1b_stats: dict[str, Any] = field(default_factory=dict)
    h2_stats: dict[str, Any] = field(default_factory=dict)
    h1b_canonical_witnesses: list[dict[str, Any]] = field(default_factory=list)
    h2_canonical_witnesses: list[dict[str, Any]] = field(default_factory=list)
    h1b_alignment_failures: list[dict[str, Any]] = field(default_factory=list)
    h2_alignment_failures: list[dict[str, Any]] = field(default_factory=list)
    counterexamples: list[dict[str, Any]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    finished_at: str | None = None
    elapsed_s: float | None = None


def _process_instance(
    inst: NSInstance,
    is_h1b: bool,
    stats: ResidualStats,
    log: ResidualLog,
    seen_canonical: dict[str, dict[str, Any]],
    instance_time_s: float,
    sample_witness_cap: int = 80,
) -> bool:
    """Process one instance.  Returns False if a lambda=3 UNSAT was found
    (caller should stop the sweep) or True to continue.
    """
    stats.streamed += 1

    # 1. Independent (1,0)-NS predicate.
    D = inst.build()
    ok, why = is_one_zero_near_split(D, list(inst.V1), list(inst.V2))
    if not ok:
        log.notes.append(f"non-(1,0)-NS: {inst.name}: {why}")
        return True
    stats.ns_confirmed += 1

    # 2. Strongly connected?
    if not D.is_strongly_connected():
        return True
    stats.strong += 1

    # 3. lambda gate (must be 3).
    lam = D.arc_connectivity()
    if lam != 3:
        stats.lambda_other += 1
        return True
    stats.lambda_eq_3 += 1

    # 4. Canonical hash; skip if seen.
    can = canonical_key(D)
    if can in seen_canonical:
        # Dedup but accumulate the labelled-instance count.
        seen_canonical[can]["count"] += 1
        return True
    stats.canonical_distinct += 1

    # 5. Cross-check.
    cross = cross_check(D, inst.name, time_limit_s=instance_time_s)
    if not cross.agree:
        stats.disagreements += 1
        log.notes.append(
            f"FATAL DISAGREE: {inst.name} ILP={cross.ilp.get('status')} "
            f"SAT={cross.sat.get('status')}"
        )
        return True

    status = cross.ilp.get("status")
    if status == "UNSAT":
        stats.verified_unsat += 1
        entry = {
            "name": inst.name,
            "canonical_hash": can,
            "n": inst.n,
            "m": len(inst.arcs),
            "V1": list(inst.V1),
            "V2": list(inst.V2),
            "internal_arc": list(inst.internal_arc),
            "arcs": [list(a) for a in inst.arcs],
            "lambda_arc": lam,
            "status": "UNSAT",
        }
        log.counterexamples.append(entry)
        seen_canonical[can] = {"name": inst.name, "count": 1, "status": "UNSAT"}
        print(
            f"  *** lambda=3 UNSAT (1,0)-NS ({'H1b' if is_h1b else 'H2'}): "
            f"{inst.name}",
            flush=True,
        )
        return False  # signal STOP

    if status != "SAT":
        log.notes.append(
            f"UNKNOWN: {inst.name} ILP={status} SAT={cross.sat.get('status')}"
        )
        return True

    # SAT.
    stats.verified_sat += 1
    witness = cross.sat.get("witness")
    align = _alignment_check(inst, witness, is_h1b=is_h1b)
    if align.aligned:
        stats.aligned += 1
    else:
        stats.not_aligned += 1
    if is_h1b and align.cutarc_in_good_colour is True:
        stats.cutarc_in_good += 1
    elif is_h1b and align.cutarc_in_good_colour is False:
        stats.cutarc_in_bad += 1
    elif is_h1b:
        stats.cutarc_undefined += 1

    seen_canonical[can] = {
        "name": inst.name,
        "count": 1,
        "status": "SAT",
        "aligned": align.aligned,
    }

    entry = {
        "name": inst.name,
        "canonical_hash": can,
        "n": inst.n,
        "m": len(inst.arcs),
        "V1": list(inst.V1),
        "V2": list(inst.V2),
        "internal_arc": list(inst.internal_arc),
        "arcs": [list(a) for a in inst.arcs],
        "lambda_arc": lam,
        "status": "SAT",
        "witness_red": [[u, v, k] for (u, v, k) in witness[0]],
        "witness_blue": [[u, v, k] for (u, v, k) in witness[1]],
        "alignment": asdict(align),
    }
    target_list = log.h1b_canonical_witnesses if is_h1b else log.h2_canonical_witnesses
    if len(target_list) < sample_witness_cap or not align.aligned:
        target_list.append(entry)
    if not align.aligned:
        fail_list = log.h1b_alignment_failures if is_h1b else log.h2_alignment_failures
        fail_list.append(entry)
        print(
            f"  [{'H1b' if is_h1b else 'H2'}] ALIGNMENT FAIL: {inst.name}  "
            f"red_strong={align.red_strong} blue_strong={align.blue_strong} "
            f"good={align.good_colour} good_has_all={align.good_has_all} "
            f"bad_has_qreach={align.bad_has_qreaching}",
            flush=True,
        )

    return True


def sweep_residual(
    name: str,
    enumerator: Iterator[NSInstance],
    is_h1b: bool,
    log: ResidualLog,
    instance_time_s: float,
    sample_witness_cap: int = 80,
    progress_every: int = 2000,
) -> ResidualStats:
    stats = ResidualStats(name=name)
    seen_canonical: dict[str, dict[str, Any]] = {}
    t0 = time.time()
    stopped = False
    for inst in enumerator:
        keep_going = _process_instance(
            inst, is_h1b, stats, log, seen_canonical,
            instance_time_s=instance_time_s,
            sample_witness_cap=sample_witness_cap,
        )
        if stats.streamed % progress_every == 0 and stats.streamed > 0:
            print(
                f"  [{name}] streamed={stats.streamed} ns={stats.ns_confirmed} "
                f"strong={stats.strong} l3={stats.lambda_eq_3} "
                f"can={stats.canonical_distinct} sat={stats.verified_sat} "
                f"unsat={stats.verified_unsat} aligned={stats.aligned} "
                f"t={time.time() - t0:.0f}s",
                flush=True,
            )
        if not keep_going:
            stopped = True
            break
    stats.elapsed_s = time.time() - t0
    if stopped:
        log.notes.append(f"sweep '{name}' stopped on lambda=3 UNSAT.")
    return stats


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Route-B residuals: exhaustive sweep over (H1b at |V_2|=3) "
        "and (H2 at |V_2|=4)."
    )
    parser.add_argument("--instance-time-s", type=float, default=8.0)
    parser.add_argument(
        "--h1b-v1-sizes",
        type=int,
        nargs="+",
        default=[2, 3],
        help="V_1 sizes to enumerate for H1b (|V_2|=3). Default: [2, 3].",
    )
    parser.add_argument(
        "--h2-v1-sizes",
        type=int,
        nargs="+",
        default=[2],
        help="V_1 sizes to enumerate for H2 (|V_2|=4). Default: [2].",
    )
    parser.add_argument(
        "--bridge-cap-h1b",
        type=int,
        default=None,
        help="Cap on bridge-subset count per (V1, V2, kernel, internal); "
        "None = exhaustive.",
    )
    parser.add_argument(
        "--bridge-cap-h2",
        type=int,
        default=None,
        help="Cap on bridge-subset count per (V1, V2, internal); None = exhaustive.",
    )
    parser.add_argument("--logs-dir", default=str(HERE / "logs"))
    args = parser.parse_args()

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    logs_dir = Path(args.logs_dir)
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / f"route_b_residuals_{timestamp}.json"

    print("=" * 72, flush=True)
    print("Route B residuals -- exhaustive sweep over §27 §7 residuals", flush=True)
    print("=" * 72, flush=True)
    print(f"  H1b V_1 sizes: {args.h1b_v1_sizes}", flush=True)
    print(f"  H2  V_1 sizes: {args.h2_v1_sizes}", flush=True)
    print(f"  bridge-cap-h1b: {args.bridge_cap_h1b}", flush=True)
    print(f"  bridge-cap-h2:  {args.bridge_cap_h2}", flush=True)
    print(f"  instance-time-s: {args.instance_time_s}", flush=True)
    print(flush=True)

    log = ResidualLog(
        started_at=time.strftime("%Y-%m-%d %H:%M:%S"),
        config={
            "instance_time_s": args.instance_time_s,
            "h1b_v1_sizes": list(args.h1b_v1_sizes),
            "h2_v1_sizes": list(args.h2_v1_sizes),
            "bridge_cap_h1b": args.bridge_cap_h1b,
            "bridge_cap_h2": args.bridge_cap_h2,
        },
    )

    t0 = time.time()

    # ---- H1b sweep -------------------------------------------------------
    print("[H1b] starting...", flush=True)
    h1b_stats = sweep_residual(
        name="H1b",
        enumerator=enumerate_h1b(
            v1_sizes=tuple(args.h1b_v1_sizes),
            bridge_cap_per_kernel=args.bridge_cap_h1b,
        ),
        is_h1b=True,
        log=log,
        instance_time_s=args.instance_time_s,
    )
    log.h1b_stats = asdict(h1b_stats)
    print(
        f"[H1b] done: streamed={h1b_stats.streamed} ns={h1b_stats.ns_confirmed} "
        f"lambda=3={h1b_stats.lambda_eq_3} canonical={h1b_stats.canonical_distinct} "
        f"sat={h1b_stats.verified_sat} unsat={h1b_stats.verified_unsat} "
        f"aligned={h1b_stats.aligned}/{h1b_stats.verified_sat} "
        f"cutarc_in_good={h1b_stats.cutarc_in_good} "
        f"elapsed={h1b_stats.elapsed_s:.0f}s",
        flush=True,
    )

    # ---- H2 sweep -------------------------------------------------------
    print("\n[H2] starting...", flush=True)
    h2_stats = sweep_residual(
        name="H2",
        enumerator=enumerate_h2(
            v1_sizes=tuple(args.h2_v1_sizes),
            bridge_cap_per_kernel=args.bridge_cap_h2,
        ),
        is_h1b=False,
        log=log,
        instance_time_s=args.instance_time_s,
    )
    log.h2_stats = asdict(h2_stats)
    print(
        f"[H2] done: streamed={h2_stats.streamed} ns={h2_stats.ns_confirmed} "
        f"lambda=3={h2_stats.lambda_eq_3} canonical={h2_stats.canonical_distinct} "
        f"sat={h2_stats.verified_sat} unsat={h2_stats.verified_unsat} "
        f"aligned={h2_stats.aligned}/{h2_stats.verified_sat} "
        f"elapsed={h2_stats.elapsed_s:.0f}s",
        flush=True,
    )

    log.finished_at = time.strftime("%Y-%m-%d %H:%M:%S")
    log.elapsed_s = time.time() - t0

    # ---- Summary -------------------------------------------------------
    print("\n" + "=" * 72, flush=True)
    print("Final verdict", flush=True)
    print("=" * 72, flush=True)

    h1b_ok = (
        h1b_stats.verified_unsat == 0
        and h1b_stats.disagreements == 0
        and h1b_stats.not_aligned == 0
        and h1b_stats.verified_sat > 0
    )
    h2_ok = (
        h2_stats.verified_unsat == 0
        and h2_stats.disagreements == 0
        and h2_stats.not_aligned == 0
        and h2_stats.verified_sat > 0
    )

    print(
        f"  H1b: {'CLOSED' if h1b_ok else 'NOT CLOSED'}  "
        f"({h1b_stats.canonical_distinct} canonical instances, "
        f"{h1b_stats.verified_sat} SAT, {h1b_stats.verified_unsat} UNSAT, "
        f"{h1b_stats.not_aligned} alignment failures)",
        flush=True,
    )
    print(
        f"  H2:  {'CLOSED' if h2_ok else 'NOT CLOSED'}  "
        f"({h2_stats.canonical_distinct} canonical instances, "
        f"{h2_stats.verified_sat} SAT, {h2_stats.verified_unsat} UNSAT, "
        f"{h2_stats.not_aligned} alignment failures)",
        flush=True,
    )

    if log.counterexamples:
        print("\n  *** lambda=3 UNSAT counterexample(s) detected ***", flush=True)
        for ce in log.counterexamples:
            print(f"    {ce['name']} n={ce['n']} m={ce['m']}", flush=True)

    print(f"\nlog: {log_path}", flush=True)
    with log_path.open("w") as f:
        json.dump(asdict(log), f, indent=2, default=str)

    return 0


if __name__ == "__main__":
    sys.exit(main())
