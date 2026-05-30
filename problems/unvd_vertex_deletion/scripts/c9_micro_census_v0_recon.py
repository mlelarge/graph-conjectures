"""
Conjecture-9 exact micro-census (Aboulker, Problem-6 companion).

Conjecture 9: exists absolute constant C with unvd(D) <= C * unvd(D-v) for
every acyclic D and every vertex v. Prop 1: C=2 for v a source/sink. OPEN for
internal vertices. This is the cheap red-team companion to Problem 6.

We enumerate ALL DAGs on n in {2,3,4,5} up to isomorphism, compute unvd(D)
EXACTLY by exhaustive tournament enumeration up to p=EXH_CAP, and for each
INTERNAL vertex v compute r(D,v)=unvd(D)/unvd(D-v). We report:
  (a) max internal ratio + witness,
  (b) whether any internal ratio > 2 (would refute C=2 for internal vertices),
  (c) ratio distribution,
  (d) per-(|V|, unvd) table.

unvd is EXACT (verified, every-tournament-checked) for any value <= EXH_CAP.
A DAG not universally contained at p=EXH_CAP is reported as ">=EXH_CAP+1"
(a true lower bound). For n<=5 the only DAGs exceeding 6 are TT_4-rich
(unvd 7..8); we flag them and exclude their (uncertain) ratios from the
strict-">2" verdict, while still reporting them.

EVIDENCE, not proof: "survives up to ..." not "proved".
"""
import itertools
import networkx as nx
from collections import defaultdict

EXH_CAP = 6  # exact exhaustive tournament enumeration up to this p

# Containment via bitset adjacency for speed.
# Tournament represented as out[v] = bitmask of out-neighbors among 0..p-1.

def labeled_tournaments_bits(p):
    pairs = list(itertools.combinations(range(p), 2))
    for bits in range(1 << len(pairs)):
        out = [0] * p
        for idx, (a, b) in enumerate(pairs):
            if (bits >> idx) & 1:
                out[b] |= (1 << a)
            else:
                out[a] |= (1 << b)
        yield out


def contains_bits(out, p, D_edges, nD):
    """Is acyclic D (edges over nodes 0..nD-1) an injective-hom subgraph of T?"""
    for perm in itertools.permutations(range(p), nD):
        ok = True
        for (u, v) in D_edges:
            if not (out[perm[u]] >> perm[v]) & 1:
                ok = False
                break
        if ok:
            return True
    return False


def every_tournament_contains(p, D_edges, nD):
    for out in labeled_tournaments_bits(p):
        if not contains_bits(out, p, D_edges, nD):
            return False
    return True


def unvd_value(D_edges, nD):
    """(val, exact). exact=True => val is the true unvd. exact=False => val is
    a strict lower bound: unvd >= val."""
    if not D_edges:
        return (max(nD, 1), True)
    p = max(2, nD)
    while p <= EXH_CAP:
        if every_tournament_contains(p, D_edges, nD):
            return (p, True)
        p += 1
    return (EXH_CAP + 1, False)  # not universal at EXH_CAP => unvd >= EXH_CAP+1


# ---- DAG enumeration up to isomorphism on exactly n vertices ----

def canon_dag(edges, n):
    edgeset = set(edges)
    best = None
    for perm in itertools.permutations(range(n)):
        relabeled = tuple(sorted((perm[a], perm[b]) for (a, b) in edgeset))
        if best is None or relabeled < best:
            best = relabeled
    return best


def all_dags_up_to_iso(n):
    fwd_pairs = list(itertools.combinations(range(n), 2))
    seen = set()
    reps = []
    for r in range(len(fwd_pairs) + 1):
        for chosen in itertools.combinations(fwd_pairs, r):
            edges = list(chosen)
            c = canon_dag(edges, n)
            if c not in seen:
                seen.add(c)
                reps.append(edges)
    return reps


def mad(edges, n):
    if not edges:
        return 0.0
    nodes = list(range(n))
    adj = defaultdict(set)
    for (a, b) in edges:
        adj[a].add(b)
    best = 0.0
    for r in range(1, n + 1):
        for sub in itertools.combinations(nodes, r):
            ss = set(sub)
            a = sum(1 for (u, v) in edges if u in ss and v in ss)
            if a:
                best = max(best, 2 * a / r)
    return best


_UNVD_CACHE = {}

def unvd_cached(edges, n):
    # compactify to 0..k-1 over vertices that appear OR keep n? unvd depends on
    # whole vertex set incl isolated. Keep n vertices (isolated count toward |V|
    # only for trivial edgeless; with edges, isolated vertices don't change
    # containment threshold but do change |V|. For D-v we pass exact node set.)
    key = (n, canon_dag(edges, n))
    if key in _UNVD_CACHE:
        return _UNVD_CACHE[key]
    val = unvd_value(edges, n)
    _UNVD_CACHE[key] = val
    return val


