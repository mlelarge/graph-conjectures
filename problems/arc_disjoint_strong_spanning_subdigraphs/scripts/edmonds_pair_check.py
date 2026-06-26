"""EDMONDS-TRANSVERSAL route to DK* alpha=1 (H5-DKSTAR).

Two-part proposal:

  Part (i) TRANSVERSAL LEMMA: fix a root r and an Edmonds packing of lambda
    arc-disjoint spanning OUT-arborescences O_1..O_lambda from r.  Every
    MIN-out-cut arc-set F = delta^+(X) with |F| = lambda and r in X is a
    PERFECT TRANSVERSAL of {O_i}: |F cap O_i| = 1 for every i AND F subseteq
    union_i O_i.  (Dually for IN-arborescences and r outside X.)

  Part (ii) PAIR-DETERMINATION (the crux): the map
       F  -->  (F cap O_1, F cap O_2)
    is INJECTIVE over the distinct min-out-cut arc-set classes (r in X side).
    If (ii) holds, #distinct min-out-cut arc-sets <= 2*(n-1)^2 = the DK* alpha=1
    core.

FALSIFIABLE PREDICTION (KILL of (ii)): a digraph D, root r, valid Edmonds
out-packing (or in-packing), and TWO DISTINCT min-out-cut arc-set classes
F != F' with F cap O_1 = F' cap O_1 and F cap O_2 = F' cap O_2.
KILL of (i): a min-out-cut class with r-in representative where some O_i has
|F cap O_i| != 1, or an arc of F outside union O_i.

We honor LABELED parallel arcs (label = index in arc list).  delta^+(X) is the
frozenset of labels leaving X; an arborescence is a frozenset of labels.

Usage:
  edmonds_pair_check.py --exhaustive 4 5 --adversarial all --max-packings 200
"""
import sys, os, json, time, itertools, subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import oracle


# ----------------------------- arc-set helpers --------------------------- #
def labeled_arcs(arcs):
    return [(i, u, v) for i, (u, v) in enumerate(arcs)]


def out_labels(larcs, X):
    """frozenset of labels of arcs leaving X."""
    return frozenset(i for (i, u, v) in larcs if u in X and v not in X)


def min_out_cut_classes(n, larcs, lam):
    """All DISTINCT labeled arc-sets delta^+(X) of size == lam (the MIN cut),
    each with the list of vertex-sets X realizing it and X^min (intersection)
    / X^max (union) reps.  Returns dict: F(frozenset) -> {Xs:[frozenset], ...}.
    Enumerate all proper nonempty subsets (n<=6 feasible)."""
    classes = {}
    verts = list(range(n))
    for mask in range(1, (1 << n) - 1):
        X = frozenset(i for i in verts if (mask >> i) & 1)
        F = out_labels(larcs, X)
        if len(F) != lam:
            continue
        classes.setdefault(F, []).append(X)
    return classes


# ----------------------- Edmonds out-arborescence packing ---------------- #
def all_arborescences(n, out_by, root, forbidden, cap=200000):
    """ALL spanning out-arborescences (frozenset of labels) avoiding `forbidden`.

    A spanning out-arborescence from `root` = a choice of EXACTLY ONE in-arc per
    non-root vertex such that the chosen-arc digraph is acyclic and every vertex
    is reachable from root.  We enumerate the product of per-vertex in-arc
    choices (NO order-duplication, unlike discovery-order growth) and keep the
    valid ones.  Bounded by prod(indeg); fine for the small n / small adversarial
    instances here.
    """
    in_arcs_by = {v: [] for v in range(n)}
    for u in out_by:
        for (i, v) in out_by[u]:
            if i not in forbidden:
                in_arcs_by[v].append((i, u))
    nonroot = [v for v in range(n) if v != root]
    # prune: every nonroot vertex must have at least one in-arc
    for v in nonroot:
        if not in_arcs_by[v]:
            return []

    results = []

    def rec(idx, chosen_labels, parent):
        if len(results) >= cap:
            return
        if idx == len(nonroot):
            # validate: acyclic + reachable from root
            # parent[v] gives the tail; build child adjacency and BFS from root
            adj = {u: [] for u in range(n)}
            for v in nonroot:
                adj[parent[v]].append(v)
            seen = {root}
            stack = [root]
            while stack:
                x = stack.pop()
                for y in adj[x]:
                    if y not in seen:
                        seen.add(y)
                        stack.append(y)
            if len(seen) == n:
                results.append(frozenset(chosen_labels))
            return
        v = nonroot[idx]
        for (i, u) in in_arcs_by[v]:
            parent[v] = u
            chosen_labels.append(i)
            rec(idx + 1, chosen_labels, parent)
            chosen_labels.pop()
            if len(results) >= cap:
                return

    rec(0, [], {})
    return results


