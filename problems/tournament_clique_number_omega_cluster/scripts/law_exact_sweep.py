"""EXACT composition-law sweep (sub-task A of next_action, H11).

Test omega_vec(T[H]) == omega_vec(T) + omega_vec(H) - 1 on a BROAD set of
exact-feasible lexicographic products using the EXACT oracle core.omega_vec
(brute force n<=7, branch-and-bound above) -- NO SAT, so no upper-bound-search
weakness. Each omega_vec call is guarded by a per-call signal.alarm so nothing
hangs; any call that exceeds the cap is recorded as "timeout" and skipped (does
NOT count as agreement or disagreement).

Falsifiable prediction: EVERY completed exact product agrees with the law
(agree=True); a single disagreement KILLS the uniform composition law H11(A).
"""
import sys, os, json, time, signal
sys.path.insert(0, os.path.dirname(__file__))
import core
import constructions as C


class Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise Timeout()


def omega_vec_guarded(n, arcs, secs):
    signal.signal(signal.SIGALRM, _alarm)
    signal.setitimer(signal.ITIMER_REAL, secs)
    try:
        v = core.omega_vec(n, arcs)
        signal.setitimer(signal.ITIMER_REAL, 0)
        return v
    except Timeout:
        return None
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


def lex_compose(nT, arcsT, nH, arcsH):
    bT = core.beats_matrix(nT, arcsT)
    bH = core.beats_matrix(nH, arcsH)
    n = nT * nH
    arcs = []
    for a in range(nT):
        for b in range(nH):
            for ap in range(nT):
                for bp in range(nH):
                    if a == ap and b == bp:
                        continue
                    if bT[a][ap] or (a == ap and bH[b][bp]):
                        arcs.append((a * nH + b, ap * nH + bp))
    return n, arcs


def circ_arcs(p, g):
    return [(i, j) for i in range(p) for j in range(p)
            if i != j and ((j - i) % p) in g]


def diverse_factors():
    """A factor per (order, omega_vec) niche, deduped to avoid blowups.
    Covers omega_vec in {1,2,3} at small orders."""
    fs = []
    # TT1,TT2,TT3 -> omega_vec=1
    for k in [1, 2, 3]:
        nt, at = C.transitive_tournament(k)
        fs.append((f"TT{k}", nt, at, 1))
    # C3 -> omega_vec=2, order 3
    nc, ac = C.directed_C3()
    fs.append(("C3", nc, ac, 2))
    # one order-4 tournament with omega_vec=2 (pick first such)
    for nt, at in C.all_tournaments(4):
        if core.omega_vec(nt, at) == 2:
            fs.append(("T4_ov2", nt, at, 2)); break
    # AC7 / QR7 -> omega_vec=3, order 7
    ac7 = circ_arcs(7, {1, 2, 4})
    fs.append(("AC7", 7, ac7, 3))
    return fs


def main():
    t0 = time.time()
    out = {"products": [], "factors": []}
    fs = diverse_factors()
    for (name, nt, at, ov_claim) in fs:
        assert core.is_tournament(nt, at), f"{name} not tournament"
        ov = core.omega_vec(nt, at)
        out["factors"].append({"name": name, "order": nt, "ov": ov})
        assert ov == ov_claim, f"{name} ov={ov} != claimed {ov_claim}"

    facts = [(name, nt, at, core.omega_vec(nt, at)) for (name, nt, at, _) in fs]

    products = []
    disagreements = []
    seen = set()
    PER_CALL_SECS = 40
    for (nameT, nT, aT, ovT) in facts:
        for (nameH, nH, aH, ovH) in facts:
            N = nT * nH
            if N < 2 or N > 12:
                continue
            Np, A = lex_compose(nT, aT, nH, aH)
            key = (Np, tuple(sorted(A)))
            if key in seen:
                continue
            seen.add(key)
            assert core.is_tournament(Np, A)
            ovp = omega_vec_guarded(Np, A, PER_CALL_SECS)
            pred = ovT + ovH - 1
            if ovp is None:
                rec = {"prod": f"{nameT}[{nameH}]", "order": Np,
                       "ovT": ovT, "ovH": ovH, "pred": pred,
                       "ov_prod": None, "status": "timeout"}
            else:
                agree = (ovp == pred)
                rec = {"prod": f"{nameT}[{nameH}]", "order": Np,
                       "ovT": ovT, "ovH": ovH, "pred": pred,
                       "ov_prod": ovp, "agree": agree}
                if not agree:
                    disagreements.append(rec)
            products.append(rec)
            print(f"  {rec['prod']} order={Np} ovT={ovT} ovH={ovH} "
                  f"pred={pred} ov_prod={ovp} "
                  f"{'AGREE' if rec.get('agree') else rec.get('status','DISAGREE')}",
                  flush=True)

    completed = [p for p in products if p.get("ov_prod") is not None]
    out["products"] = products
    out["n_products"] = len(products)
    out["n_completed"] = len(completed)
    out["n_disagreements"] = len(disagreements)
    out["disagreements"] = disagreements
    out["all_agree"] = (len(disagreements) == 0 and len(completed) > 0)
    out["elapsed_s"] = round(time.time() - t0, 2)

    dp = os.path.join(os.path.dirname(__file__), "..", "data", "law_exact_sweep.json")
    with open(os.path.abspath(dp), "w") as f:
        json.dump(out, f, indent=2)

    print("\n=== SUMMARY ===", flush=True)
    print(json.dumps({
        "n_products": out["n_products"],
        "n_completed": out["n_completed"],
        "n_disagreements": out["n_disagreements"],
        "all_agree": out["all_agree"],
        "disagreements": disagreements,
        "elapsed_s": out["elapsed_s"],
    }, indent=2), flush=True)


if __name__ == "__main__":
    main()
