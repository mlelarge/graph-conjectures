"""Cross-check decide_mfas (structural theorem) against brute force on
every non-isomorphic tournament for n <= nmax. Prints disagreements.
"""
from __future__ import annotations
import argparse, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sweep import all_tournaments, canonical_key  # noqa: E402
from structural import decide_mfas                # noqa: E402
from brute import decide                          # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--nmax", type=int, default=6)
    p.add_argument("--nmin", type=int, default=3)
    args = p.parse_args()

    total_disagreements = 0
    for n in range(args.nmin, args.nmax + 1):
        t0 = time.time()
        seen = set()
        total = agree = 0
        bad_examples = []
        for T in all_tournaments(n):
            key = canonical_key(T)
            if key in seen:
                continue
            seen.add(key)
            total += 1
            s = decide_mfas(T)
            b = decide(T, "matching")
            if s["found"] == b["found"]:
                agree += 1
            else:
                bad_examples.append((T, s, b))
        dt = time.time() - t0
        print(f"n={n}: {agree}/{total} agree ({dt:.1f}s)")
        if bad_examples:
            print(f"  DISAGREEMENTS: {len(bad_examples)}")
            for T, s, b in bad_examples[:5]:
                print(f"    T = {T}")
                print(f"      structural says {s['found']}, brute says {b['found']}")
        total_disagreements += len(bad_examples)
    print(f"TOTAL DISAGREEMENTS: {total_disagreements}")
    sys.exit(0 if total_disagreements == 0 else 1)


if __name__ == "__main__":
    main()
