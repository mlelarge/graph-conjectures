"""Phase 4 Vehicle 6 driver.

Sweeps `generators.glue_sad` over the SAD-decomposable inner-part library,
verifies each candidate via SAT (with witness retention!), and runs the
P1/P2/P3 pattern checks from CL1 (team/08).

Per the spec:
  * target >= 50 verified lambda=3 SAT candidates per ordered template pair;
  * stream 2000-5000 candidates total;
  * log everything (including witness 2-coloring) to a JSON file;
  * print pattern-check tables to stdout.

CL1 pattern definitions (in our notation):

  P1 (bridge-direction monochromaticity). Every T_2 -> T_1 bridge has the
     same color in the witness. (After we normalize the witness so the
     b21 bridges are majority-blue if they have one.) We measure: among
     all candidates, what fraction has 100% of its b21 bridges sharing a
     single color, and what fraction has 100% of its b12 bridges sharing
     a single color. CL1 hypothesis (3) only requires *direction*
     monochromaticity (each direction goes mostly to one color, but each
     direction does contain both colors); pattern P1 in the empirical
     report is the stricter "every b21 bridge is monochromatic." We
     report both.

  P2 (tight 3-cut compartment (2,1) split). For every tight 3-cut
     delta^+(X) of D, classify the X by which compartments (S1n, I,
     S2n) it touches and tabulate the (R, B) color split. The CL1
     predictions are:
        * any tight 3-cut with X meeting both V_1 and V_2 splits (2, 1);
        * the predicted (2, 1) signature is determined locally by the
          interface bridge it contains.
     We measure: fraction of tight 3-cuts whose color split is exactly
     (2, 1), grouped by compartment signature.

  P3 (degree-3 vertex out-cut (2,1) split). For every vertex v with
     d^+(v) = 3, its three out-arcs split (2, 1) in color (one minority,
     two majority). The "free" version follows from strong-decomposition
     definition; the CL1-strengthened version (per team/08 §1.2) says
     this is forced *exactly* when d^+(v) = 3. We measure the fraction
     of (instance, deg-3 vertex) pairs whose out-cut splits (2, 1).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from itertools import combinations
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from cross_check import cross_check  # noqa: E402
from digraph import Digraph  # noqa: E402
from generators.canonicalize import canonical_key  # noqa: E402
from generators.glue_sad import (  # noqa: E402
    SadGenConfig,
    SadGluedInstance,
    generate_sad_gluings,
    passes_arc_strong_exactly_3,
    vertex_degree_feasible,
)
from generators.sad_inner_parts import SadInnerPart, build_library  # noqa: E402
from verifier_ilp import verify_ilp  # noqa: E402
from verifier_sat import verify_sat  # noqa: E402


# ----------------------------------------------------------------------------
# Pattern analysis primitives
# ----------------------------------------------------------------------------


def _compartment_of_vertex(
    v: int, interface_start: int, interface_end: int
) -> str:
    """Return 'S1n', 'I', or 'S2n' for vertex `v` under the merged labelling."""
    if v < interface_start:
        return "S1n"
    if v < interface_end:
        return "I"
    return "S2n"


def _keyed_arcs(arcs: list[tuple[int, int]]) -> list[tuple[int, int, int]]:
    """Convert an arc-list into the (u, v, k) keys used by the verifier,
    accounting for parallel-arc multiplicities."""
    ctr: Counter = Counter()
    out: list[tuple[int, int, int]] = []
    for (u, v) in arcs:
        k = ctr[(u, v)]
        out.append((u, v, k))
        ctr[(u, v)] += 1
    return out


def _normalize_witness(
    inst: SadGluedInstance,
    keyed_arcs: list[tuple[int, int, int]],
    color_of: dict[tuple[int, int, int], str],
) -> dict[tuple[int, int, int], str]:
    """Optionally swap R <-> B globally so that majority of b21 bridges is B.

    Returns the (possibly flipped) color_of dict.
    """
    interface_end = inst.n_non1 + inst.s
    side2_start = interface_end
    b21_keys = [
        ke for ke in keyed_arcs
        if ke[0] >= side2_start and ke[1] < inst.n_non1
    ]
    if not b21_keys:
        return color_of
    rB = sum(1 for ke in b21_keys if color_of[ke] == "B")
    rR = sum(1 for ke in b21_keys if color_of[ke] == "R")
    if rB >= rR:
        return color_of
    flipped = {ke: ("B" if c == "R" else "R") for ke, c in color_of.items()}
    return flipped


@dataclass
class PatternRecord:
    """Per-instance summary of pattern compliance."""

    # P1
    b12_count: int = 0
    b21_count: int = 0
    b12_mono: bool = False  # all b12 bridges same color
    b21_mono: bool = False
    b12_majority_color: str | None = None
    b21_majority_color: str | None = None
    b12_color_count: tuple[int, int] = (0, 0)  # (R, B)
    b21_color_count: tuple[int, int] = (0, 0)

    # P2 (tight 3-cuts)
    n_tight3: int = 0
    # Group tight 3-cuts by "compartment signature" sorted tuple of
    # (compartment-pair) for each of the three cut arcs.
    tight3_signature_counts: dict[str, int] = field(default_factory=dict)
    # For each signature, count of (R, B) color splits across the cut.
    tight3_signature_splits: dict[str, dict[str, int]] = field(
        default_factory=dict
    )
    # CL1 P2 predicate: at least one tight 3-cut crossing V_1 and V_2 has
    # the predicted (2, 1) signature. We report the fraction (2,1) of
    # *all* tight 3-cuts as the headline number.
    n_tight3_split_21: int = 0  # cuts splitting (2,1) or (1,2)
    n_tight3_split_30: int = 0  # monochromatic 3-cuts (would falsify SAD)

    # P3 (degree-3 vertex out-cuts)
    n_deg3_out_vertices: int = 0
    n_deg3_out_split_21: int = 0
    n_deg3_in_vertices: int = 0
    n_deg3_in_split_21: int = 0


def _enumerate_tight_3_cuts(
    keyed_arcs: list[tuple[int, int, int]], n: int, cap: int = 5000
) -> list[tuple[frozenset[int], list[tuple[int, int, int]]]]:
    """Return a list of (X, cut_arcs) for every X with |delta^+(X)| == 3.

    For n up to ~14 this enumerates ~2^n subsets; we early-prune by cut
    size. Returns at most `cap` tight cuts (the analysis is unaffected
    in expectation, since for n <= 14 the count is small).
    """
    out: list[tuple[frozenset[int], list[tuple[int, int, int]]]] = []
    V = list(range(n))
    # Faster: iterate subsets via combinations but only up to n / 2 then
    # use the complement; we'd be careful about delta^+ vs delta^-.
    # Actually delta^+(X) and delta^+(V \ X) are different cuts (they
    # have different sizes in directed graphs). So enumerate all proper
    # non-empty X.
    for r in range(1, n):
        for X_tup in combinations(V, r):
            X = frozenset(X_tup)
            cut_arcs: list[tuple[int, int, int]] = []
            size = 0
            for ke in keyed_arcs:
                u, v, _ = ke
                if u in X and v not in X:
                    cut_arcs.append(ke)
                    size += 1
                    if size > 3:
                        break
            if size == 3:
                out.append((X, cut_arcs))
                if len(out) >= cap:
                    return out
    return out


def _classify_arc_compartments(
    arc: tuple[int, int, int], interface_start: int, interface_end: int
) -> tuple[str, str]:
    u, v, _ = arc
    return (
        _compartment_of_vertex(u, interface_start, interface_end),
        _compartment_of_vertex(v, interface_start, interface_end),
    )


def analyse_patterns(
    inst: SadGluedInstance,
    witness: tuple[list[tuple[int, int, int]], list[tuple[int, int, int]]],
    enumerate_tight3: bool = True,
) -> PatternRecord:
    """Run the P1, P2, P3 pattern checks on a single verified candidate."""
    keyed_arcs = _keyed_arcs(list(inst.arcs))
    red_arcs, blue_arcs = witness
    red_set = set(red_arcs)
    blue_set = set(blue_arcs)
    color_of: dict[tuple[int, int, int], str] = {}
    for ke in keyed_arcs:
        if ke in red_set:
            color_of[ke] = "R"
        elif ke in blue_set:
            color_of[ke] = "B"
        else:
            color_of[ke] = "?"
    color_of = _normalize_witness(inst, keyed_arcs, color_of)

    rec = PatternRecord()
    interface_start = inst.n_non1
    interface_end = inst.n_non1 + inst.s
    side2_start = interface_end

    # -- P1 ----------------------------------------------------------------
    b12_keys = [
        ke for ke in keyed_arcs
        if ke[0] < interface_start and ke[1] >= side2_start
    ]
    b21_keys = [
        ke for ke in keyed_arcs
        if ke[0] >= side2_start and ke[1] < interface_start
    ]
    rec.b12_count = len(b12_keys)
    rec.b21_count = len(b21_keys)
    b12_R = sum(1 for ke in b12_keys if color_of[ke] == "R")
    b12_B = len(b12_keys) - b12_R
    b21_R = sum(1 for ke in b21_keys if color_of[ke] == "R")
    b21_B = len(b21_keys) - b21_R
    rec.b12_color_count = (b12_R, b12_B)
    rec.b21_color_count = (b21_R, b21_B)
    rec.b12_mono = (b12_R == 0) or (b12_B == 0)
    rec.b21_mono = (b21_R == 0) or (b21_B == 0)
    rec.b12_majority_color = "R" if b12_R >= b12_B else "B"
    rec.b21_majority_color = "R" if b21_R >= b21_B else "B"

    # -- P2 ----------------------------------------------------------------
    if enumerate_tight3 and inst.n <= 14:
        tight3 = _enumerate_tight_3_cuts(keyed_arcs, inst.n)
        rec.n_tight3 = len(tight3)
        sig_counts: dict[str, int] = defaultdict(int)
        sig_splits: dict[str, dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        n21 = 0
        n30 = 0
        for X, cut_arcs in tight3:
            # compartment signature
            sig_parts = []
            for a in cut_arcs:
                comp = _classify_arc_compartments(a, interface_start, interface_end)
                sig_parts.append(comp)
            sig_parts.sort()
            sig_key = "|".join(f"{a}->{b}" for a, b in sig_parts)
            sig_counts[sig_key] += 1
            # color split
            R = sum(1 for a in cut_arcs if color_of[a] == "R")
            B = 3 - R
            split = f"R{R}B{B}"
            sig_splits[sig_key][split] = sig_splits[sig_key].get(split, 0) + 1
            if (R == 2 and B == 1) or (R == 1 and B == 2):
                n21 += 1
            elif R == 0 or B == 0:
                n30 += 1
        rec.tight3_signature_counts = dict(sig_counts)
        rec.tight3_signature_splits = {
            k: dict(v) for k, v in sig_splits.items()
        }
        rec.n_tight3_split_21 = n21
        rec.n_tight3_split_30 = n30

    # -- P3 ----------------------------------------------------------------
    outd: Counter = Counter()
    ind: Counter = Counter()
    for u, v, _ in keyed_arcs:
        outd[u] += 1
        ind[v] += 1
    for v in range(inst.n):
        if outd[v] == 3:
            rec.n_deg3_out_vertices += 1
            out_keys = [ke for ke in keyed_arcs if ke[0] == v]
            R = sum(1 for ke in out_keys if color_of[ke] == "R")
            B = 3 - R
            if (R, B) in {(2, 1), (1, 2)}:
                rec.n_deg3_out_split_21 += 1
        if ind[v] == 3:
            rec.n_deg3_in_vertices += 1
            in_keys = [ke for ke in keyed_arcs if ke[1] == v]
            R = sum(1 for ke in in_keys if color_of[ke] == "R")
            B = 3 - R
            if (R, B) in {(2, 1), (1, 2)}:
                rec.n_deg3_in_split_21 += 1

    return rec


# ----------------------------------------------------------------------------
# Driver
# ----------------------------------------------------------------------------


@dataclass
class V6Stats:
    streamed: int = 0
    deg_gate_pass: int = 0
    kappa3_pass: int = 0
    kappa_higher: int = 0
    kappa_lower: int = 0
    verified_sat: int = 0
    verified_unsat: int = 0
    disagreements: int = 0
    elapsed_s: float = 0.0

    @property
    def hit_rate_k3(self) -> float:
        return self.kappa3_pass / max(self.streamed, 1)


@dataclass
class V6Log:
    started_at: str
    config: dict[str, Any] = field(default_factory=dict)
    library: list[dict[str, Any]] = field(default_factory=list)
    stats: dict[str, Any] = field(default_factory=dict)
    pair_counts: dict[str, int] = field(default_factory=dict)
    pair_kappa3_counts: dict[str, int] = field(default_factory=dict)
    pair_higher_counts: dict[str, int] = field(default_factory=dict)
    candidates: list[dict[str, Any]] = field(default_factory=list)
    pattern_summary: dict[str, Any] = field(default_factory=dict)
    canonical_summary: dict[str, Any] = field(default_factory=dict)
    cl1_violations: list[dict[str, Any]] = field(default_factory=list)
    finished_at: str | None = None
    elapsed_s: float | None = None
    notes: list[str] = field(default_factory=list)


def _entry_for_candidate(
    inst: SadGluedInstance,
    sat_witness: tuple[list[tuple[int, int, int]], list[tuple[int, int, int]]],
    cross: Any,
    rec: PatternRecord,
    canonical: str,
) -> dict[str, Any]:
    red, blue = sat_witness
    return {
        "name": inst.name,
        "n": inst.n,
        "m": len(inst.arcs),
        "part1": inst.part1_name,
        "part2": inst.part2_name,
        "s": inst.s,
        "n_non1": inst.n_non1,
        "S1": list(inst.S1),
        "S2": list(inst.S2),
        "phi": [list(p) for p in inst.phi],
        "bridges_12": [list(b) for b in inst.bridges_12],
        "bridges_21": [list(b) for b in inst.bridges_21],
        "arcs": [list(a) for a in inst.arcs],
        "ilp_status": cross.ilp.get("status"),
        "sat_status": cross.sat.get("status"),
        "ilp_time": cross.ilp.get("time_s"),
        "sat_time": cross.sat.get("time_s"),
        "witness_red": [[u, v, k] for (u, v, k) in red],
        "witness_blue": [[u, v, k] for (u, v, k) in blue],
        "canonical_hash": canonical,
        "patterns": asdict(rec),
    }


def run_sweep(
    parts: list[SadInnerPart],
    cfg: SadGenConfig,
    cap_streamed: int,
    cap_per_pair: int,
    instance_time_s: float,
    log: V6Log,
) -> None:
    stats = V6Stats()
    t0 = time.time()
    pair_streamed: dict[tuple[str, str], int] = defaultdict(int)
    pair_kappa3: dict[tuple[str, str], int] = defaultdict(int)
    pair_higher: dict[tuple[str, str], int] = defaultdict(int)
    pair_verified: dict[tuple[str, str], int] = defaultdict(int)

    for inst in generate_sad_gluings(parts, cfg, ordered_pairs=True):
        if stats.streamed >= cap_streamed:
            break
        stats.streamed += 1
        pair = (inst.part1_name, inst.part2_name)
        pair_streamed[pair] += 1

        if not vertex_degree_feasible(list(inst.arcs), inst.n):
            continue
        stats.deg_gate_pass += 1

        D = inst.build()
        if not D.is_strongly_connected():
            stats.kappa_lower += 1
            continue
        lam = D.arc_connectivity()
        if lam < 3:
            stats.kappa_lower += 1
            continue
        if lam > 3:
            stats.kappa_higher += 1
            pair_higher[pair] += 1
            continue
        stats.kappa3_pass += 1
        pair_kappa3[pair] += 1

        if pair_verified[pair] >= cap_per_pair:
            continue

        # Cross-check
        cross = cross_check(D, inst.name, time_limit_s=instance_time_s)
        if not cross.agree:
            stats.disagreements += 1
            log.notes.append(
                f"FATAL: cross-check disagree on {inst.name}: "
                f"ILP={cross.ilp.get('status')} SAT={cross.sat.get('status')}"
            )
            print(f"  *** FATAL DISAGREE: {inst.name}", flush=True)
            continue

        status = cross.ilp.get("status")
        if status == "UNSAT":
            stats.verified_unsat += 1
            print(
                f"  *** UNSAT 3-arc-strong candidate ***  name={inst.name}  "
                f"n={inst.n}  m={len(inst.arcs)}",
                flush=True,
            )
            # Stop-on-counterexample protocol (manual): log it conspicuously.
            log.notes.append(
                f"COUNTEREXAMPLE candidate: {inst.name} -- run "
                f"team/01 checklist and produce team/12 report."
            )
            entry: dict[str, Any] = {
                "name": inst.name,
                "n": inst.n,
                "m": len(inst.arcs),
                "part1": inst.part1_name,
                "part2": inst.part2_name,
                "s": inst.s,
                "S1": list(inst.S1),
                "S2": list(inst.S2),
                "arcs": [list(a) for a in inst.arcs],
                "bridges_12": [list(b) for b in inst.bridges_12],
                "bridges_21": [list(b) for b in inst.bridges_21],
                "ilp_status": "UNSAT",
                "sat_status": cross.sat.get("status"),
            }
            log.candidates.append(entry)
            continue

        if status != "SAT":
            log.notes.append(
                f"UNKNOWN status on {inst.name}: ILP={status} "
                f"SAT={cross.sat.get('status')}"
            )
            continue

        stats.verified_sat += 1
        pair_verified[pair] += 1
        witness = cross.sat.get("witness")
        if witness is None:
            log.notes.append(f"no SAT witness recovered for {inst.name}")
            continue

        rec = analyse_patterns(inst, witness)
        canonical = canonical_key(D)
        entry = _entry_for_candidate(inst, witness, cross, rec, canonical)
        log.candidates.append(entry)

        # CL1-violation check: at this point inst's parts are SAD by
        # construction (hypothesis 1), bridge counts are >= 2 each
        # (hypothesis 2 satisfied by config), so hypothesis (3) and (4)
        # are the predicate of interest. We flag any candidate where the
        # witness exhibits a violation of the *empirical* CL1 patterns:
        # in particular a tight 3-cut not splitting (2,1) (which would
        # mean either monochromatic, hence the cut is uncovered in one
        # color — but the witness IS a SAD so this should not happen
        # for non-degenerate cuts).
        if rec.n_tight3_split_30 > 0:
            log.cl1_violations.append({
                "name": inst.name,
                "kind": "monochromatic_tight3",
                "count": rec.n_tight3_split_30,
                "details": "witness has a tight 3-cut with all 3 arcs the same color",
            })

        if stats.streamed - (stats.streamed // 200) * 200 == 0:
            print(
                f"  [V6] streamed={stats.streamed} k3={stats.kappa3_pass} "
                f"sat={stats.verified_sat} unsat={stats.verified_unsat} "
                f"elapsed={time.time() - t0:.0f}s",
                flush=True,
            )

    stats.elapsed_s = time.time() - t0
    log.stats = asdict(stats)
    log.pair_counts = {f"{a}->{b}": c for (a, b), c in pair_streamed.items()}
    log.pair_kappa3_counts = {f"{a}->{b}": c for (a, b), c in pair_kappa3.items()}
    log.pair_higher_counts = {f"{a}->{b}": c for (a, b), c in pair_higher.items()}


# ----------------------------------------------------------------------------
# Pattern aggregation
# ----------------------------------------------------------------------------


def aggregate_patterns(log: V6Log) -> dict[str, Any]:
    """Aggregate P1, P2, P3 pattern fractions across all SAT candidates."""
    cands = [c for c in log.candidates if c.get("sat_status") == "SAT"]
    if not cands:
        return {"n_candidates": 0}

    n = len(cands)
    # P1
    n_b21_mono = sum(1 for c in cands if c["patterns"]["b21_mono"])
    n_b12_mono = sum(1 for c in cands if c["patterns"]["b12_mono"])
    # Direction-monochromatic both
    n_both_mono = sum(
        1 for c in cands
        if c["patterns"]["b21_mono"] and c["patterns"]["b12_mono"]
    )

    # Bridge color split averages
    avg_b21 = (
        sum(c["patterns"]["b21_color_count"][0] for c in cands) / n,
        sum(c["patterns"]["b21_color_count"][1] for c in cands) / n,
    )
    avg_b12 = (
        sum(c["patterns"]["b12_color_count"][0] for c in cands) / n,
        sum(c["patterns"]["b12_color_count"][1] for c in cands) / n,
    )

    # P2: tight 3-cut splits, aggregated
    total_t3 = sum(c["patterns"]["n_tight3"] for c in cands)
    total_t3_21 = sum(c["patterns"]["n_tight3_split_21"] for c in cands)
    total_t3_30 = sum(c["patterns"]["n_tight3_split_30"] for c in cands)
    # Fraction of instances with at least one tight 3-cut and all of them
    # splitting (2, 1)
    n_t3_all_21 = sum(
        1 for c in cands
        if c["patterns"]["n_tight3"] > 0
        and c["patterns"]["n_tight3_split_21"] == c["patterns"]["n_tight3"]
    )
    n_with_t3 = sum(1 for c in cands if c["patterns"]["n_tight3"] > 0)

    # P3
    total_deg3_out = sum(c["patterns"]["n_deg3_out_vertices"] for c in cands)
    total_deg3_out_21 = sum(
        c["patterns"]["n_deg3_out_split_21"] for c in cands
    )
    total_deg3_in = sum(c["patterns"]["n_deg3_in_vertices"] for c in cands)
    total_deg3_in_21 = sum(c["patterns"]["n_deg3_in_split_21"] for c in cands)

    # Per-pair tabulation
    per_pair: dict[str, dict[str, Any]] = {}
    pair_buckets: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for c in cands:
        pair_buckets[(c["part1"], c["part2"])].append(c)
    for (a, b), bucket in pair_buckets.items():
        k = len(bucket)
        per_pair[f"{a}->{b}"] = {
            "n": k,
            "p1_b21_mono_frac": sum(1 for c in bucket if c["patterns"]["b21_mono"]) / k,
            "p1_b12_mono_frac": sum(1 for c in bucket if c["patterns"]["b12_mono"]) / k,
            "p1_both_mono_frac": sum(
                1 for c in bucket
                if c["patterns"]["b21_mono"] and c["patterns"]["b12_mono"]
            ) / k,
            "p2_t3_total": sum(c["patterns"]["n_tight3"] for c in bucket),
            "p2_t3_21_total": sum(c["patterns"]["n_tight3_split_21"] for c in bucket),
            "p2_t3_30_total": sum(c["patterns"]["n_tight3_split_30"] for c in bucket),
            "p3_deg3_out_total": sum(c["patterns"]["n_deg3_out_vertices"] for c in bucket),
            "p3_deg3_out_21_total": sum(c["patterns"]["n_deg3_out_split_21"] for c in bucket),
            "p3_deg3_in_total": sum(c["patterns"]["n_deg3_in_vertices"] for c in bucket),
            "p3_deg3_in_21_total": sum(c["patterns"]["n_deg3_in_split_21"] for c in bucket),
        }

    return {
        "n_candidates": n,
        "p1": {
            "b21_mono_fraction": n_b21_mono / n,
            "b12_mono_fraction": n_b12_mono / n,
            "both_mono_fraction": n_both_mono / n,
            "avg_b21_RB_after_normalize": avg_b21,
            "avg_b12_RB_after_normalize": avg_b12,
        },
        "p2": {
            "total_tight3_cuts": total_t3,
            "fraction_21_split": (total_t3_21 / total_t3) if total_t3 else None,
            "fraction_mono_30_split": (total_t3_30 / total_t3) if total_t3 else None,
            "n_instances_with_tight3": n_with_t3,
            "n_instances_all_tight3_21": n_t3_all_21,
            "fraction_instances_all_tight3_21": (
                n_t3_all_21 / n_with_t3 if n_with_t3 else None
            ),
        },
        "p3": {
            "deg3_out_vertices_total": total_deg3_out,
            "fraction_deg3_out_21": (
                total_deg3_out_21 / total_deg3_out if total_deg3_out else None
            ),
            "deg3_in_vertices_total": total_deg3_in,
            "fraction_deg3_in_21": (
                total_deg3_in_21 / total_deg3_in if total_deg3_in else None
            ),
        },
        "per_pair": per_pair,
    }


def aggregate_canonical(log: V6Log) -> dict[str, Any]:
    """Canonical-hash deduplication: count labeled-distinct vs
    iso-canonical-distinct."""
    cands = [c for c in log.candidates if c.get("sat_status") == "SAT"]
    keys: dict[str, list[str]] = defaultdict(list)
    for c in cands:
        keys[c["canonical_hash"]].append(c["name"])
    classes = sorted(keys.values(), key=len, reverse=True)
    size_dist = Counter(len(c) for c in classes)
    return {
        "n_labeled_distinct": len(cands),
        "n_canonical_distinct": len(keys),
        "largest_iso_class_size": len(classes[0]) if classes else 0,
        "iso_class_size_distribution": {
            str(k): v for k, v in sorted(size_dist.items())
        },
    }


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------


def main() -> int:
    p = argparse.ArgumentParser(description="Phase 4 Vehicle 6 driver")
    p.add_argument("--cap-streamed", type=int, default=3000)
    p.add_argument("--cap-per-pair", type=int, default=60)
    p.add_argument("--interfaces-per-pair", type=int, default=8)
    p.add_argument("--bridges-per-setup", type=int, default=2)
    p.add_argument("--instance-time-s", type=float, default=10.0)
    p.add_argument("--logs-dir", default=str(HERE / "logs"))
    p.add_argument("--seed", type=int, default=20260516)
    args = p.parse_args()

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    logs_dir = Path(args.logs_dir)
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / f"phase4v6_{timestamp}.json"

    print("=" * 72, flush=True)
    print("Phase 4 Vehicle 6 — SAD-decomposable inner-part gluings", flush=True)
    print("=" * 72, flush=True)

    parts = build_library()
    print(f"Inner-part library: {len(parts)} entries", flush=True)
    for pp in parts:
        D = pp.build()
        print(
            f"  {pp.name:16s} n={pp.n:2d} m={len(pp.arcs):3d} "
            f"lambda={D.arc_connectivity()} family={pp.family}",
            flush=True,
        )
    print(flush=True)

    log = V6Log(
        started_at=time.strftime("%Y-%m-%d %H:%M:%S"),
        config={
            "cap_streamed": args.cap_streamed,
            "cap_per_pair": args.cap_per_pair,
            "interfaces_per_pair": args.interfaces_per_pair,
            "bridges_per_setup": args.bridges_per_setup,
            "instance_time_s": args.instance_time_s,
            "seed": args.seed,
        },
        library=[
            {
                "name": pp.name,
                "n": pp.n,
                "m": len(pp.arcs),
                "lambda": pp.lambda_arc,
                "family": pp.family,
            }
            for pp in parts
        ],
    )

    cfg = SadGenConfig(
        interface_sizes=(1, 2, 3, 4),
        bridge_count_pairs=(
            (2, 2), (2, 3), (3, 2), (3, 3),
            (2, 4), (4, 2), (3, 4), (4, 3),
            (4, 4), (5, 2), (2, 5),
        ),
        interfaces_per_pair=args.interfaces_per_pair,
        bridges_per_setup=args.bridges_per_setup,
        seed=args.seed,
    )

    t0 = time.time()
    run_sweep(
        parts=parts,
        cfg=cfg,
        cap_streamed=args.cap_streamed,
        cap_per_pair=args.cap_per_pair,
        instance_time_s=args.instance_time_s,
        log=log,
    )

    # Aggregation
    log.pattern_summary = aggregate_patterns(log)
    log.canonical_summary = aggregate_canonical(log)
    log.finished_at = time.strftime("%Y-%m-%d %H:%M:%S")
    log.elapsed_s = time.time() - t0

    # -- Stdout report ---------------------------------------------------------
    print("=" * 72, flush=True)
    print("Sweep complete.", flush=True)
    s = log.stats
    print(
        f"  streamed={s['streamed']} deg_ok={s['deg_gate_pass']} "
        f"kappa=3 exactly={s['kappa3_pass']} "
        f"kappa>3 (rejected)={s['kappa_higher']} "
        f"kappa<3={s['kappa_lower']}",
        flush=True,
    )
    print(
        f"  verified_sat={s['verified_sat']} verified_unsat={s['verified_unsat']} "
        f"disagreements={s['disagreements']} elapsed={s['elapsed_s']:.0f}s",
        flush=True,
    )
    rej_higher = s["kappa_higher"] / max(s["streamed"], 1)
    print(
        f"  hit-rate(kappa=3)={100 * s['kappa3_pass'] / max(s['streamed'], 1):.1f}%"
        f"  reject-rate(kappa>3)={100 * rej_higher:.1f}%",
        flush=True,
    )

    cs = log.canonical_summary
    print(
        f"  canonical: {cs['n_labeled_distinct']} labeled-distinct -> "
        f"{cs['n_canonical_distinct']} canonical-distinct  "
        f"(largest iso-class={cs['largest_iso_class_size']})",
        flush=True,
    )

    # Pattern tables
    ps = log.pattern_summary
    if ps.get("n_candidates", 0) > 0:
        print("\n" + "=" * 72, flush=True)
        print("P1 (bridge-direction monochromaticity)", flush=True)
        print("=" * 72, flush=True)
        p1 = ps["p1"]
        print(
            f"  P1a (every b21 mono):      "
            f"{100 * p1['b21_mono_fraction']:6.1f}% "
            f"({int(p1['b21_mono_fraction'] * ps['n_candidates'])}"
            f"/{ps['n_candidates']})",
            flush=True,
        )
        print(
            f"  P1b (every b12 mono):      "
            f"{100 * p1['b12_mono_fraction']:6.1f}% "
            f"({int(p1['b12_mono_fraction'] * ps['n_candidates'])}"
            f"/{ps['n_candidates']})",
            flush=True,
        )
        print(
            f"  P1c (both mono):           "
            f"{100 * p1['both_mono_fraction']:6.1f}% "
            f"({int(p1['both_mono_fraction'] * ps['n_candidates'])}"
            f"/{ps['n_candidates']})",
            flush=True,
        )
        print(
            f"  avg b21 (R, B) after norm: ({p1['avg_b21_RB_after_normalize'][0]:.2f}, "
            f"{p1['avg_b21_RB_after_normalize'][1]:.2f})",
            flush=True,
        )
        print(
            f"  avg b12 (R, B) after norm: ({p1['avg_b12_RB_after_normalize'][0]:.2f}, "
            f"{p1['avg_b12_RB_after_normalize'][1]:.2f})",
            flush=True,
        )

        print("\n" + "=" * 72, flush=True)
        print("P2 (tight 3-cut color split)", flush=True)
        print("=" * 72, flush=True)
        p2 = ps["p2"]
        print(f"  total tight 3-cuts:        {p2['total_tight3_cuts']}", flush=True)
        f21 = p2["fraction_21_split"]
        f30 = p2["fraction_mono_30_split"]
        print(
            f"  fraction (2, 1) split:     "
            f"{100 * (f21 or 0):6.2f}%",
            flush=True,
        )
        print(
            f"  fraction mono (3, 0):      "
            f"{100 * (f30 or 0):6.4f}% "
            f"(should be 0 by SAD definition)",
            flush=True,
        )
        f_all21 = p2["fraction_instances_all_tight3_21"]
        print(
            f"  instances with all-tight-3 (2,1):"
            f"  {100 * (f_all21 or 0):6.2f}% "
            f"({p2['n_instances_all_tight3_21']}"
            f"/{p2['n_instances_with_tight3']})",
            flush=True,
        )

        print("\n" + "=" * 72, flush=True)
        print("P3 (degree-3 vertex out-/in-cut (2, 1) split)", flush=True)
        print("=" * 72, flush=True)
        p3 = ps["p3"]
        print(
            f"  deg-3 out vertices:        {p3['deg3_out_vertices_total']}  "
            f"(2, 1) split fraction: "
            f"{100 * (p3['fraction_deg3_out_21'] or 0):6.2f}%",
            flush=True,
        )
        print(
            f"  deg-3 in vertices:         {p3['deg3_in_vertices_total']}  "
            f"(2, 1) split fraction: "
            f"{100 * (p3['fraction_deg3_in_21'] or 0):6.2f}%",
            flush=True,
        )

        # Per-pair table (top by candidate count)
        print("\n" + "=" * 72, flush=True)
        print("Per-pair P1/P2/P3 fractions (sorted by candidate count)", flush=True)
        print("=" * 72, flush=True)
        pp_items = sorted(
            ps["per_pair"].items(), key=lambda x: -x[1]["n"]
        )
        print(
            f"  {'pair':50s}  {'n':>4s}  {'P1a':>6s}  {'P1b':>6s}  "
            f"{'P1c':>6s}  {'P2-21':>8s}  {'P3o':>8s}",
            flush=True,
        )
        for name, d in pp_items[:30]:
            p2_frac = (
                d["p2_t3_21_total"] / d["p2_t3_total"]
                if d["p2_t3_total"] else None
            )
            p3_frac = (
                d["p3_deg3_out_21_total"] / d["p3_deg3_out_total"]
                if d["p3_deg3_out_total"] else None
            )
            print(
                f"  {name:50s}  {d['n']:4d}  "
                f"{100*d['p1_b21_mono_frac']:5.1f}%  "
                f"{100*d['p1_b12_mono_frac']:5.1f}%  "
                f"{100*d['p1_both_mono_frac']:5.1f}%  "
                f"{(100*p2_frac) if p2_frac is not None else 0:7.2f}%  "
                f"{(100*p3_frac) if p3_frac is not None else 0:7.2f}%",
                flush=True,
            )

    if log.cl1_violations:
        print("\n" + "=" * 72, flush=True)
        print(f"CL1-violation candidates: {len(log.cl1_violations)}", flush=True)
        print("=" * 72, flush=True)
        for v in log.cl1_violations[:10]:
            print(f"  {v['name']:60s}  {v['kind']}  {v.get('details', '')}", flush=True)

    if s["verified_unsat"] > 0:
        print("\n" + "=" * 72, flush=True)
        print("WARNING: UNSAT 3-arc-strong candidate(s) found!", flush=True)
        print(
            f"   Run team/01 checklist; canonicalize; produce team/12 report.",
            flush=True,
        )

    print(f"\nlog: {log_path}", flush=True)
    with log_path.open("w") as f:
        json.dump(asdict(log), f, indent=2, default=str)

    return 0


if __name__ == "__main__":
    sys.exit(main())
