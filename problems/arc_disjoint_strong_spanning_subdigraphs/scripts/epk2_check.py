"""Historical EPK-2 checker.

EPK-2 is FALSE.  The family B_k in `alpha1_core_counterexample.py` has
2^k minimum out-cut arc-sets avoiding one root, whereas an ordered pair of
spanning in-arborescences has at most (n-1)^2 transversal signatures.  At
k=6 this is 64 > 49, independently of which packing is chosen.  Retain this
script only as a record of the earlier finite-instance experiments and as a
checker for the still-valid Transversal Lemma.

Two claims being GROUNDED (both UNIVERSAL):

TRANSVERSAL LEMMA (Part 1, claimed symbolic-proof-essentially-complete):
  For a lambda-arc-strong digraph D, root r, and ANY Edmonds packing
  T_1..T_lambda of arc-disjoint spanning IN-arborescences to r, every global
  min-cut arc-set F = delta^+(X) with r NOT in X satisfies
     |F cap T_i| = 1 for all i   AND   F subset union(T_i).
  (A violation would contradict the claimed symbolic derivation.)

EPK-2 (Part 2, the falsifiable core):
  For every lambda-arc-strong D and root r there EXISTS a packing AND an ordered
  tree pair (T_a, T_b) such that  F |-> (F cap T_a, F cap T_b)  is INJECTIVE
  over all min-cut arc-sets F = delta^+(X) with side X avoiding r.
  This is the 2-respect (d=2) determination -> #distinct min-out-cut arc-sets
  <= 2(n-1)^2, the alpha=1 core of H5-DKSTAR.

KILL (verdict=fail): a single strong digraph D + root r such that NO in-arb
packing admits ANY injective ordered tree pair over the min-cut arc-sets with
side avoiding r (mirrored with out-packings for sides containing r), OR any
transversal-lemma violation.

Arcs carry a LABEL = index, so parallel arcs are distinct.  delta^+(X) := the
frozenset of LABELS of arcs leaving X.  A spanning in-arborescence to r is a
choice of exactly one out-arc (by label) for each v != r, acyclic, all reaching
r.  Packing = lambda mutually arc-disjoint such arborescences.
"""
import sys, os, json, time, itertools, subprocess, random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import oracle


# --------------------------------------------------------------------------- #
#  Labeled-arc primitives
# --------------------------------------------------------------------------- #
def labeled_arcs(arcs):
    return [(i, int(u), int(v)) for i, (u, v) in enumerate(arcs)]


def out_arc_labels(larcs, X):
    return frozenset(i for (i, u, v) in larcs if u in X and v not in X)


def min_outcut_arcsets_avoiding_r(n, larcs, r, lam):
    """All DISTINCT min-cut arc-sets F = delta^+(X) of size == lam with r not in X
    (X nonempty proper).  Returns set of frozensets-of-labels."""
    res = set()
    verts = list(range(n))
    for mask in range(1, (1 << n) - 1):
        X = frozenset(i for i in verts if (mask >> i) & 1)
        if r in X:
            continue
        F = out_arc_labels(larcs, X)
        if len(F) == lam:
            res.add(F)
    return res


# --------------------------------------------------------------------------- #
#  In-arborescence packing to root r
# --------------------------------------------------------------------------- #
def out_arcs_by_vertex(n, larcs):
    """vertex -> list of (label, head) for arcs LEAVING that vertex."""
    d = {v: [] for v in range(n)}
    for (i, u, v) in larcs:
        d[u].append((i, v))
    return d


def is_inarb(n, r, choice):
    """choice: dict v->(label,head) for v!=r.  Check every v reaches r (acyclic,
    all funnel to r)."""
    for start in range(n):
        if start == r:
            continue
        seen = set()
        cur = start
        while cur != r:
            if cur in seen:
                return False  # cycle, never reaches r
            seen.add(cur)
            if cur not in choice:
                return False
            cur = choice[cur][1]
    return True


def enumerate_inarbs(n, larcs, r, cap=None):
    """All spanning in-arborescences to r as frozenset-of-labels.  Each v!=r
    picks one out-arc.  cap limits product blow-up (then sample)."""
    obv = out_arcs_by_vertex(n, larcs)
    nonroot = [v for v in range(n) if v != r]
    # dead if any nonroot has no out-arc
    for v in nonroot:
        if not obv[v]:
            return []
    sizes = [len(obv[v]) for v in nonroot]
    total = 1
    for s in sizes:
        total *= s
    arbs = set()
    if cap is None or total <= cap:
        for combo in itertools.product(*[obv[v] for v in nonroot]):
            choice = {nonroot[i]: combo[i] for i in range(len(nonroot))}
            if is_inarb(n, r, choice):
                arbs.add(frozenset(combo[i][0] for i in range(len(nonroot))))
    else:
        rng = random.Random(12345)
        tries = 0
        target = min(cap, 4000)
        while len(arbs) < target and tries < cap * 4:
            tries += 1
            combo = tuple(rng.choice(obv[v]) for v in nonroot)
            choice = {nonroot[i]: combo[i] for i in range(len(nonroot))}
            if is_inarb(n, r, choice):
                arbs.add(frozenset(c[0] for c in combo))
    return list(arbs)