def main():
    print(f"# Conjecture-9 micro-census. EXACT tournament exhaustion up to p={EXH_CAP}.")
    print(f"# unvd > {EXH_CAP} reported as '>={EXH_CAP+1}' (true lower bound).")
    print(flush=True)

    rows = []
    internal_ratios = []          # (ratio, exact_flag) exact only if both exact
    over2_exact = []              # ratios >2 where BOTH unvd values are exact
    over2_any = []                # ratios >2 using values as-reported (incl lb)
    max_internal_exact = (0.0, None)

    for n in range(2, 6):
        reps = all_dags_up_to_iso(n)
        print(f"# n={n}: {len(reps)} iso DAGs", flush=True)
        for edges in reps:
            if not edges:
                continue
            uD, uD_exact = unvd_cached(edges, n)
            md = mad(edges, n)
            # degrees
            indeg = defaultdict(int); outdeg = defaultdict(int)
            for (a, b) in edges:
                outdeg[a] += 1; indeg[b] += 1
            best_ratio = None
            for v in range(n):
                if indeg[v] > 0 and outdeg[v] > 0:  # internal
                    # build D - v on n-1 vertices, relabel survivors 0..n-2
                    survivors = [u for u in range(n) if u != v]
                    relab = {u: i for i, u in enumerate(survivors)}
                    e2 = [(relab[a], relab[b]) for (a, b) in edges
                          if a != v and b != v]
                    nv = n - 1
                    if not e2:
                        uDv, uDv_exact = (max(nv, 1), True)
                    else:
                        uDv, uDv_exact = unvd_cached(e2, nv)
                    if uDv == 0:
                        continue
                    ratio = uD / uDv
                    both_exact = uD_exact and uDv_exact
                    internal_ratios.append((ratio, both_exact))
                    if best_ratio is None or ratio > best_ratio:
                        best_ratio = ratio
                    if ratio > 2 + 1e-9:
                        over2_any.append((edges, v, uD, uD_exact, uDv, uDv_exact, ratio))
                        if both_exact:
                            over2_exact.append((edges, v, uD, uDv, ratio))
                    if both_exact and ratio > max_internal_exact[0]:
                        max_internal_exact = (ratio, (list(edges), v, uD, uDv))
            rows.append((n, len(edges), round(md, 3), uD, uD_exact,
                         (round(best_ratio, 3) if best_ratio is not None else None)))

    by_n = defaultdict(list)
    for row in rows:
        by_n[row[0]].append(row)

    print()
    print("## Per-n summary (|V|, unvd, internal-deletion ratios)")
    for n in sorted(by_n):
        recs = by_n[n]
        us_exact = [r[3] for r in recs if r[4]]
        lb_count = sum(1 for r in recs if not r[4])
        ratios = [r[5] for r in recs if r[5] is not None]
        print(f"  n={n}: {len(recs)} nonedgeless DAGs | "
              f"max EXACT unvd={max(us_exact) if us_exact else None} | "
              f"#DAGs with unvd>={EXH_CAP+1}: {lb_count} | "
              f"max internal-deletion ratio={max(ratios) if ratios else None}")

    print()
    print("## (|V|, unvd) distribution table")
    cell = defaultdict(int)
    for (n, na, md, u, ex, br) in rows:
        label = f"{u}" if ex else f">={u}"
        cell[(n, label)] += 1
    print(f"  {'|V|':>3}  {'unvd':>6}  count")
    for (n, label) in sorted(cell, key=lambda x: (x[0], x[1])):
        print(f"  {n:>3}  {label:>6}  {cell[(n, label)]}")

    print()
    print("## Internal-vertex deletion ratio summary (all internal (D,v) pairs)")
    if internal_ratios:
        from statistics import mean
        vals = [r for (r, _) in internal_ratios]
        exact_vals = [r for (r, e) in internal_ratios if e]
        print(f"  internal pairs: {len(vals)}  (both-exact: {len(exact_vals)})")
        print(f"  max ratio (any): {max(vals):.4f}")
        print(f"  max ratio (both-exact): {max(exact_vals) if exact_vals else None}")
        print(f"  mean (both-exact): {mean(exact_vals) if exact_vals else None}")
        buckets = defaultdict(int)
        for r in exact_vals:
            buckets[round(r, 2)] += 1
        print("  distribution of EXACT ratios (ratio->count):")
        for b in sorted(buckets):
            print(f"    {b}: {buckets[b]}")

    print()
    print("## Any internal ratio strictly > 2 (with BOTH unvd values EXACT)?")
    if over2_exact:
        print(f"  YES ({len(over2_exact)}): finite CERTIFICATE refuting C=2 for "
              f"internal vertices.")
        for (e, v, uD, uDv, r) in over2_exact[:15]:
            print(f"    edges={e} del v={v}: unvd(D)={uD} unvd(D-v)={uDv} ratio={r:.3f}")
    else:
        print("  NO (within exact range). All exact-evaluable internal ratios <=2.")
        print("  => EVIDENCE that C=2 may extend to internal vertices; NOT a proof.")
    if over2_any and not over2_exact:
        print(f"  ({len(over2_any)} ratios >2 exist but involve a lower-bound unvd;")
        print("   these are inconclusive on C=2 because the bound is not exact.)")

    print()
    r, w = max_internal_exact
    if w:
        e, v, uD, uDv = w
        print(f"## Max EXACT internal-deletion ratio witness: ratio={r:.4f}")
        print(f"   edges={e} del internal v={v}: unvd(D)={uD}, unvd(D-v)={uDv}")

    print()
    print(f"RANGE COVERED: |V(D)| in [2,5]; unvd EXACT for values <= {EXH_CAP} "
          f"(verified over ALL tournaments). Values > {EXH_CAP} are lower bounds.")


if __name__ == "__main__":
    main()
