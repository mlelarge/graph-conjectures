"""GROUND the k=4 circulant proposal (D11, lens=explicit-construction).

Goal: find the SMALLEST 4-omega_vec-critical circulant via the EXACT omega_vec
oracle directly (decoupled from the dom reduction), and re-confirm that dom>=4
is almost-absent among circulants (forcing Paley, no ladder).

Plan:
 (1) for n in [13,15], enumerate ALL valid circulant tournament generators g
     (exactly one of {x, n-x} in g for each antipodal pair, |g|=(n-1)//2);
 (2) filter to those with identity-order backedge clique == 4
     (necessary upper-bound filter: omega_vec <= omega_of_order(identity));
 (3) for each survivor, EXACT ov = core.omega_vec_bb(n, arcs, ub=4); if ov==4
     record core.is_k_omega_vec_critical(n, arcs, 4);
 (4) print omega_vec histogram, 4-critical generators, smallest 4-critical order.
 (5) re-confirm dom>=4 counts over the COMPLETE circulant enumeration for
     n in {13,15,17,19,21,23} (dom via vertex-0-fixed cover, sound by
     vertex-transitivity); list the n=19 dom>=4 generators.
 (6) test the two n=19 dom>=4 candidates (QR_19 and reverse) for exact
     omega_vec (ub=4) and (if ==4) one-vertex-deletion omega_vec (vertex-
     transitive, one deletion suffices for criticality of that one value).

Everything FOREGROUND, hard wall via signal.alarm.
"""
import sys, os, json, time, itertools, signal
sys.path.insert(0, os.path.dirname(__file__))
import core


def circ_arcs(n, g):
    return [(i, (i + d) % n) for i in range(n) for d in g]


def valid_generators(n):
    """Yield each valid circulant tournament generator g (a frozenset of the
    (n-1)//2 differences, exactly one per antipodal pair {x, n-x})."""
    m = (n - 1) // 2
    pairs = [(x, n - x) for x in range(1, m + 1)]  # x in 1..m, partner n-x in m+1..n-1
    for choice in itertools.product(*[(a, b) for (a, b) in pairs]):
        yield frozenset(choice)


def identity_clique(n, g):
    """omega of the identity-order backedge graph (arcs going 'backward' under
    natural order 0<1<...<n-1).  Uses core for soundness."""
    arcs = circ_arcs(n, g)
    return core.omega_of_order(n, arcs, list(range(n)))


def dom_vt(n, g, ub):
    """dom(circulant) via cover sets that CONTAIN vertex 0 (sound by vertex-
    transitivity: some minimum dominating set contains 0 after rotation).
    Returns dom if <= ub else ub+1."""
    # closed[v] = {v} U out-neighbours = {(v+d)%n : d in {0} U g}
    Ng = {0} | set(g)
    closed = [frozenset((v + d) % n for d in Ng) for v in range(n)]
    full = set(range(n))
    if closed[0] == full:
        return 1
    others = [v for v in range(n)]
    # size 1 already handled (need vertex 0 in set; closed[0] != full)
    for size in range(2, ub + 1):
        for rest in itertools.combinations(range(1, n), size - 1):
            cov = set(closed[0])
            for x in rest:
                cov |= closed[x]
                if len(cov) == n:
                    break
            if cov == full:
                return size
    return ub + 1


class Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise Timeout()