def find_packings(arbs, lam, max_packings=200):
    """Find arc-disjoint lambda-tuples of in-arborescences (as label-sets).
    Backtracking; returns up to max_packings ordered-lambda-tuples (each a list
    of label-frozensets)."""
    packings = []
    m = len(arbs)
    if m < lam:
        return packings

    def bt(start, chosen, used):
        if len(packings) >= max_packings:
            return
        if len(chosen) == lam:
            packings.append(list(chosen))
            return
        # prune: need lam-len(chosen) more from arbs[start:]
        for i in range(start, m):
            A = arbs[i]
            if used & A:
                continue
            chosen.append(A)
            bt(i + 1, chosen, used | A)
            chosen.pop()
            if len(packings) >= max_packings:
                return

    bt(0, [], frozenset())
    return packings


# --------------------------------------------------------------------------- #
#  The two checks for one (D, r) root-case (side avoiding r, in-packings)
# --------------------------------------------------------------------------- #
def check_root_case(n, larcs, r, lam, packings, mincuts):
    """Return dict: transversal violations + whether an injective d2-pair exists
    over SOME packing.  mincuts = set of min-cut arc-sets (frozensets of labels)
    with side avoiding r."""
    transversal_violations = []
    found_injective_pair = False
    pair_witness = None

    if not mincuts:
        # no min-cuts on this side -> EPK-2 vacuously holds, transversal vacuous
        return {"transversal_violations": [], "injective_pair": True,
                "n_mincuts": 0, "n_packings": len(packings),
                "vacuous": True}

    for pk in packings:
        # transversal lemma check for THIS packing
        union = frozenset().union(*pk)
        ok_packing = True
        for F in mincuts:
            for Ti in pk:
                if len(F & Ti) != 1:
                    transversal_violations.append(
                        {"root": r, "F": sorted(F), "tree": sorted(Ti),
                         "inter": len(F & Ti)})
                    ok_packing = False
            if not (F <= union):
                transversal_violations.append(
                    {"root": r, "F": sorted(F), "not_subset_union": True})
                ok_packing = False
        # d2 injective pair: try every ordered tree pair (a,b)
        if not found_injective_pair:
            L = len(pk)
            for a in range(L):
                for b in range(L):
                    sigs = {}
                    inj = True
                    for F in mincuts:
                        sig = (frozenset(F & pk[a]), frozenset(F & pk[b]))
                        if sig in sigs and sigs[sig] != F:
                            inj = False
                            break
                        sigs[sig] = F
                    if inj:
                        found_injective_pair = True
                        pair_witness = {"root": r, "a": a, "b": b}
                        break
                if found_injective_pair:
                    break

    return {"transversal_violations": transversal_violations,
            "injective_pair": found_injective_pair,
            "pair_witness": pair_witness,
            "n_mincuts": len(mincuts),
            "n_packings": len(packings),
            "vacuous": False}


def reverse_arcs(arcs):
    return [(v, u) for (u, v) in arcs]