def _random_arborescence(n, out_by, root, rng):
    """One random spanning out-arborescence (frozenset of labels) via random-BFS
    frontier growth, or None if growth gets stuck (graph not root-connected)."""
    in_arc = {root: None}
    labels = []
    frontier = list(out_by[root])  # (label, v)
    rng.shuffle(frontier)
    while len(in_arc) < n:
        # rebuild frontier of arcs from covered to uncovered
        opts = []
        for u in in_arc:
            for (i, v) in out_by[u]:
                if v not in in_arc:
                    opts.append((i, v))
        if not opts:
            return None
        i, v = rng.choice(opts)
        in_arc[v] = i
        labels.append(i)
    return frozenset(labels)


def pack_out_arborescences(n, larcs, lam, root, max_packings):
    """Enumerate (up to max_packings) sets of lam ARC-DISJOINT spanning
    out-arborescences rooted at `root`.  Each packing = tuple of `lam`
    frozensets(labels), pairwise arc-disjoint.

    Implementation: SIMULTANEOUS backtracking.  We build the lam trees together
    in a single DFS that, at each step, picks a non-root vertex v not yet
    covered by tree t and assigns it an in-arc (label not used by ANY of the lam
    trees so far -> automatic arc-disjointness).  This avoids enumerating the
    full (possibly exponential) arborescence list and prunes via global
    disjointness immediately.

    Soundness: by Edmonds' branching theorem a lam-arc-strong digraph has lam
    arc-disjoint spanning out-arborescences from EVERY root, so for lam>=2 at
    least one packing MUST be found; a count of 0 flags a bug (asserted by the
    caller's diagnostics).
    """
    out_by = {u: [] for u in range(n)}
    for (i, u, v) in larcs:
        out_by[u].append((i, v))

    # Cap the candidate-arborescence list: we only need a FEW disjoint packings,
    # not the full (possibly astronomically large) set.  This keeps the packer
    # foreground-feasible on dense multidigraphs (e.g. the private-in pocket).
    # We also inject DIVERSE random arborescences (random-BFS growth) so the
    # candidate pool is not dominated by trees that all share the same low-index
    # in-arcs (which would never be mutually disjoint).
    DET_CAP = 2000
    det = all_arborescences(n, out_by, root, frozenset(), cap=DET_CAP)
    cand = set(det)
    if len(det) >= DET_CAP:
        # enumeration was truncated (dense instance) -> the first DET_CAP trees
        # may all share low-index in-arcs and never be mutually disjoint.  Inject
        # DIVERSE random arborescences so the candidate pool can realize packings.
        import random as _rnd
        rng = _rnd.Random(12345)
        for _ in range(5000):
            t = _random_arborescence(n, out_by, root, rng)
            if t is not None:
                cand.add(t)
    all_arbs = list(cand)
    packings = []

    def backtrack(forbidden, current):
        if len(packings) >= max_packings:
            return
        if len(current) == lam:
            packings.append(tuple(current))
            return
        for tree in all_arbs:
            if forbidden & tree:
                continue
            if tree in current:
                continue
            current.append(tree)
            backtrack(forbidden | tree, current)
            current.pop()
            if len(packings) >= max_packings:
                return

    backtrack(frozenset(), [])
    return packings


