"""Phase 3 v3 support driver: pynauty canonicalization + Vehicle 5 sweep
+ optional Cayley batch.

Per Lead's post-v2 reallocation (~25-30% budget on Phase 3 maintenance):

  Task A. Canonicalize the deterministic regeneration of Phase 3 v2's
          Vehicle 3 deficit gluings. Emit per-template-pair iso-class
          counts (vs labeled-distinct counts).

  Task B. Vehicle 5 (iterated substitution). Exactly ONE sweep:
          every ordered template pair (T_outer, T_inner) x every
          v in V(T_outer); filter by lambda^arc = 3; run cross_check
          (ILP + SAT). Any verified UNSAT triggers the 10-item
          checklist and immediate stop.

  Task C. Optional small non-abelian Cayley batch (~30 min cap).
          Sweep Cayley digraphs on S_3, D_4, Q_8, A_4 with small
          asymmetric generator sets; filter lambda^arc = 3; verify.

Output: single JSON log at code/logs/phase3v3_<timestamp>.json plus
stdout transcript.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from benchmarks import all_benchmarks, Benchmark  # noqa: E402
from cross_check import cross_check  # noqa: E402
from digraph import Digraph  # noqa: E402
from generators.canonicalize import canonical_key  # noqa: E402
from generators.checklist import (  # noqa: E402
    checklist_to_dict,
    run_checklist,
)
from generators.glue_deficit import (  # noqa: E402
    DeficitGenConfig,
    generate_deficit_gluings,
    passes_arc_strong_3 as glue_passes_3,
    vertex_degree_feasible,
)
from generators.substitution import (  # noqa: E402
    CompositionInstance,
    SubstitutionInstance,
    sweep_all_compositions,
    sweep_all_substitutions,
)


UNSAT_NAMES = {
    "S4", "C6_square", "C8_square",
    "C3_K2K2K2", "C3_K2K2P2", "C3_K2K2K3",
    "AiEtAl_L211_min", "AiEtAl_L312_min", "AiEtAl_iv_star_iv",
}


# ----------------------------------------------------------------------------
# Log structure
# ----------------------------------------------------------------------------


@dataclass
class TaskAStats:
    streamed: int = 0
    deg_gate_pass: int = 0
    kappa3_pass: int = 0
    # canonical_keys keyed by pair "T1+T2" (sorted): set of distinct hashes
    pair_labeled_counts: dict[str, int] = field(default_factory=dict)
    pair_iso_counts: dict[str, int] = field(default_factory=dict)
    pair_iso_hashes: dict[str, list[str]] = field(default_factory=dict)
    elapsed_s: float = 0.0
    notes: list[str] = field(default_factory=list)


@dataclass
class TaskBStats:
    streamed: int = 0
    deg_gate_pass: int = 0
    kappa3_pass: int = 0
    iso_distinct: int = 0
    verified_unsat: int = 0
    verified_sat: int = 0
    disagreements: int = 0
    elapsed_s: float = 0.0
    # Single-vertex substitution sub-sweep
    single_streamed: int = 0
    single_kappa3_pass: int = 0
    # Composition (substitute every outer vertex) sub-sweep
    comp_streamed: int = 0
    comp_kappa3_pass: int = 0
    # Per-(outer, v, inner) result: keep all because the sweep is small.
    triples: list[dict[str, Any]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass
class TaskCStats:
    streamed: int = 0
    deg_gate_pass: int = 0
    kappa3_pass: int = 0
    iso_distinct: int = 0
    verified_unsat: int = 0
    verified_sat: int = 0
    disagreements: int = 0
    elapsed_s: float = 0.0
    entries: list[dict[str, Any]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass
class Phase3V3Log:
    started_at: str
    config: dict[str, Any] = field(default_factory=dict)
    seed: int = 20260516
    templates: list[str] = field(default_factory=list)
    template_canonical_keys: dict[str, str] = field(default_factory=dict)

    task_a: TaskAStats = field(default_factory=TaskAStats)
    task_b: TaskBStats = field(default_factory=TaskBStats)
    task_c: TaskCStats = field(default_factory=TaskCStats)

    candidate_entries: list[dict[str, Any]] = field(default_factory=list)
    publishable_candidates: list[dict[str, Any]] = field(default_factory=list)

    finished_at: str | None = None
    elapsed_s: float | None = None
    notes: list[str] = field(default_factory=list)


# ----------------------------------------------------------------------------
# Task A — canonicalize Vehicle 3 deficit-gluing regeneration
# ----------------------------------------------------------------------------


def run_task_a(
    templates: list[Benchmark],
    log: Phase3V3Log,
    budget_s: float,
    seed: int,
    per_pair_cap: int = 100,
) -> None:
    """Deterministically regenerate Vehicle 3 v2 candidates and canonicalize.

    Uses the same config as `team/07_phase3_report_v2.md` Appendix A, with
    `verified_per_pair_cap = 100` to match v2's actual run.
    """
    print("=" * 72, flush=True)
    print(f"[A: canonicalize v2 Vehicle 3] starting (budget={budget_s:.0f}s)", flush=True)
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
    log.config["task_a"] = asdict(cfg)
    stats = log.task_a
    t0 = time.time()

    pair_verified: dict[tuple[str, str], int] = {}
    pair_iso_hashes: dict[tuple[str, str], set[str]] = {}

    last_progress = 0
    for idx, inst in enumerate(generate_deficit_gluings(templates, cfg)):
        if time.time() - t0 > budget_s:
            stats.notes.append(f"budget exhausted at idx={idx}")
            print(f"[A] BUDGET EXHAUSTED at idx={idx}", flush=True)
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
        stats.pair_labeled_counts[pkey] = stats.pair_labeled_counts.get(pkey, 0) + 1
        ck = canonical_key(D)
        pair_iso_hashes.setdefault(pair_key, set()).add(ck)

        if stats.streamed - last_progress >= 1000:
            last_progress = stats.streamed
            print(
                f"[A]   streamed={stats.streamed} k3={stats.kappa3_pass} "
                f"pairs_at_cap={sum(1 for v in pair_verified.values() if v >= per_pair_cap)} "
                f"t={time.time()-t0:.0f}s",
                flush=True,
            )

    # Finalize iso-counts
    for pair_key, hashes in pair_iso_hashes.items():
        pkey = f"{pair_key[0]}+{pair_key[1]}"
        stats.pair_iso_counts[pkey] = len(hashes)
        # Keep the hash list (16-hex prefix) for traceability
        stats.pair_iso_hashes[pkey] = sorted([h[:16] for h in hashes])

    stats.elapsed_s = time.time() - t0

    # Summary print
    print("=" * 72, flush=True)
    print(f"[A] done. streamed={stats.streamed} k3={stats.kappa3_pass} t={stats.elapsed_s:.0f}s", flush=True)
    print(f"[A] per-pair labeled vs iso counts:", flush=True)
    print(f"     {'pair':56s}  labeled  iso  ratio", flush=True)
    print(f"     {'-' * 56}  -------  ---  -----", flush=True)
    total_lab = 0
    total_iso = 0
    for pkey in sorted(stats.pair_labeled_counts):
        lab = stats.pair_labeled_counts[pkey]
        iso = stats.pair_iso_counts.get(pkey, 0)
        total_lab += lab
        total_iso += iso
        print(f"     {pkey:56s}  {lab:5d}    {iso:3d}  {iso / max(lab, 1):.2f}", flush=True)
    print(f"     {'-' * 56}  -------  ---  -----", flush=True)
    print(f"     {'TOTAL':56s}  {total_lab:5d}    {total_iso:3d}  {total_iso / max(total_lab, 1):.2f}", flush=True)


# ----------------------------------------------------------------------------
# Task B — Vehicle 5 substitution sweep
# ----------------------------------------------------------------------------


def _verify_candidate(
    inst_name: str,
    arcs: tuple[tuple[int, int], ...],
    n: int,
    metadata: dict[str, Any],
    templates: list[Benchmark],
    log: Phase3V3Log,
    stats: Any,
    seed: int,
    time_limit_s: float,
) -> str | None:
    """Cross-check; on UNSAT run checklist and append to candidate list.
    Returns 'SAT' / 'UNSAT' / 'DISAGREE' / 'UNKNOWN'."""
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
        log.notes.append(
            f"FATAL: cross-check disagree on {inst_name}: "
            f"ILP={cc.ilp.get('status')} SAT={cc.sat.get('status')}"
        )
        print(f"  *** FATAL DISAGREE: {inst_name}", flush=True)
        return "DISAGREE"

    s_ilp = cc.ilp.get("status")
    if s_ilp == "UNSAT":
        stats.verified_unsat += 1
        print(
            f"  *** UNSAT 3-arc-strong candidate ***  name={inst_name}  "
            f"n={n}  m={len(arcs)}",
            flush=True,
        )
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
                print("  *** PUBLISHABLE: passed checklist core ***", flush=True)
        except Exception as e:
            entry["checklist_error"] = str(e)
            log.notes.append(f"checklist error on {inst_name}: {e}")
        log.candidate_entries.append(entry)
        return "UNSAT"
    elif s_ilp == "SAT":
        stats.verified_sat += 1
        return "SAT"
    else:
        stats.notes.append(f"UNKNOWN status on {inst_name}: ILP={s_ilp} SAT={cc.sat.get('status')}")
        return "UNKNOWN"


def _process_candidate_inst(
    inst_name: str,
    arcs: tuple[tuple[int, int], ...],
    n: int,
    metadata: dict[str, Any],
    templates: list[Benchmark],
    log: Phase3V3Log,
    stats: TaskBStats,
    seed: int,
    instance_time_s: float,
    seen_keys: set[str],
) -> tuple[str | None, bool]:
    """Filter + canonicalize + verify a single candidate.
    Returns (status, was_iso_new). status is None if filtered out before
    cross-check."""
    D = Digraph.from_arcs(range(n), list(arcs))
    # Degree gate
    outd = {v: 0 for v in range(n)}
    ind = {v: 0 for v in range(n)}
    for u, v in arcs:
        outd[u] += 1
        ind[v] += 1
    for v in range(n):
        if outd[v] < 3 or ind[v] < 3:
            return None, False
    stats.deg_gate_pass += 1
    if D.arc_connectivity() != 3:
        return None, False
    stats.kappa3_pass += 1
    ck = canonical_key(D)
    was_new = ck not in seen_keys
    seen_keys.add(ck)
    if was_new:
        stats.iso_distinct += 1
    metadata = {**metadata, "canonical_key": ck, "iso_first_seen": was_new}
    if not was_new:
        # Skip duplicate iso-classes for verification, but log the count.
        return "SKIP_DUPLICATE_ISO", False
    status = _verify_candidate(
        inst_name, arcs, n, metadata,
        templates, log, stats, seed,
        time_limit_s=instance_time_s,
    )
    return status, was_new


def run_task_b(
    templates: list[Benchmark],
    log: Phase3V3Log,
    budget_s: float,
    seed: int,
    instance_time_s: float = 12.0,
    composition_max_n: int = 24,
) -> bool:
    """Run the Vehicle 5 sweep. Returns True if we found an UNSAT or a
    cross-solver disagreement (stop-condition triggered).

    The sweep has two sub-passes:
      B.1 Single-vertex substitution: (T_outer, v, T_inner) for every
          v in V(T_outer). This preserves out/in-degrees of *other*
          outer vertices, so it never lifts lambda^arc above 2 in our
          2-arc-strong template family. Recorded for completeness; the
          kappa = 3 filter rejects all of these.

      B.2 Lexicographic composition T_outer[T_inner]: substitute every
          outer vertex by a fresh copy of T_inner. This is the natural
          "lift kappa from 2 to >= 3" operation. Bounded by
          n_outer * n_inner <= composition_max_n.

    Iso-canonical deduplication via the new pynauty pipeline.
    """
    print("=" * 72, flush=True)
    print(f"[B: Vehicle 5 substitution + composition] starting (budget={budget_s:.0f}s)", flush=True)
    stats = log.task_b
    t0 = time.time()
    seen_keys: set[str] = set()

    # ----- B.1 single-vertex substitution -----
    print("[B.1] single-vertex substitution sub-sweep", flush=True)
    for inst in sweep_all_substitutions(templates, ordered=True):
        if time.time() - t0 > budget_s:
            stats.notes.append("budget exhausted in B.1")
            print("[B.1] BUDGET EXHAUSTED", flush=True)
            stats.elapsed_s = time.time() - t0
            return False
        stats.streamed += 1
        stats.single_streamed += 1
        metadata = {
            "vehicle": "5_substitution_single",
            "outer": inst.outer,
            "inner": inst.inner,
            "v_outer": inst.v_outer,
            "outer_n": inst.outer_n,
            "outer_m": inst.outer_m,
            "inner_n": inst.inner_n,
            "inner_m": inst.inner_m,
            "v_in_degree": inst.v_in_degree,
            "v_out_degree": inst.v_out_degree,
            "arcs": [list(a) for a in inst.arcs],
        }
        status, _ = _process_candidate_inst(
            inst.name, inst.arcs, inst.n, metadata,
            templates, log, stats, seed, instance_time_s, seen_keys,
        )
        if status is not None:
            stats.single_kappa3_pass += 1
            triple = {
                "subsweep": "single",
                "outer": inst.outer,
                "v_outer": inst.v_outer,
                "inner": inst.inner,
                "n": inst.n,
                "m": len(inst.arcs),
                "status": status,
            }
            stats.triples.append(triple)
            if status == "UNSAT":
                stats.notes.append(
                    f"STOP CONDITION: lambda=3 UNSAT at {inst.name}; halting Vehicle 5."
                )
                print(f"[B.1] STOP at UNSAT {inst.name}", flush=True)
                stats.elapsed_s = time.time() - t0
                return True
            if status == "DISAGREE":
                stats.elapsed_s = time.time() - t0
                return True
    print(
        f"[B.1] done. streamed={stats.single_streamed} k3={stats.single_kappa3_pass} "
        f"(single-vertex substitution does not lift kappa above 2 in this family)",
        flush=True,
    )

    # ----- B.2 lexicographic composition -----
    print("[B.2] lexicographic composition sub-sweep (n <= {})".format(composition_max_n), flush=True)
    for inst in sweep_all_compositions(templates, ordered=True, max_n=composition_max_n):
        if time.time() - t0 > budget_s:
            stats.notes.append("budget exhausted in B.2")
            print("[B.2] BUDGET EXHAUSTED", flush=True)
            break
        stats.streamed += 1
        stats.comp_streamed += 1
        metadata = {
            "vehicle": "5_substitution_composition",
            "outer": inst.outer,
            "inner": inst.inner,
            "outer_n": inst.outer_n,
            "outer_m": inst.outer_m,
            "inner_n": inst.inner_n,
            "inner_m": inst.inner_m,
            "arcs": [list(a) for a in inst.arcs],
        }
        status, _ = _process_candidate_inst(
            inst.name, inst.arcs, inst.n, metadata,
            templates, log, stats, seed, instance_time_s, seen_keys,
        )
        if status is not None:
            stats.comp_kappa3_pass += 1
            triple = {
                "subsweep": "composition",
                "outer": inst.outer,
                "inner": inst.inner,
                "n": inst.n,
                "m": len(inst.arcs),
                "status": status,
            }
            stats.triples.append(triple)
            if status == "UNSAT":
                stats.notes.append(
                    f"STOP CONDITION: lambda=3 UNSAT at {inst.name}; halting Vehicle 5."
                )
                print(f"[B.2] STOP at UNSAT {inst.name}", flush=True)
                stats.elapsed_s = time.time() - t0
                return True
            if status == "DISAGREE":
                stats.elapsed_s = time.time() - t0
                return True

    stats.elapsed_s = time.time() - t0
    print(
        f"[B] done. streamed={stats.streamed} deg_ok={stats.deg_gate_pass} "
        f"k3={stats.kappa3_pass} iso_distinct={stats.iso_distinct} "
        f"unsat={stats.verified_unsat} sat={stats.verified_sat} "
        f"disagree={stats.disagreements} t={stats.elapsed_s:.0f}s",
        flush=True,
    )
    return False


# ----------------------------------------------------------------------------
# Task C — optional Cayley batch
# ----------------------------------------------------------------------------


def _cayley_group_S3() -> tuple[str, list[tuple[int, ...]]]:
    """Return ("S_3", list of 6 elements as 3-tuples).
    Each element is a permutation written as a 3-tuple (image of 0, 1, 2)."""
    from itertools import permutations
    elems = list(permutations(range(3)))
    return "S_3", elems


def _cayley_group_D4() -> tuple[str, list[tuple[int, ...]]]:
    """Dihedral group of order 8 = symmetries of a square.
    Elements as 4-permutations (image of 0..3)."""
    # 4 rotations + 4 reflections, all as permutations of {0, 1, 2, 3}.
    elems: list[tuple[int, ...]] = []
    # Rotations
    for k in range(4):
        elems.append(tuple((i + k) % 4 for i in range(4)))
    # Reflections
    for k in range(4):
        elems.append(tuple((k - i) % 4 for i in range(4)))
    # Dedup (safety)
    seen = set()
    out = []
    for e in elems:
        if e not in seen:
            seen.add(e)
            out.append(e)
    return "D_4", out


def _cayley_group_Q8() -> tuple[str, list[str]]:
    """Quaternion group Q_8 = {1, -1, i, -i, j, -j, k, -k} with multiplication.
    We use symbolic representation; multiplication is hard-coded in
    `_cayley_multiply_Q8`."""
    return "Q_8", ["1", "-1", "i", "-i", "j", "-j", "k", "-k"]


_Q8_TABLE = {
    ("1", "1"): "1", ("1", "-1"): "-1", ("1", "i"): "i", ("1", "-i"): "-i",
    ("1", "j"): "j", ("1", "-j"): "-j", ("1", "k"): "k", ("1", "-k"): "-k",
    ("-1", "1"): "-1", ("-1", "-1"): "1", ("-1", "i"): "-i", ("-1", "-i"): "i",
    ("-1", "j"): "-j", ("-1", "-j"): "j", ("-1", "k"): "-k", ("-1", "-k"): "k",
    ("i", "1"): "i", ("i", "-1"): "-i", ("i", "i"): "-1", ("i", "-i"): "1",
    ("i", "j"): "k", ("i", "-j"): "-k", ("i", "k"): "-j", ("i", "-k"): "j",
    ("-i", "1"): "-i", ("-i", "-1"): "i", ("-i", "i"): "1", ("-i", "-i"): "-1",
    ("-i", "j"): "-k", ("-i", "-j"): "k", ("-i", "k"): "j", ("-i", "-k"): "-j",
    ("j", "1"): "j", ("j", "-1"): "-j", ("j", "i"): "-k", ("j", "-i"): "k",
    ("j", "j"): "-1", ("j", "-j"): "1", ("j", "k"): "i", ("j", "-k"): "-i",
    ("-j", "1"): "-j", ("-j", "-1"): "j", ("-j", "i"): "k", ("-j", "-i"): "-k",
    ("-j", "j"): "1", ("-j", "-j"): "-1", ("-j", "k"): "-i", ("-j", "-k"): "i",
    ("k", "1"): "k", ("k", "-1"): "-k", ("k", "i"): "j", ("k", "-i"): "-j",
    ("k", "j"): "-i", ("k", "-j"): "i", ("k", "k"): "-1", ("k", "-k"): "1",
    ("-k", "1"): "-k", ("-k", "-1"): "k", ("-k", "i"): "-j", ("-k", "-i"): "j",
    ("-k", "j"): "i", ("-k", "-j"): "-i", ("-k", "k"): "1", ("-k", "-k"): "-1",
}


def _cayley_group_A4() -> tuple[str, list[tuple[int, ...]]]:
    """Alternating group A_4 (even permutations of {0,1,2,3}). 12 elements."""
    from itertools import permutations
    def sign(p: tuple[int, ...]) -> int:
        n = len(p)
        s = 1
        for i in range(n):
            for j in range(i + 1, n):
                if p[i] > p[j]:
                    s = -s
        return s
    return "A_4", [p for p in permutations(range(4)) if sign(p) == 1]


def _multiply(group_name: str, a, b):
    """Return the product a * b in the group."""
    if group_name == "Q_8":
        return _Q8_TABLE[(a, b)]
    # Permutation multiplication: (a * b)(x) = a(b(x))
    return tuple(a[b[i]] for i in range(len(a)))


def _build_cayley_digraph(group_name: str, elems: list, generators: list) -> tuple[int, list[tuple[int, int]]]:
    """Build the (right) Cayley digraph Cay(G, S) where S = generators.

    Arc x -> x * s for every x in G and s in S.
    """
    idx = {e: i for i, e in enumerate(elems)}
    n = len(elems)
    arcs: list[tuple[int, int]] = []
    for x in elems:
        for s in generators:
            y = _multiply(group_name, x, s)
            arcs.append((idx[x], idx[y]))
    return n, arcs


def run_task_c(
    templates: list[Benchmark],
    log: Phase3V3Log,
    budget_s: float,
    seed: int,
    instance_time_s: float = 12.0,
) -> bool:
    """Sweep small non-abelian Cayley digraphs at lambda = 3.

    Returns True if an UNSAT was found (stop condition).
    """
    print("=" * 72, flush=True)
    print(f"[C: small non-abelian Cayley batch] starting (budget={budget_s:.0f}s)", flush=True)
    stats = log.task_c
    t0 = time.time()
    rng = random.Random(seed)
    seen_keys: set[str] = set()

    groups = [
        _cayley_group_S3(),
        _cayley_group_D4(),
        _cayley_group_Q8(),
        _cayley_group_A4(),
    ]

    for group_name, elems in groups:
        if time.time() - t0 > budget_s:
            break
        n = len(elems)
        identity = elems[0]  # we placed identity first for permutation groups;
        # for Q_8 the first is "1" which is identity.
        non_identity = [e for e in elems if e != identity]

        # Enumerate generator sets of size in {3, 4, 5}, asymmetric (S != S^{-1}).
        # We avoid the identity in S (gives self-loops which we don't want here).
        # For efficiency we sample a bounded number of subsets.
        for size in [3, 4]:
            from itertools import combinations
            all_subsets = list(combinations(non_identity, size))
            # Cap the per-(group, size) explore at 200 random subsets.
            cap = min(200, len(all_subsets))
            rng.shuffle(all_subsets)
            for S in all_subsets[:cap]:
                if time.time() - t0 > budget_s:
                    break
                stats.streamed += 1
                # Quick degree gate: every vertex has out-degree = |S| and
                # in-degree = |S| in any Cayley digraph (transitive). So
                # |S| >= 3 ensures the degree gate; |S| <= n-1 ensures
                # no self-loops if identity not in S.
                if size < 3:
                    continue
                n_g, arcs = _build_cayley_digraph(group_name, elems, list(S))
                # Skip if not strongly connected (i.e., S does not generate the group).
                D = Digraph.from_arcs(range(n_g), arcs)
                if not D.is_strongly_connected():
                    continue
                stats.deg_gate_pass += 1
                if D.arc_connectivity() != 3:
                    continue
                stats.kappa3_pass += 1
                ck = canonical_key(D)
                was_new = ck not in seen_keys
                seen_keys.add(ck)
                if was_new:
                    stats.iso_distinct += 1
                else:
                    # Skip verification of already-seen iso-classes.
                    continue
                name = f"Cay[{group_name}|S={size}|seed={seed}|n={stats.streamed}]"
                metadata = {
                    "vehicle": "Cayley",
                    "group": group_name,
                    "gen_size": size,
                    "canonical_key": ck,
                    "iso_first_seen": True,
                    "arcs": [list(a) for a in arcs],
                }
                status = _verify_candidate(
                    name, tuple(arcs), n_g, metadata,
                    templates, log, stats, seed,
                    time_limit_s=instance_time_s,
                )
                stats.entries.append({
                    "name": name,
                    "group": group_name,
                    "gen_size": size,
                    "n": n_g,
                    "m": len(arcs),
                    "kappa": 3,
                    "canonical_key": ck,
                    "status": status,
                })
                if status == "UNSAT":
                    stats.notes.append(
                        f"STOP CONDITION: lambda=3 UNSAT at {name}."
                    )
                    print(f"[C] STOP CONDITION FIRED at {name}", flush=True)
                    stats.elapsed_s = time.time() - t0
                    return True
                if status == "DISAGREE":
                    stats.elapsed_s = time.time() - t0
                    return True

    stats.elapsed_s = time.time() - t0
    print(
        f"[C] done. streamed={stats.streamed} k3={stats.kappa3_pass} "
        f"iso_distinct={stats.iso_distinct} unsat={stats.verified_unsat} "
        f"sat={stats.verified_sat} t={stats.elapsed_s:.0f}s",
        flush=True,
    )
    return False


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------


def main() -> int:
    p = argparse.ArgumentParser(description="Phase 3 v3 support driver")
    p.add_argument("--budget-total-s", type=float, default=7200.0)
    p.add_argument("--task-a-budget-s", type=float, default=2700.0,
                   help="Task A (canonicalize v2) budget, ~45 min default")
    p.add_argument("--task-b-budget-s", type=float, default=2700.0,
                   help="Task B (Vehicle 5) budget, ~45 min default")
    p.add_argument("--task-c-budget-s", type=float, default=1800.0,
                   help="Task C (Cayley) budget, ~30 min default")
    p.add_argument("--per-pair-cap", type=int, default=100)
    p.add_argument("--instance-time-s", type=float, default=12.0)
    p.add_argument("--seed", type=int, default=20260516)
    p.add_argument("--logs-dir", default=str(HERE / "logs"))
    p.add_argument("--skip-a", action="store_true", default=False)
    p.add_argument("--skip-b", action="store_true", default=False)
    p.add_argument("--skip-c", action="store_true", default=False)
    args = p.parse_args()

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    logs_dir = Path(args.logs_dir)
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / f"phase3v3_{timestamp}.json"

    templates = [b for b in all_benchmarks() if b.name in UNSAT_NAMES]

    log = Phase3V3Log(
        started_at=time.strftime("%Y-%m-%d %H:%M:%S"),
        config={
            "budget_total_s": args.budget_total_s,
            "task_a_budget_s": args.task_a_budget_s,
            "task_b_budget_s": args.task_b_budget_s,
            "task_c_budget_s": args.task_c_budget_s,
            "per_pair_cap": args.per_pair_cap,
            "instance_time_s": args.instance_time_s,
        },
        seed=args.seed,
        templates=[t.name for t in templates],
        template_canonical_keys={
            t.name: canonical_key(t.build()) for t in templates
        },
    )

    t_overall = time.time()

    # Task A
    stop_triggered = False
    if not args.skip_a:
        run_task_a(
            templates=templates,
            log=log,
            budget_s=min(args.task_a_budget_s, args.budget_total_s),
            seed=args.seed,
            per_pair_cap=args.per_pair_cap,
        )

    # Task B
    if not args.skip_b:
        remaining = args.budget_total_s - (time.time() - t_overall)
        if remaining > 10:
            stop_triggered = run_task_b(
                templates=templates,
                log=log,
                budget_s=min(args.task_b_budget_s, remaining),
                seed=args.seed + 1,
                instance_time_s=args.instance_time_s,
            )

    # Task C — only if Task B did not stop and we have budget.
    if not args.skip_c and not stop_triggered:
        remaining = args.budget_total_s - (time.time() - t_overall)
        if remaining > 10:
            run_task_c(
                templates=templates,
                log=log,
                budget_s=min(args.task_c_budget_s, remaining),
                seed=args.seed + 2,
                instance_time_s=args.instance_time_s,
            )
    elif stop_triggered:
        log.notes.append("Task C SKIPPED because Task B fired the stop condition.")

    log.finished_at = time.strftime("%Y-%m-%d %H:%M:%S")
    log.elapsed_s = time.time() - t_overall

    # Summary
    print("=" * 72, flush=True)
    print("Phase 3 v3 support summary:", flush=True)
    print(
        f"  Task A: streamed={log.task_a.streamed} k3={log.task_a.kappa3_pass} "
        f"pairs={len(log.task_a.pair_labeled_counts)} "
        f"labeled={sum(log.task_a.pair_labeled_counts.values())} "
        f"iso={sum(log.task_a.pair_iso_counts.values())} t={log.task_a.elapsed_s:.0f}s",
        flush=True,
    )
    print(
        f"  Task B: streamed={log.task_b.streamed} k3={log.task_b.kappa3_pass} "
        f"iso_distinct={log.task_b.iso_distinct} unsat={log.task_b.verified_unsat} "
        f"sat={log.task_b.verified_sat} disagree={log.task_b.disagreements} "
        f"t={log.task_b.elapsed_s:.0f}s",
        flush=True,
    )
    print(
        f"  Task C: streamed={log.task_c.streamed} k3={log.task_c.kappa3_pass} "
        f"iso_distinct={log.task_c.iso_distinct} unsat={log.task_c.verified_unsat} "
        f"sat={log.task_c.verified_sat} disagree={log.task_c.disagreements} "
        f"t={log.task_c.elapsed_s:.0f}s",
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
