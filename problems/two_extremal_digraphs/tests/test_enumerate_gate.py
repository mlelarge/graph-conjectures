"""Correctness gate + output-integrity tests for the fast 2-extremal enumerator.

Run with the venv active:  python -m pytest tests/test_enumerate_gate.py -q
(or just `python tests/test_enumerate_gate.py` for a script-style run).

These checks are VERIFICATION, not proof:
  - the small-n gate (|L_3|=1, |L_4|=1, |L_5|=3) reproduces known values;
  - every digraph in each dumped L_n.json independently re-passes the 2-extremal
    test and carries a distinct canonical certificate.
"""
import os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCRIPTS = os.path.join(ROOT, "scripts")
DATA = os.path.join(ROOT, "data")
sys.path.insert(0, SCRIPTS)

from enumerate_2extremal_v0_recon import is_2extremal, sym_cycle  # noqa: E402


def _load(n):
    path = os.path.join(DATA, f"L_{n}.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def test_primitive_sanity():
    for c in (3, 5, 7):
        assert is_2extremal(sym_cycle(c), c), f"sym C{c} must be 2-extremal"
    assert not is_2extremal(sym_cycle(4), 4), "sym C4 must NOT be 2-extremal"


def test_gate_sizes():
    expected = {3: 1, 4: 1, 5: 3}
    for n, want in expected.items():
        d = _load(n)
        assert d is not None, f"L_{n}.json missing; run scripts/enumerate.py first"
        assert len(d) == want, f"|L_{n}|={len(d)} expected {want}"


def test_dumped_files_reverify():
    for n in range(3, 9):
        d = _load(n)
        if d is None:
            continue
        canons = set()
        for o in d:
            assert o["n"] == n
            arcs = frozenset(tuple(a) for a in o["arcs"])
            assert is_2extremal(arcs, n), f"L_{n} member failed re-verification"
            canons.add(o["canon"])
        assert len(canons) == len(d), f"L_{n} has duplicate canonical forms"


if __name__ == "__main__":
    test_primitive_sanity()
    test_gate_sizes()
    test_dumped_files_reverify()
    print("all gate + integrity checks passed")
