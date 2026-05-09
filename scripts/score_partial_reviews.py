#!/usr/bin/env python3
"""Score partial review records for proof/disproof triage.

The scores are deliberately heuristic. They are meant to help sort a reading
queue, not to predict mathematical truth.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path


IMPORTANCE_DIFFICULTY = {
    "Low": 2,
    "Medium": 3,
    "High": 4,
    "Outstanding": 5,
}

CONFIDENCE_RANK = {
    "high": 3,
    "medium": 2,
    "low": 1,
}

BIG_PROBLEM_TERMS = (
    "tutte",
    "cycle double cover",
    "berge-fulkerson",
    "erdos-hajnal",
    "erdos hajnal",
    "sidorenko",
    "reconstruction conjecture",
    "barnette",
    "hadwiger",
    "caccetta",
    "zarankiewicz",
    "hill's conjecture",
    "shannon capacity",
    "major open",
    "long-standing",
    "longstanding",
    "famous",
    "equivalent to the cycle double cover",
)

CLOSE_PROOF_TERMS = (
    "all sufficiently large",
    "all cases except",
    "single base case",
    "reduced to the single",
    "finite cases",
    "small-to-moderate",
    "narrowed to",
    "exact value",
    "computational verification",
    "verified computationally",
    "at most 28 vertices",
)

POSITIVE_PROGRESS_TERMS = (
    "proved for",
    "confirmed for",
    "verified for",
    "established for",
    "resolved for",
    "shown for",
    "extended to",
    "asymptotically",
    "upper bound",
    "lower bound",
    "special classes",
    "restricted classes",
    "partial results",
    "partial progress",
)

NEGATIVE_PROGRESS_TERMS = (
    "counterexample",
    "disproved",
    "fails",
    "does not hold",
    "shown to fail",
    "false",
    "hardness",
    "inapproximability",
    "barrier",
    "cannot be",
)

EXACT_OR_SEARCH_TERMS = (
    "crossing number",
    "shannon capacity",
    "spectrum",
    "obstacle number",
    "smallest",
    "largest",
    "exact value",
    "algorithm",
    "complexity",
)

MANUAL_OVERRIDES: dict[str, dict[str, object]] = {
    # Landmarks: lots of progress, but not good short-term targets.
    "5_flow_conjecture": {"proof_score": 2, "disproof_score": 2, "difficulty": 5},
    "cycle_double_cover_conjecture": {"proof_score": 2, "disproof_score": 2, "difficulty": 5},
    "the_berge_fulkerson_conjecture": {"proof_score": 2, "disproof_score": 2, "difficulty": 5},
    "sidorenkos_conjecture": {"proof_score": 2, "disproof_score": 2, "difficulty": 5},
    "the_erdos_hajnal_conjecture": {"proof_score": 3, "disproof_score": 2, "difficulty": 5},
    "caccetta_haggkvist_conjecture": {"proof_score": 2, "disproof_score": 2, "difficulty": 5},
    "reconstruction_conjecture": {"proof_score": 2, "disproof_score": 2, "difficulty": 5},
    "barnettes_conjecture": {"proof_score": 3, "disproof_score": 2, "difficulty": 5},
    "shannon_capacity_of_the_seven_cycle": {
        "proof_score": 2,
        "disproof_score": 3,
        "difficulty": 5,
    },
    # Cases with an especially narrow remaining gap.
    "chromatic_number_of_frac_3_3_power_of_graph": {
        "proof_score": 5,
        "disproof_score": 2,
        "difficulty": 3,
    },
    "splitting_a_digraph_with_minimum_outdegree_constraints": {
        "proof_score": 4,
        "disproof_score": 2,
        "difficulty": 4,
    },
    "choice_number_of_k_chromatic_graphs_of_bounded_order": {
        "proof_score": 4,
        "disproof_score": 2,
        "difficulty": 3,
    },
    "3_edge_coloring_conjecture": {"proof_score": 4, "disproof_score": 2, "difficulty": 3},
    "a_gold_grabbing_game": {"proof_score": 4, "disproof_score": 2, "difficulty": 2},
    "chromatic_number_of_random_lifts_of_complete_graphs": {
        "proof_score": 4,
        "disproof_score": 2,
        "difficulty": 3,
    },
    "behzads_conjecture": {"proof_score": 3, "disproof_score": 1, "difficulty": 4},
    "does_the_symmetric_chromatic_function_distinguish_trees": {
        "proof_score": 5,
        "disproof_score": 2,
        "difficulty": 3,
    },
    "3_decomposition_conjecture": {"proof_score": 5, "disproof_score": 1, "difficulty": 3},
    "unit_vector_flows": {"proof_score": 3, "disproof_score": 4, "difficulty": 3},
    "the_crossing_number_of_the_hypercube": {
        "proof_score": 2,
        "disproof_score": 4,
        "difficulty": 4,
    },
    "weak_pentagon_problem": {
        "proof_score": 3,
        "disproof_score": 2,
        "difficulty": 4,
        "open_check": "yes: full cubic triangle-free case remains open",
    },
}

COUNTEREXAMPLE_TARGETS = [
    (
        "directed_cycle_of_length_twice_the_minimum_outdegree",
        "Best clean finite counterexample search: encode an oriented graph with minimum outdegree $k$ and no directed path of length $2k$.",
    ),
    (
        "pebbling_a_cartesian_product",
        "Concrete candidate-driven search around Graham's conjecture, though exact pebbling computations can get expensive.",
    ),
    (
        "earth_moon_problem",
        "Computationally natural: search for a 10-chromatic biplanar graph or eliminate promising candidate families.",
    ),
    (
        "unit_vector_flows",
        "A related conjecture was recently disproved, but the remaining flow conjecture is more geometric and less directly searchable.",
    ),
]


@dataclass(frozen=True)
class ScoredProblem:
    slug: str
    title: str
    url: str
    category: str
    importance: str
    confidence: str
    reviewed_at: str
    citation_count: int
    open_check: str
    proof_score: int
    disproof_score: int
    difficulty: int
    lean: str
    note: str
    summary: str


def clamp(value: int, low: int = 1, high: int = 5) -> int:
    return max(low, min(high, value))


def has_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def sentence(text: str, limit: int = 220) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return ""
    first = re.split(r"(?<=[.!?])\s+", text, maxsplit=1)[0]
    if len(first) <= limit:
        return first
    return first[: limit - 1].rstrip() + "…"


def open_check_for(summary: str) -> str:
    low = summary.lower()
    if "low confidence" in low:
        return "yes, but low-confidence review"
    if ("disproved" in low or "counterexample" in low or "fails" in low) and "open" in low:
        return "mixed: related claim/variant false; residual problem open"
    if ("resolved" in low or "proved" in low) and "remain" in low and "open" in low:
        return "mixed: important cases solved; full problem open"
    if "remains open" in low or "still open" in low or "unresolved" in low:
        return "yes: full/general case open"
    return "yes: classified partial, so a residual original question is open"


def score_record(problem: dict, review: dict) -> ScoredProblem:
    slug = review["slug"]
    summary = re.sub(r"\s+", " ", review.get("summary", "")).strip()
    text = f"{problem.get('title', '')} {summary}".lower()
    confidence = review.get("confidence", "")
    citation_count = len(review.get("since_posted") or [])
    importance = problem.get("importance", {}).get("label", "Medium")

    proof_score = 2
    if citation_count >= 3:
        proof_score += 1
    if has_any(text, POSITIVE_PROGRESS_TERMS):
        proof_score += 1
    if has_any(text, CLOSE_PROOF_TERMS):
        proof_score += 1
    if importance == "Outstanding":
        proof_score -= 1
    if has_any(text, BIG_PROBLEM_TERMS):
        proof_score -= 1
    if confidence == "low":
        proof_score -= 1
    proof_score = clamp(proof_score)

    disproof_score = 1
    if has_any(text, NEGATIVE_PROGRESS_TERMS):
        disproof_score += 2
    if has_any(text, EXACT_OR_SEARCH_TERMS):
        disproof_score += 1
    if "lower bound" in text or "hardness" in text or "inapproximability" in text:
        disproof_score += 1
    if has_any(text, POSITIVE_PROGRESS_TERMS) and not has_any(text, NEGATIVE_PROGRESS_TERMS):
        disproof_score -= 1
    disproof_score = clamp(disproof_score)

    difficulty = IMPORTANCE_DIFFICULTY.get(importance, 3)
    if has_any(text, BIG_PROBLEM_TERMS):
        difficulty += 1
    if has_any(text, CLOSE_PROOF_TERMS):
        difficulty -= 1
    if proof_score >= 4 and importance != "Outstanding":
        difficulty -= 1
    if confidence == "low":
        difficulty += 1
    min_difficulty = {"Low": 1, "Medium": 2, "High": 3, "Outstanding": 5}.get(importance, 2)
    difficulty = max(difficulty, min_difficulty)
    difficulty = clamp(difficulty)

    open_check = open_check_for(summary)

    override = MANUAL_OVERRIDES.get(slug, {})
    proof_score = int(override.get("proof_score", proof_score))
    disproof_score = int(override.get("disproof_score", disproof_score))
    difficulty = int(override.get("difficulty", difficulty))
    open_check = str(override.get("open_check", open_check))

    if proof_score >= disproof_score + 2:
        lean = "prove"
    elif disproof_score >= proof_score + 2:
        lean = "disprove"
    else:
        lean = "balanced"

    category = " > ".join(s["label"] for s in problem.get("subject_path", []))
    return ScoredProblem(
        slug=slug,
        title=problem.get("title", slug),
        url=problem.get("canonical_url", ""),
        category=category,
        importance=importance,
        confidence=confidence,
        reviewed_at=review.get("reviewed_at", ""),
        citation_count=citation_count,
        open_check=open_check,
        proof_score=proof_score,
        disproof_score=disproof_score,
        difficulty=difficulty,
        lean=lean,
        note=sentence(summary),
        summary=summary,
    )


def load_scores(data_dir: Path) -> list[ScoredProblem]:
    problems = json.loads((data_dir / "problems.json").read_text(encoding="utf-8"))
    by_slug = {p["slug"]: p for p in problems}
    rows: list[ScoredProblem] = []
    for path in sorted((data_dir / "reviews").glob("*.json")):
        if path.name.endswith(".raw.json"):
            continue
        review = json.loads(path.read_text(encoding="utf-8"))
        if review.get("status") != "partial":
            continue
        slug = review.get("slug") or path.stem
        if slug not in by_slug:
            raise KeyError(f"review {path} has unknown slug {slug!r}")
        rows.append(score_record(by_slug[slug], review))
    return sorted(rows, key=lambda r: r.title.lower())


def write_csv(rows: list[ScoredProblem], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "slug",
        "title",
        "url",
        "category",
        "importance",
        "confidence",
        "reviewed_at",
        "citation_count",
        "open_check",
        "lean",
        "proof_score",
        "disproof_score",
        "difficulty",
        "note",
        "summary",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: getattr(row, field) for field in fields})


def md_link(row: ScoredProblem) -> str:
    title = row.title.replace("|", "\\|")
    if row.url:
        return f"[{title}]({row.url})"
    return title


def table(rows: list[ScoredProblem]) -> str:
    lines = [
        "| Problem | Lean | Proof | Disproof | Difficulty | Confidence | Open check | Note |",
        "|---|---:|---:|---:|---:|---|---|---|",
    ]
    for row in rows:
        note = row.note.replace("|", "\\|")
        lines.append(
            "| "
            + " | ".join(
                [
                    md_link(row),
                    row.lean,
                    str(row.proof_score),
                    str(row.disproof_score),
                    str(row.difficulty),
                    row.confidence,
                    row.open_check.replace("|", "\\|"),
                    note,
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def write_markdown(rows: list[ScoredProblem], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    by_confidence: dict[str, int] = {}
    for row in rows:
        by_confidence[row.confidence] = by_confidence.get(row.confidence, 0) + 1
    confidence_summary = ", ".join(
        f"{name}: {by_confidence[name]}" for name in ("high", "medium", "low") if name in by_confidence
    )

    proof_targets = sorted(
        rows,
        key=lambda r: (
            -r.proof_score,
            r.difficulty,
            -CONFIDENCE_RANK.get(r.confidence, 0),
            r.title.lower(),
        ),
    )[:20]
    disproof_targets = sorted(
        rows,
        key=lambda r: (
            -r.disproof_score,
            r.difficulty,
            -CONFIDENCE_RANK.get(r.confidence, 0),
            r.title.lower(),
        ),
    )[:15]
    low_confidence = sorted(
        [r for r in rows if r.confidence != "high"],
        key=lambda r: (CONFIDENCE_RANK.get(r.confidence, 0), r.title.lower()),
    )
    by_slug = {row.slug: row for row in rows}
    counterexample_rows = [
        (idx, by_slug[slug], rationale)
        for idx, (slug, rationale) in enumerate(COUNTEREXAMPLE_TARGETS, start=1)
        if slug in by_slug
    ]
    counterexample_lines = [
        "| Rank | Problem | Proof | Disproof | Difficulty | Rationale |",
        "|---:|---|---:|---:|---:|---|",
    ]
    for idx, row, rationale in counterexample_rows:
        counterexample_lines.append(
            f"| {idx} | {md_link(row)} | {row.proof_score} | {row.disproof_score} | {row.difficulty} | {rationale} |"
        )

    content = f"""# Partial-status problem triage

