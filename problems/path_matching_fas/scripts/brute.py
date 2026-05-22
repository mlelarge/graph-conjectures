"""Brute-force decision procedure for the matching-FAS and path-FAS
problems on a single tournament.

For n <= 9 this is fast enough; for n = 10 it takes ~10s, n = 11 ~minutes.
"""
from __future__ import annotations
from itertools import permutations
from typing import Sequence

# Allow `python3 scripts/brute.py` from the problem folder.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from verify import verify  # noqa: E402


def decide(T: Sequence[Sequence[int]], target: str) -> dict:
    """Return a dict {found: bool, order: list[int]|None, info: dict|None}.

    `target` is one of:
      - 'matching'
      - 'path': exact connected path back-arc graph
      - 'linear_forest'
      - 'path_fas': formal Problem 4.4 path-FAS target; equivalent to
        'linear_forest' for the back-arc graph
      - 'forest'
    """
    if target == "formal_path":
        target = "path_fas"
    if target not in {"matching", "path", "linear_forest", "path_fas", "forest"}:
        raise ValueError(f"unknown target {target!r}")
    n = len(T)
    key = "is_linear_forest" if target == "path_fas" else f"is_{target}"
    for P in permutations(range(n)):
        info = verify(T, list(P))
        if info[key]:
            return {"found": True, "order": list(P), "info": info}
    return {"found": False, "order": None, "info": None}


def decide_all(T: Sequence[Sequence[int]]) -> dict:
    """Run decide for every target on the same tournament. Returns dict
    keyed by target.
    """
    out = {}
    for tgt in ("matching", "path", "path_fas", "linear_forest", "forest"):
        out[tgt] = decide(T, tgt)
    return out


if __name__ == "__main__":
    import argparse, json
    p = argparse.ArgumentParser()
    p.add_argument("--T", required=True,
                   help="Tournament as JSON: nested list of 0/1 entries.")
    args = p.parse_args()
    T = json.loads(args.T)
    out = decide_all(T)
    # Pretty-print without dumping the full arc list.
    for k, v in out.items():
        print(f"== target={k} found={v['found']} order={v['order']}")
        if v["found"]:
            info = v["info"]
            print("   arcs:", info["arcs"], "max_deg:", info["max_degree"])
