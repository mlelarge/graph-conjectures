"""FULLY INDEPENDENT re-verification of P11 (AC_19 is 3-omega_vec-critical).

Written from scratch by the verifier. Does NOT import probe_p19's has_le2_order.
The triangle-free DFS below is my own implementation. The upper bound and
deletion use the CANONICAL core (core.omega_of_order, core.omega_vec_bb,
core.omega_vec_bruteforce) for grounding.

Stages:
  (0) build AC_19 from the rule g(p)={1..(p-3)/2} U {(p+1)/2}, p=19
  (1) structural checks: is_tournament, g partitions {1..p-1} with -g, |g|=(p-1)/2,
      rotation automorphism (vertex-transitive)
  (2) METHOD-VALIDATE my triangle-free DFS == canonical omega_vec on small witnesses
      (both directions: ov>=3 <=> NO triangle-free order; ov<=2 <=> some tri-free order)
  (3) UPPER bound: min omega over p rotation orders (canonical core.omega_of_order)
  (4) DELETION: canonical core.omega_vec_bb(AC_19 - 0, ub=3) == 2
  (5) LOWER bound: my independent triangle-free DFS, fixed-first vertex 0
      (sound for vertex-transitive T) -> expect NO triangle-free order => ov>=3
"""
import os
import sys, time, json, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core


def circulant_arcs(p, g):
    gs = set(g)
    arcs = []
    for i in range(p):
        for j in range(p):
            if i != j and ((j - i) % p) in gs:
                arcs.append((i, j))
    return arcs


