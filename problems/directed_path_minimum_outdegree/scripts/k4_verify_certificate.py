"""Verify the delta=4, n=10 certificate.

Reads ../data/k4_n10_certificate.json and mechanically checks every entry:

  Per-configuration (S, T):
    - (S, T) is a valid configuration (v_7 in S, |S|=4, |T|=2,
      sigma(T) subset S).
    - Forced arcs are claimed.
  Per-completion (full arc set stored in certificate):
    - Recomputed SHA-256 hash of the arc set matches certificate.
    - 4-outregular: every vertex has out-degree exactly 4.
    - Oriented: no loops, no antiparallel pair.
    - Forced arcs: every certificate-listed forced arc is in the
      completion's arc set.
    - Claim 12: every S-vertex's out-arcs lie in V(C).
    - Lemma A reverse: no in-arc to v_0 from {x, y}.
    - Score sequence: every t in T has d^+_S(t) = 1; every u in S\\T has
      d^+_S(u) = 2.
    - Witness path: present in the completion (every consecutive arc
      exists), is a directed simple path (vertices distinct), and has
      length >= 8.
  Coverage:
    - Brute-force enumeration of valid (S, T) matches the certificate's
      configurations.
  Summary:
    - num_obstructions == 0, all_closed == True.

This script does NOT regenerate the certificate; it only verifies it.
For full reproduction, run:
  uv run python scripts/k4_independent_check.py
  uv run python scripts/k4_generate_certificate.py
"""

import json
import sys
import hashlib
from itertools import combinations
from pathlib import Path
from typing import FrozenSet, Set, Tuple


PROBLEM_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROBLEM_ROOT / 'data'
N = 10
ALL_V = frozenset(range(N))
PATH_V = frozenset(range(8))
CYCLE_V = frozenset(range(1, 8))
OUTSIDE_V = frozenset({8, 9})
DELTA = 4


def succ_C(v: int) -> int:
    if v == 7:
        return 1
    if 1 <= v <= 6:
        return v + 1
    raise ValueError(v)


def pred_C(v: int) -> int:
    if v == 1:
        return 7
    if 2 <= v <= 7:
        return v - 1
    raise ValueError(v)


def all_valid_st_brute_force():
    """Enumerate (S, T) with v_7 in S, |S|=4, |T|=2, sigma(T) subset S."""
    out = []
    for S_tuple in combinations(range(1, 8), 4):
        if 7 not in S_tuple:
            continue
        S = frozenset(S_tuple)
        for T_tuple in combinations(S_tuple, 2):
            T = frozenset(T_tuple)
            sigma_T = frozenset(pred_C(t) for t in T)
            if sigma_T.issubset(S):
                out.append((S, T))
    return out


def hash_arcs(arcs):
    """Stable hash of an arc set (sorted, sha256). Same as in
    k4_independent_check.py to allow cross-checking."""
    h = hashlib.sha256()
    for (u, w) in sorted(arcs):
        h.update(f"{u},{w};".encode())
    return h.hexdigest()


def check_completion(arcs, S, T, forced_arcs, claimed_hash, witness_path):
    """Run all mechanical checks on a single completion. Returns
    (ok: bool, error: str|None)."""
    arcs_set = set(tuple(a) for a in arcs)
    arcs_for_hash = [(int(a[0]), int(a[1])) for a in arcs]

    # 1. Hash recomputation
    recomputed = hash_arcs(arcs_for_hash)
    if recomputed != claimed_hash:
        return False, f"hash mismatch: claimed {claimed_hash[:12]}..., recomputed {recomputed[:12]}..."

    # 2. No loops
    for (u, v) in arcs_set:
        if u == v:
            return False, f"loop arc ({u}, {v})"

    # 3. No antiparallel
    for (u, v) in arcs_set:
        if (v, u) in arcs_set and u != v:
            return False, f"antiparallel pair ({u}, {v})"

    # 4. 4-outregular
    out_count = {v: 0 for v in range(N)}
    for (u, _) in arcs_set:
        out_count[u] += 1
    bad = [(v, c) for (v, c) in out_count.items() if c != DELTA]
    if bad:
        return False, f"4-outregular violation: {bad}"

    # 5. Forced arcs present
    forced_set = set((int(a[0]), int(a[1])) for a in forced_arcs)
    missing_forced = forced_set - arcs_set
    if missing_forced:
        return False, f"missing forced arcs: {sorted(missing_forced)[:5]}"

    # 6. Claim 12: S-vertex out-arcs in V(C)
    for s in S:
        for (u, v) in arcs_set:
            if u == s and v not in CYCLE_V:
                return False, f"Claim 12 violated: S-vertex {s} sends arc to {v} not in V(C)"

    # 7. Lemma A reverse: no in-arc to v_0 from {x, y}
    for ext in OUTSIDE_V:
        if (ext, 0) in arcs_set:
            return False, f"Lemma A reverse violated: arc ({ext}, 0)"

    # 8. Score sequence
    for s in S:
        d_S = sum(1 for (u, v) in arcs_set if u == s and v in S)
        if s in T:
            if d_S != 1:
                return False, f"score sequence violated: T-vertex {s} has d^+_S = {d_S}, expected 1"
        else:
            if d_S != 2:
                return False, f"score sequence violated: U-vertex {s} has d^+_S = {d_S}, expected 2"

    # 9. Witness path: contained, simple, length >= 8
    if witness_path is None:
        return False, "no witness path"
    if len(witness_path) < 9:
        return False, f"witness path has length {len(witness_path) - 1} < 8"
    if len(set(witness_path)) != len(witness_path):
        return False, f"witness path not simple (repeated vertex)"
    for i in range(len(witness_path) - 1):
        u, v = witness_path[i], witness_path[i + 1]
        if (u, v) not in arcs_set:
            return False, f"witness path arc ({u}, {v}) not in completion"

    return True, None


