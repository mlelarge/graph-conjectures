"""Analyze the JSON output of sleeping_block_skew_sweep.py.

Reports:
  - per-template: number of admissible perturbations; collision rates for
    sleeping vs visible signatures; mean state-class size.
  - aggregate verdict: sleeping-block alive or refuted across the sample?
  - state-space growth: distinct sleeping vs visible signatures per
    surviving prefix.

Usage:
  uv run python scripts/analyze_sleeping_sweep.py --in /tmp/sleeping_sweep.json
"""
from __future__ import annotations

import argparse
import json


def analyze(path: str) -> str:
    with open(path) as f:
        d = json.load(f)
    out = []
    out.append(f"# Sleeping-block skew sweep analysis ({path})")
    out.append(f"")
    out.append(f"- samples: {d['n_samples']}, depth: {d['depth']}, seed: {d['seed']}")
    out.append(f"- flips range: {d['flips_range']}, templates: {d['templates']}")
    out.append(f"- admissible: {d['admissible']} / {d['n_samples']}  "
               f"({100*d['admissible']/max(d['n_samples'],1):.1f}%)")
    out.append(f"- total sleeping-block extension collisions: "
               f"{d['total_sleeping_collisions']}")
    out.append(f"- total visible-latent extension collisions: "
               f"{d['total_visible_collisions']}")
    out.append(f"- elapsed: {d['elapsed_sec']}s")
    out.append("")
    out.append("## Per template")
    for tmpl, stats in d["per_template"].items():
        adm = max(stats["admissible"], 1)
        out.append(f"### {tmpl}")
        out.append(f"  - tried: {stats['tried']}, admissible: {stats['admissible']}")
        out.append(f"  - visible collisions: {stats['visible_collisions']}, "
                   f"sleeping collisions: {stats['sleeping_collisions']}")
        out.append(f"  - mean visible classes: "
                   f"{stats['visible_classes_sum']/adm:.1f}")
        out.append(f"  - mean sleeping classes: "
                   f"{stats['sleeping_classes_sum']/adm:.1f}")
        out.append(f"  - mean surviving prefixes: "
                   f"{stats['surviving_prefixes_sum']/adm:.1f}")
        # Refinement ratio: sleeping_classes / visible_classes
        if stats["visible_classes_sum"] > 0:
            ratio = stats["sleeping_classes_sum"] / stats["visible_classes_sum"]
            out.append(f"  - refinement ratio sleeping/visible: {ratio:.3f}")

    out.append("")
    out.append("## Verdict")
    if d["total_sleeping_collisions"] == 0 and d["admissible"] > 0:
        out.append("- **sleeping-block survives** the sweep: zero "
                   "extendability collisions on the admissible sample.")
    elif d["total_sleeping_collisions"] > 0:
        out.append(f"- **sleeping-block REFUTED**: "
                   f"{d['total_sleeping_collisions']} collisions found across "
                   "the sweep.  See sleeping_collision_examples in JSON.")
    else:
        out.append("- inconclusive: no admissible tournaments in sample.")

    if d["total_visible_collisions"] > 0 and d["total_sleeping_collisions"] == 0:
        out.append(f"- **visible-latent vs sleeping-block**: visible-latent "
                   f"had {d['total_visible_collisions']} collisions on the "
                   "same sample, sleeping-block 0.  Sleeping-block strictly "
                   "improves on visible-latent here.")
    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="in_path", required=True)
    parser.add_argument("--out")
    args = parser.parse_args()
    text = analyze(args.in_path)
    print(text)
    if args.out:
        with open(args.out, "w") as f:
            f.write(text)


if __name__ == "__main__":
    main()
