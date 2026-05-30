"""Port-Relation Census for Q7.1 (D71).

Q7.1 (`docs/two_route_final_synthesis.md` §4): is there a *composable
non-monotone ordering primitive*?  This module formalizes a
"composable ordering primitive" as a port gadget and exhaustively
classifies the relations such gadgets realize.

A **gadget** is a tournament T together with k ordered port pairs
(x_1, y_1), ..., (x_k, y_k).  Over all valid LFOs sigma of T (orders
whose back-arc graph is a linear forest), each port pair gives a bit

    b_i(sigma) = 1[sigma(y_i) < sigma(x_i)]        (y_i before x_i)

and the gadget realizes the relation

    R_T = { (b_1(sigma), ..., b_k(sigma)) : sigma a valid LFO of T }
        subseteq {0,1}^k.

We classify each R_T by:
  * monotonicity: is R_T downward-closed?  (Theorem 3.1 says the
    consecutive-toggle substrate yields only downward-closed relations.)
  * Schaefer type: 0-valid, 1-valid, Horn (closed under AND),
    dual-Horn (closed under OR), affine (closed under ternary XOR),
    bijunctive (closed under majority).  A relation is *non-Schaefer*
    iff none of these hold — a non-Schaefer composable relation would
    yield NP-hardness via Schaefer's dichotomy.

**Composability filter.**  A gadget is composable only if its port
endpoints can be wired to other gadgets without breaking the LFO
degree-2 back-arc budget.  Operationally, a bit-vector b in R_T is
*composably realizable* if some witnessing LFO sigma realizes b with
every port endpoint having back-degree <= 1 (residual capacity >= 1).
The composable relation is

    R_T^comp = { b in R_T : b has a residual-capacity witness }.

A gadget is a *composable non-monotone primitive* if R_T^comp is
non-empty, non-monotone, and equals R_T (every realizable vector is
composably realizable).  We also report the weaker notion where only
R_T^comp (not all of R_T) must be non-monotone.

Decision for Q7.1:
  * If no composable non-monotone relation exists up to (n, k):
    evidence for an impossibility theorem -> hardness route closed
    -> Path-FAS likely in P.
  * If one exists: the first serious hardness substrate not killed by
    Theorems 5.1, 6.1, or toggle monotonicity.
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import sys
from collections import Counter
from typing import Iterable, Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from verify import verify  # noqa: E402


Matrix = list[list[int]]


# ----------------------------------------------------------------------
# 1. Tournament enumeration
# ----------------------------------------------------------------------

def all_tournaments(n: int) -> Iterable[Matrix]:
    """Yield every labeled tournament on n vertices (2^C(n,2) of them)."""
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    for bits in itertools.product((0, 1), repeat=len(pairs)):
        T = [[0] * n for _ in range(n)]
        for (i, j), bit in zip(pairs, bits):
            if bit:
                T[i][j] = 1
            else:
                T[j][i] = 1
        yield T


def _upper_sig(T: Matrix, n: int, perm: Sequence[int]) -> tuple:
    """Upper-triangle signature of T under vertex relabeling `perm`."""
    return tuple(
        T[perm[i]][perm[j]]
        for i in range(n) for j in range(i + 1, n)
    )


def tournament_iso_reps(n: int) -> list[Matrix]:
    """One representative per isomorphism class of tournament on n
    vertices.  Sound for the census because every port-tuple is
    enumerated per representative, so all realizable relations are
    covered."""
    perms = list(itertools.permutations(range(n)))
    canons: set[tuple] = set()
    for T in all_tournaments(n):
        canons.add(min(_upper_sig(T, n, p) for p in perms))
    reps: list[Matrix] = []
    for sig in canons:
        T = [[0] * n for _ in range(n)]
        idx = 0
        for i in range(n):
            for j in range(i + 1, n):
                if sig[idx]:
                    T[i][j] = 1
                else:
                    T[j][i] = 1
                idx += 1
        reps.append(T)
    return reps


def tournament_reps_by_extension(n: int) -> list[Matrix]:
    """Generate one representative per isomorphism class on n vertices
    by extending the (n-1)-class reps one vertex at a time, deduping by
    canonical key.  Feasible for n = 7 (456 classes) where brute
    canonicalization over 2^C(7,2) labeled tournaments is not."""
    from lfo_extend_census import extend_by_one  # noqa: E402
    from tournament_canonical import (  # noqa: E402
        canonical_key, key_to_string, string_to_matrix,
    )

    if n <= 5:
        return tournament_iso_reps(n)
    base = tournament_reps_by_extension(n - 1)
    seen: dict[str, None] = {}
    for T in base:
        for U in extend_by_one(T):
            seen.setdefault(key_to_string(canonical_key(U)), None)
    return [string_to_matrix(s) for s in seen]


def tournaments_from_reps(path: str) -> Iterable[Matrix]:
    """Yield tournaments from a reps JSONL/JSON file (each record has a
    'matrix' or 'T' field)."""
    with open(path, encoding="utf-8") as fh:
        text = fh.read().strip()
    records: list = []
    if text.startswith("["):
        records = json.loads(text)
    else:
        for line in text.splitlines():
            line = line.strip()
            if line:
                records.append(json.loads(line))
    for rec in records:
        if isinstance(rec, dict):
            mat = rec.get("matrix") or rec.get("T") or rec.get("tournament")
        else:
            mat = rec
        if mat is not None:
            yield [list(row) for row in mat]


# ----------------------------------------------------------------------
# 2. Valid LFOs and back-degrees
# ----------------------------------------------------------------------

def valid_lfos(T: Matrix) -> list[tuple[int, ...]]:
    """All orders whose back-arc graph is a linear forest."""
    n = len(T)
    out: list[tuple[int, ...]] = []
    for P in itertools.permutations(range(n)):
        if verify(T, list(P))["is_linear_forest"]:
            out.append(P)
    return out


def back_degrees(T: Matrix, P: Sequence[int]) -> list[int]:
    """Undirected back-arc degree of each vertex under order P."""
    n = len(T)
    pos = [0] * n
    for i, v in enumerate(P):
        pos[v] = i
    deg = [0] * n
    for u in range(n):
        for v in range(n):
            if T[u][v] and pos[u] > pos[v]:
                deg[u] += 1
                deg[v] += 1
    return deg


# ----------------------------------------------------------------------
# 3. Port relation extraction
# ----------------------------------------------------------------------

def build_lfo_cache(T: Matrix) -> list[tuple[tuple[int, ...], tuple[int, ...]]]:
    """For each valid LFO of T, cache (pos_vector, back_degree_vector).

    Computing back-degrees once per LFO (rather than once per
    port-tuple) is the key speedup for the n=7 census."""
    n = len(T)
    cache: list[tuple[tuple[int, ...], tuple[int, ...]]] = []
    for P in itertools.permutations(range(n)):
        if not verify(T, list(P))["is_linear_forest"]:
            continue
        pos = [0] * n
        for i, v in enumerate(P):
            pos[v] = i
        deg = back_degrees(T, P)
        cache.append((tuple(pos), tuple(deg)))
    return cache


def port_relation_cached(
    lfo_cache: Sequence[tuple[tuple[int, ...], tuple[int, ...]]],
    ports: Sequence[tuple[int, int]],
) -> tuple[frozenset, frozenset, frozenset]:
    """Return (R_T, R_comp_lenient, R_comp_strict) from a cached LFO list.

    R_T               = all realizable bit-vectors.
    R_comp_lenient    = b with SOME witness having every port endpoint
                        at back-degree <= 1 (over-approximation; sound
                        for NEGATIVE results).
    R_comp_strict     = b for which EVERY witness has every port endpoint
                        at back-degree <= 1 (uniform residual capacity;
                        the robust object required for POSITIVE claims)."""
    port_vertices: set[int] = set()
    for x, y in ports:
        port_vertices.add(x)
        port_vertices.add(y)
    total: dict[tuple[int, ...], int] = {}
    capacity: dict[tuple[int, ...], int] = {}
    for pos, deg in lfo_cache:
        bits = tuple(1 if pos[y] < pos[x] else 0 for (x, y) in ports)
        total[bits] = total.get(bits, 0) + 1
        if all(deg[v] <= 1 for v in port_vertices):
            capacity[bits] = capacity.get(bits, 0) + 1
    R = frozenset(total)
    R_comp = frozenset(b for b in total if capacity.get(b, 0) > 0)
    R_comp_strict = frozenset(
        b for b in total if capacity.get(b, 0) == total[b]
    )
    return R, R_comp, R_comp_strict


def port_relation(
    T: Matrix,
    lfos: Sequence[Sequence[int]],
    ports: Sequence[tuple[int, int]],
) -> tuple[frozenset, frozenset]:
    """Return (R_T, R_T^comp) — kept for backward-compat / tests.

    R_T = set of bit-vectors realizable by some valid LFO.
    R_T^comp = lenient composable shadow (some witness has capacity)."""
    R: set[tuple[int, ...]] = set()
    R_comp: set[tuple[int, ...]] = set()
    port_vertices = set()
    for x, y in ports:
        port_vertices.add(x)
        port_vertices.add(y)
    for P in lfos:
        pos = [0] * len(T)
        for i, v in enumerate(P):
            pos[v] = i
        bits = tuple(1 if pos[y] < pos[x] else 0 for (x, y) in ports)
        R.add(bits)
        deg = back_degrees(T, P)
        if all(deg[v] <= 1 for v in port_vertices):
            R_comp.add(bits)
    return frozenset(R), frozenset(R_comp)


# ----------------------------------------------------------------------
# 4. Classification: monotonicity + Schaefer type
# ----------------------------------------------------------------------

def is_downward_closed(R: frozenset, k: int) -> bool:
    """R is downward-closed iff for every b in R, every coordinatewise
    smaller vector is also in R."""
    Rset = set(R)
    for b in R:
        for combo in itertools.product(*[range(bi + 1) for bi in b]):
            if combo not in Rset:
                return False
    return True


def _and(a, b):
    return tuple(x & y for x, y in zip(a, b))


def _or(a, b):
    return tuple(x | y for x, y in zip(a, b))


def _maj(a, b, c):
    return tuple(1 if (x + y + z) >= 2 else 0 for x, y, z in zip(a, b, c))


def _xor3(a, b, c):
    return tuple(x ^ y ^ z for x, y, z in zip(a, b, c))


def schaefer_flags(R: frozenset, k: int) -> dict:
    Rset = set(R)
    zero = tuple([0] * k)
    one = tuple([1] * k)
    is_horn = all(_and(a, b) in Rset for a in R for b in R)
    is_dual_horn = all(_or(a, b) in Rset for a in R for b in R)
    is_affine = all(_xor3(a, b, c) in Rset for a in R for b in R for c in R)
    is_bijunctive = all(_maj(a, b, c) in Rset for a in R for b in R for c in R)
    is_0valid = (zero in Rset)
    is_1valid = (one in Rset)
    schaefer = (is_horn or is_dual_horn or is_affine or is_bijunctive
                or is_0valid or is_1valid)
    return {
        "horn": is_horn,
        "dual_horn": is_dual_horn,
        "affine": is_affine,
        "bijunctive": is_bijunctive,
        "zero_valid": is_0valid,
        "one_valid": is_1valid,
        "schaefer_tractable": schaefer,
        "non_schaefer": (not schaefer) and len(R) > 0,
    }


# ----------------------------------------------------------------------
# 5. Census driver
# ----------------------------------------------------------------------

def census(
    n: int,
    k: int,
    reps_path: str | None = None,
    require_full_composable: bool = True,
    use_iso_reps: bool = False,
) -> dict:
    """Run the port-relation census at (n, k).

    `require_full_composable`: if True, a "composable non-monotone
    primitive" requires R_T^comp == R_T (every realizable vector is
    composably realizable) and R_T^comp non-monotone.  If False, only
    R_T^comp non-monotone is required.
    `use_iso_reps`: enumerate isomorphism-class representatives instead
    of all labeled tournaments (sound; far faster for n >= 6)."""
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    if reps_path:
        tourns = tournaments_from_reps(reps_path)
    elif use_iso_reps:
        tourns = (tournament_reps_by_extension(n) if n >= 7
                  else tournament_iso_reps(n))
    else:
        tourns = all_tournaments(n)

    distinct_relations: set[frozenset] = set()
    monotone_relations: set[frozenset] = set()
    nonmonotone_relations: set[frozenset] = set()
    nonmono_composable: list[dict] = []
    nonschaefer_relations: set[frozenset] = set()
    nonschaefer_composable: list[dict] = []        # lenient R_comp non-Schaefer
    nonschaefer_composable_strict: list[dict] = []  # strict R_comp non-Schaefer
    schaefer_counter: Counter[str] = Counter()
    tournaments_seen = 0
    no_instances = 0

    orientations = list(itertools.product((0, 1), repeat=k))

    def disjoint(port_tuple) -> bool:
        seen: set[int] = set()
        for x, y in port_tuple:
            if x in seen or y in seen:
                return False
            seen.add(x)
            seen.add(y)
        return True

    # Composability requires INDEPENDENTLY attachable ports: pairwise-
    # disjoint vertex sets (2k distinct vertices).  Shared-vertex ports
    # merely encode order-transitivity (a betweenness artifact) and are
    # not independently composable under the degree-2 budget.
    port_tuples = [pt for pt in itertools.combinations(pairs, k)
                   if disjoint(pt)]
    n_port_tuples = len(port_tuples)

    def flip(rel, o):
        return frozenset(tuple(bi ^ oi for bi, oi in zip(b, o)) for b in rel)

    for T in tourns:
        tournaments_seen += 1
        lfo_cache = build_lfo_cache(T)
        if not lfo_cache:
            no_instances += 1
            continue
        for port_tuple in port_tuples:
            R_base, Rc_base, Rcs_base = port_relation_cached(lfo_cache, port_tuple)
            # orientation is a free design choice; non-Schaefer-ness is
            # NOT flip-invariant, so try all 2^k coordinate complements.
            for o in orientations:
                R = flip(R_base, o)
                R_comp = flip(Rc_base, o)
                R_comp_strict = flip(Rcs_base, o)
                _classify_and_record(
                    T, port_tuple, o, R, R_comp, R_comp_strict, k,
                    distinct_relations, monotone_relations,
                    nonmonotone_relations, nonschaefer_relations,
                    schaefer_counter, nonmono_composable,
                    nonschaefer_composable, nonschaefer_composable_strict,
                    require_full_composable,
                )
    out = _summarize(
        n, k, reps_path, use_iso_reps, tournaments_seen, no_instances,
        distinct_relations, monotone_relations, nonmonotone_relations,
        nonschaefer_relations, schaefer_counter, nonmono_composable,
        nonschaefer_composable, require_full_composable,
    )
    out["disjoint_port_tuples_per_tournament"] = n_port_tuples
    out["composable_nonschaefer_strict_found"] = len(nonschaefer_composable_strict) > 0
    out["composable_nonschaefer_strict_examples"] = nonschaefer_composable_strict[:5]
    return out


def _classify_and_record(
    T, port_tuple, o, R, R_comp, R_comp_strict, k,
    distinct_relations, monotone_relations, nonmonotone_relations,
    nonschaefer_relations, schaefer_counter, nonmono_composable,
    nonschaefer_composable, nonschaefer_composable_strict,
    require_full_composable,
):
    distinct_relations.add(R)
    if is_downward_closed(R, k):
        monotone_relations.add(R)
    else:
        nonmonotone_relations.add(R)

    flags = schaefer_flags(R, k)
    for key in ("horn", "dual_horn", "affine", "bijunctive",
                "zero_valid", "one_valid"):
        if flags[key]:
            schaefer_counter[key] += 1
    if flags["non_schaefer"]:
        nonschaefer_relations.add(R)

    # Strict composable shadow: every witness has port capacity (uniform
    # residual capacity).  Required for a POSITIVE hardness primitive.
    strict_flags = schaefer_flags(R_comp_strict, k) if R_comp_strict else None
    if strict_flags and strict_flags["non_schaefer"] and len(nonschaefer_composable_strict) < 10:
        nonschaefer_composable_strict.append({
            "T": [row[:] for row in T],
            "ports": list(port_tuple),
            "orientation": list(o),
            "R_T": sorted(tuple(b) for b in R),
            "R_comp_strict": sorted(tuple(b) for b in R_comp_strict),
        })

    # Composability is judged on R_comp — the relation that SURVIVES
    # attachment (only residual-capacity witnesses).  The full R_T may
    # be non-Schaefer (e.g. NAE) yet collapse to a Schaefer R_comp once
    # the degree-2 budget prunes vectors lacking a capacity witness.
    # Hardness needs R_comp itself to be non-Schaefer.
    comp_mono = is_downward_closed(R_comp, k) if R_comp else True
    comp_nonmono = bool(R_comp) and not comp_mono
    comp_flags = schaefer_flags(R_comp, k) if R_comp else None
    full_comp = (R_comp == R)
    is_primitive = comp_nonmono and (full_comp or not require_full_composable)
    if is_primitive and len(nonmono_composable) < 10:
        nonmono_composable.append({
            "T": [row[:] for row in T],
            "ports": list(port_tuple),
            "orientation": list(o),
            "R_T": sorted(tuple(b) for b in R),
            "R_comp": sorted(tuple(b) for b in R_comp),
            "full_composable": full_comp,
            "R_T_schaefer": flags,
            "R_comp_schaefer": comp_flags,
        })
    # The decisive hardness signal: R_comp itself non-Schaefer.
    if comp_flags and comp_flags["non_schaefer"] and len(nonschaefer_composable) < 10:
        nonschaefer_composable.append({
            "T": [row[:] for row in T],
            "ports": list(port_tuple),
            "orientation": list(o),
            "R_T": sorted(tuple(b) for b in R),
            "R_comp": sorted(tuple(b) for b in R_comp),
            "full_composable": full_comp,
        })


def _summarize(
    n, k, reps_path, use_iso_reps, tournaments_seen, no_instances,
    distinct_relations, monotone_relations, nonmonotone_relations,
    nonschaefer_relations, schaefer_counter, nonmono_composable,
    nonschaefer_composable, require_full_composable,
):
    source = reps_path or ("iso_reps" if use_iso_reps else "all_labeled")
    return {
        "n": n,
        "k": k,
        "source": source,
        "tournaments_seen": tournaments_seen,
        "no_instances": no_instances,
        "distinct_relations": len(distinct_relations),
        "monotone_relations": len(monotone_relations),
        "nonmonotone_relations": len(nonmonotone_relations),
        "nonschaefer_relations": len(nonschaefer_relations),
        "schaefer_type_counts": dict(schaefer_counter),
        "composable_nonmonotone_found": len(nonmono_composable) > 0,
        "composable_nonmonotone_examples": nonmono_composable[:5],
        "composable_nonschaefer_found": len(nonschaefer_composable) > 0,
        "composable_nonschaefer_examples": nonschaefer_composable[:5],
        "require_full_composable": require_full_composable,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=5)
    parser.add_argument("--k", type=int, default=2)
    parser.add_argument("--reps", type=str, default=None,
                        help="Path to a reps JSON/JSONL file (for n=7).")
    parser.add_argument("--allow-partial-composable", action="store_true",
                        help="Only require R_comp non-monotone (not R_comp==R).")
    parser.add_argument("--iso", action="store_true",
                        help="Enumerate isomorphism-class reps (fast for n>=6).")
    args = parser.parse_args()
    out = census(
        args.n,
        args.k,
        reps_path=args.reps,
        require_full_composable=not args.allow_partial_composable,
        use_iso_reps=args.iso,
    )
    print(json.dumps(out, indent=2, default=list))


if __name__ == "__main__":
    main()
