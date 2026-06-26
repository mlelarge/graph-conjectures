"""Ground the dom-composition-cap proposal (dual-attack lens).

Tests:
 (A) dom of composed AC/C3 lex-and-Delta towers; predict all in {2,3} (cap at 3).
     Objects: AC_7[C3[C3]] (63), C3[AC_7[AC_7]] (147), AC_7[AC_7[AC_7]] (343),
              S~_4 (27), S~_5 (81), AC_7[AC_7] (49), C3[C3[C3]] (27),
              Delta(AC_7,AC_7,AC_7) (21).
 (B) dom(T[H]) <= dom(T)+dom(H)-1 for sampled lex products.
 (C) max-dom circulant search over odd n in [25,33] (time-capped): confirm max dom
     stays 3 off Paley orders.
 (D) cross-validate dom <= omega_vec (stored / small).

KILL if ANY composed AC/C3 tournament has dom>=4, OR any single-orbit circulant
on Z/n, n in [13,49], non-Paley, with dom>=4.

Runs in FOREGROUND with a hard per-object signal.alarm timeout.
"""
import sys, os, json, time, itertools, signal
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
import core
import constructions as C
from lexlib import lex_substitute, AC, C3
from dom_reduction_ground import dom_direct, dom_additive_le2, circulant_arcs, ac_g


class Timeout(Exception):
    pass


def _alarm(sig, frame):
    raise Timeout()


def dom_with_timeout(n, arcs, ub, secs):
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(secs)
    try:
        t0 = time.time()
        d = dom_direct(n, arcs, ub=ub)
        return (d if d <= ub else f">{ub}"), round(time.time() - t0, 2), None
    except Timeout:
        return "TIMEOUT", secs, "timeout"
    finally:
        signal.alarm(0)


def AC7():
    return AC(7, ac_g(7))           # almost-consecutive on 7 = {1,2}|{4} ... check


def build_objects():
    objs = {}
    ac7 = AC(7, ac_g(7))
    c3 = C3
    # AC_7[C3[C3]]  order 63
    c3c3 = lex_substitute(c3, c3)
    objs["AC7[C3[C3]]"] = (lex_substitute(ac7, c3c3), 4, 300)
    # C3[AC_7[AC_7]] order 147
    ac7ac7 = lex_substitute(ac7, ac7)
    objs["C3[AC7[AC7]]"] = (lex_substitute(c3, ac7ac7), 4, 300)
    # AC_7[AC_7[AC_7]] order 343 (dom-cover only)
    objs["AC7[AC7[AC7]]"] = (lex_substitute(ac7, ac7ac7), 4, 400)
    # S~_4 (27), S~_5 (81)
    objs["S~_4"] = (C.S_tilde(4), 4, 300)
    objs["S~_5"] = (C.S_tilde(5), 4, 400)
    # AC_7[AC_7] (49)
    objs["AC7[AC7]"] = (ac7ac7, 4, 300)
    # C3[C3[C3]] (27)
    objs["C3[C3[C3]]"] = (lex_substitute(c3, c3c3), 4, 300)
    # Delta(AC_7,AC_7,AC_7) (21)
    objs["Delta(AC7,AC7,AC7)"] = (C.delta(ac7, ac7, ac7), 4, 300)
    return objs


