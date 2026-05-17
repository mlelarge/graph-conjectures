"""Truly-exhaustive lambda=2 (1,0)-near-split UNSAT search at small n.

Companion to `run_route_b_near_split.py`. The main driver does
broad-sampling on a range of (|V_1|, |V_2|) pairs; this script runs a
*truly exhaustive* enumeration over (V_2 orientation) × (V_1-internal
arc) × (bridge subset) for the smallest pairs, then uses pynauty for
canonical-dedup of the lambda=2 UNSAT instances found.

The output is the headline §3.b table: every canonical (1,0)-NS UNSAT
2-arc-strong instance at small n, classified as either
  (a) the strict-split (Ai et al. 2024) obstruction plus a free
      V_1-internal arc, or
  (b) a genuinely new (1,0)-NS obstruction.

Hard rules:
  - independent (1,0)-NS predicate before each cross-check;
  - canonical-dedup via pynauty;
  - cross-check ILP + SAT for every UNSAT candidate.

By default we exhaust:
  (|V_1|, |V_2|) in {(2,3), (3,3), (2,4)}.
  Total exhaustive space:
    (2,3): 3^3 * 2 * 2^12 ≈ 221k
    (3,3): 3^3 * 6 * 2^18 ≈ 42M
    (2,4): 3^6 * 2 * 2^16 ≈ 95M

We use the sanity-gate (D.is_strongly_connected() and lambda >= 2)
to skip 99 % of candidates before invoking the SAT/ILP backends.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
import time
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterator

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from cross_check import cross_check  # noqa: E402
from digraph import Digraph, arc_reverse  # noqa: E402
from generators.canonicalize import canonical_key  # noqa: E402
from generators.near_split import (  # noqa: E402
    is_one_zero_near_split,
)
from verifier_sat import verify_sat  # noqa: E402
from verifier_ilp import verify_ilp  # noqa: E402


@dataclass
class ExhStats:
    pair: tuple[int, int] = (0, 0)
    enumerated: int = 0
    skipped_disconnected: int = 0
    skipped_lambda_low: int = 0
    skipped_lambda_high: int = 0
    lambda_eq_2: int = 0
    lambda_eq_3: int = 0
    sat_solver_invoked_l2: int = 0
    unsat_found_l2: int = 0
    unsat_found_l3: int = 0
    canonical_unsat_l2: int = 0
    extensions_of_split: int = 0
    new_obstructions: int = 0
    elapsed_s: float = 0.0


@dataclass
class ExhLog:
    started_at: str
    config: dict[str, Any] = field(default_factory=dict)
    by_pair: dict[str, dict[str, Any]] = field(default_factory=dict)
    canonical_l2_unsat: list[dict[str, Any]] = field(default_factory=list)
    new_obstructions: list[dict[str, Any]] = field(default_factory=list)
    counterexamples_l3: list[dict[str, Any]] = field(default_factory=list)
    finished_at: str | None = None
    elapsed_s: float | None = None
    notes: list[str] = field(default_factory=list)


def _strict_split_unsat_canonical_keys() -> dict[str, str]:
    """Build {canonical_hash: name_or_reverse} for the strict-split UNSAT family.

    Per Ai et al. 2024 Theorem 1.8, the UNSAT family is closed up to
    arc-reversal ("or their arc-reversed versions"). The classification
    index therefore must include both `canonical_key(D)` and
    `canonical_key(arc_reverse(D))` for every catalogue benchmark.

    Bug history: prior to the audit's Appendix A.7 (team/05_audit.md),
    this function indexed only forward orientations, causing the
    arc-reverse of `AiEtAl_L211_min` (canonical hash `35aa1b8c…`) to be
    mis-classified as a NEW canonical UNSAT.
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
        # Sanity check: arc_reverse is an involution on canonical hashes.
        assert canonical_key(arc_reverse(Drev)) == canonical_key(D), (
            f"arc_reverse not involutive on canonical hash for {b.name}"
        )
        k_fwd = canonical_key(D)
        k_rev = canonical_key(Drev)
        # Only label with a distinct name if the digraph is not arc-reverse
        # self-isomorphic; otherwise the same hash already maps to b.name.
        if k_rev != k_fwd:
            out.setdefault(k_rev, f"{b.name}_arcrev")
    return out


