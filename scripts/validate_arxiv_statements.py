#!/usr/bin/env python3
"""Fail when an arXiv state record has an empty or placeholder statement."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


PROJECT = Path(__file__).resolve().parent.parent

PLACEHOLDER_RX = re.compile(
    r"(?is)("
    r"\[(?:full\s+|verbatim\s+)?statement(?:\s+text)?\b|"
    r"\[statement\s+(?:not\s+available|unavailable)\b|"
    r"\[[^\]]*(?:truncated|not\s+captured|not\s+reproduced)[^\]]*\]|"
    r"\[(?:asymptotic\s+)?formula\b|"
    r"\[a\s+bound\s+of\s+order\b"
    r")"
)
TRAILING_CLAUSE_RX = re.compile(r"(?i)\b(?:such that|such):\s*$")


def statement_issue(statement: object) -> str | None:
    if not isinstance(statement, str) or not statement.strip():
        return "empty statement_text"
    if PLACEHOLDER_RX.search(statement):
        return "placeholder or truncated statement_text"
    if TRAILING_CLAUSE_RX.search(statement):
        return "statement_text ends before its conclusion"
    return None


def load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc


def validate(data_dir: Path) -> list[str]:
    errors: list[str] = []

    aggregate_path = data_dir / "arxiv_conjectures.json"
    aggregate = load_json(aggregate_path)
    if not isinstance(aggregate, list):
        errors.append(f"{aggregate_path}: expected a JSON array")
        aggregate = []

    counters: dict[str, int] = {}
    for index, record in enumerate(aggregate):
        if not isinstance(record, dict):
            errors.append(f"{aggregate_path}[{index}]: expected an object")
            continue
        safe_id = record.get("safe_id") or record.get("arxiv_id", "").replace("/", "_")
        paper_index = counters.get(safe_id, 0)
        counters[safe_id] = paper_index + 1
        review_id = f"{safe_id}__{paper_index:02d}"
        if issue := statement_issue(record.get("statement_text")):
            errors.append(f"{aggregate_path}:{review_id}: {issue}")
        for related in record.get("also_stated_in") or []:
            if related.get("arxiv_id") == record.get("arxiv_id"):
                errors.append(f"{aggregate_path}:{review_id}: self-reference in also_stated_in")

    extracted_dir = data_dir / "arxiv_extracted"
    for path in sorted(extracted_dir.glob("*.json")):
        records = load_json(path)
        if not isinstance(records, list):
            errors.append(f"{path}: expected a JSON array")
            continue
        for index, record in enumerate(records):
            if not isinstance(record, dict) or record.get("role") != "states":
                continue
            if issue := statement_issue(record.get("statement_text")):
                label = record.get("title") or f"record {index}"
                errors.append(f"{path}:{label}: {issue}")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=PROJECT / "data")
    args = parser.parse_args(argv)

    try:
        errors = validate(args.data_dir)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1

    if errors:
        print(f"arXiv statement validation failed ({len(errors)} issue(s)):", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("arXiv statement validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