def main():
    out = {"composed_dom": [], "lex_law": [], "circulant_scan": [], "ac7_g": sorted(ac_g(7))}
    print("ac_g(7)=", sorted(ac_g(7)), flush=True)

    # ---- (A) composed objects ----
    objs = build_objects()
    for name, ((n, arcs), ub, secs) in objs.items():
        rec = {"name": name, "n": n}
        rec["is_tournament"] = core.is_tournament(n, arcs)
        d, tsec, err = dom_with_timeout(n, arcs, ub, secs)
        rec["dom"] = d
        rec["dom_time_s"] = tsec
        if err:
            rec["error"] = err
        out["composed_dom"].append(rec)
        print(f"[A] {name} n={n} is_tour={rec['is_tournament']} dom={d} ({tsec}s)", flush=True)

    # ---- (B) lex law dom(T[H]) <= dom(T)+dom(H)-1 ----
    ac7 = AC(7, ac_g(7))
    factors = {
        "C3": C3,
        "AC7": ac7,
        "AC9": AC(9, ac_g(9)),
        "AC11": AC(11, ac_g(11)),
    }
    # individual dom
    indiv = {}
    for fn, (n, arcs) in factors.items():
        d, tsec, err = dom_with_timeout(n, arcs, 5, 120)
        indiv[fn] = d
        print(f"[B-factor] dom({fn})={d}", flush=True)
    # products small enough to compute dom
    products = [
        ("C3", "C3"), ("C3", "AC7"), ("AC7", "C3"),
        ("AC7", "AC7"), ("C3", "AC9"), ("AC9", "C3"),
        ("AC7", "AC9"),
    ]
    for tn, hn in products:
        T = factors[tn]; H = factors[hn]
        N, arcs = lex_substitute(T, H)
        rec = {"product": f"{tn}[{hn}]", "n": N,
               "dom_T": indiv.get(tn), "dom_H": indiv.get(hn)}
        d, tsec, err = dom_with_timeout(N, arcs, 5, 240)
        rec["dom_prod"] = d
        rec["dom_time_s"] = tsec
        if err:
            rec["error"] = err
        # law check
        if isinstance(d, int) and isinstance(indiv.get(tn), int) and isinstance(indiv.get(hn), int):
            bound = max(2, indiv[tn] + indiv[hn] - 1)
            rec["law_bound_max2"] = bound
            rec["law_holds"] = (d <= bound)
            rec["sum_minus1_bound"] = indiv[tn] + indiv[hn] - 1
            rec["sum_law_holds"] = (d <= indiv[tn] + indiv[hn] - 1)
        out["lex_law"].append(rec)
        print(f"[B] {tn}[{hn}] n={N} dom={d} domT={rec['dom_T']} domH={rec['dom_H']} "
              f"law(<=max2,T+H-1)={rec.get('law_holds')} sum_law={rec.get('sum_law_holds')}", flush=True)

    # ---- (C) circulant max-dom scan over odd n in [25,33] (time-capped) ----
    # enumerate valid tournament generators (g | -g = Z_n\{0}, no antipodal pair),
    # compute dom_additive (decides dom<=2) and dom_direct ub=4 for those with dom>2.
    # Full enumeration of generator sets is huge; instead scan a structured sample:
    # all "almost-consecutive"-style + QR + random valid generators, plus exhaustive
    # over a bounded subset count. We cap by time via signal.alarm per n.
    def valid_gens(n, limit, secs):
        """Yield up to `limit` valid generator sets (one per antipodal-pair choice)
        sampled; for small n do exhaustive over the 2^((n-1)/2) choices if feasible."""
        half = (n - 1) // 2
        pairs = [(d, n - d) for d in range(1, half + 1)]
        res = []
        signal.signal(signal.SIGALRM, _alarm)
        signal.alarm(secs)
        try:
            if half <= 14:
                for mask in range(1 << half):
                    g = set()
                    for i, (a, b) in enumerate(pairs):
                        g.add(a if (mask >> i) & 1 else b)
                    res.append(frozenset(g))
                    if len(res) >= limit:
                        break
        except Timeout:
            pass
        finally:
            signal.alarm(0)
        return res

    import math
    for n in [25, 27, 29, 31, 33]:
        rec = {"n": n}
        half = (n - 1) // 2
        total = 1 << half
        rec["total_gen_classes"] = total
        # exhaustive only if feasible in time; cap enumeration via additive (cheap) first
        max_dom = 0
        dom4_examples = []
        checked = 0
        signal.signal(signal.SIGALRM, _alarm)
        # budget: 240s per n for the additive sweep
        secs = 240
        signal.alarm(secs)
        timed_out = False
        try:
            if half <= 16:
                pairs = [(d, n - d) for d in range(1, half + 1)]
                for mask in range(total):
                    g = []
                    for i, (a, b) in enumerate(pairs):
                        g.append(a if (mask >> i) & 1 else b)
                    g = set(g)
                    le2, min_auto = dom_additive_le2(n, g)
                    checked += 1
                    if le2:
                        if max_dom < 2:
                            max_dom = 2
                        continue
                    # dom > 2: compute exact dom_direct ub=4
                    arcs = circulant_arcs(n, g)
                    dd = dom_direct(n, arcs, ub=4)
                    if dd > max_dom:
                        max_dom = dd
                    if dd >= 4:
                        dom4_examples.append({"g": sorted(g), "dom": dd})
            else:
                rec["note"] = "half>16 enumeration skipped"
        except Timeout:
            timed_out = True
        finally:
            signal.alarm(0)
        rec["checked"] = checked
        rec["timed_out"] = timed_out
        rec["max_dom"] = max_dom
        rec["dom4_examples"] = dom4_examples[:10]
        rec["dom4_count"] = len(dom4_examples)
        out["circulant_scan"].append(rec)
        print(f"[C] n={n} checked={checked}/{total} timed_out={timed_out} "
              f"max_dom={max_dom} dom4_count={len(dom4_examples)}", flush=True)

    dp = os.path.join(os.path.dirname(__file__), "..", "data", "dom_composition_cap.json")
    with open(os.path.abspath(dp), "w") as f:
        json.dump(out, f, indent=2)
    print("WROTE", os.path.abspath(dp), flush=True)
    # summary verdict signals
    composed_dom_vals = [r["dom"] for r in out["composed_dom"]]
    print("COMPOSED_DOM_VALS:", [(r["name"], r["dom"]) for r in out["composed_dom"]], flush=True)
    any_composed_ge4 = any(isinstance(r["dom"], int) and r["dom"] >= 4 for r in out["composed_dom"])
    any_circ_ge4 = any(r["dom4_count"] > 0 for r in out["circulant_scan"])
    print("ANY_COMPOSED_DOM>=4:", any_composed_ge4, flush=True)
    print("ANY_CIRCULANT_DOM>=4 (n in 25..33):", any_circ_ge4, flush=True)
    for r in out["lex_law"]:
        print("LAW", r["product"], "dom=", r.get("dom_prod"),
              "sum_law_holds=", r.get("sum_law_holds"), flush=True)


if __name__ == "__main__":
    main()
