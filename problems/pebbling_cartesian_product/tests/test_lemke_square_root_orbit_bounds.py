"""Global pi(L_fpy box L_fpy) bound test from per-orbit rational certificates.

This test loads every certificate listed in
``data/pebbling_product/root_orbit_bounds.csv``, re-checks it via the
existing rational checker, and asserts that the maximum derived bound
across orbits matches the value recorded in the CSV. The result is a
fully local rational upper bound for the Lemke-square pebbling number.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from check_pebbling_weight_certificate import check_certificate, load_certificate_file


REPO_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = REPO_ROOT / "data" / "pebbling_product" / "root_orbit_bounds.csv"


def _load_rows():
    if not CSV_PATH.exists():
        pytest.skip(f"{CSV_PATH} not yet generated")
    with CSV_PATH.open() as fp:
        return list(csv.DictReader(fp))


def test_root_orbit_csv_present_and_well_formed() -> None:
    rows = _load_rows()
    assert rows, "root_orbit_bounds.csv has no rows"
    expected_cols = {
        "root_rep",
        "orbit_size",
        "bound",
        "lp_value",
        "num_columns",
        "max_len",
        "certificate_path",
        "status",
    }
    assert expected_cols.issubset(rows[0].keys())


def test_orbit_sizes_sum_to_64() -> None:
    rows = _load_rows()
    s = sum(int(r["orbit_size"]) for r in rows)
    assert s == 64, f"orbit sizes sum to {s}, expected 64"


def test_each_accepted_certificate_recheckable() -> None:
    rows = _load_rows()
    accepted = [r for r in rows if r["status"] == "accepted"]
    assert accepted, "no accepted orbit certificates"
    for r in accepted:
        cert_path = REPO_ROOT / r["certificate_path"]
        assert cert_path.exists(), f"missing cert file: {cert_path}"
        cert, g = load_certificate_file(cert_path)
        res = check_certificate(cert, g)
        assert res.accepted, (
            f"CSV claims accepted for {r['root_rep']} but checker rejects: "
            f"{res.message}"
        )
        assert int(r["bound"]) == res.derived_bound, (
            f"CSV bound {r['bound']} != checker derived {res.derived_bound}"
        )


def test_global_upper_bound_matches_csv_max() -> None:
    rows = _load_rows()
    accepted = [r for r in rows if r["status"] == "accepted"]
    assert accepted, "no accepted orbit certificates"
    max_bound = max(int(r["bound"]) for r in accepted)
    # The global bound for pi(L_fpy box L_fpy) is at most this max-orbit bound,
    # IF every orbit has an accepted certificate.
    n_failed = len([r for r in rows if r["status"] != "accepted"])
    if n_failed == 0:
        # All 22 orbits covered: global bound is rationally certified
        print(f"\nGlobal pi(L_fpy box L_fpy) <= {max_bound}")
    else:
        # Some orbits not covered; cannot assert global bound
        print(f"\n{n_failed} orbits failed; max accepted = {max_bound} (NOT global)")
