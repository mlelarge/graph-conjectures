"""Oracle CLI + API for the Bang-Jensen-Yeo strong arc decomposition problem.

Central decision problem (SAD): given a digraph D = (V, A), does there exist a
2-colouring A = A_R u A_B such that BOTH colour classes (V, A_R) and (V, A_B)
are spanning and strongly connected?  Equivalently: every directed cut
delta^+(X), emptyset != X subsetneq V, contains arcs of both colours.

This is the exact computational ground truth the research engine grounds every
proposal against.  It is a thin, sound wrapper over the project's two
independent verifiers in `code/` (SAT-with-arborescence-witnesses and the
ILP/cutting-plane verifier).  "Sound" here means:
  - every reported SAT comes with a witness re-validated by an independent
    strong-connectivity check on both colour classes (digraph.is_strongly_connected);
  - every reported UNSAT is a solver-level refutation; on demand we cross-check
    SAT<->UNSAT agreement between the two backends so an UNSAT is never a silent
    encoding bug.

The engine invokes:
    <problem_dir>/.venv/bin/python <problem_dir>/scripts/oracle.py <subcmd> ...

Subcommands:
    check <name>                  run a named built-in benchmark
    decide <n> <arcs-json>        SAD-decide an explicit digraph
    arc-strong <n> <arcs-json>    report arc-connectivity lambda^arc(D)
    benchmarks                    run the whole benchmark suite, report agreement

Arcs are passed as a JSON list of [u, v] pairs over vertices 0..n-1; parallel
arcs (multi-arcs) are allowed and meaningful (lambda^arc counts multiplicity).

API (importable):
    check_construction(n, arcs, name=..., cross_check=True) -> dict
    arc_connectivity(n, arcs) -> int
"""
from __future__ import annotations

import argparse
import json
import os
import sys

# The verifier lives in ../code; make it importable without packaging.
_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE = os.path.join(os.path.dirname(_HERE), "code")
if _CODE not in sys.path:
    sys.path.insert(0, _CODE)

from digraph import Digraph  # noqa: E402
from verifier_sat import verify_sat  # noqa: E402

try:
    from verifier_ilp import verify_ilp  # noqa: E402
    _HAVE_ILP = True
except Exception:  # pragma: no cover - pulp/gurobi optional at import time
    _HAVE_ILP = False


# --------------------------------------------------------------------------- #
#  Core grounding routine
# --------------------------------------------------------------------------- #

def _build(n: int, arcs) -> Digraph:
    return Digraph.from_arcs(range(n), [(int(u), int(v)) for u, v in arcs])


def arc_connectivity(n: int, arcs) -> int:
    """Exact lambda^arc(D) = min out-cut size (multiplicity-aware)."""
    return _build(n, arcs).arc_connectivity()


def check_construction(n, arcs, name="construction", time_limit_s=60.0,
                       cross_check=True):
    """SAD-decide an explicit digraph and report the exact verdict + witness.

    Returns a dict with:
      name, n, m_arcs, arc_strong (lambda^arc),
      sad: "SAT" | "UNSAT" | "UNKNOWN",
      witness: {"red": [...], "blue": [...]} on SAT (re-validated), else None,
      backend, time_s,
      cross_check: None or {"ilp": <status>, "agree": bool}  (when requested).

    The verdict is the load-bearing fact: SAT means a strong arc decomposition
    exists; UNSAT means none exists (a genuine obstruction).
    """
    D = _build(n, arcs)
    lam = D.arc_connectivity()
    res = verify_sat(D, time_limit_s=time_limit_s)
    out = {
        "name": name,
        "n": n,
        "m_arcs": D.m(),
        "arc_strong": lam,
        "sad": res["status"],
        "backend": res.get("backend"),
        "time_s": round(res.get("time_s", 0.0), 4),
        "witness": None,
        "cross_check": None,
    }
    if res["status"] == "SAT" and res.get("witness") is not None:
        red, blue = res["witness"]
        out["witness"] = {
            "red": [[u, v] for (u, v, _k) in red],
            "blue": [[u, v] for (u, v, _k) in blue],
        }
    if cross_check and _HAVE_ILP:
        try:
            ilp = verify_ilp(D, time_limit_s=time_limit_s)
            agree = (
                ilp["status"] == res["status"]
                if res["status"] in ("SAT", "UNSAT")
                and ilp["status"] in ("SAT", "UNSAT")
                else None
            )
            out["cross_check"] = {"ilp": ilp["status"], "agree": agree}
            if agree is False:
                out["sad"] = "DISAGREE"
                out["_alarm"] = (
                    "SAT/UNSAT disagreement between SAT and ILP backends -- "
                    "treat as UNKNOWN; do NOT use this verdict."
                )
        except Exception as exc:  # pragma: no cover
            out["cross_check"] = {"ilp": "error", "agree": None,
                                  "error": str(exc)}
    return out


# --------------------------------------------------------------------------- #
#  CLI
# --------------------------------------------------------------------------- #

def _named_benchmarks():
    from benchmarks import all_benchmarks
    return {b.name: b for b in all_benchmarks()}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_chk = sub.add_parser("check", help="SAD-decide a named built-in benchmark")
    p_chk.add_argument("name")

    p_dec = sub.add_parser("decide", help="SAD-decide an explicit digraph")
    p_dec.add_argument("n", type=int)
    p_dec.add_argument("arcs", help='JSON list of [u,v] pairs, e.g. "[[0,1],[1,0]]"')
    p_dec.add_argument("--name", default="construction")
    p_dec.add_argument("--no-cross-check", action="store_true")
    p_dec.add_argument("--time-limit", type=float, default=60.0)

    p_lam = sub.add_parser("arc-strong", help="arc-connectivity lambda^arc(D)")
    p_lam.add_argument("n", type=int)
    p_lam.add_argument("arcs", help='JSON list of [u,v] pairs')

    sub.add_parser("benchmarks", help="run the full benchmark suite + agreement")

    args = ap.parse_args()

    if args.cmd == "check":
        bm = _named_benchmarks()
        if args.name not in bm:
            ap.error(f"unknown benchmark {args.name!r}; "
                     f"available: {', '.join(sorted(bm))}")
        b = bm[args.name]
        res = check_construction(b.n, b.arcs, name=b.name)
        res["expected"] = b.expected
        res["source"] = b.source
        res["matches_expected"] = (res["sad"] == b.expected)
        print(json.dumps(res, indent=2, default=str))

    elif args.cmd == "decide":
        arcs = json.loads(args.arcs)
        res = check_construction(args.n, arcs, name=args.name,
                                 time_limit_s=args.time_limit,
                                 cross_check=not args.no_cross_check)
        print(json.dumps(res, indent=2, default=str))

    elif args.cmd == "arc-strong":
        arcs = json.loads(args.arcs)
        print(json.dumps({"n": args.n, "m_arcs": len(arcs),
                          "arc_strong": arc_connectivity(args.n, arcs)},
                         indent=2))

    elif args.cmd == "benchmarks":
        bm = _named_benchmarks()
        rows, n_ok = [], 0
        for name, b in sorted(bm.items()):
            res = check_construction(b.n, b.arcs, name=name)
            ok = (res["sad"] == b.expected)
            n_ok += ok
            rows.append({"name": name, "expected": b.expected,
                         "got": res["sad"], "lambda": res["arc_strong"],
                         "ok": ok})
        print(json.dumps({"n_benchmarks": len(rows), "n_ok": n_ok,
                          "all_pass": n_ok == len(rows), "rows": rows},
                         indent=2))


if __name__ == "__main__":
    main()
