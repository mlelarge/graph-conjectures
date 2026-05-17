"""Phase 3 driver: hunt for a 3-arc-strong digraph violating WC3.

Runs Vehicle 3 (glued obstruction-template pairs across 3-arc interfaces),
optionally followed by Vehicle 1 (laminar tight-3-cut systems) if the
search budget is not yet exhausted.

Usage:
    uv run python code/run_phase3.py
    uv run python code/run_phase3.py --budget-s 600
    uv run python code/run_phase3.py --max-interfaces 30 --max-bridges 12

Outputs:
 - stdout: progress and findings
 - code/logs/phase3_<timestamp>.json: structured log of every candidate
   tested, plus the configuration and findings summary.
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
from typing import Any

# Allow `python code/run_phase3.py` or `python run_phase3.py` from code/.
HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from benchmarks import all_benchmarks, Benchmark  # noqa: E402
from cross_check import cross_check  # noqa: E402
from digraph import Digraph  # noqa: E402
from generators.checklist import (  # noqa: E402
    ChecklistResult,
    checklist_to_dict,
    independent_min_cut,
    run_checklist,
)
from generators.glue import (  # noqa: E402
    GenConfig,
    GluedInstance,
    generate_gluings,
    passes_arc_strong_3,
)
from generators.laminar import enumerate_laminar  # noqa: E402


# ----------------------------------------------------------------------------
# Logging
# ----------------------------------------------------------------------------


@dataclass
class CandidateLogEntry:
    idx: int
    name: str
    n: int
    m: int
    template1: str
    template2: str
    S1: list[int]
    S2: list[int]
    phi: list[list[int]]
    bridge_arcs: list[list[int]]
    bridge_pattern: list[str]
    arcs: list[list[int]]
    arc_connectivity: int
    strong: bool
    is_3_arc_strong: bool
    skipped_reason: str | None = None
    cross_check: dict[str, Any] | None = None
    checklist: dict[str, Any] | None = None
    is_candidate: bool = False


@dataclass
class Phase3Log:
    started_at: str
    config: dict[str, Any]
    seed: int
    templates: list[str]
    candidates_total_streamed: int = 0
    candidates_skipped_not_3_arc_strong: int = 0
    candidates_verified: int = 0
    candidates_unsat: int = 0
    publishable_candidates: list[dict[str, Any]] = field(default_factory=list)
    sample_entries: list[dict[str, Any]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    finished_at: str | None = None
    elapsed_s: float | None = None


# ----------------------------------------------------------------------------
# Vehicle 3 sweep
# ----------------------------------------------------------------------------


def run_vehicle3(
    templates: list[Benchmark],
    config: GenConfig,
    overall_budget_s: float,
    per_instance_time_limit_s: float,
    log: Phase3Log,
    sample_log_every: int,
) -> tuple[list[GluedInstance], list[dict[str, Any]]]:
    """Run the Vehicle 3 sweep.

    Returns (candidate_unsat_instances, all_entries_kept). Logs into `log`.
    """
    t0 = time.time()
    candidate_unsat: list[GluedInstance] = []
    entries_kept: list[dict[str, Any]] = []

    # Set up RNG (for any tiebreaks; not currently used in the deterministic
    # path, but we save the seed for the reproducibility item).
    rng = random.Random(config.seed)

    print(
        f"[vehicle3] templates: {[t.name for t in templates]}",
        flush=True,
    )
    print(
        f"[vehicle3] config: ordered_pairs={config.ordered_pairs}, "
        f"allow_self_glue={config.allow_self_glue}, "
        f"max_interfaces_per_pair={config.max_interfaces_per_pair}, "
        f"max_bridges_per_interface={config.max_bridges_per_interface}, "
        f"per_instance_time_limit_s={per_instance_time_limit_s}, "
        f"overall_budget_s={overall_budget_s}, "
        f"seed={config.seed}",
        flush=True,
    )

    for idx, inst in enumerate(generate_gluings(templates, config)):
        log.candidates_total_streamed += 1
        elapsed = time.time() - t0
        if elapsed > overall_budget_s:
            log.notes.append(
                f"vehicle3: overall budget exhausted after {elapsed:.1f}s "
                f"and {idx} candidates streamed"
            )
            print(f"[vehicle3] OVERALL BUDGET EXHAUSTED at idx={idx}", flush=True)
            break

        D = inst.build()
        strong = D.is_strongly_connected()
        k = D.arc_connectivity() if strong else 0
        is_3 = strong and (k == 3 if config.require_arc_conn_exactly_3 else k >= 3)

        if not is_3:
            log.candidates_skipped_not_3_arc_strong += 1
            if idx % sample_log_every == 0:
                entries_kept.append(
                    asdict(
                        CandidateLogEntry(
                            idx=idx,
                            name=inst.name,
                            n=inst.n,
                            m=len(inst.arcs),
                            template1=inst.template1,
                            template2=inst.template2,
                            S1=list(inst.S1),
                            S2=list(inst.S2),
                            phi=[list(p) for p in inst.phi],
                            bridge_arcs=[list(a) for a in inst.bridge_arcs],
                            bridge_pattern=list(inst.bridge_pattern),
                            arcs=[list(a) for a in inst.arcs],
                            arc_connectivity=k,
                            strong=strong,
                            is_3_arc_strong=False,
                            skipped_reason=("not_strongly_connected" if not strong else f"kappa'={k}"),
                        )
                    )
                )
            if idx > 0 and idx % 5000 == 0:
                print(
                    f"[vehicle3] progress: idx={idx} verified={log.candidates_verified} "
                    f"unsat={log.candidates_unsat} elapsed={time.time() - t0:.1f}s "
                    f"(skipped)",
                    flush=True,
                )
            continue

        # Verify (cross-check)
        log.candidates_verified += 1
        cc = cross_check(D, inst.name, time_limit_s=per_instance_time_limit_s)
        entry = asdict(
            CandidateLogEntry(
                idx=idx,
                name=inst.name,
                n=inst.n,
                m=len(inst.arcs),
                template1=inst.template1,
                template2=inst.template2,
                S1=list(inst.S1),
                S2=list(inst.S2),
                phi=[list(p) for p in inst.phi],
                bridge_arcs=[list(a) for a in inst.bridge_arcs],
                bridge_pattern=list(inst.bridge_pattern),
                arcs=[list(a) for a in inst.arcs],
                arc_connectivity=k,
                strong=strong,
                is_3_arc_strong=True,
                cross_check={
                    "ilp": cc.ilp.get("status"),
                    "sat": cc.sat.get("status"),
                    "agree": cc.agree,
                    "t_ilp": cc.ilp.get("time_s"),
                    "t_sat": cc.sat.get("time_s"),
                },
            )
        )

        if not cc.agree:
            log.notes.append(
                f"FATAL DISAGREEMENT on candidate idx={idx} name={inst.name}: "
                f"ILP={cc.ilp.get('status')} SAT={cc.sat.get('status')}"
            )
            print(
                f"[vehicle3] FATAL DISAGREEMENT idx={idx} name={inst.name} "
                f"ILP={cc.ilp.get('status')} SAT={cc.sat.get('status')}",
                flush=True,
            )
            entries_kept.append(entry)
            continue

        if cc.ilp["status"] == "UNSAT" and cc.sat["status"] == "UNSAT":
            log.candidates_unsat += 1
            print(
                f"[vehicle3] *** UNSAT 3-arc-strong candidate found ***",
                flush=True,
            )
            print(
                f"           idx={idx} name={inst.name} n={inst.n} m={len(inst.arcs)} k={k}",
                flush=True,
            )
            candidate_unsat.append(inst)
            # Run the checklist on this candidate
            checklist_res = run_checklist(
                instance_name=inst.name,
                arcs=list(inst.arcs),
                n=inst.n,
                templates=templates,
                seed=config.seed,
                cross_check_result=cc,
                do_minimization=True,
                time_limit_s=per_instance_time_limit_s,
            )
            entry["checklist"] = checklist_to_dict(checklist_res)
            entry["is_candidate"] = checklist_res.overall_publishable_as_candidate
            if checklist_res.overall_publishable_as_candidate:
                log.publishable_candidates.append(entry)
                print(
                    f"[vehicle3] *** PUBLISHABLE CANDIDATE (passed checklist core)",
                    flush=True,
                )
            else:
                print(
                    f"[vehicle3]     candidate UNSAT but checklist marks it as "
                    f"not yet publishable (item3_pass="
                    f"{checklist_res.item3_pass}, "
                    f"trivial_explainer={checklist_res.item3_trivial_explainer})",
                    flush=True,
                )

        # Always keep verified entries; sample the others.
        entries_kept.append(entry)

        if idx % 100 == 0 and idx > 0:
            print(
                f"[vehicle3] progress: idx={idx} verified={log.candidates_verified} "
                f"unsat={log.candidates_unsat} elapsed={time.time() - t0:.1f}s",
                flush=True,
            )

    return candidate_unsat, entries_kept


# ----------------------------------------------------------------------------
# Vehicle 1 sweep
# ----------------------------------------------------------------------------


def run_vehicle1(
    templates: list[Benchmark],
    n_range: range,
    max_k: int,
    overall_budget_s: float,
    per_instance_time_limit_s: float,
    log: Phase3Log,
) -> tuple[list[Any], list[dict[str, Any]]]:
    """Run the Vehicle 1 sweep (laminar tight-3-cut systems)."""
    t0 = time.time()
    print(
        f"[vehicle1] starting: n_range={list(n_range)} max_k={max_k}",
        flush=True,
    )
    candidates: list[Any] = []
    entries: list[dict[str, Any]] = []

    for idx, inst in enumerate(enumerate_laminar(n_range, max_k=max_k)):
        elapsed = time.time() - t0
        if elapsed > overall_budget_s:
            log.notes.append(
                f"vehicle1: budget exhausted after {elapsed:.1f}s and {idx} candidates"
            )
            print(f"[vehicle1] BUDGET EXHAUSTED at idx={idx}", flush=True)
            break
        D = inst.build()
        strong = D.is_strongly_connected()
        k = D.arc_connectivity() if strong else 0
        entry = {
            "idx": idx,
            "name": inst.name,
            "n": inst.n,
            "m": len(inst.arcs),
            "shells": [list(s) for s in inst.shells],
            "arcs": [list(a) for a in inst.arcs],
            "arc_connectivity": k,
            "strong": strong,
        }
        if not strong or k < 3:
            entry["skipped_reason"] = (
                "not_strongly_connected" if not strong else f"kappa'={k}"
            )
            entries.append(entry)
            continue
        cc = cross_check(D, inst.name, time_limit_s=per_instance_time_limit_s)
        entry["cross_check"] = {
            "ilp": cc.ilp.get("status"),
            "sat": cc.sat.get("status"),
            "agree": cc.agree,
            "t_ilp": cc.ilp.get("time_s"),
            "t_sat": cc.sat.get("time_s"),
        }
        if cc.agree and cc.ilp["status"] == "UNSAT" and cc.sat["status"] == "UNSAT":
            print(
                f"[vehicle1] *** UNSAT 3-arc-strong laminar candidate at idx={idx}",
                flush=True,
            )
            candidates.append(inst)
            checklist_res = run_checklist(
                instance_name=inst.name,
                arcs=list(inst.arcs),
                n=inst.n,
                templates=templates,
                seed=0,
                cross_check_result=cc,
                do_minimization=True,
                time_limit_s=per_instance_time_limit_s,
            )
            entry["checklist"] = checklist_to_dict(checklist_res)
            entry["is_candidate"] = checklist_res.overall_publishable_as_candidate
        entries.append(entry)

    return candidates, entries


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 3 driver for WC3 hunt")
    parser.add_argument("--budget-s", type=float, default=2400.0, help="overall wall-clock budget for the entire run, in seconds")
    parser.add_argument("--instance-time-s", type=float, default=20.0, help="per-instance time limit for the verifier")
    parser.add_argument("--max-interfaces", type=int, default=24, help="max interfaces (S1, S2, phi) per template pair")
    parser.add_argument("--max-bridges", type=int, default=8, help="max bridge sets per interface")
    parser.add_argument("--num-bridges", type=int, default=3, help="number of bridge arcs per gluing (Phase-3 spec says 3)")
    parser.add_argument("--extended-bridge-sweep", action="store_true", default=False, help="after the 3-bridge sweep, also run num_bridges = 4")
    parser.add_argument("--bridge-counts", type=str, default="", help="comma-separated list of num_bridges values to sweep (overrides --num-bridges and --extended-bridge-sweep)")
    parser.add_argument("--allow-self-glue", action="store_true", default=True)
    parser.add_argument("--no-self-glue", dest="allow_self_glue", action="store_false")
    parser.add_argument("--ordered-pairs", action="store_true", default=True)
    parser.add_argument("--unordered-pairs", dest="ordered_pairs", action="store_false")
    parser.add_argument("--seed", type=int, default=20260516)
    parser.add_argument("--sample-log-every", type=int, default=200, help="log one in N rejected (non-3-arc-strong) candidates as a sample for the JSON log")
    parser.add_argument("--run-vehicle1", action="store_true", default=False)
    parser.add_argument("--vehicle1-budget-s", type=float, default=300.0)
    parser.add_argument("--logs-dir", default=str(HERE / "logs"))
    args = parser.parse_args()

    started_at = time.strftime("%Y-%m-%d %H:%M:%S")
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    logs_dir = Path(args.logs_dir)
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / f"phase3_{timestamp}.json"

    # Filter benchmarks to the 8 UNSAT templates per the spec.
    UNSAT_NAMES = {
        "S4", "C6_square", "C8_square",
        "C3_K2K2K2", "C3_K2K2P2", "C3_K2K2K3",
        "AiEtAl_L211_min", "AiEtAl_L312_min",
    }
    templates = [b for b in all_benchmarks() if b.name in UNSAT_NAMES]

    overall_t0 = time.time()

    if args.bridge_counts:
        bridge_counts = sorted({int(x) for x in args.bridge_counts.split(",")})
    elif args.extended_bridge_sweep:
        bridge_counts = sorted(set([args.num_bridges] + [4]))
    else:
        bridge_counts = [args.num_bridges]

    log = Phase3Log(
        started_at=started_at,
        config={"bridge_counts": bridge_counts},
        seed=args.seed,
        templates=[t.name for t in templates],
    )

    for nb in bridge_counts:
        elapsed = time.time() - overall_t0
        remaining = args.budget_s - elapsed
        if remaining <= 30:
            log.notes.append(f"skipping num_bridges={nb}: budget exhausted")
            print(f"[main] skipping num_bridges={nb} (remaining={remaining:.1f}s)", flush=True)
            continue
        print(f"[main] sweeping with num_bridges={nb} (remaining_budget={remaining:.1f}s)", flush=True)
        config = GenConfig(
            max_interfaces_per_pair=args.max_interfaces,
            max_bridges_per_interface=args.max_bridges,
            num_bridges=nb,
            allow_self_glue=args.allow_self_glue,
            ordered_pairs=args.ordered_pairs,
            require_arc_conn_exactly_3=True,
            seed=args.seed,
        )
        log.config[f"sweep_num_bridges_{nb}"] = asdict(config)

        vehicle3_candidates, v3_entries = run_vehicle3(
            templates=templates,
            config=config,
            overall_budget_s=remaining,
            per_instance_time_limit_s=args.instance_time_s,
            log=log,
            sample_log_every=args.sample_log_every,
        )
        log.sample_entries.extend(v3_entries)

    v1_entries: list[dict[str, Any]] = []
    elapsed = time.time() - overall_t0
    remaining = args.budget_s - elapsed
    if args.run_vehicle1 and remaining > 30:
        v1_budget = min(remaining, args.vehicle1_budget_s)
        v1_candidates, v1_entries = run_vehicle1(
            templates=templates,
            n_range=range(7, 11),
            max_k=3,
            overall_budget_s=v1_budget,
            per_instance_time_limit_s=args.instance_time_s,
            log=log,
        )
        log.sample_entries.extend(v1_entries)
    else:
        log.notes.append(
            f"vehicle1: not run (run_vehicle1={args.run_vehicle1}, remaining_budget={remaining:.1f}s)"
        )

    log.finished_at = time.strftime("%Y-%m-%d %H:%M:%S")
    log.elapsed_s = time.time() - overall_t0

    # Final summary
    print("=" * 72, flush=True)
    print(f"Phase 3 summary:", flush=True)
    print(f"  candidates streamed:               {log.candidates_total_streamed}", flush=True)
    print(f"  candidates skipped (not 3-arc-strong): {log.candidates_skipped_not_3_arc_strong}", flush=True)
    print(f"  candidates verified (3-arc-strong): {log.candidates_verified}", flush=True)
    print(f"  candidates UNSAT (3-arc-strong + UNSAT): {log.candidates_unsat}", flush=True)
    print(f"  publishable candidates (passed checklist core): {len(log.publishable_candidates)}", flush=True)
    print(f"  elapsed: {log.elapsed_s:.1f}s", flush=True)
    print(f"  log path: {log_path}", flush=True)
    for note in log.notes:
        print(f"  note: {note}", flush=True)
    print("=" * 72, flush=True)

    # Write JSON log
    with log_path.open("w") as f:
        json.dump(asdict(log), f, indent=2, default=str)

    return 0


if __name__ == "__main__":
    sys.exit(main())