def check_digraph(n, arcs, tag, arb_cap=20000, max_packings=200):
    """Full EPK-2 + transversal check for ALL roots.  IN-packings handle sides
    avoiding r; OUT-packings (= in-packings on the reverse digraph, sides
    containing r become sides avoiding r) handle the mirror.  Returns a record;
    is_kill=True iff some root-case finds NO injective pair across all packings,
    OR a transversal violation occurs."""
    lam = oracle.arc_connectivity(n, arcs)
    if lam < 1:
        return {"tag": tag, "strong": False, "lambda": lam, "skip": True}

    larcs = labeled_arcs(arcs)
    rlarcs = labeled_arcs(reverse_arcs(arcs))  # same labels, reversed direction

    kills = []
    transversal_violations = []
    worst = {"min_packings_seen": None}

    for r in range(n):
        # --- side avoiding r: IN-arborescence packing to r ---
        mincuts = min_outcut_arcsets_avoiding_r(n, larcs, r, lam)
        arbs = enumerate_inarbs(n, larcs, r, cap=arb_cap)
        packings = find_packings(arbs, lam, max_packings=max_packings)
        if mincuts and not packings:
            # Edmonds guarantees lam arc-disjoint in-arbs exist for lam-arc-strong;
            # if we found none, our enumeration capped out -> report, not a kill
            kills.append({"root": r, "side": "avoiding_r", "reason":
                          "NO_PACKING_FOUND (enumeration cap)", "lambda": lam,
                          "n_arbs": len(arbs), "n_mincuts": len(mincuts)})
            continue
        res = check_root_case(n, larcs, r, lam, packings, mincuts)
        transversal_violations += res["transversal_violations"]
        if not res["injective_pair"]:
            kills.append({"root": r, "side": "avoiding_r",
                          "reason": "NO_INJECTIVE_PAIR", "lambda": lam,
                          "n_mincuts": res["n_mincuts"],
                          "n_packings": res["n_packings"]})

        # --- side CONTAINING r: OUT-arborescence packing FROM r ---
        # delta^+(X) with r in X. In reverse digraph, delta^+_rev(V\X) with side
        # V\X avoiding r and labels preserved -> mirror via reverse + in-arbs.
        # min-cut arc-sets containing-r side, expressed in ORIGINAL labels:
        mincuts_rev = min_outcut_arcsets_avoiding_r(n, rlarcs, r, lam)
        arbs_rev = enumerate_inarbs(n, rlarcs, r, cap=arb_cap)
        packings_rev = find_packings(arbs_rev, lam, max_packings=max_packings)
        if mincuts_rev and not packings_rev:
            kills.append({"root": r, "side": "containing_r", "reason":
                          "NO_PACKING_FOUND (enumeration cap)", "lambda": lam,
                          "n_arbs": len(arbs_rev),
                          "n_mincuts": len(mincuts_rev)})
            continue
        res2 = check_root_case(n, rlarcs, r, lam, packings_rev, mincuts_rev)
        transversal_violations += res2["transversal_violations"]
        if not res2["injective_pair"]:
            kills.append({"root": r, "side": "containing_r",
                          "reason": "NO_INJECTIVE_PAIR", "lambda": lam,
                          "n_mincuts": res2["n_mincuts"],
                          "n_packings": res2["n_packings"]})

    real_kills = [k for k in kills if k["reason"] == "NO_INJECTIVE_PAIR"]
    cap_misses = [k for k in kills if k["reason"].startswith("NO_PACKING")]
    return {"tag": tag, "n": n, "lambda": lam,
            "is_kill": len(real_kills) > 0 or len(transversal_violations) > 0,
            "real_kills": real_kills,
            "cap_misses": cap_misses,
            "n_transversal_violations": len(transversal_violations),
            "transversal_violations": transversal_violations[:5],
            "arcs": [list(a) for a in arcs]}


# --------------------------------------------------------------------------- #
#  Generators
# --------------------------------------------------------------------------- #
def gen_simple_digraphs(n):
    geng = subprocess.Popen(["geng", "-cq", str(n)], stdout=subprocess.PIPE)
    directg = subprocess.Popen(["directg", "-Tq"], stdin=geng.stdout,
                               stdout=subprocess.PIPE)
    geng.stdout.close()
    for line in directg.stdout:
        line = line.decode().strip()
        if not line:
            continue
        toks = line.split()
        nv = int(toks[0]); nums = list(map(int, toks[2:]))
        arcs = [(nums[i], nums[i + 1]) for i in range(0, len(nums), 2)]
        yield nv, arcs
    directg.wait(); geng.wait()


def bidirected_K22():
    # arcs 02,03,12,13,20,21,30,31 (CHARGE-2 witness from the proposal)
    return 4, [(0, 2), (0, 3), (1, 2), (1, 3), (2, 0), (2, 1), (3, 0), (3, 1)]


def g11_bundle(k, mult=3):
    s, o = 0, 1
    arcs = [(s, o)] * mult + [(o, s)] * mult
    for j in range(k):
        p = 2 + j
        arcs += [(s, p)] * mult + [(p, o)] * mult
    return (k + 2), arcs


def Kstar(n):
    return n, [(i, j) for i in range(n) for j in range(n) if i != j]


def doubled_cycle(n):
    arcs = []
    for i in range(n):
        arcs += [(i, (i + 1) % n), (i, (i + 2) % n)]
    return n, arcs


def random_multidigraph(n, maxmult, rng):
    arcs = []
    for u in range(n):
        for v in range(n):
            if u == v:
                continue
            m = rng.randint(0, maxmult)
            arcs += [(u, v)] * m
    return n, arcs


