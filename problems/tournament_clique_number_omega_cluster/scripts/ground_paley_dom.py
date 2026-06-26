"""GROUND the Graham-Spencer Paley-dom reduction proposal (lens=literature-reduction).

Computes dom(Paley(p)) = dom(QR_p) for the proposal's prime list and checks the
falsifiable prediction:
  dom(QR_p) for p in [7,11,19,23,31,43,47,59,67,71,79,83]
  predicted     = 3,  3, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5
  i.e. monotone non-decreasing, dom>=5 for all p>=67, dom=4 only finite window.

Also re-checks Property 3.2 direction dom(T) <= omega_vec(T) on a small control.

Arc convention: i -> (i+d) mod p for d in g (matches probe_p19 / dom_reduction_ground).
QR tournament needs p = 3 mod 4 so g = quadratic residues is a valid generator
(g and -g partition {1..p-1}); residues mod p that are 1 mod 4 give g symmetric -> NOT a tournament.
"""
import sys, os, json, time, itertools
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
import core


def qr_set(p):
    return sorted({(x * x) % p for x in range(1, p)})


def circulant_arcs(p, g):
    return [(i, (i + d) % p) for i in range(p) for d in g]


def dom_direct(n, arcs, ub=6):
    """Smallest |X| with closed-out-nbhd covering V; cap at ub (returns ub+1 if dom>ub)."""
    beats = core.beats_matrix(n, arcs)
    closed = []
    for v in range(n):
        s = {v}
        for w in range(n):
            if beats[v][w]:
                s.add(w)
        closed.append(s)
    full = set(range(n))
    for size in range(1, ub + 1):
        for X in itertools.combinations(range(n), size):
            cov = set()
            for x in X:
                cov |= closed[x]
                if len(cov) == n:
                    break
            if cov == full:
                return size
    return ub + 1


def main():
    primes = [7, 11, 19, 23, 31, 43, 47, 59, 67, 71, 79, 83]
    predicted = [3, 3, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5]
    out = {"scan": [], "monotone": None, "matches_prediction": None}

    print("p  | p%4 | is_tourn | dom(QR_p) | predicted | time_s", flush=True)
    doms = []
    for p, pred in zip(primes, predicted):
        g = qr_set(p)
        arcs = circulant_arcs(p, g)
        is_t = core.is_tournament(p, arcs)
        t0 = time.time()
        # cap ub: dom values are small (<=5 expected); ub=6 lets us see dom>5 as 7
        d = dom_direct(p, arcs, ub=6)
        dt = round(time.time() - t0, 2)
        doms.append(d)
        out["scan"].append({"p": p, "p_mod4": p % 4, "is_tournament": is_t,
                            "dom": d, "predicted": pred, "time_s": dt})
        print(f"{p:3d}|  {p%4}  | {is_t}    | {d}        | {pred}       | {dt}", flush=True)

    out["monotone"] = all(doms[i] <= doms[i + 1] for i in range(len(doms) - 1))
    out["matches_prediction"] = (doms == predicted)
    out["doms"] = doms
    out["predicted"] = predicted

    # dom>=5 for all p>=67 ?
    ge67 = [d for p, d in zip(primes, doms) if p >= 67]
    out["dom_ge5_for_p_ge_67"] = all(d >= 5 for d in ge67)
    # dom=4 window
    out["dom4_window"] = [p for p, d in zip(primes, doms) if d == 4]

    print("\nDOMS      :", doms, flush=True)
    print("PREDICTED :", predicted, flush=True)
    print("monotone non-decreasing:", out["monotone"], flush=True)
    print("matches prediction exactly:", out["matches_prediction"], flush=True)
    print("dom>=5 for all p>=67:", out["dom_ge5_for_p_ge_67"], flush=True)
    print("dom=4 window primes:", out["dom4_window"], flush=True)

    # --- Property 3.2 direction control: dom<=omega_vec on a small object ---
    # QR_7 small enough for exact omega_vec
    g7 = qr_set(7)
    arcs7 = circulant_arcs(7, g7)
    ov7 = core.omega_vec_bb(7, arcs7, ub=4)
    d7 = dom_direct(7, arcs7, ub=6)
    out["prop32_control_QR7"] = {"dom": d7, "omega_vec": ov7, "dom_le_ov": d7 <= ov7}
    print("\nProp3.2 control QR_7: dom=", d7, "omega_vec=", ov7,
          "dom<=ov:", d7 <= ov7, flush=True)

    with open(os.path.join(os.path.dirname(__file__), "..", "data", "ground_paley_dom.json"), "w") as f:
        json.dump(out, f, indent=2)


if __name__ == "__main__":
    main()
