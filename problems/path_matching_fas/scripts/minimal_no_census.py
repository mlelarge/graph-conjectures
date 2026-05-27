"""Minimal-NO obstruction catalogue for Path-FAS (Aboulker 4.4).

For each minimal LFO-NO tournament (the smallest LFO-NO instances after
hereditary closure) we collect:

  1. Score sequence and score windows.
  2. Forced-backedge graph H (vertex degrees, cycle status, linear-forest
     status).
  3. Flexible-pair overlap graph G_flex (edge count, max clique).
  4. Interaction graph J = H ∪ G_flex (treewidth: exact for n ≤ 9,
     min-fill-in upper bound otherwise; also clique lower bound).
  5. Modular decomposition (strong modules and prime status).
  6. NO obstruction classification:
        - forced_degree     (some vertex in H has undirected degree ≥ 3)
        - forced_cycle      (H contains an undirected cycle)
        - hall_failure      (score windows fail Hall's condition globally)
        - bounded_width_no  (J has small treewidth but instance is NO;
                             indicates Track A DP needs sharper state)
        - large_width_no    (J has large treewidth; substrate for Track B
                             NP-hardness gadgets)
        - unclassified      (none of the above applied; rare)

The script writes
  data/minimal_no_obstruction_catalogue_n{N}.json

with both a per-instance catalogue and an aggregate summary.

Reuses:
  - decide_path_fas_bruteforce  (path_fas.py)
  - interaction_graph build helpers
  - tournament_canonical.string_to_matrix (for n=9 rep keys)

References:
  - Modular decomposition: Cunningham (1972), DOI 10.1137/0501067.
  - Treewidth heuristic: NetworkX
    networkx.algorithms.approximation.treewidth_min_fill_in.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import Counter, defaultdict
from typing import Iterable, Sequence

import networkx as nx

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from interaction_graph import (  # noqa: E402
    build_H_and_Gflex,
    build_J,
    exact_treewidth,
    hall_feasible,
    indegrees,
    is_H_linear_forest,
    score_windows,
    treewidth_upper_bound,
)
from path_fas import decide_path_fas_bruteforce  # noqa: E402
from tournament_canonical import string_to_matrix  # noqa: E402


Matrix = Sequence[Sequence[int]]


# ---------------------------------------------------------------------------
# Modular decomposition (small-n, enumerative).
# ---------------------------------------------------------------------------

def _is_module(T: Matrix, S: set[int]) -> bool:
    n = len(T)
    for w in range(n):
        if w in S:
            continue
        vals = [T[w][x] for x in S]
        if not (all(vals) or not any(vals)):
            return False
    return True


def all_modules(T: Matrix) -> list[frozenset[int]]:
    """All non-trivial modules (sizes 2..n-1)."""
    n = len(T)
    import itertools
    out: list[frozenset[int]] = []
    for r in range(2, n):
        for sub in itertools.combinations(range(n), r):
            if _is_module(T, set(sub)):
                out.append(frozenset(sub))
    return out


def strong_modules(T: Matrix) -> list[frozenset[int]]:
    mods = all_modules(T)
    strong: list[frozenset[int]] = []
    for M in mods:
        ok = True
        for N in mods:
            if M == N:
                continue
            if M & N and not (M <= N or N <= M):
                ok = False
                break
        if ok:
            strong.append(M)
    return strong


def modular_summary(T: Matrix) -> dict:
    n = len(T)
    mods = all_modules(T)
    strong = strong_modules(T)
    return {
        "n": n,
        "nontrivial_module_count": len(mods),
        "strong_module_count": len(strong),
        "is_prime": len(mods) == 0,
        "strong_modules": sorted([sorted(M) for M in strong]),
        "max_strong_module_size": max((len(M) for M in strong), default=0),
    }


# ---------------------------------------------------------------------------
# Obstruction classification.
# ---------------------------------------------------------------------------

def classify_obstruction(
    T: Matrix,
    H: nx.DiGraph,
    Gflex: nx.Graph,
    J: nx.Graph,
    tw_J: int,
    hall_ok: bool,
    bounded_tw_threshold: int = 4,
) -> dict:
    """Pick a primary obstruction label and record all triggered signals.

    Threshold rationale: max LFO back-degree is 2, so the score-window
    DP frontier already needs ~ Theta(B(k)) states; a J-width <= 4 is
    "small" by that standard.  Width above 4 is "large".  The caller
    can tune the threshold.
    """
    signals: list[str] = []

    H_und = H.to_undirected()
    max_und = max((H_und.degree(v) for v in H_und.nodes()), default=0)
    H_has_cycle = (H_und.number_of_edges() > 0
                   and not nx.is_forest(H_und))

    if max_und >= 3:
        signals.append("forced_degree")
    if H_has_cycle:
        signals.append("forced_cycle")
    if not hall_ok:
        signals.append("hall_failure")
    if tw_J <= bounded_tw_threshold:
        signals.append("bounded_width_no")
    else:
        signals.append("large_width_no")

    # Primary label = first hard combinatorial signal, else width verdict.
    if "forced_degree" in signals:
        primary = "forced_degree"
    elif "forced_cycle" in signals:
        primary = "forced_cycle"
    elif "hall_failure" in signals:
        primary = "hall_failure"
    elif "bounded_width_no" in signals:
        primary = "bounded_width_no"
    elif "large_width_no" in signals:
        primary = "large_width_no"
    else:
        primary = "unclassified"

    return {
        "signals": signals,
        "primary": primary,
        "H_max_und_degree": max_und,
        "H_has_cycle": H_has_cycle,
    }


# ---------------------------------------------------------------------------
# Per-instance record.
# ---------------------------------------------------------------------------

def analyze_one(
    T: Matrix,
    name: str,
    *,
    radius: int = 2,
    do_exact_tw: bool = True,
    do_modular: bool = True,
    bounded_tw_threshold: int = 4,
) -> dict:
    n = len(T)
    H, Gflex = build_H_and_Gflex(T, radius)
    J = build_J(T, radius)

    # cliques in G_flex (interval graph has polynomial maximum clique
    # equal to max number of windows overlapping at one position).
    Gflex_omega = (max((len(c) for c in nx.find_cliques(Gflex)), default=0)
                   if Gflex.number_of_edges() else
                   (1 if Gflex.number_of_nodes() else 0))
    J_omega = (max((len(c) for c in nx.find_cliques(J)), default=0)
               if J.number_of_edges() else
               (1 if J.number_of_nodes() else 0))

    tw_ub = treewidth_upper_bound(J)
    tw_exact: int | None = None
    if do_exact_tw and n <= 11:
        try:
            tw_exact = exact_treewidth(J)
        except Exception:
            tw_exact = None
    tw_for_classifier = tw_exact if tw_exact is not None else tw_ub
    tw_kind = "exact" if tw_exact is not None else "min_fill_upper"

    hall_ok = hall_feasible(T, radius)

    H_und = H.to_undirected()
    H_info = {
        "n_edges": H.number_of_edges(),
        "edges": sorted([list(e) for e in H.edges()]),
        "max_outdeg": max((H.out_degree(v) for v in H.nodes()), default=0),
        "max_indeg": max((H.in_degree(v) for v in H.nodes()), default=0),
        "max_und_degree": max((H_und.degree(v) for v in H_und.nodes()), default=0),
        "is_linear_forest": is_H_linear_forest(H),
        "has_und_cycle": (H_und.number_of_edges() > 0
                          and not nx.is_forest(H_und)),
    }

    Gflex_info = {
        "n_edges": Gflex.number_of_edges(),
        "edges": [list(e) for e in Gflex.edges()],
        "max_clique": Gflex_omega,
    }

    J_info = {
        "n_edges": J.number_of_edges(),
        "treewidth_exact": tw_exact,
        "treewidth_min_fill_upper": tw_ub,
        "treewidth_kind_used": tw_kind,
        "treewidth_for_classifier": tw_for_classifier,
        "max_clique": J_omega,
        "tw_lower_bound": max(0, J_omega - 1),
    }

    obstruction = classify_obstruction(
        T, H, Gflex, J, tw_for_classifier, hall_ok,
        bounded_tw_threshold=bounded_tw_threshold,
    )

    rec = {
        "name": name,
        "n": n,
        "T": [list(row) for row in T],
        "score_sequence": sorted(sum(row) for row in T),
        "indegrees": indegrees(T),
        "windows": score_windows(T, radius),
        "hall_ok": hall_ok,
        "H": H_info,
        "G_flex": Gflex_info,
        "J": J_info,
        "obstruction": obstruction,
    }
    if do_modular:
        rec["modular"] = modular_summary(T)
    return rec


# ---------------------------------------------------------------------------
# Loaders.
# ---------------------------------------------------------------------------

def load_n7_minimal_NOs(path: str) -> Iterable[tuple[str, Matrix, dict]]:
    """All n=7 LFO-NO records are minimal (verified in
    lfo_combinatorial_no_analysis.json: all_vertex_minimal=True)."""
    with open(path) as fh:
        data = json.load(fh)
    for bucket in data["buckets"]:
        if bucket["summary"]["lfo_no"] == 0:
            continue
        for rec in bucket["records"]:
            if rec.get("has_lfo") is False:
                meta = {"no_kind": rec.get("no_kind") or "combinatorial",
                        "iso_index": rec["iso_index"]}
                yield f"7#{rec['iso_index']}", rec["T"], meta


def load_n8_minimal_NOs(extend_path: str, minimal8_path: str
                        ) -> Iterable[tuple[str, Matrix, dict]]:
    """Minimal n=8 NOs = those NOs containing no induced n=7 NO."""
    with open(extend_path) as fh:
        ext = json.load(fh)
    iso_to_T = {r["iso_index"]: r["T"] for r in ext["no_records"]}
    iso_to_kind = {r["iso_index"]: r.get("no_kind") for r in ext["no_records"]}
    with open(minimal8_path) as fh:
        m8 = json.load(fh)
    for r in m8["records"]:
        T = iso_to_T.get(r["iso_index"])
        if T is not None:
            meta = {"no_kind": iso_to_kind.get(r["iso_index"]),
                    "iso_index": r["iso_index"]}
            yield f"8#{r['iso_index']}", T, meta


def load_n9_minimal_NOs(reps_path: str, census_path: str
                        ) -> Iterable[tuple[str, Matrix, dict]]:
    """Minimal n=9 NOs.

    `lfo_reps_n9.jsonl` lists canonical keys indexed by `iso_index`.
    `lfo_census_n9_results.jsonl` reports has_lfo and contains_lower_no.
    Minimal NO = has_lfo False AND contains_lower_no False.
    """
    keys: list[str] = []
    with open(reps_path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                keys.append(json.loads(line)["key"])
    with open(census_path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if r["has_lfo"] or r["contains_lower_no"]:
                continue
            key = keys[r["iso_index"]]
            meta = {"no_kind": r.get("no_kind"), "iso_index": r["iso_index"]}
            yield f"9#{r['iso_index']}", string_to_matrix(key), meta


# ---------------------------------------------------------------------------
# Aggregator.
# ---------------------------------------------------------------------------

def aggregate(records: list[dict]) -> dict:
    primary = Counter(r["obstruction"]["primary"] for r in records)
    kind = Counter(r.get("no_kind") for r in records)
    signal_counter: Counter[str] = Counter()
    for r in records:
        for s in r["obstruction"]["signals"]:
            signal_counter[s] += 1
    tw_dist = Counter(r["J"]["treewidth_for_classifier"] for r in records)
    omega_dist = Counter(r["J"]["max_clique"] for r in records)
    h_deg_dist = Counter(r["H"]["max_und_degree"] for r in records)
    n_edges_dist = Counter(r["J"]["n_edges"] for r in records)
    hall_fail = sum(1 for r in records if not r["hall_ok"])
    h_cycle = sum(1 for r in records if r["H"]["has_und_cycle"])
    prime_count = sum(1 for r in records if r.get("modular", {}).get("is_prime"))
    score_seq_hist = Counter(tuple(r["score_sequence"]) for r in records)
    # Bounded-width example pick
    bounded = sorted(
        (r for r in records if r["obstruction"]["primary"] == "bounded_width_no"),
        key=lambda r: (r["J"]["treewidth_for_classifier"], r["J"]["n_edges"]),
    )
    large = sorted(
        (r for r in records if r["obstruction"]["primary"] == "large_width_no"),
        key=lambda r: -r["J"]["treewidth_for_classifier"],
    )
    return {
        "total": len(records),
        "no_kind_hist": dict(sorted((str(k), v) for k, v in kind.items())),
        "primary_obstruction_hist": dict(sorted(primary.items())),
        "signal_hist": dict(sorted(signal_counter.items())),
        "J_treewidth_hist": dict(sorted(tw_dist.items())),
        "J_max_clique_hist": dict(sorted(omega_dist.items())),
        "H_max_und_degree_hist": dict(sorted(h_deg_dist.items())),
        "J_n_edges_hist": dict(sorted(n_edges_dist.items())),
        "hall_failure_count": hall_fail,
        "H_with_und_cycle_count": h_cycle,
        "prime_modular_count": prime_count,
        "score_sequence_hist_top10": [
            [list(s), c] for s, c in score_seq_hist.most_common(10)
        ],
        "first_bounded_width_no_example": bounded[0]["name"] if bounded else None,
        "first_large_width_no_example": large[0]["name"] if large else None,
    }


# ---------------------------------------------------------------------------
# CLI.
# ---------------------------------------------------------------------------

def main() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.abspath(os.path.join(here, "..", "data"))

    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, required=True, choices=[7, 8, 9])
    parser.add_argument("--out", default=None)
    parser.add_argument("--limit", type=int, default=None,
                        help="Process at most this many instances.")
    parser.add_argument("--bounded-tw", type=int, default=4,
                        help="Threshold for 'bounded-width' label.")
    parser.add_argument("--no-exact-tw", action="store_true",
                        help="Skip exact treewidth (use min-fill only).")
    parser.add_argument("--no-modular", action="store_true",
                        help="Skip modular decomposition computation.")
    parser.add_argument("--progress", type=int, default=25)
    args = parser.parse_args()

    if args.n == 7:
        loader = load_n7_minimal_NOs(
            os.path.join(data_dir, "lfo_full_n7.json"))
    elif args.n == 8:
        loader = load_n8_minimal_NOs(
            os.path.join(data_dir, "lfo_extend_census_n8.json"),
            os.path.join(data_dir, "lfo_minimal8_analysis.json"),
        )
    else:
        loader = load_n9_minimal_NOs(
            os.path.join(data_dir, "lfo_reps_n9.jsonl"),
            os.path.join(data_dir, "lfo_census_n9_results.jsonl"),
        )

    out_path = (args.out or
                os.path.join(data_dir,
                             f"minimal_no_obstruction_catalogue_n{args.n}.json"))

    t0 = time.time()
    records: list[dict] = []
    iterator = enumerate(loader, start=1)
    for i, (name, T, meta) in iterator:
        if args.limit is not None and i > args.limit:
            break
        rec = analyze_one(
            T, name=name,
            do_exact_tw=not args.no_exact_tw,
            do_modular=not args.no_modular,
            bounded_tw_threshold=args.bounded_tw,
        )
        rec["no_kind"] = meta.get("no_kind")
        records.append(rec)
        if args.progress and i % args.progress == 0:
            print(f"  analyzed {i} ({round(time.time() - t0, 1)}s) "
                  f"last={name}", flush=True)

    summary = aggregate(records)
    summary["input_n"] = args.n
    summary["bounded_tw_threshold"] = args.bounded_tw
    summary["seconds"] = round(time.time() - t0, 2)

    payload = {"summary": summary, "records": records}
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w") as fh:
        json.dump(payload, fh, indent=2)
    print(json.dumps(summary, indent=2))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
