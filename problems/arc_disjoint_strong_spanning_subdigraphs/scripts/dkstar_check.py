"""DK*(alpha): ARC-SET refinement of the killed DK(alpha) (G11).

DK*(alpha) (UNIVERSAL): for every lambda-arc-strong digraph D on n vertices and
every alpha>=1, the number of DISTINCT ARC-SETS
    { delta^+(X) : emptyset != X subsetneq V, |delta^+(X)| <= alpha*lambda }
is at most n^{2*alpha}.

Difference vs DK(alpha): DK counts VERTEX sets X; DK* counts the resulting
labeled ARC-SETS delta^+(X) (a multiset of labeled arcs).  The proposal claims
G11's 2^k vertex-sets collapse because they share ONE arc-set, so DK* may
survive where DK died.  THE SKEPTIC TEST is whether an adversarial family gives
each toggle a PRIVATE distinguishing arc, turning 2^k vertex-sets into 2^k
DISTINCT arc-sets -> a super-polynomial KILL of DK* at the sharper granularity.

Arcs carry a LABEL (their index in the arc list) so parallel arcs are distinct.
delta^+(X) := frozenset of LABELS of arcs leaving X.

Three arms in one foreground process:
  ARM-1  rebuild G11, confirm vertex-set vs arc-set counts (loophole check).
  ARM-2  generic exhaustive census n=4,5 (lambda>=1 strata) -- universal gate.
  ARM-3  adversarial hunt: private-arc, nested, chained, interval gadgets.
"""
import sys, os, json, time, itertools, subprocess, math

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import oracle

ALPHAS = [("1", 1.0), ("4/3", 4.0 / 3.0), ("5/3", 5.0 / 3.0), ("2", 2.0)]


def labeled_arcs(arcs):
    """Return list of (label, u, v); label = index so parallels are distinct."""
    return [(i, u, v) for i, (u, v) in enumerate(arcs)]


def out_arc_labels(larcs, X):
    """frozenset of labels of arcs leaving X (the labeled arc-set delta^+(X))."""
    return frozenset(i for (i, u, v) in larcs if u in X and v not in X)


def arcset_census(n, arcs, lam):
    """For each alpha: (#distinct arc-sets, #vertex-sets, ratios) for cuts
    of size <= alpha*lam.  Enumerate all 2^n-2 proper nonempty subsets."""
    larcs = labeled_arcs(arcs)
    thr = {lbl: a * lam for (lbl, a) in ALPHAS}
    vsets = {lbl: 0 for (lbl, _a) in ALPHAS}
    asets = {lbl: set() for (lbl, _a) in ALPHAS}
    verts = list(range(n))
    for mask in range(1, (1 << n) - 1):
        X = frozenset(i for i in verts if (mask >> i) & 1)
        F = out_arc_labels(larcs, X)
        s = len(F)
        for (lbl, _a) in ALPHAS:
            if s <= thr[lbl]:
                vsets[lbl] += 1
                asets[lbl].add(F)
    out = {}
    for (lbl, a) in ALPHAS:
        denom = n ** (2.0 * a)
        nstar = len(asets[lbl])
        out[lbl] = {"n_vsets": vsets[lbl], "n_arcsets": nstar,
                    "denom_n^2a": denom,
                    "ratio_arcset": nstar / denom,
                    "ratio_vset": vsets[lbl] / denom}
    return out


class Tracker:
    def __init__(self):
        self.worst = {lbl: {"ratio_arcset": -1.0} for (lbl, _a) in ALPHAS}
        self.kills = []  # ratio_arcset > 1 (DK* KILL)

    def update(self, n, arcs, lam, tag):
        cc = arcset_census(n, arcs, lam)
        for (lbl, _a) in ALPHAS:
            r = cc[lbl]["ratio_arcset"]
            if r > self.worst[lbl]["ratio_arcset"]:
                self.worst[lbl] = {"ratio_arcset": round(r, 5),
                                   "n_arcsets": cc[lbl]["n_arcsets"],
                                   "n_vsets": cc[lbl]["n_vsets"],
                                   "n": n, "lambda": lam, "tag": tag}
            if r > 1.0:
                self.kills.append({"alpha": lbl, "ratio_arcset": round(r, 5),
                                   "n_arcsets": cc[lbl]["n_arcsets"],
                                   "n": n, "lambda": lam, "tag": tag,
                                   "arcs": [list(a) for a in arcs]})
        return cc

    def summary(self):
        return {"worst_per_alpha": self.worst, "kills": self.kills,
                "DKstar_survives": len(self.kills) == 0}