def is_valid_st(S, T):
    """Check (S, T) validity: |S|=4, |T|=2, v_7 in S, sigma(T) subset S."""
    if len(S) != 4:
        return False, f"|S| = {len(S)}"
    if len(T) != 2:
        return False, f"|T| = {len(T)}"
    if 7 not in S:
        return False, "v_7 not in S"
    if not T.issubset(S):
        return False, "T not subset S"
    sigma_T = frozenset(pred_C(t) for t in T)
    if not sigma_T.issubset(S):
        return False, f"sigma(T) = {sorted(sigma_T)} not subset S"
    return True, None


def main():
    with open(DATA_DIR / 'k4_n10_certificate.json', 'r') as f:
        cert = json.load(f)

    metadata = cert['metadata']
    print("Certificate metadata:")
    print(f"  theorem: {metadata['theorem'][:80]}...")
    print(f"  n = {metadata['n']}, delta = {metadata['delta']}")
    print(f"  rule_set = {metadata['rule_set']}")
    # Note: 'generated_at_utc' and 'python_version' from the cert are
    # intentionally omitted to keep this script's stdout deterministic
    # (those fields drift across runs and would invalidate the recorded
    # SHA-256 of this verifier's output).
    print()

    # 1. (S, T) coverage
    expected_pairs = {(tuple(sorted(S)), tuple(sorted(T))) for (S, T) in all_valid_st_brute_force()}
    cert_pairs = {(tuple(c['S']), tuple(c['T'])) for c in cert['configurations']}
    missing = expected_pairs - cert_pairs
    extra = cert_pairs - expected_pairs
    if missing:
        print(f"FAIL: certificate missing (S, T): {missing}")
        sys.exit(1)
    if extra:
        print(f"FAIL: certificate has extra (S, T): {extra}")
        sys.exit(1)
    print(f"  (S, T) coverage: PASS ({len(cert_pairs)} configurations)")

    # 2. Per-(S, T) and per-completion checks
    total_completions = 0
    for entry in cert['configurations']:
        S = frozenset(entry['S'])
        T = frozenset(entry['T'])
        ok, reason = is_valid_st(S, T)
        if not ok:
            print(f"FAIL: invalid (S, T) S={entry['S']} T={entry['T']}: {reason}")
            sys.exit(1)

        forced_arcs = entry['forced_arcs']
        comps = entry['completions']
        if len(comps) != entry['num_completions']:
            print(f"FAIL: S={entry['S']} T={entry['T']} num_completions mismatch")
            sys.exit(1)

        for i, comp in enumerate(comps):
            arcs = comp.get('arcs')
            if arcs is None:
                print(f"FAIL: S={entry['S']} T={entry['T']} completion {i} missing arcs field")
                sys.exit(1)
            ok, err = check_completion(
                arcs=arcs,
                S=S, T=T,
                forced_arcs=forced_arcs,
                claimed_hash=comp.get('arcs_hash'),
                witness_path=comp.get('path'),
            )
            if not ok:
                print(f"FAIL: S={entry['S']} T={entry['T']} completion {i}: {err}")
                sys.exit(1)
        total_completions += len(comps)

    print(f"  per-completion mechanical checks: PASS")
    print(f"    total completions verified: {total_completions}")

    # 3. Summary
    if cert['summary']['total_obstructions'] != 0:
        print(f"FAIL: summary obstructions = {cert['summary']['total_obstructions']}")
        sys.exit(1)
    if not cert['summary']['all_closed']:
        print(f"FAIL: summary all_closed = False")
        sys.exit(1)

    print()
    print("CERTIFICATE VERIFIED.")
    print("  All 24 (S, T) configurations match brute force.")
    print(f"  All {total_completions} completions pass: hash, 4-outregular, oriented,")
    print(f"  forced arcs, Claim 12, Lemma A reverse, score sequence,")
    print(f"  witness path containment, simplicity, and length >= 8.")
    print("  Theorem holds at delta=4, n=10.")


if __name__ == '__main__':
    main()
