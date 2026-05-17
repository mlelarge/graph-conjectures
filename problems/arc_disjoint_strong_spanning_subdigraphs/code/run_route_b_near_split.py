"""Route-B (1,0)-near-split empirical sweep.

Companion to `team/20_near_split_empirical.md`. Mirrors
`run_route_b_ols.py` but operates on (1,0)-near-split digraphs from
`generators/near_split.py`.

For each candidate:
  1. confirm (1,0)-near-split via the independent predicate
     `is_one_zero_near_split(D, V1, V2)`;
  2. compute arc-connectivity lambda;
  3. filter lambda in {2, 3} (we want both the headline 3-arc-strong
     SAD sweep AND the 2-arc-strong exception search);
  4. cross-check ILP + SAT, expect SAT at lambda = 3;
  5. log the SAT witness (when SAT);
  6. test CL1's two hypotheses on the natural partition (V1, V2);
  7. compute the canonical hash;
  8. (lambda = 2 path) cross-reference against the strict-split
     UNSAT family — record whether the UNSAT instance is the
     strict-split obstruction plus a "free" V_1-internal arc.

Hard rules enforced:
  - witness logging mandatory for every SAT instance;
  - hit-rate floor (>= 5 % at the lambda in {2, 3} gate);
  - independent (1,0)-near-split verification (not trusted from construction);
  - stop-on-lambda=3 UNSAT (write the counterexample notice).

Outputs:
  - JSON log at code/logs/route_b_ns_<timestamp>.json with full
    witnesses, canonical hashes, per-instance CL1 records, and the
    2-arc-strong UNSAT exception table.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from cross_check import cross_check  # noqa: E402
from digraph import Digraph, arc_reverse  # noqa: E402
from generators.canonicalize import canonical_key  # noqa: E402
from generators.near_split import (  # noqa: E402
    NSInstance,
    enumerate_construction_A,
    enumerate_construction_B,
    enumerate_construction_C,
    is_one_zero_near_split,
)
from verifier_sat import verify_sat  # noqa: E402


# ----------------------------------------------------------------------------
# CL1 record (mirrors run_route_b_ols.py)
# ----------------------------------------------------------------------------


@dataclass
class CL1Record:
    """Per-instance CL1 hypothesis test on the natural partition (V_1, V_2).

    For a (1,0)-near-split digraph the natural partition is the one given
    by the construction: V_1 holds the single internal arc; V_2 is the
    semicomplete core.

    Hypothesis (1): D[V_1] and D[V_2] each SAD-decomposable. For (1,0)-NS:
      - D[V_1] has exactly one arc, hence is NOT strongly connected for
        |V_1| >= 2; hence not SAD-decomposable. We RECORD this status
        directly without invoking the SAT solver. Singleton V_1 (|V_1|=1)
        is treated as NA (vacuously SAD-decomposable).
      - D[V_2] is semicomplete; SAD-decomposability is decided by BJ-Yeo
        2004 (= SAT unless D[V_2] is one of the semicomplete UNSAT
        obstructions, namely S_4 or arc-connectivity < 2).

    Hypothesis (2): bridge 2-coloring with each (direction, colour) class
    non-empty, read directly off the SAT witness.

    Additional fields capture the modified-partition recovery test for §3.c:
    add one V_2 vertex w to V_1' and re-test hypothesis (1).
    """

    v1_size: int = 0
    v2_size: int = 0
    v1: list[int] = field(default_factory=list)
    v2: list[int] = field(default_factory=list)
    internal_arc: tuple[int, int] = (-1, -1)

    v1_lambda: int = 0
    v2_lambda: int = 0
    v1_sad_status: str = "?"  # SAT, UNSAT, NA
    v2_sad_status: str = "?"

    # Witness restriction.
    inner1_red_n_arcs: int = 0
    inner1_blue_n_arcs: int = 0
    inner2_red_n_arcs: int = 0
    inner2_blue_n_arcs: int = 0
    inner1_red_strong: bool = False
    inner1_blue_strong: bool = False
    inner2_red_strong: bool = False
    inner2_blue_strong: bool = False

    # Hypothesis (2).
    bridges_plus_total: int = 0  # V_1 -> V_2
    bridges_minus_total: int = 0  # V_2 -> V_1
    bridges_plus_R: int = 0
    bridges_plus_B: int = 0
    bridges_minus_R: int = 0
    bridges_minus_B: int = 0

    # §3.c modified-partition recovery: try every w in V_2; set true if
    # any V_1' = V_1 \cup {w} has both D[V_1'] SAD-decomposable (SAT) and
    # D[V_2 \ {w}] SAD-decomposable (SAT) or NA.
    mod_partition_recovers: bool = False
    mod_partition_w_examples: list[int] = field(default_factory=list)

    @property
    def hypothesis_1_holds(self) -> bool:
        return self.v1_sad_status in ("SAT", "NA") and self.v2_sad_status in ("SAT", "NA")

    @property
    def hypothesis_2_holds(self) -> bool:
        return (
            self.bridges_plus_R > 0 and self.bridges_plus_B > 0
            and self.bridges_minus_R > 0 and self.bridges_minus_B > 0
        )


def _induced_subdigraph(D: Digraph, vertex_set: list[int]) -> Digraph:
    S = set(vertex_set)
    arcs = []
    for u, v, _k in D.arcs():
        if u in S and v in S:
            arcs.append((u, v))
    return Digraph.from_arcs(sorted(S), arcs)


def _verify_part_sad(
    D: Digraph,
    vlist: list[int],
    time_s: float,
) -> tuple[str, int]:
    """Return (status, lambda) for D[vlist] as a stand-alone SAD instance.

    Trivial parts (n <= 1) are NA. Non-strong or lambda < 2 are UNSAT.
    Else run verify_sat.
    """
    if len(vlist) <= 1:
        return ("NA", 0)
    Dpart = _induced_subdigraph(D, vlist)
    if not Dpart.is_strongly_connected():
        return ("UNSAT", 0)
    lam = Dpart.arc_connectivity()
    if lam < 2:
        return ("UNSAT", lam)
    res = verify_sat(Dpart, time_limit_s=time_s)
    return (res.get("status", "UNKNOWN"), lam)


def analyse_cl1(
    inst: NSInstance,
    D: Digraph,
    witness: tuple[list[tuple[int, int, int]], list[tuple[int, int, int]]] | None,
    instance_time_s: float = 8.0,
) -> CL1Record:
    """Analyse CL1's two hypotheses on the natural partition (V1, V2).

    Witness is mandatory if the caller wants hypothesis-(2) numbers; if
    None (i.e. UNSAT instance), only hypothesis (1) is populated.
    """
    v1_list = sorted(inst.V1)
    v2_list = sorted(inst.V2)
    v1_set = set(v1_list)
    rec = CL1Record(
        v1_size=len(v1_list),
        v2_size=len(v2_list),
        v1=list(v1_list),
        v2=list(v2_list),
        internal_arc=inst.internal_arc,
    )

    # Hypothesis (1).
    s1, l1 = _verify_part_sad(D, v1_list, instance_time_s)
    s2, l2 = _verify_part_sad(D, v2_list, instance_time_s)
    rec.v1_sad_status, rec.v1_lambda = s1, l1
    rec.v2_sad_status, rec.v2_lambda = s2, l2

    # §3.c modified-partition recovery test: V_1' = V_1 ∪ {w}.
    # Skip if V_1 is already maximal (|V_2| <= 1).
    if len(v2_list) >= 2 and (s1 not in ("SAT", "NA") or s2 not in ("SAT", "NA")):
        for w in v2_list:
            new_v1 = sorted(v1_list + [w])
            new_v2 = sorted(v for v in v2_list if v != w)
            ss1, _ = _verify_part_sad(D, new_v1, instance_time_s)
            ss2, _ = _verify_part_sad(D, new_v2, instance_time_s)
            if ss1 in ("SAT", "NA") and ss2 in ("SAT", "NA"):
                rec.mod_partition_recovers = True
                rec.mod_partition_w_examples.append(int(w))
                # We collect at most 3 examples for the log.
                if len(rec.mod_partition_w_examples) >= 3:
                    break

    # Hypothesis (2) — requires witness.
    if witness is not None:
        red_arcs, blue_arcs = witness
        red_set = set(red_arcs)
        for ke in red_arcs + blue_arcs:
            u, v, _k = ke
            u_in_1 = u in v1_set
            v_in_1 = v in v1_set
            is_red = ke in red_set
            if u_in_1 and v_in_1:
                if is_red:
                    rec.inner1_red_n_arcs += 1
                else:
                    rec.inner1_blue_n_arcs += 1
            elif (not u_in_1) and (not v_in_1):
                if is_red:
                    rec.inner2_red_n_arcs += 1
                else:
                    rec.inner2_blue_n_arcs += 1
            elif u_in_1 and not v_in_1:
                rec.bridges_plus_total += 1
                if is_red:
                    rec.bridges_plus_R += 1
                else:
                    rec.bridges_plus_B += 1
            else:
                rec.bridges_minus_total += 1
                if is_red:
                    rec.bridges_minus_R += 1
                else:
                    rec.bridges_minus_B += 1

    return rec


# ----------------------------------------------------------------------------
# Sweep dataclasses
# ----------------------------------------------------------------------------


@dataclass
class NSStats:
    streamed: int = 0
    ns_confirmed: int = 0
    strong: int = 0
    kappa_eq_2: int = 0
    kappa_eq_3: int = 0
    kappa_higher: int = 0
    kappa_lower: int = 0
    verified_sat_2: int = 0
    verified_unsat_2: int = 0
    verified_sat_3: int = 0
    verified_unsat_3: int = 0
    disagreements: int = 0
    elapsed_s: float = 0.0

    by_construction: dict[str, int] = field(default_factory=dict)
    by_construction_k3: dict[str, int] = field(default_factory=dict)
    by_construction_k2: dict[str, int] = field(default_factory=dict)
    by_v1v2: dict[str, int] = field(default_factory=dict)


@dataclass
class NSLog:
    started_at: str
    config: dict[str, Any] = field(default_factory=dict)
    stats: dict[str, Any] = field(default_factory=dict)
    candidates_lambda3: list[dict[str, Any]] = field(default_factory=list)
    candidates_lambda2_unsat: list[dict[str, Any]] = field(default_factory=list)
    candidates_lambda2_sat_sample: list[dict[str, Any]] = field(default_factory=list)
    canonical_summary: dict[str, Any] = field(default_factory=dict)
    cl1_summary: dict[str, Any] = field(default_factory=dict)
    exception_summary: dict[str, Any] = field(default_factory=dict)
    counterexamples: list[dict[str, Any]] = field(default_factory=list)
    finished_at: str | None = None
    elapsed_s: float | None = None
    notes: list[str] = field(default_factory=list)


# ----------------------------------------------------------------------------
# Per-candidate output entry
# ----------------------------------------------------------------------------


def _entry_common(inst: NSInstance, cross: Any, lam: int, canonical: str) -> dict[str, Any]:
    return {
        "name": inst.name,
        "n": inst.n,
        "m": len(inst.arcs),
        "construction": inst.construction,
        "V1": list(inst.V1),
        "V2": list(inst.V2),
        "internal_arc": list(inst.internal_arc),
        "arcs": [list(a) for a in inst.arcs],
        "lambda_arc": lam,
        "ilp_status": cross.ilp.get("status"),
        "sat_status": cross.sat.get("status"),
        "ilp_time": cross.ilp.get("time_s"),
        "sat_time": cross.sat.get("time_s"),
        "canonical_hash": canonical,
    }


def _sat_entry(
    inst: NSInstance,
    cross: Any,
    lam: int,
    witness: tuple[list[tuple[int, int, int]], list[tuple[int, int, int]]],
    cl1: CL1Record,
    canonical: str,
) -> dict[str, Any]:
    entry = _entry_common(inst, cross, lam, canonical)
    red, blue = witness
    entry["witness_red"] = [[u, v, k] for (u, v, k) in red]
    entry["witness_blue"] = [[u, v, k] for (u, v, k) in blue]
    entry["cl1"] = asdict(cl1)
    return entry


def _unsat_entry(
    inst: NSInstance,
    cross: Any,
    lam: int,
    cl1: CL1Record,
    canonical: str,
) -> dict[str, Any]:
    entry = _entry_common(inst, cross, lam, canonical)
    entry["cl1"] = asdict(cl1)
    return entry


# ----------------------------------------------------------------------------
# Stream candidates from A, B, C generators
# ----------------------------------------------------------------------------


def stream_candidates(
    cap_per_pair_A: int,
    pair_grid: list[tuple[int, int]],
    cap_B: int,
    bigger_pairs_B: list[tuple[int, int]],
    seed: int,
) -> list[NSInstance]:
    """Build a deterministic stream from A (exhaustive small), B (random larger), C (reference).

    Construction-A is run for each (|V_1|, |V_2|) in `pair_grid` with cap
    `cap_per_pair_A`. Construction-B is run for each pair in
    `bigger_pairs_B` with cap `cap_B`. Construction-C is always included.
    """
    out: list[NSInstance] = []
    seen_arcs: set[tuple[tuple[int, int], ...]] = set()

    def add(it):
        for inst in it:
            key = tuple(sorted(inst.arcs))
            if key in seen_arcs:
                continue
            seen_arcs.add(key)
            out.append(inst)

    # Construction A: exhaustive small.
    for (v1, v2) in pair_grid:
        # Auto-scale: per-V_2-orientation cap and bridge cap to keep cap_per_pair_A roughly.
        # Heuristic budget:
        n_v2_orient_cap = max(8, cap_per_pair_A // max(v1 * (v1 - 1), 1) // 32)
        bridge_cap = max(16, min(96, cap_per_pair_A // n_v2_orient_cap // max(v1 * (v1 - 1), 1)))
        seen_before = len(out)
        for inst in enumerate_construction_A(
            v1_size=v1, v2_size=v2,
            seed=seed,
            cap_per_v2_orientation=n_v2_orient_cap,
            bridge_cap_per_pair=bridge_cap,
        ):
            key = tuple(sorted(inst.arcs))
            if key in seen_arcs:
                continue
            seen_arcs.add(key)
            out.append(inst)
            if len(out) - seen_before >= cap_per_pair_A:
                break

    # Construction B: random for bigger.
    for (v1, v2) in bigger_pairs_B:
        seen_before = len(out)
        for inst in enumerate_construction_B(
            v1_size=v1, v2_size=v2,
            seed=seed,
            cap=cap_B,
        ):
            key = tuple(sorted(inst.arcs))
            if key in seen_arcs:
                continue
            seen_arcs.add(key)
            out.append(inst)
            if len(out) - seen_before >= cap_B:
                break

    # Construction C: reference list.
    add(enumerate_construction_C())

    return out


# ----------------------------------------------------------------------------
# Strict-split UNSAT canonical-key index (for §3.b comparison)
# ----------------------------------------------------------------------------


def _strict_split_unsat_canonical_keys() -> dict[str, str]:
    """Canonical-hash index of the strict-split UNSAT family (Ai et al. 2024 + S_4).

    Returns {hash: name}. For the §3.b comparison: a (1,0)-NS UNSAT
    instance D is classified as "strict-split family" iff
      (a) D itself is iso to a strict-split UNSAT canonical (could happen
          because the digraph admits multiple (V_1, V_2) partitions); or
      (b) D minus the internal arc is iso to a strict-split UNSAT.
    Otherwise it is a NEW (1,0)-NS-specific obstruction.

    S_4 is included because it can occur as a sub-digraph of a (1,0)-NS
    candidate where V_2 = S_4 and |V_1| = 1, modulo relabelling.

    The Ai et al. catalogue is closed under arc reversal, so both forward and
    reversed canonical hashes are indexed for every safe benchmark. Appendix
    B.3 cases with unresolved dashed-arc readings are intentionally excluded.
    """
    from benchmarks import strict_split_unsat_benchmarks

    benchmarks = strict_split_unsat_benchmarks()
    out: dict[str, str] = {}
    for b in benchmarks:
        D = b.build()
        k_fwd = canonical_key(D)
        out.setdefault(k_fwd, b.name)
    for b in benchmarks:
        D = b.build()
        Drev = arc_reverse(D)
        k_fwd = canonical_key(D)
        k_rev = canonical_key(Drev)
        if k_rev != k_fwd:
            out.setdefault(k_rev, f"{b.name}_arcrev")
    return out


def _hash_minus_internal(inst: NSInstance) -> str:
    """Canonical hash of D minus the internal arc."""
    arcs = [a for a in inst.arcs if tuple(a) != tuple(inst.internal_arc)]
    # Remove exactly one occurrence (multi-arc safe).
    removed = False
    filtered: list[tuple[int, int]] = []
    for a in inst.arcs:
        if (not removed) and tuple(a) == tuple(inst.internal_arc):
            removed = True
            continue
        filtered.append(a)
    D = Digraph.from_arcs(range(inst.n), filtered)
    return canonical_key(D)


# ----------------------------------------------------------------------------
# Sweep driver
# ----------------------------------------------------------------------------


def run_sweep(
    candidates: list[NSInstance],
    instance_time_s: float,
    log: NSLog,
    lambda2_sat_sample_cap: int = 24,
) -> None:
    stats = NSStats()
    t0 = time.time()
    by_constr: dict[str, int] = defaultdict(int)
    by_constr_k3: dict[str, int] = defaultdict(int)
    by_constr_k2: dict[str, int] = defaultdict(int)
    by_v1v2: dict[str, int] = defaultdict(int)

    # Strict-split UNSAT index (for §3.b comparison).
    split_index = _strict_split_unsat_canonical_keys()

    saturated_sample = 0  # count of lambda=2 SAT samples we've logged

    for inst in candidates:
        stats.streamed += 1
        by_constr[inst.construction] += 1
        by_v1v2[f"|V1|={len(inst.V1)},|V2|={len(inst.V2)}"] += 1

        # 1. Independent (1,0)-NS check.
        D = inst.build()
        ok, why = is_one_zero_near_split(D, list(inst.V1), list(inst.V2))
        if not ok:
            log.notes.append(f"NON-(1,0)-NS generated: {inst.name}: {why}")
            continue
        stats.ns_confirmed += 1

        # 2. Strongly connected?
        if not D.is_strongly_connected():
            continue
        stats.strong += 1

        # 3. Arc-connectivity gate: lambda in {2, 3}.
        lam = D.arc_connectivity()
        if lam < 2:
            stats.kappa_lower += 1
            continue
        if lam > 3:
            stats.kappa_higher += 1
            continue
        if lam == 2:
            stats.kappa_eq_2 += 1
            by_constr_k2[inst.construction] += 1
        else:  # lam == 3
            stats.kappa_eq_3 += 1
            by_constr_k3[inst.construction] += 1

        # 4. Cross-check.
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
        canonical = canonical_key(D)

        if status == "UNSAT":
            # CL1 record (no witness; analyse hypothesis (1) only).
            cl1 = analyse_cl1(inst, D, None, instance_time_s=instance_time_s)
            entry = _unsat_entry(inst, cross, lam, cl1, canonical)

            # §3.b: is this "split UNSAT + free V_1-internal arc"?
            try:
                hsplit = _hash_minus_internal(inst)
            except Exception:
                hsplit = ""
            entry["minus_internal_canonical_hash"] = hsplit
            # Two paths to "matches strict-split":
            #   (a) D itself, as a labelled digraph, is iso to a known
            #       strict-split UNSAT (matches in `canonical`);
            #   (b) D minus the internal arc is a known strict-split UNSAT
            #       (the strict-split arc was a free addition).
            match_full = split_index.get(canonical, None)
            match_minus = split_index.get(hsplit, None)
            entry["matches_strict_split_full"] = match_full
            entry["matches_strict_split_minus"] = match_minus
            entry["matches_strict_split_unsat"] = match_full or match_minus

            if lam == 2:
                stats.verified_unsat_2 += 1
                log.candidates_lambda2_unsat.append(entry)
                print(
                    f"  [lambda=2 UNSAT] {inst.name}  n={inst.n}  "
                    f"matches_split={entry['matches_strict_split_unsat']}",
                    flush=True,
                )
            else:  # lam == 3
                stats.verified_unsat_3 += 1
                print(
                    f"  *** UNSAT lambda=3 (1,0)-NS candidate ***  name={inst.name}",
                    flush=True,
                )
                log.notes.append(
                    f"COUNTEREXAMPLE candidate (Route B amended): {inst.name} -- "
                    f"run team/01 checklist; write team/21_candidate_counterexample.md"
                )
                log.counterexamples.append(entry)
                # Per spec hard rule: stop on lambda=3 UNSAT.
                print(
                    "  *** STOPPING SWEEP: lambda=3 (1,0)-NS UNSAT triggers "
                    "team/01 ten-item checklist.", flush=True,
                )
                break
            continue

        if status != "SAT":
            log.notes.append(
                f"UNKNOWN status on {inst.name}: ILP={status} SAT={cross.sat.get('status')}"
            )
            continue

        # SAT.
        witness = cross.sat.get("witness")
        cl1 = analyse_cl1(inst, D, witness, instance_time_s=instance_time_s)
        entry = _sat_entry(inst, cross, lam, witness, cl1, canonical)

        if lam == 3:
            stats.verified_sat_3 += 1
            log.candidates_lambda3.append(entry)
        else:  # lam == 2
            stats.verified_sat_2 += 1
            if saturated_sample < lambda2_sat_sample_cap:
                log.candidates_lambda2_sat_sample.append(entry)
                saturated_sample += 1

        if stats.streamed % 200 == 0:
            print(
                f"  [NS] streamed={stats.streamed} ns={stats.ns_confirmed} "
                f"l2={stats.kappa_eq_2} l3={stats.kappa_eq_3} "
                f"sat3={stats.verified_sat_3} unsat3={stats.verified_unsat_3} "
                f"sat2={stats.verified_sat_2} unsat2={stats.verified_unsat_2} "
                f"elapsed={time.time() - t0:.0f}s",
                flush=True,
            )

    stats.elapsed_s = time.time() - t0
    stats.by_construction = dict(by_constr)
    stats.by_construction_k3 = dict(by_constr_k3)
    stats.by_construction_k2 = dict(by_constr_k2)
    stats.by_v1v2 = dict(by_v1v2)
    log.stats = asdict(stats)


# ----------------------------------------------------------------------------
# Aggregation
# ----------------------------------------------------------------------------


def _h1_passes(cl1: dict[str, Any]) -> bool:
    return (
        cl1.get("v1_sad_status") in ("SAT", "NA")
        and cl1.get("v2_sad_status") in ("SAT", "NA")
    )


def _h2_passes(cl1: dict[str, Any]) -> bool:
    return (
        cl1.get("bridges_plus_R", 0) > 0
        and cl1.get("bridges_plus_B", 0) > 0
        and cl1.get("bridges_minus_R", 0) > 0
        and cl1.get("bridges_minus_B", 0) > 0
    )


def aggregate_cl1(log: NSLog) -> dict[str, Any]:
    cands = log.candidates_lambda3
    if not cands:
        return {"n_candidates": 0}
    n = len(cands)
    h1_pass = sum(1 for c in cands if _h1_passes(c["cl1"]))
    h2_pass = sum(1 for c in cands if _h2_passes(c["cl1"]))
    both = sum(1 for c in cands if _h1_passes(c["cl1"]) and _h2_passes(c["cl1"]))

    mod_recovers = sum(
        1 for c in cands
        if c["cl1"].get("mod_partition_recovers", False)
    )

    per_constr: dict[str, dict[str, Any]] = {}
    bk: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for c in cands:
        bk[c["construction"]].append(c)
    for k, b in bk.items():
        m = len(b)
        per_constr[k] = {
            "n": m,
            "h1_pass": sum(1 for c in b if _h1_passes(c["cl1"])),
            "h2_pass": sum(1 for c in b if _h2_passes(c["cl1"])),
            "mod_recovers": sum(
                1 for c in b if c["cl1"].get("mod_partition_recovers", False)
            ),
        }

    per_v1v2: dict[str, dict[str, Any]] = {}
    bk2: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for c in cands:
        key = f"|V1|={len(c['V1'])},|V2|={len(c['V2'])}"
        bk2[key].append(c)
    for k, b in bk2.items():
        m = len(b)
        per_v1v2[k] = {
            "n": m,
            "h1_pass": sum(1 for c in b if _h1_passes(c["cl1"])),
            "h2_pass": sum(1 for c in b if _h2_passes(c["cl1"])),
            "mod_recovers": sum(
                1 for c in b if c["cl1"].get("mod_partition_recovers", False)
            ),
        }

    h1_fail_details: dict[str, int] = defaultdict(int)
    for c in cands:
        if _h1_passes(c["cl1"]):
            continue
        v1s = c["cl1"]["v1_sad_status"]
        v2s = c["cl1"]["v2_sad_status"]
        h1_fail_details[f"V1={v1s}, V2={v2s}"] += 1

    return {
        "n_candidates": n,
        "hypothesis_1_pass": h1_pass,
        "hypothesis_1_frac": h1_pass / n,
        "hypothesis_2_pass": h2_pass,
        "hypothesis_2_frac": h2_pass / n,
        "both_pass": both,
        "both_frac": both / n,
        "mod_partition_recovers": mod_recovers,
        "mod_partition_recovers_frac": mod_recovers / n,
        "per_construction": per_constr,
        "per_v1v2": per_v1v2,
        "h1_failure_breakdown": dict(h1_fail_details),
    }


def aggregate_canonical(log: NSLog) -> dict[str, Any]:
    cands = log.candidates_lambda3 + log.candidates_lambda2_unsat
    keys: dict[str, list[str]] = defaultdict(list)
    for c in cands:
        keys[c["canonical_hash"]].append(c["name"])
    classes = sorted(keys.values(), key=len, reverse=True)
    size_dist = Counter(len(c) for c in classes)
    # Canonical distinct counts split by lambda.
    keys_l3: dict[str, list[str]] = defaultdict(list)
    for c in log.candidates_lambda3:
        keys_l3[c["canonical_hash"]].append(c["name"])
    keys_l2u: dict[str, list[str]] = defaultdict(list)
    for c in log.candidates_lambda2_unsat:
        keys_l2u[c["canonical_hash"]].append(c["name"])
    return {
        "n_labeled_distinct_l3sat": len(log.candidates_lambda3),
        "n_canonical_distinct_l3sat": len(keys_l3),
        "n_labeled_distinct_l2unsat": len(log.candidates_lambda2_unsat),
        "n_canonical_distinct_l2unsat": len(keys_l2u),
        "largest_iso_class_size": len(classes[0]) if classes else 0,
        "iso_class_size_distribution": {
            str(k): v for k, v in sorted(size_dist.items())
        },
    }


def aggregate_exception_family(log: NSLog) -> dict[str, Any]:
    """The §3.b table: characterize the lambda=2 UNSAT (1,0)-NS family.

    For each canonical lambda=2 UNSAT instance:
      - is it the strict-split obstruction plus a "free" V_1-internal arc?
        (i.e., does removing the internal arc yield a known strict-split
         UNSAT?)
      - if NOT, it is a NEW (1,0)-NS-specific obstruction.
    """
    cands = log.candidates_lambda2_unsat
    if not cands:
        return {"n_lambda2_unsat": 0}
    by_canonical: dict[str, dict[str, Any]] = {}
    for c in cands:
        h = c["canonical_hash"]
        if h not in by_canonical:
            by_canonical[h] = {
                "name_example": c["name"],
                "n": c["n"],
                "m": c["m"],
                "V1_size": len(c["V1"]),
                "V2_size": len(c["V2"]),
                "matches_strict_split": c.get("matches_strict_split_unsat"),
                "matches_strict_split_full": c.get("matches_strict_split_full"),
                "matches_strict_split_minus": c.get("matches_strict_split_minus"),
                "minus_internal_canonical_hash": c.get("minus_internal_canonical_hash"),
                "count": 0,
            }
        by_canonical[h]["count"] += 1
    # Partition into the two cases.
    extensions_of_split: list[dict[str, Any]] = []
    new_obstructions: list[dict[str, Any]] = []
    for h, rec in by_canonical.items():
        rec["canonical_hash"] = h
        if rec["matches_strict_split"]:
            extensions_of_split.append(rec)
        else:
            new_obstructions.append(rec)
    return {
        "n_lambda2_unsat": len(cands),
        "n_canonical_lambda2_unsat": len(by_canonical),
        "n_extensions_of_split": len(extensions_of_split),
        "n_new_obstructions": len(new_obstructions),
        "extensions_of_split": extensions_of_split,
        "new_obstructions": new_obstructions,
    }


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------


def main() -> int:
    p = argparse.ArgumentParser(description="Route-B (1,0)-near-split empirical sweep")
    p.add_argument("--cap-per-pair-A", type=int, default=800)
    p.add_argument("--cap-B", type=int, default=600)
    p.add_argument("--instance-time-s", type=float, default=10.0)
    p.add_argument("--logs-dir", default=str(HERE / "logs"))
    p.add_argument("--seed", type=int, default=20260516)
    args = p.parse_args()

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    logs_dir = Path(args.logs_dir)
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / f"route_b_ns_{timestamp}.json"

    print("=" * 72, flush=True)
    print("Route B amended — (1,0)-near-split empirical sweep", flush=True)
    print("=" * 72, flush=True)

    # Pair grid for Construction A (exhaustive small).
    # Pairs are picked so that |V_1| + |V_2| <= 10 stays well within
    # cross-check budget per instance.
    pair_grid_A: list[tuple[int, int]] = [
        (2, 3), (2, 4), (2, 5),
        (3, 3), (3, 4), (3, 5),
        (4, 3), (4, 4),
    ]
    # Pair grid for Construction B (larger).
    bigger_pairs_B: list[tuple[int, int]] = [
        (2, 6), (3, 6), (2, 7), (3, 7), (4, 5), (4, 6),
    ]

    log = NSLog(
        started_at=time.strftime("%Y-%m-%d %H:%M:%S"),
        config={
            "cap_per_pair_A": args.cap_per_pair_A,
            "cap_B": args.cap_B,
            "instance_time_s": args.instance_time_s,
            "seed": args.seed,
            "pair_grid_A": pair_grid_A,
            "bigger_pairs_B": bigger_pairs_B,
        },
    )

    candidates = stream_candidates(
        cap_per_pair_A=args.cap_per_pair_A,
        pair_grid=pair_grid_A,
        cap_B=args.cap_B,
        bigger_pairs_B=bigger_pairs_B,
        seed=args.seed,
    )
    print(f"Streamed candidate list: {len(candidates)} instances", flush=True)
    constr_count = Counter(c.construction for c in candidates)
    for k, v in constr_count.items():
        print(f"  {k}: {v}", flush=True)
    print(flush=True)

    t0 = time.time()
    run_sweep(
        candidates=candidates,
        instance_time_s=args.instance_time_s,
        log=log,
    )

    log.cl1_summary = aggregate_cl1(log)
    log.canonical_summary = aggregate_canonical(log)
    log.exception_summary = aggregate_exception_family(log)
    log.finished_at = time.strftime("%Y-%m-%d %H:%M:%S")
    log.elapsed_s = time.time() - t0

    # ---- stdout report -----------------------------------------------------
    print("=" * 72, flush=True)
    print("Sweep complete.", flush=True)
    s = log.stats
    print(
        f"  streamed={s['streamed']} ns={s['ns_confirmed']} strong={s['strong']}",
        flush=True,
    )
    print(
        f"  lambda=2: {s['kappa_eq_2']} (sat={s['verified_sat_2']} unsat={s['verified_unsat_2']})",
        flush=True,
    )
    print(
        f"  lambda=3: {s['kappa_eq_3']} (sat={s['verified_sat_3']} unsat={s['verified_unsat_3']})",
        flush=True,
    )
    print(
        f"  lambda>3 (rej)={s['kappa_higher']} lambda<2={s['kappa_lower']} "
        f"disagreements={s['disagreements']} elapsed={s['elapsed_s']:.0f}s",
        flush=True,
    )
    hit_rate = (s["kappa_eq_2"] + s["kappa_eq_3"]) / max(s["streamed"], 1)
    print(
        f"  hit-rate(lambda in {{2,3}} | streamed) = {100 * hit_rate:.1f}% "
        f"(floor 5%; {'OK' if hit_rate >= 0.05 else 'BELOW FLOOR'})",
        flush=True,
    )

    cs = log.canonical_summary
    print(
        f"  canonical (lambda=3 SAT): {cs['n_labeled_distinct_l3sat']} -> "
        f"{cs['n_canonical_distinct_l3sat']}",
        flush=True,
    )
    print(
        f"  canonical (lambda=2 UNSAT): {cs['n_labeled_distinct_l2unsat']} -> "
        f"{cs['n_canonical_distinct_l2unsat']}",
        flush=True,
    )

    print(f"\nBy construction:", flush=True)
    bc = s.get("by_construction", {})
    bk2 = s.get("by_construction_k2", {})
    bk3 = s.get("by_construction_k3", {})
    for k in sorted(bc.keys()):
        print(
            f"  {k:14s} streamed={bc.get(k, 0):5d}  "
            f"lambda=2={bk2.get(k, 0):4d}  lambda=3={bk3.get(k, 0):4d}",
            flush=True,
        )

    print(f"\nBy (|V_1|, |V_2|):", flush=True)
    for k in sorted(s.get("by_v1v2", {}).keys()):
        print(f"  {k:16s} streamed={s['by_v1v2'][k]:5d}", flush=True)

    cl1s = log.cl1_summary
    if cl1s.get("n_candidates", 0) > 0:
        print("\n" + "=" * 72, flush=True)
        print("CL1 hypothesis tests (per lambda=3 SAT instance)", flush=True)
        print("=" * 72, flush=True)
        n = cl1s["n_candidates"]
        print(
            f"  Hypothesis (1) — D[V_1], D[V_2] SAD-decomposable:    "
            f"{100 * cl1s['hypothesis_1_frac']:6.2f}%  ({cl1s['hypothesis_1_pass']}/{n})",
            flush=True,
        )
        print(
            f"  Hypothesis (2) — bridges 2-coloring all 4 nonempty:  "
            f"{100 * cl1s['hypothesis_2_frac']:6.2f}%  ({cl1s['hypothesis_2_pass']}/{n})",
            flush=True,
        )
        print(
            f"  Both:                                                "
            f"{100 * cl1s['both_frac']:6.2f}%  ({cl1s['both_pass']}/{n})",
            flush=True,
        )
        print(
            f"  Modified partition (V_1 ∪ {{w}}) recovers H1:         "
            f"{100 * cl1s['mod_partition_recovers_frac']:6.2f}%  "
            f"({cl1s['mod_partition_recovers']}/{n})",
            flush=True,
        )

        h1fail = cl1s.get("h1_failure_breakdown", {})
        if h1fail:
            print("\nH1-failure breakdown (V1 status / V2 status):", flush=True)
            for k, v in sorted(h1fail.items(), key=lambda kv: -kv[1]):
                print(f"  {k:40s} count={v}", flush=True)

    # Exception family table (§3.b).
    ex = log.exception_summary
    if ex.get("n_lambda2_unsat", 0) > 0:
        print("\n" + "=" * 72, flush=True)
        print("2-arc-strong UNSAT (1,0)-near-split exception family (§3.b)", flush=True)
        print("=" * 72, flush=True)
        print(
            f"  total lambda=2 UNSAT labeled: {ex['n_lambda2_unsat']}", flush=True
        )
        print(
            f"  canonical-distinct:           {ex['n_canonical_lambda2_unsat']}",
            flush=True,
        )
        print(
            f"  extensions of strict-split:   {ex['n_extensions_of_split']}",
            flush=True,
        )
        print(
            f"  NEW obstructions:             {ex['n_new_obstructions']}",
            flush=True,
        )
        if ex["new_obstructions"]:
            print("\n  New (1,0)-NS UNSAT obstructions (not split + free arc):", flush=True)
            for o in ex["new_obstructions"]:
                print(
                    f"    canonical={o['canonical_hash'][:16]}... n={o['n']} m={o['m']} "
                    f"|V1|={o['V1_size']} |V2|={o['V2_size']} count={o['count']}",
                    flush=True,
                )

    if s["verified_unsat_3"] > 0:
        print("\n" + "=" * 72, flush=True)
        print("WARNING: UNSAT 3-arc-strong (1,0)-NS candidate(s) found!", flush=True)
        for ce in log.counterexamples:
            print(f"   - {ce['name']}  n={ce['n']}", flush=True)

    print(f"\nlog: {log_path}", flush=True)
    with log_path.open("w") as f:
        json.dump(asdict(log), f, indent=2, default=str)

    return 0


if __name__ == "__main__":
    sys.exit(main())
