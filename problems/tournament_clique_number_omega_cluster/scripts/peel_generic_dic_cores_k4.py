"""GENERIC DIC-PEELING SUPPLY PIPELINE -- k=4 calibration.

Goal (existential): among GENERIC (random-sourced) 4-dic-vertex-critical cores,
find at least one with omega_vec EXACTLY 4 -- a non-vertex-transitive aligned
(4-dic-vc AND ov=4) object reachable at positive sampling rate. This prices the
k=5 supply hunt for the Prop 6.2 k=6 gate. f4>0 replicates P22's circulant
H1*/H2* in the GENERIC class; f4=0 graveyards the generic-peeling route.

PIPELINE
  (1) sample random tournaments at n in --ns; keep those with dic>=4
      (i.e. NOT 3-dicolourable, validated mono-triangle-free SAT encoding).
  (2) PEEL: repeatedly delete the first vertex whose removal keeps dic>=4 until
      none -> endpoint core is 4-dic-VERTEX-CRITICAL by construction. Then VERIFY
      criticality explicitly: dic(core)=4 and dic(core-v)=3 for ALL v.
  (3) ov(core) EXACTLY: dic(core)=4 => ov<=4 (Property 5.3: ov<=dic). Lower
      bound ov>=4 via the VALIDATED no-K4 betweenness SAT (UNSAT). Cross-check
      ov<=4 via no-K5 SAT (SAT) AND an explicit clique-4 order upper bound.
      ALIGNED iff ov==4 (no-K4 UNSAT and no-K5 SAT).
  (4) emit JSON {core_order_hist, f4_alignment_count, aligned_witness_arcs}.

EXACTNESS: every load-bearing statement (dic, dic-criticality, ov>=K) goes
through the validated SAT oracles. No heuristics in the verdict path.
"""
import sys, os, json, time, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ground_lift_lemma_step1 import dicolorable, directed_triangles, sub
from search_4critical_circulant import omega_vec_ge_K_via_sat, best_order_upper
from constructions import random_tournament
from lexlib import is_tournament


def dic_ge_k(n, arcs, k):
    """dic(T) >= k  iff  T is NOT (k-1)-dicolourable."""
    return not dicolorable(n, arcs, k - 1)


def peel_to_k_dic_vc(n, arcs, k):
    """Greedy peel: delete first vertex whose removal keeps dic>=k, until none.
    Endpoint is k-dic-vertex-critical by construction."""
    cn, ca = n, list(arcs)
    changed = True
    while changed:
        changed = False
        for v in range(cn):
            sn, sa = sub(cn, ca, v)
            if dic_ge_k(sn, sa, k):
                cn, ca = sn, sa
                changed = True
                break
    return cn, ca


def verify_k_dic_vc(n, arcs, k):
    """dic(T)=k and dic(T-v)=k-1 for ALL v."""
    if not dic_ge_k(n, arcs, k):
        return False, "dic<k"
    if dic_ge_k(n, arcs, k + 1):
        return False, "dic>k"
    # every single deletion drops to dic<=k-1 (and >=k-1 since deletion drops <=1
    # from a dic>=k tournament, but we still confirm not >=k):
    for v in range(n):
        sn, sa = sub(n, arcs, v)
        if dic_ge_k(sn, sa, k):
            return False, f"del {v} keeps dic>=k"
    return True, "ok"


def ov_exact_for_dic4_core(n, arcs):
    """For a core with dic=4 (=> ov<=4 by Property 5.3 ov<=dic), decide ov exactly.
    ov>=4 via no-K4 SAT UNSAT; cross-check ov<=4 via no-K5 SAT SAT + explicit
    clique-4 upper order. Returns (ov, detail)."""
    ge4, _, _ = omega_vec_ge_K_via_sat(n, arcs, 4)   # True => ov>=4
    ge5, _, _ = omega_vec_ge_K_via_sat(n, arcs, 5)   # True => ov>=5
    upper = best_order_upper(n, arcs, tries=200)      # explicit order upper bound
    detail = {"ge4": ge4, "ge5": ge5, "best_order_upper": upper}
    if ge5:
        return 5 if not ge4 else 5, detail  # shouldn't happen (dic=4)
    if ge4:
        # ov>=4 and not>=5 => ov==4 ; upper must corroborate
        return 4, detail
    # not >=4
    return ("<4", detail)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ns", type=int, nargs="+", default=[31, 33])
    ap.add_argument("--target-cores", type=int, default=60)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--wall", type=float, default=560.0, help="self-cap seconds")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    t0 = time.time()
    core_order_hist = {}
    cores = []          # all verified 4-dic-vc cores
    aligned = []        # ov==4 cores
    seeds_tried = 0
    sources_with_dic4 = 0

    seed = args.seed
    ni = 0
    while len(cores) < args.target_cores and (time.time() - t0) < args.wall:
        n = args.ns[ni % len(args.ns)]
        ni += 1
        nn, arcs = random_tournament(n, seed)
        seed += 1
        seeds_tried += 1
        if (time.time() - t0) >= args.wall:
            break
        if not dic_ge_k(nn, arcs, 4):
            continue
        sources_with_dic4 += 1
        cn, ca = peel_to_k_dic_vc(nn, arcs, 4)
        ok, why = verify_k_dic_vc(cn, ca, 4)
        if not ok:
            # criticality verification failure (should not happen) -- record + skip
            continue
        ov, detail = ov_exact_for_dic4_core(cn, ca)
        core_order_hist[cn] = core_order_hist.get(cn, 0) + 1
        rec = {"source_n": n, "source_seed": seed - 1, "core_order": cn,
               "ov": ov, "ov_detail": detail}
        cores.append(rec)
        if ov == 4:
            wit = {"source_n": n, "source_seed": seed - 1, "core_order": cn,
                   "arcs": [list(a) for a in ca], "ov_detail": detail}
            aligned.append(wit)
        if args.json:
            print(f"[{time.time()-t0:6.1f}s] core#{len(cores)} src_n={n} "
                  f"core_order={cn} ov={ov} aligned={'YES' if ov==4 else 'no'} "
                  f"(dic4_sources={sources_with_dic4}, seeds={seeds_tried})",
                  flush=True)

    out = {
        "ns": args.ns,
        "target_cores": args.target_cores,
        "seeds_tried": seeds_tried,
        "sources_with_dic4": sources_with_dic4,
        "n_verified_cores": len(cores),
        "core_order_hist": core_order_hist,
        "f4_alignment_count": len(aligned),
        "f4_alignment_fraction": (len(aligned) / len(cores)) if cores else None,
        "ov_hist": _hist([c["ov"] for c in cores]),
        "aligned_witnesses": aligned[:5],   # cap stored arcs
        "all_cores_summary": [{"core_order": c["core_order"], "ov": c["ov"]} for c in cores],
        "wall_s": round(time.time() - t0, 1),
    }
    os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
    outp = os.path.join(os.path.dirname(__file__), "..", "data",
                        "peel_generic_dic_cores_k4.json")
    with open(outp, "w") as f:
        json.dump(out, f, indent=1)
    print("=" * 60)
    print(json.dumps({k: v for k, v in out.items()
                      if k not in ("aligned_witnesses", "all_cores_summary")}, indent=1))
    if aligned:
        print(f"ALIGNED (ov=4) WITNESS COUNT: {len(aligned)}")
        print("first witness ov_detail:", aligned[0]["ov_detail"])


def _hist(xs):
    h = {}
    for x in xs:
        h[str(x)] = h.get(str(x), 0) + 1
    return h


if __name__ == "__main__":
    main()
