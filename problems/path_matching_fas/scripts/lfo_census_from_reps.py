"""Resumable exact LFO census from compact representative JSONL files.

For n=9 this uses the exact n=8 NO list as a hereditary filter:
if an n=9 tournament contains an induced n=8 NO subtournament, it is
automatically LFO NO and the expensive backtracker is skipped.

Results are written one JSON object per representative, so interrupted
runs can resume by counting existing output lines.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import Counter
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lfo_backtrack import find_lfo_order  # noqa: E402
from lfo_extend_census import min_fas_dp  # noqa: E402
from tournament_canonical import canonical_key, key_to_string, string_to_matrix  # noqa: E402


def score_sequence(T: Sequence[Sequence[int]]) -> tuple[int, ...]:
    return tuple(sorted(sum(row) for row in T))


def induced(T: Sequence[Sequence[int]], keep: Sequence[int]) -> list[list[int]]:
    return [[int(T[u][v]) for v in keep] for u in keep]


def load_representative_keys(path: str) -> list[str]:
    keys = []
    with open(path) as f:
        for line in f:
            if line.strip():
                keys.append(json.loads(line)["key"])
    return keys


def load_no_keys(path: str) -> tuple[set[str], set[str], set[str]]:
    with open(path) as f:
        data = json.load(f)
    all_no = set()
    size_no = set()
    combinatorial_no = set()
    for record in data["no_records"]:
        key = key_to_string(canonical_key(record["T"]))
        all_no.add(key)
        if record["no_kind"] == "size":
            size_no.add(key)
        elif record["no_kind"] == "combinatorial":
            combinatorial_no.add(key)
    return all_no, size_no, combinatorial_no


def induced_no_hits(
    T: Sequence[Sequence[int]],
    lower_no: set[str],
    lower_size: set[str],
    lower_combinatorial: set[str],
) -> dict:
    n = len(T)
    hits = []
    for deleted in range(n):
        keep = [v for v in range(n) if v != deleted]
        key = key_to_string(canonical_key(induced(T, keep)))
        if key not in lower_no:
            continue
        if key in lower_size:
            kind = "size"
        elif key in lower_combinatorial:
            kind = "combinatorial"
        else:
            kind = "unknown"
        hits.append({"deleted_vertex": deleted, "kind": kind})
    return {
        "contains_lower_no": bool(hits),
        "hit_count": len(hits),
        "hit_kind_hist": dict(sorted(Counter(h["kind"] for h in hits).items())),
        "first_hits": hits[:10],
    }


def count_existing_lines(path: str) -> int:
    if not os.path.exists(path):
        return 0
    with open(path) as f:
        return sum(1 for line in f if line.strip())


def summarize_results(path: str) -> dict:
    counters: Counter[str] = Counter()
    score_no_hist: Counter[str] = Counter()
    score_yes_hist: Counter[str] = Counter()
    min_fas_hist: Counter[int] = Counter()
    search_nodes = 0
    searched = 0

    if not os.path.exists(path):
        return {}

    with open(path) as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            counters["processed"] += 1
            if r["has_lfo"]:
                counters["lfo_yes"] += 1
                score_yes_hist[str(tuple(r["score_sequence"]))] += 1
            else:
                counters["lfo_no"] += 1
                counters[f"{r['no_kind']}_no"] += 1
                score_no_hist[str(tuple(r["score_sequence"]))] += 1
                if r["contains_lower_no"]:
                    counters["no_contains_lower_no"] += 1
                else:
                    counters["minimal_no"] += 1
            min_fas_hist[r["min_fas"]] += 1
            if r.get("searched"):
                searched += 1
                search_nodes += r.get("search_nodes", 0)

    out = dict(sorted(counters.items()))
    out["searched_count"] = searched
    out["avg_search_nodes"] = round(search_nodes / searched, 2) if searched else 0
    out["min_fas_hist"] = dict(sorted(min_fas_hist.items()))
    out["score_no_hist"] = dict(sorted(score_no_hist.items()))
    out["score_yes_hist"] = dict(sorted(score_yes_hist.items()))
    return out


def write_summary(path: str, summary: dict) -> None:
    with open(path, "w") as f:
        json.dump(summary, f, indent=2)


def main() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.abspath(os.path.join(here, "..", "data"))
    default_reps = os.path.join(data_dir, "lfo_reps_n9.jsonl")
    default_lower = os.path.join(data_dir, "lfo_extend_census_n8.json")
    default_out = os.path.join(data_dir, "lfo_census_n9_results.jsonl")

    p = argparse.ArgumentParser()
    p.add_argument("--reps", default=default_reps)
    p.add_argument("--lower-census", default=default_lower)
    p.add_argument("--out", default=default_out)
    p.add_argument("--summary-out", default=None)
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--progress", type=int, default=1000)
    p.add_argument("--restart", action="store_true")
    args = p.parse_args()

    summary_out = args.summary_out or args.out.replace(".jsonl", "_summary.json")
    if args.restart and os.path.exists(args.out):
        os.remove(args.out)

    keys = load_representative_keys(args.reps)
    total = len(keys) if args.limit is None else min(len(keys), args.limit)
    start = count_existing_lines(args.out)
    if start >= total:
        summary = {
            "representatives": len(keys),
            "target": total,
            "complete": start >= len(keys),
            **summarize_results(args.out),
        }
        write_summary(summary_out, summary)
        print(json.dumps(summary, indent=2))
        return

    lower_no, lower_size, lower_combinatorial = load_no_keys(args.lower_census)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)

    t0 = time.time()
    mode = "a" if start else "w"
    with open(args.out, mode) as f:
        for idx in range(start, total):
            T = string_to_matrix(keys[idx])
            min_fas = min_fas_dp(T)
            hit = induced_no_hits(T, lower_no, lower_size, lower_combinatorial)
            search = None
            if hit["contains_lower_no"]:
                has_lfo = False
                searched = False
            else:
                search = find_lfo_order(T)
                has_lfo = search["found"]
                searched = True

            record = {
                "iso_index": idx,
                "score_sequence": list(score_sequence(T)),
                "min_fas": min_fas,
                "has_lfo": has_lfo,
                "no_kind": (
                    None if has_lfo else
                    "size" if min_fas > len(T) - 1 else
                    "combinatorial"
                ),
                "contains_lower_no": hit["contains_lower_no"],
                "lower_hit_count": hit["hit_count"],
                "lower_hit_kind_hist": hit["hit_kind_hist"],
                "searched": searched,
                "search_nodes": search["nodes"] if search else 0,
                "search_pruned_degree": search["pruned_degree"] if search else 0,
                "search_pruned_cycle": search["pruned_cycle"] if search else 0,
            }
            f.write(json.dumps(record, separators=(",", ":")))
            f.write("\n")

            done = idx + 1
            if args.progress and done % args.progress == 0:
                f.flush()
                elapsed = round(time.time() - t0, 1)
                partial = summarize_results(args.out)
                summary = {
                    "representatives": len(keys),
                    "target": total,
                    "processed_this_run": done - start,
                    "elapsed_this_run": elapsed,
                    "complete": done >= len(keys),
                    **partial,
                }
                write_summary(summary_out, summary)
                print(f"processed {done}/{total}; "
                      f"YES={summary.get('lfo_yes', 0)} "
                      f"NO={summary.get('lfo_no', 0)} "
                      f"minimalNO={summary.get('minimal_no', 0)} "
                      f"searched={summary.get('searched_count', 0)} "
                      f"elapsed={elapsed}s",
                      flush=True)

    summary = {
        "representatives": len(keys),
        "target": total,
        "processed_this_run": total - start,
        "elapsed_this_run": round(time.time() - t0, 2),
        "complete": total >= len(keys),
        **summarize_results(args.out),
    }
    write_summary(summary_out, summary)
    print(json.dumps(summary, indent=2))
    print(f"wrote {args.out}")
    print(f"wrote {summary_out}")


if __name__ == "__main__":
    main()
