"""Exact recursive language of the q_0=1 face.

For B_k = C3[B_{k-1}], q_0=1 means the order has no backward colour-0
arc, equivalently it is a linear extension of the canonical colour-0 poset.

At the top level, the only colour-0 comparabilities between modules are the
complete relation M_0 < M_1.  The third module M_2 is top-level incomparable
for colour 0.  Hence a parent order is on the q_0=1 face iff

* each induced child order is on the q_0=1 face; and
* the top lattice path never starts M_1 before M_0 is complete.

This module records that small theorem as a checkable predicate.
"""

from __future__ import annotations

from stilde_crossing_recursion import direct_q
from stilde_profile_closure import lattice_path, module_orders


def path_has_m0_before_m1(states):
    """Whether a top-level path places every M_0 vertex before every M_1 vertex."""

    states = tuple(states)
    if not states:
        raise ValueError("states must be a non-empty lattice path")
    if states[0] != (0, 0, 0):
        raise ValueError("states must start at (0,0,0)")
    m = states[-1][0]
    if states[-1] != (m, m, m):
        raise ValueError("states must end at (m,m,m)")
    previous = states[0]
    for state in states[1:]:
        delta = tuple(state[i] - previous[i] for i in range(3))
        if sorted(delta) != [0, 0, 1]:
            raise ValueError("states must be a monotone unit lattice path")
        previous = state
    return all(state[1] == 0 or state[0] == m for state in states)


def q0_face_recursive_condition(order, depth):
    """The recursive condition equivalent to q_0(order)=1.

    The base depth 0 has one vertex and is vacuously on the face.
    """

    if depth < 0:
        raise ValueError("depth must be non-negative")
    if depth == 0:
        return tuple(order) == (0,)

    modules = module_orders(order, depth)
    states = lattice_path(order, depth)
    if not path_has_m0_before_m1(states):
        return False
    return all(direct_q(module, depth - 1, 0) == 1 for module in modules)


def is_q0_face(order, depth):
    """Direct check for membership in the q_0=1 face."""

    return direct_q(tuple(order), depth, 0) == 1
