"""Build the absorbing-core artefact from the n=14 sweep + n<=12 lattice.

For each of the 10 absorbing classes that appear in data/n14_full.jsonl,
emit:
  - class id, min_order, |T|, member_count
  - representative gadget graph6 + ports (smallest-order member)
  - full trace set
  - axis coverage flags (TT_join, TT_split, TM, MT)
  - n=14 absorption count
  - n=14 absorption fraction
  - which structural classes it absorbs

Output: data/n14_absorbing_core.json
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from decomposition import BOUNDARY_COLOUR  # noqa: E402
from coverage_check import load_lattice, trace_set_from_class  # noqa: E402


def axis_coverage(traces):
    a = {"TT_join": False, "TT_split": False, "TM": False, "MT": False}
    for chi, pi in traces:
        b = (BOUNDARY_COLOUR[chi[0]], BOUNDARY_COLOUR[chi[1]])
        if b == ("T", "T"):
            if len(pi) == 1:
                a["TT_join"] = True
            elif len(pi) == 2:
                a["TT_split"] = True
        elif b == ("T", "M"):
            a["TM"] = True
        elif b == ("M", "T"):
            a["MT"] = True
    return a


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--lattice",
        type=Path,
        default=ROOT / "data" / "gadget_lattice_2pole_n12_both.json",
    )
    parser.add_argument(
        "--n14",
        type=Path,
        default=ROOT / "data" / "n14_full.jsonl",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "data" / "n14_absorbing_core.json",
    )
    args = parser.parse_args()

    lattice = load_lattice(args.lattice)
    classes_by_id = {c["id"]: c for c in lattice["classes"]}

    # Read n=14 records and tally absorbers (overall + by structural class).
    absorber_total: Counter = Counter()
    absorber_by_struct: dict = {}
    total_records = 0
    with args.n14.open() as f:
        for line in f:
            r = json.loads(line)
            total_records += 1
            if r.get("absorbing_class_id") is None:
                continue
            cid = r["absorbing_class_id"]
            sc = r["structural_class"]
            absorber_total[cid] += 1
            absorber_by_struct.setdefault(cid, Counter())[sc] += 1

    core = []
    for cid in sorted(absorber_total, key=lambda k: -absorber_total[k]):
        cls = classes_by_id[cid]
        traces = trace_set_from_class(cls)
        axes = axis_coverage(traces)
        # Find smallest-order representative gadget
        members = [g for g in lattice["gadgets"] if g["id"] in cls["members"]]
        rep = min(members, key=lambda g: g["n"])
        core.append({
            "id": cid,
            "min_order": cls["min_order"],
            "trace_count": cls["trace_count"],
            "member_count": cls["member_count"],
            "representative": {
                "graph6": rep["graph6"],
                "ports": rep["ports"],
                "n": rep["n"],
            },
            "traces": [
                {"chi": list(chi), "pi": [list(b) for b in pi]}
                for chi, pi in sorted(traces)
            ],
            "axis_coverage": axes,
            "n14_absorption_total": absorber_total[cid],
            "n14_absorption_fraction": absorber_total[cid] / total_records,
            "n14_absorption_by_structural_class": dict(absorber_by_struct[cid]),
        })

    out = {
        "lattice_meta": lattice["meta"],
        "n14_records_total": total_records,
        "absorbing_class_count": len(core),
        "absorbing_classes": core,
    }
    args.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.output}", file=sys.stderr)
    print(f"absorbing classes: {len(core)}", file=sys.stderr)
    for c in core:
        print(
            f"  {c['id']}: |T|={c['trace_count']} min_order={c['min_order']} "
            f"absorbs {c['n14_absorption_total']} "
            f"axes={[k for k, v in c['axis_coverage'].items() if v]}",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
