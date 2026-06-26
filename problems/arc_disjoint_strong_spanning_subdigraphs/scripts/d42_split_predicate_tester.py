"""Test small sufficient predicates for D42 split-core lambda >= 2.

D52 showed endpoint-region features that correlate with successful
pending split choices.  This script samples D42 split choices, computes a
small feature vector, and searches conjunctions of simple threshold atoms
for sampled sufficient predicates:

    predicate(choice) => lambda(split core) >= 2.

The goal is not a perfect classifier.  We want a clean, nonempty,
zero-false-positive condition that can become the combinatorial core of a
Prescribed Pending Missing Entry Lemma.
"""
from __future__ import annotations

import itertools
import os
import random
import sys
from collections import Counter

_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE = os.path.join(os.path.dirname(_HERE), "code")
for _p in (_CODE, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from digraph import Digraph  # noqa: E402
from chain_kernel_witness import host_arcs  # noqa: E402


SEED = 5321
SAMPLES = 2500
MAX_CONJUNCTION = 4
MIN_SUPPORT = 10
MIN_PRECISION = 0.90
MAX_LOCAL_CHOICES = 80


def region(v):
    if v == 2:
        return "u"
    if v in {3, 4, 5}:
        return "cage"
    if v in {6, 7}:
        return "heads"
    if v == 8:
        return "v"
    if v in {10, 12, 14}:
        return "chainK"
    if v in {15, 16}:
        return "roots"
    if 17 <= v <= 23:
        return "ladder"
    return f"other{v}"


def relabel_core_arcs(arcs, v2):
    idx = {v: i for i, v in enumerate(v2)}
    return [(idx[u], idx[v]) for u, v in arcs if u in idx and v in idx]


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


def d42_split_setup():
    rng = random.Random(SEED)
    v1 = (0, 1, 9, 11, 13)
    v2 = tuple(v for v in range(24) if v not in v1)
    host = list(host_arcs())
    host_set = set(host)
    core_arcs = relabel_core_arcs(host, v2)
    rel = {v: i for i, v in enumerate(v2)}
    vertices = (9, 11, 13)
    per_vertex = {s: local_split_choices(host_set, v2, s, rng) for s in vertices}
    return v2, core_arcs, rel, vertices, per_vertex


def sample_rows():
    rng = random.Random(SEED)
    v2, core_arcs, rel, vertices, per_vertex = d42_split_setup()

    rows = []
    seen = set()
    attempts = 0
    while len(seen) < SAMPLES and attempts < 40 * SAMPLES:
        attempts += 1
        key = tuple(rng.randrange(len(per_vertex[s])) for s in vertices)
        if key in seen:
            continue
        seen.add(key)
        choice = {s: per_vertex[s][key[i]] for i, s in enumerate(vertices)}

        split_arcs, pairs = split_arcs_and_pairs(choice, rel, vertices)
        lam = Digraph.from_arcs(range(len(v2)), core_arcs + split_arcs).arc_connectivity()
        features = feature_counts(pairs)
        rows.append({
            "key": key,
            "lambda": lam,
            "good": lam >= 2,
            "pairs": tuple(sorted(pairs)),
            "choice": choice,
            "features": features,
        })
    return rows


def split_arcs_and_pairs(choice, rel, vertices):
    split_arcs = []
    pairs = []
    for s in vertices:
        for x, y in choice[s]:
            split_arcs.append((rel[x], rel[y]))
            pairs.append((region(x), region(y)))
    return split_arcs, pairs


def feature_counts(pairs):
    c = Counter(pairs)
    out = {
        "u_chainK": c[("u", "chainK")],
        "heads_chainK": c[("heads", "chainK")],
        "roots_chainK": c[("roots", "chainK")],
        "roots_cage": c[("roots", "cage")],
        "roots_heads": c[("roots", "heads")],
        "roots_return": c[("roots", "cage")] + c[("roots", "heads")],
        "u_or_heads_chainK": c[("u", "chainK")] + c[("heads", "chainK")],
        "total_chainK_heads": sum(1 for _src, dst in pairs if dst == "chainK"),
        "chainK_to_cage_or_heads": (
            c[("chainK", "cage")]
            + c[("chainK", "heads")]
        ),
        "nonroot_to_chainK": (
            c[("u", "chainK")]
            + c[("heads", "chainK")]
            + c[("v", "chainK")]
            + c[("chainK", "chainK")]
        ),
    }
    return out


def out_cut_size(arcs, mask):
    total = 0
    for u, v in arcs:
        if (mask >> u) & 1 and not ((mask >> v) & 1):
            total += 1
    return total


def deficient_core_cuts(n, core_arcs):
    cuts = []
    for mask in range(1, (1 << n) - 1):
        core_out = out_cut_size(core_arcs, mask)
        if core_out <= 1:
            cuts.append((mask, core_out))
    return cuts


def split_repairs_all_deficient_cuts(deficient_cuts, split_arcs):
    for mask, core_out in deficient_cuts:
        out = core_out
        for u, v in split_arcs:
            if (mask >> u) & 1 and not ((mask >> v) & 1):
                out += 1
                if out >= 2:
                    break
        if out < 2:
            return False, (mask, out)
    return True, None


def best_candidate(features):
    return features["u_chainK"] >= 1 and features["u_or_heads_chainK"] >= 2


def exact_best_candidate_check():
    v2, core_arcs, rel, vertices, per_vertex = d42_split_setup()
    deficient = deficient_core_cuts(len(v2), core_arcs)
    all_repaired = 0
    selected = 0
    repaired = 0
    bad = 0
    bad_example = None
    total = 1
    for s in vertices:
        total *= len(per_vertex[s])

    for product in itertools.product(*(range(len(per_vertex[s])) for s in vertices)):
        choice = {s: per_vertex[s][product[i]] for i, s in enumerate(vertices)}
        split_arcs, pairs = split_arcs_and_pairs(choice, rel, vertices)
        features = feature_counts(pairs)
        ok, witness = split_repairs_all_deficient_cuts(deficient, split_arcs)
        if ok:
            all_repaired += 1
        if not best_candidate(features):
            continue
        selected += 1
        if ok:
            repaired += 1
        else:
            bad += 1
            if bad_example is None:
                bad_example = {
                    "key": product,
                    "pairs": tuple(sorted(pairs)),
                    "features": features,
                    "witness": witness,
                }

    return {
        "local_counts": {s: len(per_vertex[s]) for s in vertices},
        "total": total,
        "deficient_core_cuts": len(deficient),
        "deficient_core_cut_details": [
            (core_out, tuple(v2[i] for i in range(len(v2)) if (mask >> i) & 1))
            for mask, core_out in deficient
        ],
        "all_repaired": all_repaired,
        "selected": selected,
        "repaired": repaired,
        "bad": bad,
        "bad_example": bad_example,
    }


def focused_specs():
    """Small atom family suggested by the D52 signal."""
    return [
        ("u_chainK>=1", "u_chainK", ">=", 1),
        ("u_chainK>=2", "u_chainK", ">=", 2),
        ("heads_chainK>=1", "heads_chainK", ">=", 1),
        ("heads_chainK>=2", "heads_chainK", ">=", 2),
        ("u_or_heads_chainK>=2", "u_or_heads_chainK", ">=", 2),
        ("u_or_heads_chainK>=3", "u_or_heads_chainK", ">=", 3),
        ("nonroot_to_chainK>=2", "nonroot_to_chainK", ">=", 2),
        ("nonroot_to_chainK>=3", "nonroot_to_chainK", ">=", 3),
        ("total_chainK_heads>=2", "total_chainK_heads", ">=", 2),
        ("total_chainK_heads>=3", "total_chainK_heads", ">=", 3),
        ("roots_return>=1", "roots_return", ">=", 1),
        ("roots_return>=2", "roots_return", ">=", 2),
        ("roots_cage>=1", "roots_cage", ">=", 1),
        ("roots_heads>=1", "roots_heads", ">=", 1),
        ("roots_chainK<=0", "roots_chainK", "<=", 0),
        ("roots_chainK<=1", "roots_chainK", "<=", 1),
        ("chainK_to_cage_or_heads>=1", "chainK_to_cage_or_heads", ">=", 1),
    ]


def threshold_specs(rows):
    """All simple one-feature thresholds, for a cheap completeness check."""
    specs = []
    features = sorted(rows[0]["features"])
    for feat in features:
        values = sorted(set(r["features"][feat] for r in rows))
        for t in values:
            if t > 0:
                specs.append((f"{feat}>={t}", feat, ">=", t))
            if t < max(values):
                specs.append((f"{feat}<={t}", feat, "<=", t))
    return specs


def atom_catalog(rows):
    specs = focused_specs() + threshold_specs(rows)
    atoms = {}
    for name, feat, op, threshold in specs:
        mask = 0
        for i, row in enumerate(rows):
            value = row["features"][feat]
            ok = value >= threshold if op == ">=" else value <= threshold
            if ok:
                mask |= 1 << i
        if mask:
            atoms.setdefault(name, mask)
    return sorted(atoms.items())


def first_row_for_mask(rows, mask):
    if not mask:
        return None
    return rows[(mask & -mask).bit_length() - 1]


def evaluate_mask(rows, mask, good_mask, total_good):
    support = mask.bit_count()
    if support == 0:
        return None
    good = (mask & good_mask).bit_count()
    bad = support - good
    return {
        "support": support,
        "good": good,
        "bad": bad,
        "precision": good / support,
        "recall": good / total_good if total_good else 0.0,
        "example_good": first_row_for_mask(rows, mask & good_mask),
        "example_bad": first_row_for_mask(rows, mask & ~good_mask),
    }


def main():
    rows = sample_rows()
    lambda_counts = Counter(r["lambda"] for r in rows)
    total_good = sum(1 for r in rows if r["good"])
    print("D42 split predicate tester")
    print(f"seed={SEED} samples={len(rows)} lambda_counts={dict(sorted(lambda_counts.items()))}")
    print(f"good(lambda>=2)={total_good}/{len(rows)}")

    atoms = atom_catalog(rows)
    good_mask = 0
    for i, row in enumerate(rows):
        if row["good"]:
            good_mask |= 1 << i

    results = []
    for size in range(1, MAX_CONJUNCTION + 1):
        for combo in itertools.combinations(atoms, size):
            names = tuple(name for name, _pred in combo)
            mask = (1 << len(rows)) - 1
            for _name, atom_mask in combo:
                mask &= atom_mask
                if mask.bit_count() < MIN_SUPPORT:
                    break
            ev = evaluate_mask(rows, mask, good_mask, total_good)
            if ev is None:
                continue
            # Keep useful candidates only: enough support and either perfect
            # precision or a strong near miss.
            if ev["support"] >= MIN_SUPPORT and (
                ev["bad"] == 0 or ev["precision"] >= MIN_PRECISION
            ):
                results.append((names, ev))

    perfect = [(names, ev) for names, ev in results if ev["bad"] == 0]
    perfect.sort(key=lambda x: (-x[1]["good"], len(x[0]), x[0]))
    near = [(names, ev) for names, ev in results if ev["bad"] != 0]
    near.sort(key=lambda x: (-x[1]["precision"], -x[1]["good"], len(x[0]), x[0]))

    print("\nTop sampled-sufficient predicates (zero false positives):")
    for names, ev in perfect[:20]:
        print(
            f"  support={ev['support']} recall={ev['recall']:.3f} "
            f"pred={' & '.join(names)}"
        )
    print("\nTop near-miss predicates (precision >= 0.90):")
    for names, ev in near[:10]:
        print(
            f"  support={ev['support']} good={ev['good']} bad={ev['bad']} "
            f"precision={ev['precision']:.3f} recall={ev['recall']:.3f} "
            f"pred={' & '.join(names)}"
        )

    assert perfect, "no sampled-sufficient predicate found"
    best_names, best_ev = perfect[0]
    print("\nBest predicate example:")
    print(f"  pred={' & '.join(best_names)}")
    ex = best_ev["example_good"]
    print(f"  lambda={ex['lambda']} pairs={ex['pairs']} features={ex['features']}")

    exact = exact_best_candidate_check()
    print("\nExact capped-suite cut check for:")
    print("  pred=u_chainK>=1 & u_or_heads_chainK>=2")
    print(
        f"  local_counts={exact['local_counts']} total={exact['total']} "
        f"deficient_core_cuts={exact['deficient_core_cuts']}"
    )
    print(f"  deficient_core_cut_details={exact['deficient_core_cut_details']}")
    print(
        f"  all_repaired={exact['all_repaired']} "
        f"  selected={exact['selected']} repaired={exact['repaired']} "
        f"bad={exact['bad']}"
    )
    if exact["bad_example"] is not None:
        print(f"  bad_example={exact['bad_example']}")
    assert exact["selected"] > 0
    assert exact["bad"] == 0
    print("ALL ASSERTIONS PASS")


if __name__ == "__main__":
    main()
