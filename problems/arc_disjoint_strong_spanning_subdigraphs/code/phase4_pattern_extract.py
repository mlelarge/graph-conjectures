"""Phase 4 pattern extraction.

Reads the JSON written by `phase4_witness_probe.py` and computes per-class
aggregated statistics aimed at the CL1 hypothesis:

  H1.  Is the bridge multiset "monochromatic by direction"?  I.e. all
       T1->T2 bridges in one color, all T2->T1 bridges in the other?
  H2.  Is the bridge color "rooted at the interface direction"?  I.e.
       T1->T2 bridges share a color, T2->T1 share a (possibly different) one?
  H3.  Per tight 3-cut, is the distribution always (1,2) or (2,1)?
       (Forced by SAD; checked.)
  H4.  How many tight 3-cuts intersect the bridge set, and in those cuts
       what is the color split?

We normalize away the SAT symmetry-break (which forces the lex-smallest arc
to R) by re-stating everything in terms of "majority on T1-side internal
arcs" vs "the other color".
"""

from __future__ import annotations

import json
from pathlib import Path
from collections import Counter


def normalize_row(row):
    """Re-label R <-> B so that bridges_S2_to_S1 are mostly the SAME color
    across instances. We pick the convention: T2->T1 bridges should be
    majority-"B" after normalization.
    """
    cc = row["color_counts"]
    b21 = cc["bridges_S2_to_S1"]
    # Already in our data b21 is mostly all-B; check if flipping is needed.
    flip = b21["R"] > b21["B"]
    if not flip:
        return row
    out = json.loads(json.dumps(row))
    for k, v in out["color_counts"].items():
        out["color_counts"][k] = {"R": v["B"], "B": v["R"]}
    for k, v in out["named_cuts"].items():
        out["named_cuts"][k] = {"size": v["size"], "R": v["B"], "B": v["R"]}
    new_t3 = []
    for tc in out["tight3_cuts"]:
        new_t3.append({"X_size": tc["X_size"], "R": tc["B"], "B": tc["R"]})
    out["tight3_cuts"] = new_t3
    out["tight3_distribution"] = Counter(
        (tc["R"], tc["B"]) for tc in new_t3
    ).most_common()
    return out


def aggregate_class(class_label, payload):
    rows = [normalize_row(r) for r in payload["rows"]]
    if not rows:
        return None
    n = len(rows)
    b12_monochrome_R = sum(1 for r in rows if r["color_counts"]["bridges_S1_to_S2"]["B"] == 0)
    b12_monochrome_B = sum(1 for r in rows if r["color_counts"]["bridges_S1_to_S2"]["R"] == 0)
    b21_monochrome_R = sum(1 for r in rows if r["color_counts"]["bridges_S2_to_S1"]["B"] == 0)
    b21_monochrome_B = sum(1 for r in rows if r["color_counts"]["bridges_S2_to_S1"]["R"] == 0)
    # Average b12 R/B and b21 R/B
    avg_b12_R = sum(r["color_counts"]["bridges_S1_to_S2"]["R"] for r in rows) / n
    avg_b12_B = sum(r["color_counts"]["bridges_S1_to_S2"]["B"] for r in rows) / n
    avg_b21_R = sum(r["color_counts"]["bridges_S2_to_S1"]["R"] for r in rows) / n
    avg_b21_B = sum(r["color_counts"]["bridges_S2_to_S1"]["B"] for r in rows) / n
    # Average d+(I) split
    avg_dI_R = sum(r["named_cuts"]["delta+(I)"]["R"] for r in rows) / n
    avg_dI_B = sum(r["named_cuts"]["delta+(I)"]["B"] for r in rows) / n
    # All tight 3-cuts splits seen across all instances
    all_t3 = Counter()
    for r in rows:
        for tc in r["tight3_cuts"]:
            all_t3[(tc["R"], tc["B"])] += 1
    # interface vertex degree-coloring: which side of the interface dominates?
    # An interface vertex u has T1-side neighbors (in side1_non) and T2-side
    # neighbors (in side2_non) and possibly bridge endpoints (also in S1n/S2n).
    return {
        "n_rows": n,
        "b12_avg": (round(avg_b12_R, 2), round(avg_b12_B, 2)),
        "b21_avg": (round(avg_b21_R, 2), round(avg_b21_B, 2)),
        "b12_R_only": b12_monochrome_B,  # B==0 means all R
        "b12_B_only": b12_monochrome_R,
        "b21_R_only": b21_monochrome_B,
        "b21_B_only": b21_monochrome_R,
        "dI_avg": (round(avg_dI_R, 2), round(avg_dI_B, 2)),
        "tight3_dist": dict(all_t3),
    }


def main():
    p = Path(__file__).resolve().parent / "logs" / "phase4_lifting_probe.json"
    data = json.loads(p.read_text())
    for cls, payload in data.items():
        if "rows" not in payload:
            continue
        agg = aggregate_class(cls, payload)
        if agg is None:
            continue
        print(f"\n== {cls}  pair={payload['pair']}  N={agg['n_rows']} ==")
        print(f"  avg b12 (T1->T2)  : R={agg['b12_avg'][0]}  B={agg['b12_avg'][1]}")
        print(f"  avg b21 (T2->T1)  : R={agg['b21_avg'][0]}  B={agg['b21_avg'][1]}")
        print(f"  b12 instances all-R / all-B : {agg['b12_R_only']} / {agg['b12_B_only']}")
        print(f"  b21 instances all-R / all-B : {agg['b21_R_only']} / {agg['b21_B_only']}")
        print(f"  avg d+(interface) R/B : {agg['dI_avg']}")
        print(f"  tight 3-cut color splits : {agg['tight3_dist']}")


if __name__ == "__main__":
    main()
