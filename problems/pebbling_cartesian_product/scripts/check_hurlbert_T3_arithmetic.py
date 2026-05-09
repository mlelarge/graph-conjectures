"""Arithmetic-only check of Hurlbert's averaged T_3 matrix for L box L at (v_1, v_1).

This is **NOT** a rational pebbling-number certificate. It is an arithmetic
reproduction of the published bound

    pi(L box L, (v_1, v_1)) <= 108

from G. Hurlbert, *The weight function lemma for graph pebbling*, Journal
of Combinatorial Optimization 34(2) (2017), 343-361 (arXiv:1101.5641),
Theorem 10. The paper's matrix T_3 is **the average of four basic tree
strategies T_1..T_4 shown in Figure 5**. The figures are not transcribed
in this project, so the four supporting trees are not available here.

What this script verifies (sufficient if and only if T_1..T_4 are valid
basic Hurlbert tree strategies whose average is T_3):

1. ``T_3`` has shape ``8 x 8``;
2. ``T_3[0][0] = 0`` (root is at (v_1, v_1));
3. every non-root entry ``T_3[i][j] >= 1`` (dual feasibility for
   alpha = 1 with this single averaged matrix; equivalently, dual
   feasibility for the four-strategy LP with alpha = 1/4 each);
4. the total of non-root entries equals ``107``;
5. the derived bound ``floor(107) + 1 = 108`` matches the paper.

What this script does NOT verify:

- the four underlying strategies T_1..T_4;
- the tree structure of any of them;
- the parent-doubling inequalities in any of them.

To upgrade this arithmetic check to an independent rational certificate
under ``scripts/check_pebbling_weight_certificate.py``, one must
hand-transcribe the four trees from Hurlbert's Figure 5 and feed them as
four separate basic strategies with dual multipliers ``1/4`` each.

Run this script directly to print a structured arithmetic-check report,
or import :func:`check_T3_arithmetic` from a test.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MATRIX_PATH = (
    REPO_ROOT
    / "data"
    / "pebbling_product"
    / "certificates"
    / "Hurlbert_T3_v1v1_arithmetic.json"
)


@dataclass
class T3CheckResult:
    accepted: bool
    matrix_shape: tuple[int, int]
    root_index: tuple[int, int]
    root_weight: int
    minimum_non_root_weight: int
    sum_non_root_weights: int
    derived_bound: int
    failures: list[str]
    label: str = (
        "arithmetic reproduction of Hurlbert 2017 Theorem 10 (108) for "
        "L box L at root (v_1, v_1); NOT an independent certificate"
    )


def check_T3_arithmetic(matrix: list[list[int]]) -> T3CheckResult:
    """Run the five arithmetic checks listed in the module docstring."""
    failures: list[str] = []

    # 1. shape
    if len(matrix) != 8 or any(len(row) != 8 for row in matrix):
        failures.append(
            f"matrix shape is not 8x8 (got {len(matrix)} rows, "
            f"row lengths {[len(r) for r in matrix]})"
        )
        return T3CheckResult(
            accepted=False,
            matrix_shape=(len(matrix), len(matrix[0]) if matrix else 0),
            root_index=(0, 0),
            root_weight=-1,
            minimum_non_root_weight=-1,
            sum_non_root_weights=-1,
            derived_bound=-1,
            failures=failures,
        )

    # All entries must be non-negative integers
    for i, row in enumerate(matrix):
        for j, x in enumerate(row):
            if not isinstance(x, int):
                failures.append(f"T_3[{i}][{j}] = {x!r} is not int")
            elif x < 0:
                failures.append(f"T_3[{i}][{j}] = {x} is negative")
    if failures:
        return T3CheckResult(
            accepted=False,
            matrix_shape=(8, 8),
            root_index=(0, 0),
            root_weight=-1,
            minimum_non_root_weight=-1,
            sum_non_root_weights=-1,
            derived_bound=-1,
            failures=failures,
        )

    # 2. root weight = 0
    root_weight = matrix[0][0]
    if root_weight != 0:
        failures.append(f"T_3[0][0] = {root_weight}, expected 0")

    # 3. non-root entries all >= 1
    minimum = None
    total = 0
    for i in range(8):
        for j in range(8):
            if (i, j) == (0, 0):
                continue
            x = matrix[i][j]
            total += x
            if minimum is None or x < minimum:
                minimum = x
            if x < 1:
                failures.append(
                    f"non-root entry T_3[{i}][{j}] = {x} is < 1"
                )

    # 4. sum of non-root entries = 107
    if total != 107:
        failures.append(f"sum of non-root entries = {total}, expected 107")

    # 5. derived bound = 108
    derived = total + 1
    if derived != 108:
        failures.append(f"derived bound floor({total}) + 1 = {derived}, expected 108")

    return T3CheckResult(
        accepted=not failures,
        matrix_shape=(8, 8),
        root_index=(0, 0),
        root_weight=root_weight,
        minimum_non_root_weight=minimum if minimum is not None else 0,
        sum_non_root_weights=total,
        derived_bound=derived,
        failures=failures,
    )


def load_T3_matrix(path: Path = DEFAULT_MATRIX_PATH) -> list[list[int]]:
    with path.open() as fp:
        payload = json.load(fp)
    return payload["matrix_T3"]


def _cli() -> None:
    import argparse

    ap = argparse.ArgumentParser(
        description=(
            "Arithmetic-only check of Hurlbert's averaged T_3 matrix for "
            "L box L at (v_1, v_1). Not an independent certificate."
        )
    )
    ap.add_argument(
        "matrix",
        nargs="?",
        default=str(DEFAULT_MATRIX_PATH),
        help="path to a JSON file with key 'matrix_T3' (8x8 nonneg ints)",
    )
    args = ap.parse_args()
    m = load_T3_matrix(Path(args.matrix))
    res = check_T3_arithmetic(m)
    verdict = "ACCEPTED" if res.accepted else "REJECTED"
    print(f"{verdict}: {res.label}")
    print(f"matrix shape: {res.matrix_shape}")
    print(f"root index: {res.root_index}, root weight: {res.root_weight}")
    print(f"minimum non-root weight: {res.minimum_non_root_weight}")
    print(f"sum of non-root weights: {res.sum_non_root_weights}")
    print(f"derived bound: floor({res.sum_non_root_weights}) + 1 = {res.derived_bound}")
    if res.failures:
        print("failures:")
        for f in res.failures:
            print(f"  - {f}")


if __name__ == "__main__":
    _cli()