Generated on {date.today().isoformat()} from `data/reviews/*.json` and `data/problems.json`.

This report selects every review whose `status` is `partial`. In this repository's literature-review taxonomy, `partial` means that meaningful progress is recorded but the original problem, a stated generalization, or a residual component remains open. The open check below is therefore a local check against the dated review record, not a fresh item-by-item web review.

## Scoring rubric

- `Proof`: 1-5 heuristic estimate that a proof route looks currently tractable from the partial results.
- `Disproof`: 1-5 heuristic estimate that a counterexample, negative answer, or refutation route looks currently tractable.
- `Difficulty`: 1-5 estimate of mathematical difficulty, where 5 means landmark/open-problem territory.
- `Lean`: `prove`, `disprove`, or `balanced`, derived from the proof/disproof scores.

Scores are triage labels, not probabilities. They combine OPG importance, review confidence, the amount and type of post-posting progress, and a few manual adjustments for famous landmark problems.

## Summary

- Partial-status problems: {len(rows)}
- Review confidence: {confidence_summary}
- Reviewed dates: {", ".join(sorted({r.reviewed_at for r in rows if r.reviewed_at}))}
- Still open: all {len(rows)} have an open residual question according to their `partial` review status.

## Counterexample-first shortlist

This is the curated ranking to try first if the goal is to disprove something rather than finish a proof.

{chr(10).join(counterexample_lines)}

## Best proof-oriented targets

{table(proof_targets)}

## Best disproof-oriented targets

{table(disproof_targets)}

## Medium/low confidence items to recheck first

{table(low_confidence)}

## Full scored list

{table(rows)}
"""
    path.write_text(content, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    here = Path(__file__).resolve().parent
    project = here.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=project / "data")
    parser.add_argument("--csv-out", type=Path, default=project / "data" / "partial_problem_scores.csv")
    parser.add_argument("--md-out", type=Path, default=project / "PARTIAL_PROBLEM_SCORES.md")
    args = parser.parse_args(argv)

    rows = load_scores(args.data_dir)
    write_csv(rows, args.csv_out)
    write_markdown(rows, args.md_out)
    print(f"scored {len(rows)} partial-status problems")
    print(f"wrote {args.csv_out}")
    print(f"wrote {args.md_out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
