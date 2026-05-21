"""Random-sampling sanity check at larger n.

Generates random tournaments at given n, decides MFAS by both the
structural theorem (`structural.decide_mfas`) and brute force
(`brute.decide`), reports disagreements. Also tracks yes/no rate.

At n >= 8 brute force is slow (n! orderings), so this is run with a
small sample.
"""
from __future__ import annotations
import argparse, os, random, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from structural import decide_mfas  # noqa: E402
from brute import decide            # noqa: E402


def random_tournament(n: int, rng: random.Random) -> list[list[int]]:
    T = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < 0.5:
                T[i][j] = 1
            else:
                T[j][i] = 1
    return T


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=7)
    p.add_argument("--samples", type=int, default=200)
    p.add_argument("--seed", type=int, default=20260521)
    p.add_argument("--no-brute", action="store_true",
                   help="Skip brute force (too slow at n >= 9)")
    args = p.parse_args()

    rng = random.Random(args.seed)
    yes_struct = 0
    disagree = 0
    bad = []
    t0 = time.time()
    for k in range(args.samples):
        T = random_tournament(args.n, rng)
        s = decide_mfas(T)
        if s["found"]:
            yes_struct += 1
        if not args.no_brute:
            b = decide(T, "matching")
            if s["found"] != b["found"]:
                disagree += 1
                if len(bad) < 5:
                    bad.append((T, s, b))
    dt = time.time() - t0
    print(f"n={args.n}, samples={args.samples}: structural YES = {yes_struct}")
    if not args.no_brute:
        print(f"  disagreements vs brute: {disagree}")
        for T, s, b in bad:
            print(f"    T = {T}; struct={s['found']}, brute={b['found']}")
    print(f"  elapsed: {dt:.1f}s")


if __name__ == "__main__":
    main()
