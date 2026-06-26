"""Probe split-digraph pending-decomposition technology on the witnesses.

This is a diagnostic inspired by the recent split-digraph SAD proofs.
For a near-split host with V1 = {p,q} plus independent vertices and V2
semicomplete, choose two split-off paths x -> s -> y through each
independent-side vertex s in V1\\{p,q}.  Add the corresponding core arcs
x -> y to the V2 semicomplete core, SAD-colour the resulting core, and
check whether the two split arcs for each s receive opposite colours.

If yes, the core SAD can be lifted in the "pending decomposition" style:
replace each coloured split arc x->y by the two arcs x->s, s->y in the
same colour.  This is not a full proof of the split-digraph theorems and
does not handle the chord endpoints p,q; it is a concrete probe for the
proof technology suggested after D48.
"""
from __future__ import annotations

import itertools
import os
import random
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass

_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE = os.path.join(os.path.dirname(_HERE), "code")
for _p in (_CODE, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from digraph import Digraph  # noqa: E402
from verifier_sat import verify_sat  # noqa: E402


SEED = 4811
MAX_LOCAL_CHOICES = 80
MAX_GLOBAL_CHOICES = 600


@dataclass(frozen=True)
class Case:
    name: str
    host_arcs: list[tuple[int, int]]
    n_host: int
    v1: tuple[int, ...]
    v2: tuple[int, ...]


def occurrence_keys(arcs):
    counts = Counter()
    out = []
    for u, v in arcs:
        key = counts[(u, v)]
        counts[(u, v)] += 1
        out.append((u, v, key))
    return out


def relabel_core_arcs(host_arcs, v2):
    idx = {v: i for i, v in enumerate(v2)}
    return [(idx[u], idx[v]) for u, v in host_arcs if u in idx and v in idx]


def local_split_choices(host_set, v2, s, rng):
    incoming = sorted(x for x in v2 if (x, s) in host_set)
    outgoing = sorted(y for y in v2 if (s, y) in host_set)
    choices = []
    if len(incoming) < 2 or len(outgoing) < 2:
        return choices
    for xs in itertools.combinations(incoming, 2):
        for ys in itertools.combinations(outgoing, 2):
            for perm in (ys, tuple(reversed(ys))):
                pairs = tuple(sorted(zip(xs, perm)))
                if any(x == y for x, y in pairs):
                    continue
                choices.append(pairs)
    choices = sorted(set(choices))
    if len(choices) > MAX_LOCAL_CHOICES:
        rng.shuffle(choices)
        choices = sorted(choices[:MAX_LOCAL_CHOICES])
    return choices


def global_choice_iter(per_vertex, rng):
    vertices = sorted(per_vertex)
    total = 1
    for v in vertices:
        total *= len(per_vertex[v])
    if total <= MAX_GLOBAL_CHOICES:
        for product in itertools.product(*(per_vertex[v] for v in vertices)):
            yield dict(zip(vertices, product))
        return

    seen = set()
    attempts = 0
    while len(seen) < MAX_GLOBAL_CHOICES and attempts < 20 * MAX_GLOBAL_CHOICES:
        attempts += 1
        choice = tuple(rng.randrange(len(per_vertex[v])) for v in vertices)
        if choice in seen:
            continue
        seen.add(choice)
        yield {v: per_vertex[v][i] for v, i in zip(vertices, choice)}


def split_probe(case, rng):
    host = list(case.host_arcs)
    host_set = set(host)
    stable = tuple(v for v in case.v1 if v not in (0, 1))
    core_arcs = relabel_core_arcs(host, case.v2)
    rel = {v: i for i, v in enumerate(case.v2)}

    per_vertex = {}
    for s in stable:
        choices = local_split_choices(host_set, case.v2, s, rng)
        if not choices:
            return {
                "name": case.name,
                "stable": stable,
                "status": "no-two-split-choice",
                "bad_vertex": s,
            }
        per_vertex[s] = choices

    if not stable:
        D = Digraph.from_arcs(range(len(case.v2)), core_arcs)
        sad = verify_sat(D, time_limit_s=30.0)
        return {
            "name": case.name,
            "stable": stable,
            "status": "no-stable-vertices",
            "core_lambda": D.arc_connectivity(),
            "core_sad": sad["status"],
        }

    tried = 0
    sad_seen = 0
    colour_pending_seen = 0
    best = None
    hit = None

    for choice in global_choice_iter(per_vertex, rng):
        tried += 1
        split_arcs = []
        split_meta = []
        for s in stable:
            for x, y in choice[s]:
                arc = (rel[x], rel[y])
                split_arcs.append(arc)
                split_meta.append((s, x, y, arc))

        all_arcs = core_arcs + split_arcs
        all_keys = occurrence_keys(all_arcs)
        split_keys = all_keys[len(core_arcs):]
        D = Digraph.from_arcs(range(len(case.v2)), all_arcs)
        core_lambda = D.arc_connectivity()
        sad = verify_sat(D, time_limit_s=30.0)
        if sad["status"] != "SAT":
            if best is None:
                best = {
                    "choice": choice,
                    "core_lambda": core_lambda,
                    "core_sad": sad["status"],
                }
            continue

        sad_seen += 1
        red, blue = sad["witness"]
        red_set, blue_set = set(red), set(blue)
        colours_by_s = defaultdict(list)
        for meta, key in zip(split_meta, split_keys):
            s = meta[0]
            if key in red_set:
                colours_by_s[s].append("R")
            elif key in blue_set:
                colours_by_s[s].append("B")
            else:
                raise AssertionError((case.name, "split key uncoloured", key))

        pending_ok = all(set(colours_by_s[s]) == {"R", "B"} for s in stable)
        if pending_ok:
            colour_pending_seen += 1
            hit = {
                "choice": choice,
                "core_lambda": core_lambda,
                "core_sad": sad["status"],
                "colours_by_s": {s: tuple(colours_by_s[s]) for s in stable},
                "split_paths": split_meta,
            }
            break
        if best is None or core_lambda > best.get("core_lambda", -1):
            best = {
                "choice": choice,
                "core_lambda": core_lambda,
                "core_sad": sad["status"],
                "colours_by_s": {s: tuple(colours_by_s[s]) for s in stable},
            }

    return {
        "name": case.name,
        "stable": stable,
        "status": "pending-hit" if hit else "no-pending-hit",
        "tried": tried,
        "core_sad_seen": sad_seen,
        "pending_seen": colour_pending_seen,
        "hit": hit,
        "best": best,
    }


def cases():
    from core_embedding_witness import host_arcs as core_host
    from dominated_witness import host_arcs as dominated_host
    from relay_free_witness import host_arcs as relay_host
    from rho_headless_witness import host_arcs as rho_host
    from saturation_kernel_witness import host_arcs as sat_host
    from chain_kernel_witness import host_arcs as chain_host

    yield Case("rho_headless_D17_and_D47_host", rho_host(), 9, (0, 1, 2), tuple(range(3, 9)))
    yield Case("dominated_D18_host", dominated_host(), 12, (0, 1, 2), tuple(range(3, 12)))
    yield Case("relay_free_D19_host", relay_host(), 15, (0, 1, 2), tuple(range(3, 15)))
    yield Case("core_embedding_D28_host", core_host(), 12, (0, 1, 2), tuple(range(3, 12)))
    yield Case("saturation_kernel_D38_host", sat_host(), 15, (0, 1, 2), tuple(range(3, 15)))
    v1 = (0, 1, 9, 11, 13)
    v2 = tuple(v for v in range(24) if v not in v1)
    yield Case("chain_kernel_D42_host", chain_host(), 24, v1, v2)


def main():
    rng = random.Random(SEED)
    rows = [split_probe(case, rng) for case in cases()]
    print("Pending decomposition split-off probe")
    print(f"seed={SEED}")
    for row in rows:
        print(
            f"{row['name']}: status={row['status']} "
            f"stable={row.get('stable')}"
        )
        if row["status"] in {"pending-hit", "no-pending-hit"}:
            print(
                f"  tried={row['tried']} core_sad_seen={row['core_sad_seen']} "
                f"pending_seen={row['pending_seen']}"
            )
        if row.get("hit"):
            hit = row["hit"]
            print(
                f"  hit_core_lambda={hit['core_lambda']} "
                f"colours_by_s={hit['colours_by_s']}"
            )
            print(f"  split_paths={hit['split_paths']}")
        elif row.get("best"):
            best = row["best"]
            print(
                f"  best_core_lambda={best.get('core_lambda')} "
                f"best_core_sad={best.get('core_sad')} "
                f"best_colours={best.get('colours_by_s')}"
            )

    assert any(r["name"] == "chain_kernel_D42_host" and r["status"] == "pending-hit" for r in rows)
    assert all(r["status"] in {"pending-hit", "no-pending-hit"} for r in rows)
    print("ALL ASSERTIONS PASS")


if __name__ == "__main__":
    main()