# ----------------------------- ARM 1 ------------------------------------- #
def g11_family(k, mult=3):
    """G11: digon backbone {0,1} mult `mult` + k toggles p with s->p,p->o mult.
    s=0 (source), o=1 (sink-side).  n=k+2."""
    s, o = 0, 1
    arcs = []
    arcs += [(s, o)] * mult
    arcs += [(o, s)] * mult
    for j in range(k):
        p = 2 + j
        arcs += [(s, p)] * mult
        arcs += [(p, o)] * mult
    return (k + 2), arcs


def run_arm1():
    rows = []
    for k in range(8, 17):
        n, arcs = g11_family(k, 3)
        lam = oracle.arc_connectivity(n, arcs)
        cc = arcset_census(n, arcs, lam)
        a2 = cc["2"]  # alpha=2 -> cuts <= 2*lambda (the proposal's headline col)
        rows.append({"k": k, "n": n, "lambda": lam,
                     "n_vsets_<=2lam": a2["n_vsets"],
                     "n_arcsets_<=2lam": a2["n_arcsets"],
                     "n^4": n ** 4})
    return rows


# ----------------------------- ARM 2 ------------------------------------- #
def gen_simple_digraphs(n):
    """All simple digraphs on n via geng (all graphs) | directg -T.
    Use geng -c n (connected underlying, no min-degree filter: include all
    lambda strata)."""
    geng = subprocess.Popen(["geng", "-cq", str(n)], stdout=subprocess.PIPE)
    directg = subprocess.Popen(["directg", "-Tq"], stdin=geng.stdout,
                               stdout=subprocess.PIPE)
    geng.stdout.close()
    for line in directg.stdout:
        line = line.decode().strip()
        if not line:
            continue
        toks = line.split()
        nv = int(toks[0]); ne = int(toks[1]); nums = list(map(int, toks[2:]))
        arcs = [(nums[i], nums[i + 1]) for i in range(0, len(nums), 2)]
        yield nv, arcs
    directg.wait(); geng.wait()


def run_arm2(n, tr):
    n_read = 0; n_lam_ge1 = 0
    for nv, arcs in gen_simple_digraphs(n):
        n_read += 1
        lam = oracle.arc_connectivity(nv, arcs)
        if lam < 1:
            continue
        n_lam_ge1 += 1
        tr.update(nv, arcs, lam, tag=f"generic_n{n}")
    return {"n": n, "n_read": n_read, "n_lambda_ge1": n_lam_ge1}


# ----------------------------- ARM 3 ------------------------------------- #
def fam_private_arc(k, mult=3):
    """G11 + a PRIVATE distinguishing arc p->s (mult 1) per toggle.
    Intent: make each toggle's presence change the arc-set delta^+(X)."""
    s, o = 0, 1
    arcs = [(s, o)] * mult + [(o, s)] * mult
    for j in range(k):
        p = 2 + j
        arcs += [(s, p)] * mult
        arcs += [(p, o)] * mult
        arcs += [(p, s)]            # private cheap arc into s
    return (k + 2), arcs


def fam_private_arc_to_o(k, mult=3):
    """G11 + private arc o->p (mult 1) per toggle: another way to make the
    toggle's IN/OUT contribution to delta^+(X) distinct."""
    s, o = 0, 1
    arcs = [(s, o)] * mult + [(o, s)] * mult
    for j in range(k):
        p = 2 + j
        arcs += [(s, p)] * mult
        arcs += [(p, o)] * mult
        arcs += [(o, p)]            # private cheap arc from o
    return (k + 2), arcs