def rule_g(p):
    return list(range(1, (p - 3) // 2 + 1)) + [(p + 1) // 2]


# -------- my OWN triangle-free reformulation --------------------------------
# omega_vec(T) <= 2  IFF  some total order has a backedge graph with NO triangle
# (omega <= 2 == triangle-free). Decide via DFS that places vertices prec-first;
# edges among placed vertices are FINAL (a later vertex b vs earlier a gives edge
# a-b iff b->a). Prune the moment placing a vertex would CREATE a triangle.

def has_triangle_free_order(n, arcs, fixed_first=None):
    """True iff some total order's backedge graph is triangle-free.
    My own from-scratch implementation (independent of probe_p19.has_le2_order)."""
    beats = core.beats_matrix(n, arcs)
    # neighbour-in-backedge sets among placed vertices, as bitmasks
    # placing b after placed set P: b's new neighbours = {a in P : beats[b][a]}
    # triangle created iff b shares >=2 mutually-adjacent placed neighbours,
    # i.e. exists a1,a2 in newnb with edge a1-a2 already present.
    full = (1 << n) - 1
    # precompute for each ordered (b): mask of a with beats[b][a]
    back_to = [0] * n  # back_to[b] = bitmask of a s.t. beats[b][a] (a would be earlier)
    for b in range(n):
        m = 0
        for a in range(n):
            if a != b and beats[b][a]:
                m |= (1 << a)
        back_to[b] = m

    adj = [0] * n  # current backedge adjacency among placed vertices (bitmask)

    sys.setrecursionlimit(10000)

    def dfs(placed_mask):
        if placed_mask == full:
            return True
        remaining = full & ~placed_mask
        rm = remaining
        while rm:
            low = rm & (-rm)
            b = low.bit_length() - 1
            rm ^= low
            newnb = back_to[b] & placed_mask  # b's neighbours among placed
            # would placing b create a triangle? triangle iff two of newnb are adjacent
            ok = True
            nb = newnb
            while nb:
                lo2 = nb & (-nb)
                a = lo2.bit_length() - 1
                nb ^= lo2
                if adj[a] & newnb:  # a adjacent to another new-neighbour -> triangle
                    ok = False
                    break
            if not ok:
                continue
            # place b
            nbb = newnb
            tmp = nbb
            while tmp:
                lo3 = tmp & (-tmp)
                a = lo3.bit_length() - 1
                tmp ^= lo3
                adj[a] |= (1 << b)
            adj[b] = newnb
            if dfs(placed_mask | (1 << b)):
                return True
            # undo
            tmp = newnb
            while tmp:
                lo4 = tmp & (-tmp)
                a = lo4.bit_length() - 1
                tmp ^= lo4
                adj[a] &= ~(1 << b)
            adj[b] = 0
        return False

    if fixed_first is not None:
        # place fixed_first first; it has no earlier neighbours
        adj[fixed_first] = 0
        return dfs(1 << fixed_first)
    return dfs(0)


def main():
    p = 19
    g = rule_g(p)
    arcs = circulant_arcs(p, g)
    out = {"P": p, "g": g}

    # (1) structural
    out["is_tournament"] = core.is_tournament(p, arcs)
    negg = set((-x) % p for x in g)
    out["g_neg_g_partition"] = (set(g) | negg == set(range(1, p)) and
                                set(g) & negg == set() and len(g) == (p - 1) // 2)
    # rotation automorphism: i->j present iff (i+1)->(j+1) present
    beats = core.beats_matrix(p, arcs)
    rot_ok = all(beats[i][j] == beats[(i + 1) % p][(j + 1) % p]
                 for i in range(p) for j in range(p) if i != j)
    out["rotation_automorphism"] = rot_ok

    # (2) METHOD VALIDATION on small witnesses vs canonical omega_vec
    val = []
    witnesses = {
        "QR_7": (7, [1, 2, 4]),            # ov expected 3
        "c9_1235": (9, [1, 2, 3, 5]),      # ov expected 3
        "consec11": (11, [1, 2, 3, 4, 5]), # ov expected 2
        "c13": (13, [1, 2, 3, 4, 5, 7]),   # P9, ov expected 3
    }
    for name, (pp, gg) in witnesses.items():
        wa = circulant_arcs(pp, gg)
        ov = core.omega_vec(pp, wa)  # canonical (bruteforce<=7, bb above)
        tf = has_triangle_free_order(pp, wa, fixed_first=None)
        # consistency: (ov<=2) == tf
        val.append({"name": name, "omega_vec": ov, "has_tri_free": tf,
                    "consistent": (ov <= 2) == tf})
    out["method_validation"] = val
    out["method_validation_all_consistent"] = all(v["consistent"] for v in val)

    # (3) UPPER bound via rotation orders (canonical core.omega_of_order)
    rot_omegas = []
    for s in range(p):
        order = [(s + t) % p for t in range(p)]
        rot_omegas.append(core.omega_of_order(p, arcs, order))
    out["upper_bound_min_omega_rotations"] = min(rot_omegas)

    # (4) DELETION (canonical bb)
    keep = [v for v in range(p) if v != 0]
    nn, sub = core.subtournament(p, arcs, keep)
    t0 = time.time()
    out["deletion_omega_vec_minus0"] = core.omega_vec_bb(nn, sub, ub=3)
    out["deletion_time_s"] = round(time.time() - t0, 2)

    # (5) LOWER bound: my independent triangle-free DFS, fixed_first=0
    t0 = time.time()
    tf0 = has_triangle_free_order(p, arcs, fixed_first=0)
    out["has_triangle_free_order_ff0"] = tf0
    out["lb_time_s"] = round(time.time() - t0, 2)

    # combine: ov = upper if no tri-free order (>=3) else <=2
    if not tf0:
        out["omega_vec"] = out["upper_bound_min_omega_rotations"]
    else:
        out["omega_vec"] = 2
    out["is_3_critical"] = (out["omega_vec"] == 3 and
                            out["deletion_omega_vec_minus0"] == 2 and
                            rot_ok)

    print(json.dumps(out, indent=2))
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'reverify_p19_indep.json'), "w") as f:
        json.dump(out, f, indent=2)


if __name__ == "__main__":
    main()