def main():
    out = {}

    # -------- (5)+(part of 1) dom>=4 census over complete circulant enum -------
    dom_counts = {}
    dom_ge4_gens = {}
    t0 = time.time()
    for n in [13, 15, 17, 19, 21, 23]:
        cnt = 0
        gens = []
        total = 0
        for g in valid_generators(n):
            total += 1
            d = dom_vt(n, g, ub=3)   # if >3 then dom>=4
            if d > 3:
                cnt += 1
                gens.append(sorted(g))
        dom_counts[n] = cnt
        dom_ge4_gens[n] = gens
        print(f"[dom>=4 census] n={n}: total_generators={total} dom>=4 count={cnt}"
              f"  gens={gens}", flush=True)
    out["dom_ge4_counts"] = dom_counts
    out["dom_ge4_generators"] = dom_ge4_gens
    out["dom_census_time_s"] = round(time.time() - t0, 2)

    # -------- (1)-(4) exact omega_vec scan for n in {13,15} --------------------
    scan = {}
    for n in [13, 15]:
        hist = {}
        crit_gens = []
        ov4_gens = []
        n_idclique4 = 0
        t0 = time.time()
        for g in valid_generators(n):
            arcs = circ_arcs(n, g)
            idc = core.omega_of_order(n, arcs, list(range(n)))
            if idc != 4:
                continue
            n_idclique4 += 1
            ov = core.omega_vec_bb(n, arcs, ub=4)
            hist[ov] = hist.get(ov, 0) + 1
            if ov == 4:
                ov4_gens.append(sorted(g))
                if core.is_k_omega_vec_critical(n, arcs, 4):
                    crit_gens.append(sorted(g))
        scan[n] = {
            "n_identity_clique_eq_4": n_idclique4,
            "omega_vec_hist": {str(k): v for k, v in sorted(hist.items())},
            "omega_vec_eq_4_generators": ov4_gens,
            "four_critical_generators": crit_gens,
            "time_s": round(time.time() - t0, 2),
        }
        print(f"[exact scan] n={n}: idclique4={n_idclique4} hist={hist}"
              f" ov4={len(ov4_gens)} crit4={len(crit_gens)} crit_gens={crit_gens}"
              f" ({scan[n]['time_s']}s)", flush=True)
    out["exact_scan"] = scan

    smallest = None
    for n in [13, 15]:
        if scan[n]["four_critical_generators"]:
            smallest = n
            break
    out["smallest_4critical_order_in_13_15"] = smallest

    # -------- (6) the two n=19 dom>=4 candidates -------------------------------
    qr19 = sorted({pow(x, 2, 19) for x in range(1, 19)})  # quadratic residues mod 19
    rev19 = sorted({(19 - x) % 19 for x in qr19})
    cands = {"QR_19": qr19, "reverse_QR_19": rev19}
    n19 = {}
    for name, g in cands.items():
        gset = frozenset(g)
        is_tour = core.is_tournament(19, circ_arcs(19, gset))
        # valid generator check
        valid = all((len(gset & {x, 19 - x}) == 1) for x in range(1, 10)) and len(gset) == 9
        rec = {"g": sorted(gset), "is_tournament": is_tour, "valid_generator": valid}
        arcs = circ_arcs(19, gset)
        d = dom_vt(19, gset, ub=4)
        rec["dom"] = d if d <= 4 else ">4"
        # exact omega_vec with ub=4 (vertex-transitive; this is the whole-tournament value)
        signal.signal(signal.SIGALRM, _alarm)
        signal.alarm(700)
        try:
            t0 = time.time()
            ov = core.omega_vec_bb(19, arcs, ub=4)
            rec["omega_vec"] = ov
            rec["omega_vec_time_s"] = round(time.time() - t0, 2)
        except Timeout:
            rec["omega_vec"] = "TIMEOUT_700s"
        finally:
            signal.alarm(0)
        # deletion (one vertex suffices for the value by vertex-transitivity)
        if rec.get("omega_vec") == 4:
            nn, sub = core.subtournament(19, arcs, [w for w in range(19) if w != 0])
            signal.signal(signal.SIGALRM, _alarm)
            signal.alarm(700)
            try:
                t0 = time.time()
                ovd = core.omega_vec_bb(nn, sub, ub=4)
                rec["omega_vec_minus_0"] = ovd
                rec["deletion_time_s"] = round(time.time() - t0, 2)
                rec["critical_value_check"] = (ovd == 3)
            except Timeout:
                rec["omega_vec_minus_0"] = "TIMEOUT_700s"
            finally:
                signal.alarm(0)
        n19[name] = rec
        print(f"[n=19 candidate {name}] {rec}", flush=True)
    out["n19_dom_ge4_candidates"] = n19

    os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
    path = os.path.join(os.path.dirname(__file__), "..", "data", "scan_k4_circulant.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print("SAVED", os.path.abspath(path), flush=True)


if __name__ == "__main__":
    main()
