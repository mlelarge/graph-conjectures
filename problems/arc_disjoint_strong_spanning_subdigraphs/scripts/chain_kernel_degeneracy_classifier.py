"""Classify one-shot B3+ hard-pair failures by chain-kernel degeneracy.

D47 showed that the D45 selected-pair suite cannot be read as an
all-hard-pairs theorem: a short-chain rho-headless hard pair can have
valid B3+ free-entry moves but every move has exit_count == 1.  This
script separates that degeneracy from the D42-style sealed multi-crossing
case, where explicit forced crossing tails exist and the known pair has
a forced-tail B3+ repair.
"""
from __future__ import annotations

import os
import sys
from collections import Counter, defaultdict

_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE = os.path.join(os.path.dirname(_HERE), "code")
for _p in (_CODE, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from b3_all_hard_pairs_search import hard_gateway_rows  # noqa: E402
from b3_selection_suite import classify_no_good, explicit_cases  # noqa: E402
from chain_crossing_selection_check import b3_plus_candidates  # noqa: E402
from check_lexist_fixedroot import subtree_through, tree_arcs  # noqa: E402


def analyze_pair(name, arcs, n, root, a, T, U, forced_tails=frozenset()):
    mult = Counter(arcs)
    Tset, Uset = tree_arcs(T), tree_arcs(U)
    X = subtree_through(T, a[0], root, n)
    exits = sorted(e for e in Uset if e[0] in X and e[1] not in X)
    assert len(exits) == 1, (name, exits)
    unique_exit = exits[0]
    exit_head = unique_exit[1]

    rows = b3_plus_candidates(T, U, mult, n, root, a, set(forced_tails))
    good = [r for r in rows if r["b3_plus_good"]]
    no_good_class = "good" if good else classify_no_good(rows)

    forced_tails = set(forced_tails)
    u_used_forced_crossings = sorted(
        s for s in forced_tails
        if s in U and s not in X and U[s] not in X
    )
    rows_touching_forced_crossing = [
        r for r in rows
        if set(r["S_w"]) & set(u_used_forced_crossings)
    ]
    good_touching_forced_crossing = [
        r for r in good
        if set(r["S_w"]) & set(u_used_forced_crossings)
    ]
    swallowed_rows = [r for r in rows if exit_head in r["S_w"]]
    valid_rows = [
        r for r in rows
        if r["valid_tree"] and r["valid_pair"]
        and r["x_formula_ok"] and r["intermediate"]
    ]

    multi_forced_crossing = len(u_used_forced_crossings) >= 2
    if good_touching_forced_crossing:
        label = "sealed-multi-crossing-b3-good"
    elif good:
        label = "b3-good"
    elif no_good_class == "exit-count" and multi_forced_crossing:
        label = "sealed-multi-crossing-b3-fail"
    elif no_good_class == "exit-count" and swallowed_rows:
        label = "short-chain-exit-head-in-subtree"
    elif no_good_class == "exit-count":
        label = "short-chain-one-exit"
    else:
        label = no_good_class

    return {
        "name": name,
        "n": n,
        "a": a,
        "X": sorted(X),
        "single_exit": unique_exit,
        "candidates": len(rows),
        "valid_candidates": len(valid_rows),
        "good": len(good),
        "class": no_good_class,
        "label": label,
        "forced_tails": sorted(forced_tails),
        "u_used_forced_crossings": u_used_forced_crossings,
        "forced_rows": len(rows_touching_forced_crossing),
        "forced_good": len(good_touching_forced_crossing),
        "swallowed_rows": len(swallowed_rows),
        "exit_counts": sorted(set(r["exit_count"] for r in rows)),
    }


def selected_cases():
    for args in explicit_cases():
        yield args

    from generalized_chain_kernel_b3_defeat import hard_pair as d47_pair
    from rho_headless_witness import dbullet_arcs as rho_arcs

    T, U = d47_pair()
    yield (
        "generalized_short_chain(D47)",
        rho_arcs(),
        8,
        0,
        (1, 5),
        T,
        U,
        frozenset(),
    )


def print_selected_cases():
    print("=== SELECTED HARD PAIRS ===")
    rows = [analyze_pair(*args) for args in selected_cases()]
    for r in rows:
        forced = (
            f" forced_crossings={r['u_used_forced_crossings']}"
            if r["forced_tails"] else ""
        )
        print(
            f"{r['name']}: label={r['label']} class={r['class']} "
            f"candidates={r['candidates']} good={r['good']} "
            f"a={r['a']} exit={r['single_exit']} "
            f"exit_counts={r['exit_counts']}{forced}"
        )

    d47 = [r for r in rows if r["name"] == "generalized_short_chain(D47)"][0]
    d42 = [r for r in rows if r["name"] == "chain_kernel(D42)"][0]
    assert d47["label"] == "short-chain-exit-head-in-subtree", d47
    assert d47["good"] == 0 and d47["class"] == "exit-count", d47
    assert d42["label"] == "sealed-multi-crossing-b3-good", d42
    assert d42["forced_good"] >= 1 and len(d42["u_used_forced_crossings"]) >= 2, d42
    return rows


def print_small_exhaustive_samples():
    print("\n=== SMALL EXHAUSTIVE FAILURE INVENTORY ===")
    from gateway_t_eq_u_witness import dbullet_arcs as tequ_arcs
    from rho_headless_witness import dbullet_arcs as rho_arcs

    cases = [
        ("t_eq_u(D10)", tequ_arcs(), 7, 0),
        ("rho_headless(D17)", rho_arcs(), 8, 0),
    ]
    for name, arcs, n, root in cases:
        _arbs, stats, failures = hard_gateway_rows(name, arcs, n, root)
        by_class = defaultdict(int)
        sample = {}
        for f in failures:
            by_class[f["class"]] += 1
            sample.setdefault(f["class"], f)
        print(f"{name}: stats={dict(stats)}")
        for cls in sorted(sample):
            f = sample[cls]
            refined = analyze_pair(
                f"{name} sample {cls}",
                arcs,
                n,
                root,
                f["a"],
                f["T"],
                f["U"],
            )
            print(
                f"  sample class={cls} count={by_class[cls]} "
                f"label={refined['label']} a={f['a']} "
                f"exit={refined['single_exit']} "
                f"exit_counts={refined['exit_counts']} "
                f"swallowed_rows={refined['swallowed_rows']}"
            )
    return True


def main():
    print_selected_cases()
    print_small_exhaustive_samples()
    print("\nALL ASSERTIONS PASS")


if __name__ == "__main__":
    main()