def fam_nested_bundle(levels, mult=3):
    """Two-level nested bundle: a hub s, hub o, and a tree of intermediate
    bundles, each toggle hanging off a sub-hub.  Approx by chaining."""
    s, o = 0, 1
    arcs = [(s, o)] * mult + [(o, s)] * mult
    nxt = 2
    prev_layer = [s]
    nodes = 2
    for L in range(levels):
        cur = []
        for parent in prev_layer:
            for _b in range(2):
                p = nxt; nxt += 1; nodes += 1
                arcs += [(parent, p)] * mult
                arcs += [(p, o)] * mult
                cur.append(p)
        prev_layer = cur
        if nodes > 18:
            break
    return nodes, arcs


def fam_interval_gadget(t, mult=3):
    """Interval/overlap gadget: a path of t digon-blocks 0-1-2-...-t, each
    consecutive pair joined by mult arcs both ways; plus a global source/sink
    pair of bundles so that prefix out-cuts realize many DISTINCT arc-sets
    (each prefix {0..i} has its own boundary arcs i->i+1)."""
    arcs = []
    for i in range(t):
        arcs += [(i, i + 1)] * mult
        arcs += [(i + 1, i)] * mult
    # close into a cycle to keep strong, with bundles
    arcs += [(t, 0)] * mult
    arcs += [(0, t)] * mult
    return (t + 1), arcs


def fam_subset_pool(t, mult=3):
    """Adversarial 'private cheap arc per cut' design: a small reservoir of
    arcs e_1..e_t (each a digon block i<->i+1 on a cycle), engineered so that
    out-cuts realize a LARGE FAMILY of distinct arc-subsets.  Doubled cycle
    C_{t}^2 thickened -> consecutive intervals give distinct boundary arc-sets."""
    n = t
    arcs = []
    for i in range(n):
        arcs += [(i, (i + 1) % n)] * mult
        arcs += [(i, (i + 2) % n)] * mult
    return n, arcs


def run_arm3(tr):
    recs = []

    def consider(tag, n, arcs):
        if n > 20:
            return
        lam = oracle.arc_connectivity(n, arcs)
        cc = tr.update(n, arcs, lam, tag=tag)
        rec = {"tag": tag, "n": n, "lambda": lam}
        for (lbl, _a) in ALPHAS:
            rec[f"arcsets<= {lbl}lam"] = cc[lbl]["n_arcsets"]
            rec[f"vsets<= {lbl}lam"] = cc[lbl]["n_vsets"]
            rec[f"ratio_aset_{lbl}"] = round(cc[lbl]["ratio_arcset"], 4)
        recs.append(rec)

    # private-arc families: the named failure mode (growth in k)
    for k in range(6, 17):
        n, arcs = fam_private_arc(k, 3)
        consider("private_p->s", n, arcs)
    for k in range(6, 17):
        n, arcs = fam_private_arc_to_o(k, 3)
        consider("private_o->p", n, arcs)
    # nested bundles
    for lv in range(2, 5):
        n, arcs = fam_nested_bundle(lv, 3)
        consider(f"nested_L{lv}", n, arcs)
    # interval / chained
    for t in range(4, 18):
        n, arcs = fam_interval_gadget(t, 3)
        consider("interval_chain", n, arcs)
    # subset-pool doubled cycle
    for t in range(5, 19):
        n, arcs = fam_subset_pool(t, 3)
        consider("subset_pool_Cn2", n, arcs)
    return recs


def main():
    t0 = time.time()
    arm1 = run_arm1()
    tr = Tracker()
    arm2_meta = []
    for n in (4, 5):
        arm2_meta.append(run_arm2(n, tr))
    arm3_recs = run_arm3(tr)
    out = {"elapsed_s": round(time.time() - t0, 2),
           "ARM1_g11_loophole": arm1,
           "ARM2_generic_census_meta": arm2_meta,
           "ARM3_adversarial_records": arm3_recs}
    out.update(tr.summary())
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