# ------------------------- the two-part check ---------------------------- #
def check_instance(n, arcs, max_packings, side="out"):
    """Run Part (i) and Part (ii) checks for ONE digraph on the chosen side.
    side='out': out-arborescences from r, classes with r in X.
    side='in' : in-arborescences to r (== out-arborescences of reverse), and
                classes whose COMPLEMENT contains r (i.e. r not in X).
    Returns dict with violation lists.
    """
    larcs = labeled_arcs(arcs)
    lam = oracle.arc_connectivity(n, arcs)
    res = {"n": n, "lambda": lam, "side": side,
           "part_i_violations": [], "part_ii_violations": [],
           "n_classes": 0, "n_packings_total": 0}
    if lam < 2:
        res["skip"] = "lambda<2"
        return res

    if side == "in":
        rarcs = [(v, u) for (u, v) in arcs]
        rlarcs = labeled_arcs(rarcs)  # SAME labels (index preserved)
    else:
        rlarcs = larcs

    classes = min_out_cut_classes(n, larcs, lam)
    res["n_classes"] = len(classes)

    for root in range(n):
        # pack on the side's digraph
        if side == "out":
            packings = pack_out_arborescences(n, rlarcs, lam, root, max_packings)
            # classes with r in X
            rel_classes = {F: Xs for F, Xs in classes.items()
                           if any(root in X for X in Xs)}
        else:
            # in-arborescences to root == out-arborescences in reverse digraph
            packings = pack_out_arborescences(n, rlarcs, lam, root, max_packings)
            # in-packing constrains min-IN-cuts delta^-(X) = delta^+(complement)
            # A min-in-cut at X (r not in X) has arc-set delta^-(X) = the labels
            # of arcs ENTERING X. In the reverse digraph, those are arcs leaving
            # X. The proposal's dual: classes with r OUTSIDE X^max are perfect
            # transversals of {I_i}.  We test on delta^-(X) classes: equivalently
            # min-out-cut classes of the REVERSE digraph.
            rev_classes = min_out_cut_classes(n, rlarcs, lam)
            rel_classes = {F: Xs for F, Xs in rev_classes.items()
                           if any(root in X for X in Xs)}

        res["n_packings_total"] += len(packings)
        if not packings:
            continue

        for packing in packings:
            O = list(packing)  # O[0..lam-1], each frozenset of labels
            # ---- Part (i): perfect transversality of every relevant class ----
            for F, Xs in rel_classes.items():
                # representative X with root in X (out) / root in X (rev)
                Xrep = next((X for X in Xs if root in X), None)
                if Xrep is None:
                    continue
                union_O = frozenset().union(*O)
                # F subseteq union O ?
                if not F.issubset(union_O):
                    res["part_i_violations"].append({
                        "root": root, "F": sorted(F), "Xrep": sorted(Xrep),
                        "reason": "F not subset of union O",
                        "missing": sorted(F - union_O)})
                for i, Oi in enumerate(O):
                    inter = len(F & Oi)
                    if inter != 1:
                        res["part_i_violations"].append({
                            "root": root, "F": sorted(F), "Xrep": sorted(Xrep),
                            "reason": f"|F cap O_{i}|={inter} != 1"})
            # ---- Part (ii): injectivity of F -> (F cap O_0, F cap O_1) -------
            pair_map = {}
            for F in rel_classes:
                key = (F & O[0], F & O[1])
                if key in pair_map and pair_map[key] != F:
                    res["part_ii_violations"].append({
                        "root": root,
                        "F": sorted(F), "Fprime": sorted(pair_map[key]),
                        "O0": sorted(O[0]), "O1": sorted(O[1]),
                        "shared_capO0": sorted(F & O[0]),
                        "shared_capO1": sorted(F & O[1]),
                        "arcs": [list(a) for a in arcs]})
                else:
                    pair_map[key] = F
            # only need ONE packing per (D,root) for part(ii) to be meaningful;
            # but check all enumerated for thoroughness
    return res