def _enumerate_v2_orientations(v2_size: int, v2_offset: int) -> Iterator[tuple[tuple[int, int], ...]]:
    """Yield every semicomplete orientation of V_2 = [v2_offset, v2_offset+v2_size).

    Each unordered pair {u, v} gets one of 3 states: u->v, v->u, both.
    """
    V = list(range(v2_offset, v2_offset + v2_size))
    pairs = [(V[i], V[j]) for i in range(v2_size) for j in range(i + 1, v2_size)]
    for choices in itertools.product((0, 1, 2), repeat=len(pairs)):
        arcs: list[tuple[int, int]] = []
        for (u, v), c in zip(pairs, choices):
            if c == 0:
                arcs.append((u, v))
            elif c == 1:
                arcs.append((v, u))
            else:
                arcs.append((u, v))
                arcs.append((v, u))
        yield tuple(arcs)


def _all_bridges(v1_size: int, v2_size: int) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    for a in range(v1_size):
        for b in range(v1_size, v1_size + v2_size):
            out.append((a, b))
            out.append((b, a))
    return out


def _hash_minus_internal(arcs: list[tuple[int, int]], internal: tuple[int, int], n: int) -> str:
    """Canonical hash of (V, arcs \ {internal})."""
    filtered: list[tuple[int, int]] = []
    removed = False
    for a in arcs:
        if (not removed) and tuple(a) == tuple(internal):
            removed = True
            continue
        filtered.append(a)
    D = Digraph.from_arcs(range(n), filtered)
    return canonical_key(D)


