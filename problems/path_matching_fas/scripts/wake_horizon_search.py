"""Random search for finite wake-horizon failures.

This is a harness around `wake_signature_probe.find_one_step_mismatch`.
It asks whether a fixed wake horizon h gives a one-step bisimulation on
the pruned forced/flexible DP state space.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from score_window_random_probe import (  # noqa: E402
    random_tournament,
    transitive_noise_tournament,
)
from wake_signature_probe import (  # noqa: E402
    find_extendability_collision,
    find_one_step_mismatch,
)


def parse_ints(raw: str) -> list[int]:
    return [int(x) for x in raw.split(",") if x]


def parse_floats(raw: str) -> list[float]:
    return [float(x) for x in raw.split(",") if x]


def make_tournament(mode: str, n: int, p: float, rng: random.Random):
    if mode == "uniform":
        return random_tournament(n, rng)
    return transitive_noise_tournament(n, p, rng)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["uniform", "skew"], default="skew")
    parser.add_argument("--check", choices=["one-step", "extendability"], default="one-step")
    parser.add_argument("--kind", choices=["visible", "wake", "sleeping"], default="wake")
    parser.add_argument("--ns", default="12,16")
    parser.add_argument("--ps", default="0.02,0.05")
    parser.add_argument("--horizons", default="2")
    parser.add_argument("--samples", type=int, default=20)
    parser.add_argument("--depth", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20260523)
    parser.add_argument("--check-extendability", action="store_true")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    ns = parse_ints(args.ns)
    ps = parse_floats(args.ps) if args.mode == "skew" else [0.0]
    horizons = parse_ints(args.horizons)
    t0 = time.time()
    groups = []

    for horizon in horizons:
        for n in ns:
            for p in ps:
                group = {
                    "horizon": horizon,
                    "mode": args.mode,
                    "n": n,
                    "p": p if args.mode == "skew" else None,
                    "check": args.check,
                    "kind": args.kind,
                    "samples": 0,
                    "mismatch": None,
                    "seconds": None,
                }
                for sample in range(args.samples):
                    T = make_tournament(args.mode, n, p, rng)
                    if args.check == "one-step":
                        mismatch = find_one_step_mismatch(
                            T,
                            depth=args.depth,
                            kind=args.kind,
                            horizon=horizon,
                            pruned=True,
                        )
                    else:
                        mismatch = find_extendability_collision(
                            T,
                            depth=args.depth,
                            kind=args.kind,
                            horizon=horizon,
                            pruned=True,
                        )
                    group["samples"] += 1
                    if mismatch is not None:
                        group["mismatch"] = {
                            "sample": sample,
                            "witness": mismatch,
                        }
                        if args.check_extendability and args.check == "one-step":
                            collision = find_extendability_collision(
                                T,
                                depth=args.depth,
                                kind=args.kind,
                                horizon=horizon,
                                pruned=True,
                            )
                            group["extendability_collision"] = collision is not None
                            if collision is not None:
                                group["extendability_collision_witness"] = collision
                        group["seconds"] = round(time.time() - t0, 3)
                        groups.append(group)
                        print(json.dumps({
                            "seed": args.seed,
                            "depth": args.depth,
                            "groups": groups,
                            "stopped_on_mismatch": True,
                        }, indent=2, default=str))
                        return
                group["seconds"] = round(time.time() - t0, 3)
                groups.append(group)
                print(
                    f"ok check={args.check} kind={args.kind} horizon={horizon} "
                    f"mode={args.mode} n={n} p={group['p']} samples={group['samples']} "
                    f"elapsed={group['seconds']}",
                    flush=True,
                )

    print(json.dumps({
        "seed": args.seed,
        "depth": args.depth,
        "groups": groups,
        "stopped_on_mismatch": False,
    }, indent=2, default=str))


if __name__ == "__main__":
    main()