# --------------------------------------------------------------------------- #
#  Main: census + stressors
# --------------------------------------------------------------------------- #
def main():
    t0 = time.time()
    cfg = {a: True for a in sys.argv[1:] if a.startswith("--") is False}
    args = sys.argv[1:]
    do_n4 = "--exhaustive-n4" in args
    do_n5 = "--isofree-n5" in args
    n5_cap = None
    if "--isofree-n5-cap" in args:
        i = args.index("--isofree-n5-cap")
        n5_cap = int(args[i + 1])
        do_n5 = True
    rand_n = 0
    if "--random-multi" in args:
        i = args.index("--random-multi")
        rand_n = int(args[i + 1])
    seed = 0
    if "--seed" in args:
        seed = int(args[args.index("--seed") + 1])

    kills = []
    transv = 0
    census = {}

    # ---- exhaustive n=4 simple ----
    if do_n4:
        c = {"n_read": 0, "n_strong": 0, "kills": 0, "transv": 0,
             "cap_misses": 0}
        for nv, arcs in gen_simple_digraphs(4):
            c["n_read"] += 1
            rec = check_digraph(nv, arcs, "n4")
            if rec.get("skip"):
                continue
            c["n_strong"] += 1
            c["cap_misses"] += len(rec.get("cap_misses", []))
            c["transv"] += rec["n_transversal_violations"]
            transv += rec["n_transversal_violations"]
            if rec["is_kill"]:
                c["kills"] += 1
                kills.append(rec)
        census["n4_exhaustive"] = c

    # ---- iso-free n=5 simple ----
    if do_n5:
        c = {"n_read": 0, "n_strong": 0, "kills": 0, "transv": 0,
             "cap_misses": 0, "capped": n5_cap}
        for nv, arcs in gen_simple_digraphs(5):
            c["n_read"] += 1
            if n5_cap is not None and c["n_strong"] >= n5_cap:
                c["stopped_at_cap"] = True
                break
            rec = check_digraph(nv, arcs, "n5")
            if rec.get("skip"):
                continue
            c["n_strong"] += 1
            c["cap_misses"] += len(rec.get("cap_misses", []))
            c["transv"] += rec["n_transversal_violations"]
            transv += rec["n_transversal_violations"]
            if rec["is_kill"]:
                c["kills"] += 1
                kills.append(rec)
        census["n5_isofree"] = c

    # ---- stressors ----
    stress = []
    def run_stress(tag, n, arcs):
        rec = check_digraph(n, arcs, tag)
        nonlocal transv
        transv += rec.get("n_transversal_violations", 0)
        if rec.get("is_kill"):
            kills.append(rec)
        stress.append({"tag": tag, "n": rec.get("n"),
                       "lambda": rec.get("lambda"),
                       "is_kill": rec.get("is_kill"),
                       "n_transv": rec.get("n_transversal_violations"),
                       "real_kills": rec.get("real_kills"),
                       "cap_misses": len(rec.get("cap_misses", []))})

    n, arcs = bidirected_K22(); run_stress("bidir_K22", n, arcs)
    for k in (3, 5, 8):
        n, arcs = g11_bundle(k, 3); run_stress(f"g11_k{k}", n, arcs)
    for nn in (4, 5):
        n, arcs = Kstar(nn); run_stress(f"Kstar_{nn}", n, arcs)
    for nn in (4, 5, 6):
        n, arcs = doubled_cycle(nn); run_stress(f"C{nn}^2", n, arcs)

    # ---- random multidigraphs ----
    if rand_n:
        rng = random.Random(seed)
        rc = {"n_attempt": 0, "n_strong": 0, "kills": 0, "transv": 0,
              "cap_misses": 0}
        done = 0
        rc["lambda_skipped_dense"] = 0
        n5only = "--rand-n5-only" in args
        while done < rand_n:
            nn = 5 if n5only else rng.choice([5, 6])
            n, arcs = random_multidigraph(nn, rng.choice([1, 2, 3]), rng)
            if not arcs:
                continue
            rc["n_attempt"] += 1
            lam = oracle.arc_connectivity(n, arcs)
            if lam < 1:
                continue
            if lam > 5:
                # dense high-lambda: packing/d2 search blows up; skip to keep
                # the random arm foreground-feasible (K* / structured high-lambda
                # already covered exactly by the stressor arm)
                rc["lambda_skipped_dense"] += 1
                continue
            done += 1
            rec = check_digraph(n, arcs, "rand_multi", arb_cap=3000,
                                max_packings=40)
            rc["n_strong"] += 1
            rc["cap_misses"] += len(rec.get("cap_misses", []))
            rc["transv"] += rec["n_transversal_violations"]
            transv += rec["n_transversal_violations"]
            if rec["is_kill"]:
                rc["kills"] += 1
                kills.append(rec)
        census["random_multi"] = rc

    out = {
        "elapsed_s": round(time.time() - t0, 2),
        "census": census,
        "stressors": stress,
        "total_real_kills": sum(len([k for k in kills if k.get("real_kills")]) for _ in [0]),
        "n_kill_records": len(kills),
        "total_transversal_violations": transv,
        "EPK2_survives": len(kills) == 0 and transv == 0,
        "kill_records": kills[:10],
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