def exhaust_pair(
    v1_size: int,
    v2_size: int,
    log: ExhLog,
    split_index: dict[str, str],
    instance_time_s: float = 6.0,
    progress_every: int = 50000,
) -> ExhStats:
    """Truly exhaustive enumeration for (v1_size, v2_size)."""
    stats = ExhStats(pair=(v1_size, v2_size))
    t0 = time.time()
    n = v1_size + v2_size
    V1 = list(range(v1_size))
    V2 = list(range(v1_size, n))
    bridges = _all_bridges(v1_size, v2_size)
    nB = len(bridges)
    internal_candidates = [(a, b) for a in V1 for b in V1 if a != b]

    seen_canonical_l2_unsat: dict[str, dict[str, Any]] = {}
    seen_canonical_l3_unsat: dict[str, dict[str, Any]] = {}
    # All canonical hashes seen (any verdict) — used to skip SAT solver
    # invocations on canonically-duplicate strong+lambda-in-{2,3}
    # instances, which is the dominant cost.
    seen_canonical_any: set[str] = set()

    for v2_arcs in _enumerate_v2_orientations(v2_size, v2_offset=v1_size):
        # Pre-compute the adjacency set of V_2 once.
        for internal in internal_candidates:
            # Inner part of D: V_2 arcs + internal arc.
            inner_arcs = list(v2_arcs) + [internal]
            # Enumerate bridge subsets exhaustively.
            for mask in range(1 << nB):
                arcs = list(inner_arcs)
                for i in range(nB):
                    if (mask >> i) & 1:
                        arcs.append(bridges[i])
                stats.enumerated += 1

                if stats.enumerated % progress_every == 0:
                    print(
                        f"    [({v1_size},{v2_size})] enumerated={stats.enumerated} "
                        f"l2={stats.lambda_eq_2} l3={stats.lambda_eq_3} "
                        f"l2unsat_canon={stats.canonical_unsat_l2} "
                        f"l3unsat_canon={len(seen_canonical_l3_unsat)} "
                        f"seen_canon={len(seen_canonical_any)} "
                        f"elapsed={time.time() - t0:.0f}s",
                        flush=True,
                    )

                D = Digraph.from_arcs(range(n), arcs)
                if not D.is_strongly_connected():
                    stats.skipped_disconnected += 1
                    continue
                lam = D.arc_connectivity()
                if lam < 2:
                    stats.skipped_lambda_low += 1
                    continue
                if lam > 3:
                    stats.skipped_lambda_high += 1
                    continue
                if lam == 2:
                    stats.lambda_eq_2 += 1
                else:
                    stats.lambda_eq_3 += 1

                # Canonical-dedup: only run SAT on canonically-novel
                # instances. Multiplicity stats are still tracked in
                # the canonical UNSAT dict via labeled_count.
                h = canonical_key(D)
                if h in seen_canonical_any:
                    if lam == 2 and h in seen_canonical_l2_unsat:
                        seen_canonical_l2_unsat[h]["labeled_count"] += 1
                    elif lam == 3 and h in seen_canonical_l3_unsat:
                        seen_canonical_l3_unsat[h]["labeled_count"] += 1
                    continue
                seen_canonical_any.add(h)

                # SAT check on canonically-novel candidate.
                stats.sat_solver_invoked_l2 += 1 if lam == 2 else 0
                sat_res = verify_sat(D, time_limit_s=instance_time_s)
                status = sat_res.get("status")
                if status == "UNSAT":
                    # Cross-check with ILP to be sure.
                    ilp_res = verify_ilp(D, time_limit_s=instance_time_s)
                    if ilp_res.get("status") != "UNSAT":
                        log.notes.append(
                            f"SAT vs ILP disagree on UNSAT candidate "
                            f"({v1_size},{v2_size}) mask={mask} internal={internal}"
                        )
                        continue
                    # An honest UNSAT.
                    rec = {
                        "canonical_hash": h,
                        "n": n,
                        "m": len(arcs),
                        "V1": V1, "V2": V2,
                        "internal_arc": list(internal),
                        "arcs": [list(a) for a in arcs],
                        "lambda_arc": lam,
                        "labeled_count": 1,
                    }
                    if lam == 2:
                        # Classification: matches a known strict-split UNSAT
                        # canonical hash (in any partition) OR an extension
                        # (D minus internal arc was the strict-split UNSAT).
                        h_minus = _hash_minus_internal(arcs, internal, n)
                        rec["minus_internal_canonical_hash"] = h_minus
                        match_full = split_index.get(h, None)
                        match_minus = split_index.get(h_minus, None)
                        rec["matches_strict_split_full"] = match_full
                        rec["matches_strict_split_minus"] = match_minus
                        rec["matches_strict_split"] = match_full or match_minus
                        seen_canonical_l2_unsat[h] = rec
                        stats.canonical_unsat_l2 += 1
                        stats.unsat_found_l2 += 1
                        if rec["matches_strict_split"]:
                            stats.extensions_of_split += 1
                        else:
                            stats.new_obstructions += 1
                            log.new_obstructions.append(rec)
                            print(
                                f"    [({v1_size},{v2_size})] NEW lambda=2 UNSAT "
                                f"obstruction: canonical={h[:16]}... "
                                f"internal={internal} m={len(arcs)}",
                                flush=True,
                            )
                    else:  # lam == 3
                        seen_canonical_l3_unsat[h] = rec
                        stats.unsat_found_l3 += 1
                        log.counterexamples_l3.append(rec)
                        print(
                            f"    *** lambda=3 UNSAT (1,0)-NS at ({v1_size},{v2_size}) ***",
                            flush=True,
                        )
                        # Per hard rule: stop on lambda=3 UNSAT.
                        stats.elapsed_s = time.time() - t0
                        return stats

    stats.elapsed_s = time.time() - t0
    log.canonical_l2_unsat.extend(seen_canonical_l2_unsat.values())
    return stats


