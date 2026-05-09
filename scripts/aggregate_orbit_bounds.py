"""Aggregate all orbit certificates into a single best-per-orbit CSV.

Scans data/pebbling_product/certificates/path_orbit_*.json, groups by
orbit representative (parsed from the filename), picks the certificate
with the smallest derived bound for each orbit, re-checks it
rationally, and writes the result to root_orbit_bounds.csv.
"""

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from check_pebbling_weight_certificate import check_certificate, load_certificate_file


def main() -> None:
    cert_dir = REPO_ROOT / "data" / "pebbling_product" / "certificates"
    pat = re.compile(r"path_orbit_(\d+)_(\d+)_(.+)\.json$")
    by_orbit: dict[tuple[int, int], list[Path]] = defaultdict(list)
    for p in cert_dir.glob("path_orbit_*.json"):
        m = pat.match(p.name)
        if m:
            r0, r1 = int(m.group(1)), int(m.group(2))
            by_orbit[(r0, r1)].append(p)

    # Compute orbits to know orbit sizes
    from run_root_orbit_certificates import compute_root_orbits
    from pebbling_graphs import load_named_graph

    L = load_named_graph("L_fpy")
    orbits = compute_root_orbits(L.n, L.edges)
    expected_reps = set(orbits.keys())

    rows: list[dict] = []
    missing = expected_reps - set(by_orbit.keys())
    if missing:
        print(f"WARNING: missing orbit reps: {sorted(missing)}")

    for rep in sorted(expected_reps):
        files = by_orbit.get(rep, [])
        best_bound: int | None = None
        best_path: Path | None = None
        best_lp_value = ""
        best_n_cols = 0
        best_max_len = 0
        for p in files:
            try:
                cert, g = load_certificate_file(p)
                res = check_certificate(cert, g)
                if not res.accepted:
                    continue
                if best_bound is None or res.derived_bound < best_bound:
                    best_bound = res.derived_bound
                    best_path = p
                    best_lp_value = res.sum_alpha_b
                    best_n_cols = len(cert.strategies)
                    # Try to extract max_len from filename
                    m = re.search(r"max_len(\d+)", p.name)
                    best_max_len = int(m.group(1)) if m else 0
            except Exception as e:
                print(f"  load error on {p.name}: {e}")

        rows.append(
            {
                "root_rep": f"({rep[0]},{rep[1]})",
                "orbit_size": len(orbits[rep]),
                "bound": str(best_bound) if best_bound is not None else "",
                "lp_value": best_lp_value,
                "num_columns": str(best_n_cols),
                "max_len": str(best_max_len) if best_max_len else "",
                "certificate_path": (
                    str(best_path.relative_to(REPO_ROOT)) if best_path else ""
                ),
                "status": "accepted" if best_bound is not None else "missing",
                "notes": "",
            }
        )

    csv_path = REPO_ROOT / "data" / "pebbling_product" / "root_orbit_bounds.csv"
    cols = [
        "root_rep", "orbit_size", "bound", "lp_value", "num_columns",
        "max_len", "certificate_path", "status", "notes",
    ]
    with csv_path.open("w", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=cols)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"Wrote {csv_path}")
    accepted = [r for r in rows if r["status"] == "accepted" and r["bound"]]
    if accepted:
        max_b = max(int(r["bound"]) for r in accepted)
        worst = [r for r in accepted if int(r["bound"]) == max_b]
        print(f"\nGlobal bound = {max_b}")
        print(f"Worst orbit(s): {[(r['root_rep'], r['bound']) for r in worst]}")
        # Show top 5
        ordered = sorted(accepted, key=lambda r: -int(r["bound"]))
        print("\nTop 5 worst:")
        for r in ordered[:5]:
            print(f"  {r['root_rep']}: bound {r['bound']}, cert {r['certificate_path']}")


if __name__ == "__main__":
    main()
