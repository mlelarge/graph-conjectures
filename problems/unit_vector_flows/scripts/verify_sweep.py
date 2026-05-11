"""Independent verifier for sweep certificates.

Reads every ``*.json`` in a sweep-results directory, reconstructs the
graph from its stored ``graph6`` string, and re-checks the witness (or
interval / infeasibility evidence) without consulting the search code
beyond :func:`witness.verify_witness` and
:func:`interval.replay_krawczyk`.

Verdict policy for ``kind == "interval_witness"``:

* Replay must succeed (``replay["ok"] is True``).
* Cert's stored verdict must match (``verdict_matches_cert is True``).
* Polynomial-system hash must match by default
  (``polynomial_hash_match is True``). Pass ``--allow-hash-mismatch`` to
  downgrade a hash mismatch to a warning -- intended for cross-version
  SymPy replays where the canonical srepr of an expression can differ
  while the underlying polynomial system is unchanged.

Usage::

    python scripts/verify_sweep.py data/sweep_results/<run-id>
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

from graphs import from_graph6
from interval import replay_krawczyk
from witness import verify_witness


def verify_one(cert_path: pathlib.Path, *, tol: float = 1e-7, allow_hash_mismatch: bool = False) -> dict:
    cert = json.loads(cert_path.read_text())
    name = cert.get("name", cert_path.stem)
    kind = cert.get("kind")
    G = from_graph6(cert["graph"]["graph6"])
    edges = [tuple(e) for e in cert["graph"]["edges"]]

    if kind == "numerical_witness" and cert["result"]["status"] == "witness":
        check = verify_witness(G, edges, cert["witness"]["vectors"], tol=tol)
        return {"name": name, "ok": check["ok"], "kind": kind, "details": check}

    if kind == "numerical_witness" and cert["result"]["status"] == "unknown":
        return {
            "name": name,
            "ok": True,
            "kind": kind,
            "details": "no witness recorded; nothing to check",
        }

    if kind == "interval_witness":
        check = replay_krawczyk(cert)
        replay_ok = bool(check.get("ok"))
        verdict_match = bool(check.get("verdict_matches_cert"))
        hash_match = bool(check.get("polynomial_hash_match"))
        notes = []
        if not replay_ok:
            notes.append("replay rejected K(I) ⊂ int(I)")
        if not verdict_match:
            notes.append("replay verdict disagrees with cert")
        if not hash_match:
            if allow_hash_mismatch:
                notes.append("polynomial_hash mismatch (downgraded to warning)")
            else:
                notes.append("polynomial_hash mismatch")
        if not hash_match and allow_hash_mismatch:
            ok = replay_ok and verdict_match
        else:
            ok = replay_ok and verdict_match and hash_match
        return {"name": name, "ok": ok, "kind": kind, "details": check, "notes": notes}

    if kind == "infeasibility":
        return {
            "name": name,
            "ok": False,
            "kind": kind,
            "details": "infeasibility verification not implemented yet",
        }

    return {"name": name, "ok": False, "kind": kind, "details": "unknown certificate kind"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir", type=pathlib.Path)
    ap.add_argument("--tol", type=float, default=1e-7)
    ap.add_argument(
        "--allow-hash-mismatch",
        action="store_true",
        help=(
            "Treat a polynomial_hash_match=False as a warning instead of a "
            "verification failure. Use only when re-verifying across a "
            "different SymPy version."
        ),
    )
    args = ap.parse_args()

    paths = sorted(p for p in args.run_dir.glob("*.json") if p.name != "summary.json")
    if not paths:
        print(f"no certificates under {args.run_dir}", file=sys.stderr)
        return 2

    failed = 0
    for p in paths:
        r = verify_one(p, tol=args.tol, allow_hash_mismatch=args.allow_hash_mismatch)
        flag = "OK" if r["ok"] else "FAIL"
        notes = "; ".join(r.get("notes", [])) if isinstance(r.get("notes"), list) else ""
        suffix = ""
        if not r["ok"]:
            suffix = f"  -- {r.get('details') if not notes else notes}"
        elif notes:
            suffix = f"  (warn: {notes})"
        print(f"[{flag}] {r['name']:14s} ({r['kind']}){suffix}")
        if not r["ok"]:
            failed += 1
    print(f"\n{len(paths) - failed}/{len(paths)} certificates verified")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