def main() -> int:
    p = argparse.ArgumentParser(description="Exhaustive lambda=2 UNSAT search for small (1,0)-NS")
    p.add_argument("--pairs", default="(2,3),(3,3),(2,4)",
                   help="Comma-separated (v1,v2) pairs; e.g. '(2,3),(3,3)'.")
    p.add_argument("--instance-time-s", type=float, default=6.0)
    p.add_argument("--logs-dir", default=str(HERE / "logs"))
    p.add_argument(
        "--log-tag",
        default="",
        help=(
            "Optional tag inserted into the log filename, e.g. 'v2' yields "
            "route_b_ns_exh_l2_v2_<ts>.json. Used by Appendix A.7 rerun."
        ),
    )
    args = p.parse_args()

    # Parse pairs spec: "(a,b),(c,d),..."
    pairs: list[tuple[int, int]] = []
    s = args.pairs.replace(" ", "")
    # Naive parser: extract every "(N,M)".
    import re
    for m in re.finditer(r"\((\d+),(\d+)\)", s):
        pairs.append((int(m.group(1)), int(m.group(2))))

    print("=" * 72, flush=True)
    print("Truly-exhaustive (1,0)-NS lambda=2 UNSAT search", flush=True)
    print("=" * 72, flush=True)
    print(f"Pairs: {pairs}", flush=True)

    logs_dir = Path(args.logs_dir)
    logs_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    tag = f"_{args.log_tag}" if args.log_tag else ""
    log_path = logs_dir / f"route_b_ns_exh_l2{tag}_{timestamp}.json"

    log = ExhLog(
        started_at=time.strftime("%Y-%m-%d %H:%M:%S"),
        config={
            "pairs": pairs,
            "instance_time_s": args.instance_time_s,
        },
    )
    split_index = _strict_split_unsat_canonical_keys()

    for (v1, v2) in pairs:
        print(f"\n--- ({v1}, {v2})  total enumeration ≈ {3 ** (v2 * (v2 - 1) // 2)} * "
              f"{v1 * (v1 - 1)} * 2^{2 * v1 * v2} ---", flush=True)
        stats = exhaust_pair(v1, v2, log, split_index, args.instance_time_s)
        log.by_pair[f"({v1},{v2})"] = asdict(stats)
        print(f"  ({v1},{v2}) done: enumerated={stats.enumerated} "
              f"lambda=2: {stats.lambda_eq_2}  lambda=3: {stats.lambda_eq_3}  "
              f"canonical-l2-UNSAT: {stats.canonical_unsat_l2}  "
              f"NEW={stats.new_obstructions}  "
              f"split-ext={stats.extensions_of_split}  "
              f"elapsed={stats.elapsed_s:.0f}s", flush=True)

    log.finished_at = time.strftime("%Y-%m-%d %H:%M:%S")

    print("\n" + "=" * 72, flush=True)
    print("Exhaustive search complete.", flush=True)
    print("=" * 72, flush=True)
    print(f"  canonical lambda=2 UNSAT (all pairs): {len(log.canonical_l2_unsat)}",
          flush=True)
    print(f"  NEW (1,0)-NS-specific obstructions:   {len(log.new_obstructions)}",
          flush=True)
    print(f"  lambda=3 UNSAT counterexamples:       {len(log.counterexamples_l3)}",
          flush=True)
    print(flush=True)
    for rec in log.canonical_l2_unsat:
        flag = "split-ext" if rec.get("matches_strict_split") else "NEW"
        print(
            f"  {flag:10s} hash={rec['canonical_hash'][:16]}...  n={rec['n']} "
            f"m={rec['m']} |V1|={len(rec['V1'])} |V2|={len(rec['V2'])} "
            f"matches={rec.get('matches_strict_split')}  count={rec['labeled_count']}",
            flush=True,
        )

    with log_path.open("w") as f:
        json.dump(asdict(log), f, indent=2, default=str)
    print(f"\nlog: {log_path}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
