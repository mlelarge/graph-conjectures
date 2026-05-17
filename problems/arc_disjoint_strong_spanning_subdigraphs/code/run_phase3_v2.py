"""Phase 3 v2 driver.

Runs three vehicles in priority order:

  P1. Vehicle 3, deficit-aware  (`generators.glue_deficit`).
       Hit-rate target: >= 50 % (we observe ~99 %; see report).
       Per-pair verified cap: configurable.

  P2. Eulerian / 6-edge-connected families  (`generators.eulerian`).
       Three families: K_{6,6} balanced orientations; perturbed circulants;
       perturbed bidirected 3-edge-connected graphs.

  P3. Constraints-first laminar v2  (`generators.laminar_v2`).
       Hand-designed S1, S2, S3a, S3c + random sparse Eulerian samples.

Each verified 3-arc-strong candidate is cross-checked under ILP+SAT.
UNSAT candidates immediately trigger the full checklist.

Output: code/logs/phase3v2_<timestamp>.json + stdout transcript.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterator

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from benchmarks import all_benchmarks, Benchmark  # noqa: E402
from cross_check import cross_check  # noqa: E402
from digraph import Digraph  # noqa: E402
from generators.checklist import (  # noqa: E402
    checklist_to_dict,
    run_checklist,
)
from generators.glue_deficit import (  # noqa: E402
    DeficitGenConfig,
    DeficitGluedInstance,
    generate_deficit_gluings,
    passes_arc_strong_3 as glue_passes_3,
    vertex_degree_feasible,
)
from generators.eulerian import (  # noqa: E402
    EulerianInstance,
    gen_K66_balanced,
    gen_circulants,
    gen_perturbed_bidirected,
    is_lambda_exactly_3,
    quick_degree_gate as eul_deg_gate,
)
from generators.laminar_v2 import (  # noqa: E402
    LaminarV2Instance,
    gen_laminar_v2,
    passes_arc_strong_3 as lam_passes_3,
    quick_degree_gate as lam_deg_gate,
)


UNSAT_NAMES = {
    "S4", "C6_square", "C8_square",
    "C3_K2K2K2", "C3_K2K2P2", "C3_K2K2K3",
    "AiEtAl_L211_min", "AiEtAl_L312_min", "AiEtAl_iv_star_iv",
}

# Templates flagged as "unproductive" in v1 - need 100 verified per the spec
UNPRODUCTIVE_NAMES = {
    "C6_square", "C8_square",
    "C3_K2K2K2", "C3_K2K2K3",
    "AiEtAl_L312_min",
}


# ----------------------------------------------------------------------------
# Log structures
# ----------------------------------------------------------------------------


@dataclass
class VehicleStats:
    streamed: int = 0
    deg_gate_pass: int = 0
    kappa3_pass: int = 0
    verified_unsat: int = 0
    verified_sat: int = 0
    disagreements: int = 0
    elapsed_s: float = 0.0
    notes: list[str] = field(default_factory=list)

    @property
    def hit_rate_kappa3(self) -> float:
        return self.kappa3_pass / max(self.streamed, 1)


@dataclass
class Phase3V2Log:
    started_at: str
    config: dict[str, Any] = field(default_factory=dict)
    seed: int = 20260516
    templates: list[str] = field(default_factory=list)

    vehicle3_stats: VehicleStats = field(default_factory=VehicleStats)
    vehicle2_K66_stats: VehicleStats = field(default_factory=VehicleStats)
    vehicle2_circ_stats: VehicleStats = field(default_factory=VehicleStats)
    vehicle2_pertB_stats: VehicleStats = field(default_factory=VehicleStats)
    vehicle1v2_stats: VehicleStats = field(default_factory=VehicleStats)

    # Per-template coverage (Vehicle 3 only)
    per_template_appearances: dict[str, int] = field(default_factory=dict)

    # Counts of verified-3-arc-strong by template pair (Vehicle 3)
    pair_counts: dict[str, int] = field(default_factory=dict)

    # Selected entries — verified candidates kept fully, rejected sampled.
    sample_entries: list[dict[str, Any]] = field(default_factory=list)
    candidate_entries: list[dict[str, Any]] = field(default_factory=list)
    publishable_candidates: list[dict[str, Any]] = field(default_factory=list)

    finished_at: str | None = None
    elapsed_s: float | None = None
    notes: list[str] = field(default_factory=list)


# ----------------------------------------------------------------------------
# Common per-candidate logic
# ----------------------------------------------------------------------------


def _verify_and_log(
    inst_name: str,
    arcs: tuple[tuple[int, int], ...],
    n: int,
    metadata: dict[str, Any],
    templates: list[Benchmark],
    log: Phase3V2Log,
    stats: VehicleStats,
    seed: int,
    time_limit_s: float = 12.0,
    keep_in_sample: bool = False,
) -> str | None:
    """Run cross_check; on UNSAT run checklist. Return the cross-check
    status string ('SAT'/'UNSAT'/'DISAGREE'/'UNKNOWN') or None on
    rejection at degree/kappa gate (the caller should have already
    filtered though)."""
    D = Digraph.from_arcs(range(n), list(arcs))
    cc = cross_check(D, inst_name, time_limit_s=time_limit_s)
    entry: dict[str, Any] = {
        "name": inst_name,
        "n": n,
        "m": len(arcs),
        **metadata,
        "cross_check": {
            "ilp": cc.ilp.get("status"),
            "sat": cc.sat.get("status"),
            "agree": cc.agree,
            "t_ilp": cc.ilp.get("time_s"),
            "t_sat": cc.sat.get("time_s"),
        },
    }
    if not cc.agree:
        stats.disagreements += 1
        log.notes.append(f"FATAL: cross-check disagree on {inst_name}: ILP={cc.ilp.get('status')} SAT={cc.sat.get('status')}")
        print(f"  *** FATAL DISAGREE: {inst_name}", flush=True)
        log.sample_entries.append(entry)
        return "DISAGREE"

    s_ilp = cc.ilp.get("status")
    if s_ilp == "UNSAT":
        stats.verified_unsat += 1
        print(f"  *** UNSAT 3-arc-strong candidate ***  name={inst_name}  n={n}  m={len(arcs)}", flush=True)
        # Run the full Lead Theorist checklist on this candidate.
        try:
            chk = run_checklist(
                instance_name=inst_name,
                arcs=list(arcs),
                n=n,
                templates=templates,
                seed=seed,
                cross_check_result=cc,
                do_minimization=True,
                time_limit_s=time_limit_s,
            )
            entry["checklist"] = checklist_to_dict(chk)
            entry["is_candidate"] = chk.overall_publishable_as_candidate
            if chk.overall_publishable_as_candidate:
                log.publishable_candidates.append(entry)
                print(f"  *** PUBLISHABLE: passed checklist core ***", flush=True)
        except Exception as e:
            entry["checklist_error"] = str(e)
            log.notes.append(f"checklist error on {inst_name}: {e}")
        log.candidate_entries.append(entry)
        return "UNSAT"
    elif s_ilp == "SAT":
        stats.verified_sat += 1
        if keep_in_sample:
            log.sample_entries.append(entry)
        return "SAT"
    else:
        stats.notes.append(f"UNKNOWN status on {inst_name}: ILP={s_ilp} SAT={cc.sat.get('status')}")
        return "UNKNOWN"


# ----------------------------------------------------------------------------
# Vehicle 3 — deficit-aware
# ----------------------------------------------------------------------------


def run_vehicle3_deficit(
    templates: list[Benchmark],
    log: Phase3V2Log,
    budget_s: float,
    seed: int,
    per_pair_cap: int = 200,
    sample_every: int = 200,
    instance_time_s: float = 12.0,
) -> None:
    """Run the deficit-aware Vehicle 3 sweep, respecting a per-pair cap."""
    print("=" * 72, flush=True)
    print(f"[P1: Vehicle 3 deficit-aware] starting (budget={budget_s:.0f}s)", flush=True)

    cfg = DeficitGenConfig(
        interface_sizes=(3, 4, 5),
        max_interfaces_per_pair_per_size=30,
        max_bridges_per_interface=24,
        max_extra_slack_per_direction=1,
        allow_self_glue=True,
        ordered_pairs=False,
        verified_per_pair_cap=per_pair_cap,
        seed=seed,
    )
    log.config["vehicle3"] = asdict(cfg)
    stats = log.vehicle3_stats
    t0 = time.time()

    # Per-pair verified count: track separately so we can cap and skip pairs.
    pair_verified: dict[tuple[str, str], int] = {}

    # We need access to the pair via inst.template1/template2, so just keep
    # checking the cap as we go.

    rng = random.Random(seed)
    last_progress_print = 0
    for idx, inst in enumerate(generate_deficit_gluings(templates, cfg)):
        elapsed = time.time() - t0
        if elapsed > budget_s:
            stats.notes.append(f"budget exhausted at idx={idx}")
            print(f"[P1] BUDGET EXHAUSTED at idx={idx}", flush=True)
            break
        stats.streamed += 1
        pair_key = tuple(sorted([inst.template1, inst.template2]))
        if pair_verified.get(pair_key, 0) >= per_pair_cap:
            continue

        if not vertex_degree_feasible(list(inst.arcs), inst.n):
            continue
        stats.deg_gate_pass += 1

        D = inst.build()
        if not glue_passes_3(D, exact=True):
            continue
        stats.kappa3_pass += 1
        pair_verified[pair_key] = pair_verified.get(pair_key, 0) + 1
        pkey = f"{pair_key[0]}+{pair_key[1]}"
        log.pair_counts[pkey] = log.pair_counts.get(pkey, 0) + 1
        for t in {inst.template1, inst.template2}:
            log.per_template_appearances[t] = log.per_template_appearances.get(t, 0) + 1

        keep_sample = (stats.kappa3_pass % sample_every == 0)
        metadata = {
            "vehicle": "3_deficit",
            "template1": inst.template1,
            "template2": inst.template2,
            "S1": list(inst.S1),
            "S2": list(inst.S2),
            "phi": [list(p) for p in inst.phi],
            "bridges_12": [list(a) for a in inst.bridges_12],
            "bridges_21": [list(a) for a in inst.bridges_21],
            "deficit_summary": list(inst.deficit_summary),
            "arcs": [list(a) for a in inst.arcs],
        }
        _verify_and_log(
            inst.name, inst.arcs, inst.n, metadata,
            templates, log, stats, seed,
            time_limit_s=instance_time_s,
            keep_in_sample=keep_sample,
        )

        if stats.streamed - last_progress_print >= 500:
            last_progress_print = stats.streamed
            print(
                f"[P1]   streamed={stats.streamed} deg_ok={stats.deg_gate_pass} "
                f"k3={stats.kappa3_pass} verified_unsat={stats.verified_unsat} "
                f"verified_sat={stats.verified_sat} elapsed={time.time()-t0:.0f}s "
                f"pair_caps_hit={sum(1 for v in pair_verified.values() if v >= per_pair_cap)}",
                flush=True,
            )

    stats.elapsed_s = time.time() - t0
    print(
        f"[P1] done. streamed={stats.streamed} deg_ok={stats.deg_gate_pass} "
        f"k3={stats.kappa3_pass} unsat={stats.verified_unsat} sat={stats.verified_sat} "
        f"disagree={stats.disagreements} elapsed={stats.elapsed_s:.0f}s",
        flush=True,
    )

    # Per-template floor check
    print("[P1] per-template appearances (each instance contributes to 1 or 2):", flush=True)
    for t in sorted(log.per_template_appearances):
        print(f"     {t:24s} : {log.per_template_appearances[t]}", flush=True)
    floor = 100
    for tname in UNPRODUCTIVE_NAMES:
        c = log.per_template_appearances.get(tname, 0)
        if c < floor:
            stats.notes.append(f"BELOW FLOOR: {tname} only {c} verified < {floor}")


# ----------------------------------------------------------------------------
# Vehicle 2 — Eulerian (3 families)
# ----------------------------------------------------------------------------


def run_vehicle2(
    templates: list[Benchmark],
    log: Phase3V2Log,
    budget_s: float,
    seed: int,
    instance_time_s: float = 12.0,
) -> None:
    """Run the three Eulerian families with simple per-family budgets."""
    print("=" * 72, flush=True)
    print(f"[P2: Vehicle 2 Eulerian] starting (budget={budget_s:.0f}s)", flush=True)
    t0 = time.time()
    rng = random.Random(seed)

    # ---- Family A: K_{6,6} balanced orientations ----
    print("[P2.A] K_{6,6} balanced orientations", flush=True)
    stats_A = log.vehicle2_K66_stats
    tA0 = time.time()
    A_budget = budget_s * 0.3
    n_samples = 800
    for k_idx, inst in enumerate(gen_K66_balanced(rng, n_samples)):
        if time.time() - tA0 > A_budget:
            stats_A.notes.append(f"budget exhausted at k={k_idx}")
            break
        stats_A.streamed += 1
        if not eul_deg_gate(list(inst.arcs), inst.n):
            continue
        stats_A.deg_gate_pass += 1
        D = inst.build()
        if not is_lambda_exactly_3(D):
            continue
        stats_A.kappa3_pass += 1
        metadata = {
            "vehicle": "2A_K66",
            "family": inst.family,
            "arcs": [list(a) for a in inst.arcs],
        }
        _verify_and_log(
            inst.name, inst.arcs, inst.n, metadata,
            templates, log, stats_A, seed,
            time_limit_s=instance_time_s,
            keep_in_sample=(stats_A.kappa3_pass % 50 == 0),
        )
    stats_A.elapsed_s = time.time() - tA0
    print(f"[P2.A] streamed={stats_A.streamed} k3={stats_A.kappa3_pass} unsat={stats_A.verified_unsat} sat={stats_A.verified_sat} t={stats_A.elapsed_s:.0f}s", flush=True)

    # ---- Family B: perturbed circulants ----
    print("[P2.B] perturbed circulants", flush=True)
    stats_B = log.vehicle2_circ_stats
    tB0 = time.time()
    B_budget = budget_s * 0.3
    # We pre-compute (n, drop) pairs that give good hit rates per the
    # smoke-test sweep.
    for n_val, drop in [(10, 10), (12, 12), (14, 14), (10, 15), (12, 18), (14, 21)]:
        if time.time() - tB0 > B_budget:
            break
        for inst in gen_circulants([n_val], rng, 50, drop_arcs_per_sample=drop):
            if time.time() - tB0 > B_budget:
                break
            stats_B.streamed += 1
            if not eul_deg_gate(list(inst.arcs), inst.n):
                continue
            stats_B.deg_gate_pass += 1
            D = inst.build()
            if not is_lambda_exactly_3(D):
                continue
            stats_B.kappa3_pass += 1
            metadata = {
                "vehicle": "2B_circ",
                "family": inst.family,
                "params": list(inst.params) if isinstance(inst.params, tuple) else inst.params,
                "arcs": [list(a) for a in inst.arcs],
            }
            _verify_and_log(
                inst.name, inst.arcs, inst.n, metadata,
                templates, log, stats_B, seed,
                time_limit_s=instance_time_s,
                keep_in_sample=(stats_B.kappa3_pass % 30 == 0),
            )
    stats_B.elapsed_s = time.time() - tB0
    print(f"[P2.B] streamed={stats_B.streamed} k3={stats_B.kappa3_pass} unsat={stats_B.verified_unsat} sat={stats_B.verified_sat} t={stats_B.elapsed_s:.0f}s", flush=True)

    # ---- Family C: perturbed bidirected ----
    print("[P2.C] perturbed bidirected 3-edge-connected", flush=True)
    stats_C = log.vehicle2_pertB_stats
    tC0 = time.time()
    C_budget = budget_s * 0.4
    for inst in gen_perturbed_bidirected([8, 10, 12], rng, 300):
        if time.time() - tC0 > C_budget:
            break
        stats_C.streamed += 1
        if not eul_deg_gate(list(inst.arcs), inst.n):
            continue
        stats_C.deg_gate_pass += 1
        D = inst.build()
        if not is_lambda_exactly_3(D):
            continue
        stats_C.kappa3_pass += 1
        metadata = {
            "vehicle": "2C_pertB",
            "family": inst.family,
            "arcs": [list(a) for a in inst.arcs],
        }
        _verify_and_log(
            inst.name, inst.arcs, inst.n, metadata,
            templates, log, stats_C, seed,
            time_limit_s=instance_time_s,
            keep_in_sample=(stats_C.kappa3_pass % 30 == 0),
        )
    stats_C.elapsed_s = time.time() - tC0
    print(f"[P2.C] streamed={stats_C.streamed} k3={stats_C.kappa3_pass} unsat={stats_C.verified_unsat} sat={stats_C.verified_sat} t={stats_C.elapsed_s:.0f}s", flush=True)


# ----------------------------------------------------------------------------
# Vehicle 1 v2 — constraints-first laminar
# ----------------------------------------------------------------------------


def run_vehicle1_v2(
    templates: list[Benchmark],
    log: Phase3V2Log,
    budget_s: float,
    seed: int,
    instance_time_s: float = 12.0,
) -> None:
    print("=" * 72, flush=True)
    print(f"[P3: Vehicle 1 v2 constraints-first laminar] starting (budget={budget_s:.0f}s)", flush=True)
    stats = log.vehicle1v2_stats
    t0 = time.time()
    rng = random.Random(seed)
    n_random = 400

    for inst in gen_laminar_v2(rng, n_random_samples=n_random):
        if time.time() - t0 > budget_s:
            stats.notes.append("budget exhausted")
            print("[P3] BUDGET EXHAUSTED", flush=True)
            break
        stats.streamed += 1
        if not lam_deg_gate(list(inst.arcs), inst.n):
            continue
        stats.deg_gate_pass += 1
        D = inst.build()
        if not lam_passes_3(D, exact=True):
            continue
        stats.kappa3_pass += 1
        metadata = {
            "vehicle": "1v2_laminar",
            "shape": inst.shape,
            "shells": [list(s) for s in inst.shells],
            "arcs": [list(a) for a in inst.arcs],
        }
        _verify_and_log(
            inst.name, inst.arcs, inst.n, metadata,
            templates, log, stats, seed,
            time_limit_s=instance_time_s,
            keep_in_sample=(stats.kappa3_pass % 30 == 0),
        )

    stats.elapsed_s = time.time() - t0
    print(f"[P3] streamed={stats.streamed} k3={stats.kappa3_pass} unsat={stats.verified_unsat} sat={stats.verified_sat} t={stats.elapsed_s:.0f}s", flush=True)


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------


def main() -> int:
    p = argparse.ArgumentParser(description="Phase 3 v2 driver")
    p.add_argument("--budget-total-s", type=float, default=3600.0)
    p.add_argument("--p1-budget-s", type=float, default=1500.0)
    p.add_argument("--p2-budget-s", type=float, default=900.0)
    p.add_argument("--p3-budget-s", type=float, default=600.0)
    p.add_argument("--per-pair-cap", type=int, default=200)
    p.add_argument("--seed", type=int, default=20260516)
    p.add_argument("--logs-dir", default=str(HERE / "logs"))
    p.add_argument("--instance-time-s", type=float, default=12.0)
    p.add_argument("--skip-p3", action="store_true", default=False, help="Skip Vehicle 1 v2 (Priority 3) entirely")
    args = p.parse_args()

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    logs_dir = Path(args.logs_dir)
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / f"phase3v2_{timestamp}.json"

    templates = [b for b in all_benchmarks() if b.name in UNSAT_NAMES]

    log = Phase3V2Log(
        started_at=time.strftime("%Y-%m-%d %H:%M:%S"),
        config={
            "budget_total_s": args.budget_total_s,
            "p1_budget_s": args.p1_budget_s,
            "p2_budget_s": args.p2_budget_s,
            "p3_budget_s": args.p3_budget_s,
            "per_pair_cap": args.per_pair_cap,
            "instance_time_s": args.instance_time_s,
        },
        seed=args.seed,
        templates=[t.name for t in templates],
    )

    t_overall = time.time()

    # P1
    run_vehicle3_deficit(
        templates=templates,
        log=log,
        budget_s=min(args.p1_budget_s, args.budget_total_s),
        seed=args.seed,
        per_pair_cap=args.per_pair_cap,
        instance_time_s=args.instance_time_s,
    )

    # P2
    remaining = args.budget_total_s - (time.time() - t_overall)
    if remaining > 30:
        run_vehicle2(
            templates=templates,
            log=log,
            budget_s=min(args.p2_budget_s, remaining),
            seed=args.seed + 1,
            instance_time_s=args.instance_time_s,
        )

    # P3
    if not args.skip_p3:
        remaining = args.budget_total_s - (time.time() - t_overall)
        if remaining > 30:
            run_vehicle1_v2(
                templates=templates,
                log=log,
                budget_s=min(args.p3_budget_s, remaining),
                seed=args.seed + 2,
                instance_time_s=args.instance_time_s,
            )

    log.finished_at = time.strftime("%Y-%m-%d %H:%M:%S")
    log.elapsed_s = time.time() - t_overall

    # Summary
    print("=" * 72, flush=True)
    print("Phase 3 v2 summary:", flush=True)
    for name, s in [
        ("Vehicle 3 (deficit gluing)", log.vehicle3_stats),
        ("Vehicle 2 (K66 balanced)", log.vehicle2_K66_stats),
        ("Vehicle 2 (circulants)", log.vehicle2_circ_stats),
        ("Vehicle 2 (perturbed bidirected)", log.vehicle2_pertB_stats),
        ("Vehicle 1 v2 (laminar)", log.vehicle1v2_stats),
    ]:
        print(
            f"  {name:36s}: streamed={s.streamed:5d}  k3={s.kappa3_pass:5d}  "
            f"unsat={s.verified_unsat:3d}  sat={s.verified_sat:5d}  "
            f"hit-rate(k3)={100*s.hit_rate_kappa3:5.1f}%  t={s.elapsed_s:.0f}s",
            flush=True,
        )
    print(f"  TOTAL UNSAT publishable candidates: {len(log.publishable_candidates)}", flush=True)
    print(f"  TOTAL elapsed: {log.elapsed_s:.0f}s", flush=True)
    print(f"  log: {log_path}", flush=True)

    with log_path.open("w") as f:
        json.dump(asdict(log), f, indent=2, default=str)

    return 0


if __name__ == "__main__":
    sys.exit(main())