# ----------------------------- adversarial ------------------------------- #
def g11_inout_bundle(k, mult=3):
    s, o = 0, 1
    arcs = [(s, o)] * mult + [(o, s)] * mult
    for j in range(k):
        p = 2 + j
        arcs += [(s, p)] * mult + [(p, o)] * mult
    return (k + 2), arcs


def bidirected_cycle(n):
    arcs = []
    for i in range(n):
        arcs += [(i, (i + 1) % n), ((i + 1) % n, i)]
    return n, arcs


def tripled_cycle(n):
    arcs = []
    for i in range(n):
        arcs += [(i, (i + 1) % n)] * 3
    return n, arcs


def private_in_pocket():
    """x1,x2 digon mult 3; x2->o mult 3; outer tripled directed cycle
    w_0..w_9 with o=w_0; each w_i -> x1 single arc.  x1=10, x2=11, w_i = 0..9,
    o = w_0 = 0."""
    x1, x2 = 10, 11
    W = list(range(10))  # w_0..w_9
    o = W[0]
    arcs = []
    arcs += [(x1, x2)] * 3 + [(x2, x1)] * 3
    arcs += [(x2, o)] * 3
    for i in range(10):
        arcs += [(W[i], W[(i + 1) % 10])] * 3   # tripled directed outer cycle
    for i in range(10):
        arcs += [(W[i], x1)]                     # private in-arc into x1
    return 12, arcs


def adversarial_instances():
    inst = []
    for k in (2, 3):
        inst.append((f"g11_inout_k{k}",) + g11_inout_bundle(k))
    for n in range(6, 13):
        inst.append((f"bidir_cycle_n{n}",) + bidirected_cycle(n))
    inst.append(("tripled_cycle_n8",) + tripled_cycle(8))
    inst.append(("private_in_pocket",) + private_in_pocket())
    return inst


# --------------------------------- driver -------------------------------- #
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


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--exhaustive", nargs="*", type=int, default=[])
    ap.add_argument("--adversarial", default="")
    ap.add_argument("--max-packings", type=int, default=200)
    args = ap.parse_args()

    t0 = time.time()
    part_i_kills = []
    part_ii_kills = []
    stats = {"n_decided": 0, "n_lam_ge2": 0, "n_classes_total": 0}
    worst = {"max_classes_for_n": {}}

    def absorb(res, tag):
        if res.get("skip"):
            return
        stats["n_lam_ge2"] += 1
        stats["n_classes_total"] += res["n_classes"]
        nn = res["n"]
        worst["max_classes_for_n"][nn] = max(
            worst["max_classes_for_n"].get(nn, 0), res["n_classes"])
        for v in res["part_i_violations"]:
            part_i_kills.append({"tag": tag, **v})
        for v in res["part_ii_violations"]:
            part_ii_kills.append({"tag": tag, **v})

    # exhaustive generic census
    for n in args.exhaustive:
        cnt = 0
        for nv, arcs in gen_simple_digraphs(n):
            stats["n_decided"] += 1
            for side in ("out", "in"):
                res = check_instance(nv, arcs, args.max_packings, side=side)
                absorb(res, f"generic_n{n}_{side}")
            cnt += 1
        stats[f"generic_n{n}_read"] = cnt

    # adversarial
    if args.adversarial:
        for entry in adversarial_instances():
            tag = entry[0]; nv = entry[1]; arcs = entry[2]
            stats["n_decided"] += 1
            for side in ("out", "in"):
                res = check_instance(nv, arcs, args.max_packings, side=side)
                absorb(res, f"adv_{tag}_{side}")

    out = {
        "elapsed_s": round(time.time() - t0, 2),
        "stats": stats,
        "worst": worst,
        "n_part_i_violations": len(part_i_kills),
        "n_part_ii_violations": len(part_ii_kills),
        "part_i_kills_sample": part_i_kills[:10],
        "part_ii_kills_sample": part_ii_kills[:10],
        "PART_i_holds": len(part_i_kills) == 0,
        "PART_ii_injective": len(part_ii_kills) == 0,
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
