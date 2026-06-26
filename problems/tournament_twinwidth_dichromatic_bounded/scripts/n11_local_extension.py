"""TERTIARY disprove probe: two-step tww<=1 LOCAL EXTENSION of the 20 n=9 PRIME
tww=1, omegaVec=2, chiVec=3 seeds (landmark prime_chi_gt_omega_at_n9) to n=11.

For each seed W (n=9):
  step A: for all 2^9 orientations of vertex 9 against W, keep tww<=1 (n=10).
  step B: from each survivor, for all 2^10 orientations of vertex 10, keep tww<=1
          (n=11). On each n=11 tww<=1 survivor test chi>=4 via NOT-3-dicolourable
          (exact). If chi>=4 AND omegaVec<=2 -> DIRECT COUNTEREXAMPLE to Conj 3.12.
          Else record (omegaVec, chiVec) cell (chi capped probe: chi=3 if
          3-dicolourable, else >=4 -> compute exact chi+omega).

All invariants exact (core.{tww, omega_vec, chi_vec, is_k_dicolourable}).
Parallel across seeds (process pool); pure foreground.
"""
from __future__ import annotations
import sys, os, json, time, argparse
from collections import Counter
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core

N9 = 9


def process_seed(args):
    idx, seed = args
    t0 = time.time()
    cell = Counter()                 # (omega,chi-tag) -> count over n=11 tww<=1
    n10_surv = 0
    n11_surv = 0
    witnesses = []                   # omega<=2, chi>=4 -> counterexamples
    # step A
    for b9 in range(1 << N9):
        a10 = list(seed) + [((9, u) if (b9 >> u) & 1 else (u, 9)) for u in range(N9)]
        if core.tww(10, a10, ub=2) > 1:
            continue
        n10_surv += 1
        # step B
        for b10 in range(1 << 10):
            a11 = a10 + [((10, u) if (b10 >> u) & 1 else (u, 10)) for u in range(10)]
            if core.tww(11, a11, ub=2) > 1:
                continue
            n11_surv += 1
            # chi>=4 test: chi<=3 iff 3-dicolourable (exact)
            if core.is_k_dicolourable(11, a11, 3):
                # chi<=3; omega>=2 always here (seed omega 2). record cell coarsely
                cell[("chi_le_3",)] += 1
            else:
                # chi>=4: the discriminating cell -- compute exact omega
                o = core.omega_vec(11, a11)
                c = core.chi_vec(11, a11)
                cell[("chi_ge_4", o, c)] += 1
                if o <= 2:
                    witnesses.append({"seed_idx": idx, "n": 11,
                                      "arcs": a11, "omega_vec": o, "chi_vec": c})
    return {"seed_idx": idx, "n10_surv": n10_surv, "n11_surv": n11_surv,
            "cell": dict(cell), "witnesses": witnesses,
            "secs": round(time.time() - t0, 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="data/h10_witnesses.json")
    ap.add_argument("--procs", type=int, default=8)
    ap.add_argument("--max-seeds", type=int, default=20)
    ap.add_argument("--out", default="data/n11_local_extension.json")
    a = ap.parse_args()

    with open(a.cache) as f:
        seeds = json.load(f)["witnesses"][:a.max_seeds]

    t0 = time.time()
    jobs = list(enumerate(seeds))
    results = []
    with Pool(a.procs) as p:
        for r in p.imap_unordered(process_seed, jobs):
            results.append(r)
            print(f"  seed {r['seed_idx']}: n10_surv={r['n10_surv']} "
                  f"n11_surv={r['n11_surv']} witnesses={len(r['witnesses'])} "
                  f"({r['secs']}s)", flush=True)

    agg = Counter()
    total_n11 = 0
    total_n10 = 0
    all_wit = []
    for r in results:
        total_n10 += r["n10_surv"]
        total_n11 += r["n11_surv"]
        for k, v in r["cell"].items():
            agg[str(k)] += v
        all_wit.extend(r["witnesses"])

    summary = {
        "n_seeds": len(seeds),
        "total_n10_tww1_survivors": total_n10,
        "total_n11_tww1_survivors_examined": total_n11,
        "n11_cell_histogram": dict(agg),
        "num_omega_le2_chi_ge4_witnesses": len(all_wit),
        "witnesses": all_wit,
        "wall_secs": round(time.time() - t0, 1),
        "per_seed": [{"seed_idx": r["seed_idx"], "n10_surv": r["n10_surv"],
                      "n11_surv": r["n11_surv"], "secs": r["secs"]} for r in results],
    }
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as f:
        json.dump(summary, f)
    print(json.dumps({k: v for k, v in summary.items() if k != "witnesses"}, indent=2))
    if all_wit:
        print("COUNTEREXAMPLE WITNESSES:", json.dumps(all_wit, indent=2))


if __name__ == "__main__":
    main()
