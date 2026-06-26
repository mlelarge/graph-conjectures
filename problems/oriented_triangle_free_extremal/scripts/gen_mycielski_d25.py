"""Generalized directed Mycielskian M_r(D25): a candidate chi=4 oriented
triangle-free graph on (r+1)*25+1 vertices.

Motivation (explicit-construction lens, attacking H2 / the t_vec lower bound):
the graveyard (G1) killed every INDEPENDENT-PACK INTERFACE coupling of D25
copies (all cap at chi_vec=3 up to n=175).  The decision log's narrowed
direction is a 3-dicritical-preserving OPERATION rather than an interface.  The
(generalized) Mycielskian is the classical chi-raising, triangle-free-preserving
cone.  The NAIVE directed Mycielskian r=1 (51 vertices) is 3-dicolourable
(oracle-verified: the shadow can copy the original's colour), so this script
exposes the GENERALIZED version M_r with r>=2 shadow layers, which lengthens the
shadow paths and is designed to block the colour-copy escape.

If core.dichromatic_number == 4 for some small r with N=(r+1)*25+1 < 209, this
improves m(4) <= 209 and pushes the t_vec lower bound at small scale.
"""
from __future__ import annotations

import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])

import core
import constructions as C


def gen_directed_mycielskian(n, arcs, r=2, z_in=True):
    """Generalized directed Mycielskian with r shadow layers + apex.

    Vertices: layer t in {0..r} holds a copy of V (id = t*n + v); apex z=(r+1)*n.
    Layer 0 carries the original arcs.  For each base arc u->v and each pair of
    consecutive layers (t,t+1) we add the Mycielski cross arcs u_t -> v_{t+1} and
    u_{t+1} -> v_t.  The apex z is completely joined to the LAST shadow layer r
    (oriented z->layer-r if z_in else layer-r->z).  Underlying graph is the
    generalized Mycielskian of a triangle-free graph => triangle-free; one-way
    cross/apex arcs keep it oriented (no digon).
    """
    z = (r + 1) * n

    def vid(t, v):
        return t * n + v

    out = [(vid(0, u), vid(0, v)) for (u, v) in arcs]
    for t in range(r):
        for (u, v) in arcs:
            out.append((vid(t, u), vid(t + 1, v)))
            out.append((vid(t + 1, u), vid(t, v)))
    for v in range(n):
        out.append((z, vid(r, v)) if z_in else (vid(r, v), z))
    return (r + 1) * n + 1, out


def cyclic_mycielskian(n, arcs, r=3):
    """CYCLIC generalized Mycielskian: r layers indexed by Z_r (no apex).

    Layer 0 carries the original arcs; for every base arc u->v and every layer t,
    add the single forward cross arc  u_t -> v_{t+1 mod r}.  With r ODD the
    layer-wrap is an odd directed skeleton, so the colour-copy escape that kills
    the acyclic (apex) Mycielskian must now CLOSE a monochromatic directed cycle
    across the r layers (the base D25 already carries dicycles via C5<-5).  This
    is the route designed to actually raise chi_vec, on N = r*25 vertices.  It is
    NOT an independent-pack interface coupling (G1): the cross join uses the FULL
    arc set of D25 between consecutive layers, arranged on an odd cyclic skeleton.
    """
    def vid(t, v):
        return (t % r) * n + v

    out = [(vid(0, u), vid(0, v)) for (u, v) in arcs]
    for t in range(r):
        for (u, v) in arcs:
            out.append((vid(t, u), vid(t + 1, v)))
    return r * n, out


def build(r=2, z_in=True):
    n, arcs = C.D25()
    return gen_directed_mycielskian(n, arcs, r, z_in)


def build_cyclic(r=3):
    n, arcs = C.D25()
    return cyclic_mycielskian(n, arcs, r)


if __name__ == "__main__":
    import json

    mode = sys.argv[1] if len(sys.argv) > 1 else "cyclic"
    if mode == "cyclic":
        r = int(sys.argv[2]) if len(sys.argv) > 2 else 3
        N, A = build_cyclic(r)
        z_in = None
    else:
        r = int(sys.argv[1]) if len(sys.argv) > 1 else 2
        z_in = (sys.argv[2].lower() in ("1", "true", "in")) if len(sys.argv) > 2 else True
        N, A = build(r, z_in)
    res = {
        "r": r, "z_in": z_in, "N": N, "m_arcs": len(A),
        "is_oriented": core.is_oriented(A),
        "is_triangle_free": core.is_triangle_free(N, A),
        # falsifiable bit: chi=4 iff NOT 3-dicolourable
        "three_dicolourable": core.is_k_dicolourable(N, A, 3),
    }
    if not res["three_dicolourable"]:
        res["four_dicolourable"] = core.is_k_dicolourable(N, A, 4)
    print(json.dumps(res, indent=2))
