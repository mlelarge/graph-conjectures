"""Computational guard for the lemma in
[docs/no_flower_dot_decomposition.md](../docs/no_flower_dot_decomposition.md):

every flower snark $J_n$ (and more generally every nontrivial snark
in the catalogue) is cyclically 4-edge-connected. By the structural
lemma, no such graph is a nontrivial 3-edge-cut dot product of two
cubic pieces each containing a cycle.

We assert directly via ``cyclic_edge_connectivity_at_most(G, 3) is
None`` for J_5, J_7, J_9, J_11, J_13.
"""
from __future__ import annotations

import pytest

from catalogue import cyclic_edge_connectivity_at_most
from graphs import flower_snark


@pytest.mark.parametrize("k", [2, 3, 4, 5, 6])
def test_flower_snark_has_no_cyclic_3_cut(k):
    G = flower_snark(k)
    cut_size = cyclic_edge_connectivity_at_most(G, 3)
    assert cut_size is None, (
        f"J_{2*k+1} has a cyclic edge cut of size {cut_size}; lemma would be violated"
    )
