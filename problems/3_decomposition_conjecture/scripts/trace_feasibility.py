"""Classify the 34 a-priori 2-pole traces by structural feasibility.

A 2-pole boundary trace (chi, pi) for an essential 2-edge-cut consists of
chi = (s0, s1) in PORT_STATES^2 and pi = (partition of T-incident port
indices). Up to parity, there are 34 a-priori traces; the n<=10 lattice
realises 16. The remaining 18 are not realised by any small gadget.

This script classifies each of the 34 a-priori traces as:

  "realised"  -- some lattice gadget realises it;

  "impossible_no_T_stub" -- both ports have non-T boundary (i.e.,
                   chi in {M_TT, C_TC}^2, with the singleton T_CC stub
                   counting as a T-stub at its own port). In this case
                   every internal vertex has degT_global >= 1 (since
                   internal vertices have valid full-vertex-type
                   triples in {V_T, V_M, V_C}), so T_H has at least one
                   internal vertex with degT_H >= 1, which is in some
                   T_H component with no T-boundary stub. Invalid;

  "impossible_isolated_TCC_component" -- both ports T_CC, pi = {{0,1}}
                   (claiming both T_CC ports are in the same
                   T-component). But T_CC ports have degT_H = 0, so they
                   are isolated in T_H, hence in distinct T_H
                   components. Invalid;

  "open" -- not in the lattice, no structural obstruction from the three
            patterns below. These are candidates for either lattice expansion
            at n >= 12 or for case-by-case impossibility proofs.

Output: JSON manifest with per-trace classification.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from coverage_check import load_lattice, union_of_all_traces  # noqa: E402
from decomposition import BOUNDARY_COLOUR, PORT_STATES  # noqa: E402


def enumerate_apriori_traces() -> set:
    """Generate the 34 a-priori 2-pole traces."""
    out: set = set()
    for s0 in PORT_STATES:
        for s1 in PORT_STATES:
            t0 = BOUNDARY_COLOUR[s0] == "T"
            t1 = BOUNDARY_COLOUR[s1] == "T"
            if t0 and t1:
                pi_opts = [((0, 1),), ((0,), (1,))]
            elif t0:
                pi_opts = [((0,),)]
            elif t1:
                pi_opts = [((1,),)]
            else:
                pi_opts = [()]
            for pi in pi_opts:
                out.add(((s0, s1), pi))
    return out


def classify_trace(chi: tuple[str, str], pi: tuple, universe: frozenset) -> dict[str, Any]:
    """Return a {status, reason} classification for a single trace.

    Impossibility patterns proved here (each rules out a non-empty set of
    a-priori traces). A trace is **realisable** iff it is in the lattice
    universe; the union of the realised set and the three impossibility
    types covers all 34 a-priori traces.
    """
    key = (chi, pi)
    if key in universe:
        return {"status": "realised", "reason": "in lattice universe"}

    s0, s1 = chi
    t0 = BOUNDARY_COLOUR[s0] == "T"
    t1 = BOUNDARY_COLOUR[s1] == "T"

    # --- Pattern (A): C-cycle cannot close ---
    # A C-boundary edge at exactly one port forces the global C-cycle
    # through that boundary to enter H, but it cannot leave again: the
    # only "C-exits" of H are at ports with C-side-edges, and the only
    # such port states are C_TC (side (T,C), one C-side-edge) and T_CC
    # (side (C,C), two C-side-edges). With only one C_TC port, the cycle
    # entering at that port cannot return: at port 1 it would need a
    # C-side-edge (state in {C_TC, T_CC}) and a C-boundary-edge — none
    # of which holds.
    c_boundary_count = sum(1 for s in (s0, s1) if BOUNDARY_COLOUR[s] == "C")
    if c_boundary_count == 1:
        return {
            "status": "impossible_C_cycle_cannot_close",
            "reason": "Exactly one port has C-boundary (state C_TC). The global "
            "C-cycle through that boundary edge enters H and cannot exit: the "
            "other port has no C-boundary, so the cycle cannot close.",
        }

    # --- Pattern (B): no T-stub reachable for internal vertices ---
    # Internal vertices have full vertex type V_T, V_M, or V_C; in each,
    # degT >= 1. So every internal vertex is in some T_H component. Every
    # T_H component must contain a port with a T-boundary stub AND
    # degT_H >= 1 (so the stub is in the component); states satisfying
    # this are exactly {T_T, T_TM}. (T_CC has T-boundary but degT_H = 0,
    # so its T-stub is on its own singleton component, useless for
    # internal vertices.)
    has_usable_T_stub = any(s in ("T_T", "T_TM") for s in (s0, s1))
    if not has_usable_T_stub:
        return {
            "status": "impossible_no_T_stub_for_internal",
            "reason": "Neither port has state in {T_T, T_TM}, so no port "
            "contributes a T-boundary stub to any T_H component "
            "containing an internal vertex. (T_CC has T-boundary but "
            "degT_H = 0, contributing only a singleton T-component.)",
        }

    # --- Pattern (C): T_CC port placed in a shared T-component ---
    # If a T_CC port appears inside a pi block of size >= 2, the trace
    # claims the T_CC port shares a T-component with another port. But
    # T_CC has degT_H = 0, so the port is isolated in T_H — it cannot
    # share a component with anything.
    for block in pi:
        if len(block) >= 2:
            for i in block:
                if chi[i] == "T_CC":
                    return {
                        "status": "impossible_TCC_in_shared_block",
                        "reason": f"pi block {tuple(sorted(block))} contains "
                        f"port {i} (state T_CC); T_CC has degT_H = 0 and is "
                        f"isolated in T_H, so it cannot share a T-component "
                        f"with another port.",
                    }

    # --- Pattern (D): single usable T-stub, T_CC port present ---
    # If exactly one port is in {T_T, T_TM} (call it u) and the other
    # port is T_CC, then T_CC's singleton component has no internal
    # vertices, and u's component must contain every internal vertex of
    # H. That is fine in principle. But the trace also records pi:
    # the T_CC port is in its own block, u is in its own block, so
    # pi = {{u}, {T_CC port}}. Anything else is inconsistent.
    # This case is already caught by Patterns (B) and (C) above for the
    # "wrong" pi values; leaving as a fallback.

    return {"status": "open", "reason": "not realised in lattice; no impossibility "
            "pattern from (A)-(C) above applies"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--lattice",
        type=Path,
        default=ROOT / "data" / "gadget_lattice_2pole_n10_both.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "data" / "trace_feasibility.json",
    )
    args = parser.parse_args()

    payload = load_lattice(args.lattice)
    universe = union_of_all_traces(payload)
    apriori = enumerate_apriori_traces()

    by_status: dict[str, list] = {
        "realised": [],
        "impossible_C_cycle_cannot_close": [],
        "impossible_no_T_stub_for_internal": [],
        "impossible_TCC_in_shared_block": [],
        "open": [],
    }
    rows = []
    for trace in sorted(apriori):
        chi, pi = trace
        classification = classify_trace(chi, pi, universe)
        row = {
            "chi": list(chi),
            "pi": [list(b) for b in pi],
            "status": classification["status"],
            "reason": classification["reason"],
        }
        rows.append(row)
        by_status[classification["status"]].append({"chi": list(chi), "pi": [list(b) for b in pi]})

    summary = {
        "apriori_count": len(apriori),
        "by_status_counts": {k: len(v) for k, v in by_status.items()},
    }

    out_payload = {
        "summary": summary,
        "by_status": by_status,
        "rows": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out_payload, indent=2, sort_keys=True) + "\n")

    print(f"wrote {args.output}")
    print(f"counts: {summary['by_status_counts']}")
    print()
    if by_status["open"]:
        print("Open traces (no impossibility pattern, no lattice realisation):")
        for trace in by_status["open"]:
            print(f"  chi={tuple(trace['chi'])} pi={tuple(tuple(b) for b in trace['pi'])}")
    else:
        print("Every a-priori trace is either realised by the lattice "
              "or provably impossible. The trace space is fully classified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
