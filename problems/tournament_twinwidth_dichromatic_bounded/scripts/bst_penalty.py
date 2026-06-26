"""BST-ordering penalty beta(T) = bstOmega(T) - omegaVec(T) for Conj 3.16 route.

A BST-ordering of a tournament T is the in-order traversal of a binary search
tree where, at each node r, the left subtree is a subset of N^-(r) (in-neighbours,
u->r) and the right subtree a subset of N^+(r) (out-neighbours, r->u).  For a
tournament, choosing a root r EXACTLY bipartitions the remaining vertices into
N^-(r) (left) and N^+(r) (right), and we recurse on each side.

  bst_orders(n, A, subset)  -- yields every BST in-order arising from a subset.
  bst_omega(n, A)           -- min over BST-orders of the back-edge clique number.
  omega_vec(n, A)           -- min over ALL orders (existing exact oracle).

Invariant (asserted on every instance): bst_omega >= omega_vec  (BST subset of all).
beta = bst_omega - omega_vec.

The reduction Conj 3.16 => 3.13 => 3.12 PREDICTS beta is bounded by a function of
omegaVec alone.  We test beta <= 1 over all n<=8 iso-classes (gentourng), and
bst_omega(S_k)=omegaVec(S_k) (BST free on the load-bearing tower).
"""
from __future__ import annotations

import json
import subprocess
import sys
from functools import lru_cache

import core
import constructions as C


def _bst_orders_subset(A, subset):
    """Yield each BST in-order traversal (as a tuple) over `subset` (a tuple of
    vertices).  Root r in subset splits the rest into L=N^-(r) (u->r) and
    R=N^+(r) (r->u); order = inorder(L) + (r,) + inorder(R)."""
    subset = tuple(subset)
    if len(subset) == 0:
        yield ()
        return
    if len(subset) == 1:
        yield subset
        return
    for r in subset:
        L = tuple(u for u in subset if u != r and A[u][r])   # u -> r : in-neighbour
        R = tuple(u for u in subset if u != r and A[r][u])   # r -> u : out-neighbour
        for lo in _bst_orders_subset(A, L):
            for ro in _bst_orders_subset(A, R):
                yield lo + (r,) + ro


def bst_omega(n, arcs, lb=1):
    """min over BST-orderings of the back-edge clique number (exact).

    `lb` is a known lower bound (e.g. omega_vec(T), since every BST order is an
    order so bst_omega >= omega_vec).  Enumeration stops as soon as some BST order
    attains `lb` -- then bst_omega == lb is proven without exhausting all orders.
    """
    if n == 0:
        return 0
    A = core._adj(n, arcs)
    best = n
    full = tuple(range(n))
    for order in _bst_orders_subset(A, full):
        w = core._backedge_clique_for_order(n, A, list(order))
        if w < best:
            best = w
            if best <= lb:
                break
    return best


def bst_omega_memo(n, arcs):
    """Memoized min-over-BST back-edge clique.  Because the back-edge clique of a
    BST-order does NOT decompose cleanly per subtree (cross-subtree back edges
    exist via the C3-style A->B->C->A wrap), we enumerate orders but memoize the
    SET of orders is too large; this falls back to bst_omega for correctness.
    Kept as the public entry (exact)."""
    return bst_omega(n, arcs)


def measure(n, arcs, name="T"):
    ov = core.omega_vec(n, arcs)
    bo = bst_omega(n, arcs, lb=ov)
    assert bo >= ov, f"SOUNDNESS VIOLATION {name}: bst_omega={bo} < omega_vec={ov}"
    return {"name": name, "n": n, "omega_vec": ov, "bst_omega": bo,
            "beta": bo - ov}


def _parse_gentourng_line(n, line):
    s = line.strip()
    bits = [c for c in s if c in "01"]
    if len(bits) != n * (n - 1) // 2:
        return None
    arcs = []
    idx = 0
    for i in range(n):
        for j in range(i + 1, n):
            arcs.append((i, j) if bits[idx] == "1" else (j, i))
            idx += 1
    return arcs


def scan(n):
    proc = subprocess.run(["gentourng", "-q", str(n)],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"gentourng failed: {proc.stderr}")
    max_beta = -1
    argmax = None
    joint = {}          # omega_vec -> max bst_omega
    cnt = 0
    beta_hist = {}
    for line in proc.stdout.splitlines():
        arcs = _parse_gentourng_line(n, line)
        if arcs is None:
            continue
        cnt += 1
        ov = core.omega_vec(n, arcs)
        bo = bst_omega(n, arcs)
        assert bo >= ov, f"SOUNDNESS VIOLATION n={n} class#{cnt}: bst={bo}<ov={ov} arcs={arcs}"
        b = bo - ov
        beta_hist[b] = beta_hist.get(b, 0) + 1
        joint[ov] = max(joint.get(ov, 0), bo)
        if b > max_beta:
            max_beta = b
            argmax = arcs
    return {"n": n, "n_classes": cnt, "max_beta": max_beta,
            "beta_histogram": beta_hist,
            "joint_omega_to_max_bst": joint,
            "argmax_arcs": argmax}


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd == "S":
        out = []
        for k in range(1, int(sys.argv[2]) + 1 if len(sys.argv) > 2 else 5):
            n, a = C.S(k)
            out.append({**measure(n, a, name=f"S_{k}")})
        print(json.dumps(out, indent=2))
    elif cmd == "scan":
        print(json.dumps(scan(int(sys.argv[2])), indent=2, default=str))
    else:
        # S_1..S_4 then scans
        res = {"S": [], "scans": {}}
        for k in range(1, 5):
            n, a = C.S(k)
            res["S"].append(measure(n, a, name=f"S_{k}"))
        for n in range(int(sys.argv[2]) if len(sys.argv) > 2 else 4,
                        int(sys.argv[3]) if len(sys.argv) > 3 else 9):
            res["scans"][n] = scan(n)
        print(json.dumps(res, indent=2, default=str))
