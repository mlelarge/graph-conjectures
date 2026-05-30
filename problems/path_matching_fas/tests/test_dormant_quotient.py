"""Tests for the Dormant-Matching Quotient Lemma probe.

These tests pin two complementary findings:

1.  No collisions on the reversed-matching family ``T_m`` for
    ``m in {8, 9, 10, 11, 12}`` at any in-gap sweep position.  This is
    the family used in ``docs/forced_frontier_probe.md`` to motivate
    the lemma.  The empirical signal here is consistent with the lemma
    on this *clean* family — i.e., the dormant aggregate is enough on
    the reversed-matching obstruction itself.

2.  A minimal refuting collision on the n = 12 ``one_block`` tournament:
    two valid length-5 prefixes have the same augmented (visible_latent +
    dormant aggregate) signature but different extendability.  The
    collision is documented and shown to persist regardless of the
    canonical multiset hashing.

The collision REFUTES the multiset-based Dormant-Matching Quotient
Lemma.  Any sound DP state must keep extra information distinguishing
how dormant components are entangled with the active-band components
via the union-find partition.

See ``docs/dormant_matching_quotient_lemma.md``.
"""

from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from dormant_quotient_probe import (  # noqa: E402
    aggregate_signature,
    augmented_signature,
    dormant_components_at,
    find_collision,
    search_reversed_matching_family,
)
from ff_signature_probe import (  # noqa: E402
    has_completion_ff,
    valid_prefix_state_ff,
    visible_latent_signature,
)
from forced_frontier_probe import reversed_matching_tournament  # noqa: E402
from sleeping_block_skew_sweep import SKEW_TEMPLATES  # noqa: E402


# ---------------------------------------------------------------------------
# Reversed-matching family: no collisions found
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("m", [8, 9, 10, 11, 12])
def test_reversed_matching_no_collision(m: int) -> None:
    """No augmented-signature collision on the reversed-matching family."""
    T = reversed_matching_tournament(m)
    # Sweep position in the dormant phase.
    only_length = max(4, m // 2 + 1)
    result = find_collision(T, only_length=only_length, require_dormant=True)
    assert result is None, (
        f"Unexpected collision at m={m}, p={only_length}: {result}"
    )


def test_reversed_matching_family_sweep() -> None:
    """Full sweep of reversed-matching m in {8..12}: no collisions."""
    rows = search_reversed_matching_family(
        m_range=[8, 9, 10, 11, 12], require_dormant=True
    )
    for row in rows:
        assert row["collision"] is None, (
            f"Unexpected collision: m={row['m']}, p={row['only_length']}"
        )


# ---------------------------------------------------------------------------
# Dormancy detection sanity checks
# ---------------------------------------------------------------------------


def test_dormant_components_empty_for_short_prefix() -> None:
    """Reversed matching m=10, prefix (0,1,2): no dormant components yet."""
    T = reversed_matching_tournament(10)
    profiles = dormant_components_at(T, 3, (0, 1, 2))
    assert profiles == []


def test_dormant_components_emerge_in_gap() -> None:
    """Reversed matching m=10 at p=5, prefix (0,1,2,3,4) has two dormant
    components {0, 10} and {1, 11}."""
    T = reversed_matching_tournament(10)
    profiles = dormant_components_at(T, 5, (0, 1, 2, 3, 4))
    assert len(profiles) == 2
    # Each is a matching edge (type (1, 1)).
    for prof in profiles:
        assert prof["type"] == (1, 1)
        # One closed, one future.
        states = sorted(rec[0] for rec in prof["vertices_state"])
        assert states == ["closed", "future"]


def test_aggregate_signature_is_multiset() -> None:
    """The aggregate is independent of dormant-component ordering."""
    T = reversed_matching_tournament(10)
    profiles = dormant_components_at(T, 5, (0, 1, 2, 3, 4))
    sig_forward = aggregate_signature(profiles)
    sig_reverse = aggregate_signature(list(reversed(profiles)))
    assert sig_forward == sig_reverse


# ---------------------------------------------------------------------------
# Refuting collision on one_block
# ---------------------------------------------------------------------------


ONE_BLOCK_COLLISION = {
    "T_name": "one_block",
    "p": 5,
    "prefix_A": (0, 3, 1, 4, 2),  # ext False
    "prefix_B": (1, 2, 0, 4, 3),  # ext True
}


def test_one_block_collision_extendability_disagrees() -> None:
    """The two collision prefixes have different extendability."""
    T = SKEW_TEMPLATES["one_block"]
    pA = ONE_BLOCK_COLLISION["prefix_A"]
    pB = ONE_BLOCK_COLLISION["prefix_B"]

    state_A = valid_prefix_state_ff(T, pA)
    state_B = valid_prefix_state_ff(T, pB)
    assert state_A is not None
    assert state_B is not None
    pA_mask, pA_deg, pA_par, pA_fout, pA_win = state_A
    pB_mask, pB_deg, pB_par, pB_fout, pB_win = state_B
    p = len(pA)
    ext_A = has_completion_ff(T, p, pA_mask, pA_deg, pA_par, tuple(pA_fout), tuple(pA_win))
    ext_B = has_completion_ff(T, p, pB_mask, pB_deg, pB_par, tuple(pB_fout), tuple(pB_win))
    assert ext_A is False
    assert ext_B is True


def test_one_block_collision_augmented_signatures_agree() -> None:
    """The two collision prefixes have the same augmented signature."""
    T = SKEW_TEMPLATES["one_block"]
    pA = ONE_BLOCK_COLLISION["prefix_A"]
    pB = ONE_BLOCK_COLLISION["prefix_B"]
    sig_A = augmented_signature(T, pA)
    sig_B = augmented_signature(T, pB)
    assert sig_A is not None
    assert sig_B is not None
    assert sig_A == sig_B, (
        "The augmented signature should agree to be a refutation."
    )


def test_one_block_collision_dormant_profiles_agree() -> None:
    """The two collision prefixes have identical dormant aggregates."""
    T = SKEW_TEMPLATES["one_block"]
    pA = ONE_BLOCK_COLLISION["prefix_A"]
    pB = ONE_BLOCK_COLLISION["prefix_B"]
    profA = dormant_components_at(T, 5, pA)
    profB = dormant_components_at(T, 5, pB)
    assert aggregate_signature(profA) == aggregate_signature(profB)
    # And both have exactly 2 dormant components, both matching edges.
    assert len(profA) == 2
    assert all(p["type"] == (1, 1) for p in profA)


def test_one_block_collision_visible_latent_signatures_agree() -> None:
    """The two collision prefixes have the same visible_latent signature
    (so the augmentation alone — adding the dormant aggregate — does not
    fix the collision)."""
    T = SKEW_TEMPLATES["one_block"]
    pA = ONE_BLOCK_COLLISION["prefix_A"]
    pB = ONE_BLOCK_COLLISION["prefix_B"]

    state_A = valid_prefix_state_ff(T, pA)
    state_B = valid_prefix_state_ff(T, pB)
    pA_mask, pA_deg, pA_par, pA_fout, pA_win = state_A
    pB_mask, pB_deg, pB_par, pB_fout, pB_win = state_B
    p = len(pA)
    vis_A = visible_latent_signature(p, pA_mask, pA_deg, pA_par, pA_fout, pA_win)
    vis_B = visible_latent_signature(p, pB_mask, pB_deg, pB_par, pB_fout, pB_win)
    assert vis_A == vis_B


def test_one_block_collision_component_partitions_differ() -> None:
    """Confirm the *root cause* of the collision: the union-find
    component partitions on the loaded backedges differ between the two
    prefixes.  This is what the lemma's multiset aggregate fails to
    capture."""
    T = SKEW_TEMPLATES["one_block"]
    pA = ONE_BLOCK_COLLISION["prefix_A"]
    pB = ONE_BLOCK_COLLISION["prefix_B"]

    state_A = valid_prefix_state_ff(T, pA)
    state_B = valid_prefix_state_ff(T, pB)
    _, _, parent_A, _, _ = state_A
    _, _, parent_B, _, _ = state_B

    def find(par, x):
        par = list(par)
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x

    # Active band = {4, 5, 6, 7}; dormants are {0, 10}, {1, 9}.
    # In prefix A: dormant {0, 10} shares root with active vertex 4.
    # In prefix B: dormants {0, 10} and {1, 9} share root with each other,
    # and active vertex 4 is in a separate component.
    rA0, rA10, rA1, rA9, rA4 = (find(parent_A, v) for v in [0, 10, 1, 9, 4])
    rB0, rB10, rB1, rB9, rB4 = (find(parent_B, v) for v in [0, 10, 1, 9, 4])

    assert rA0 == rA10 == rA4
    assert rA1 == rA9
    assert rA0 != rA1  # The two dormant components are separate in A

    assert rB0 == rB10 == rB1 == rB9
    assert rB4 != rB0  # Dormants merged, but active 4 is separate in B


def test_collision_search_finds_the_one_block_witness() -> None:
    """The automated search returns a collision on ``one_block``."""
    T = SKEW_TEMPLATES["one_block"]
    result = find_collision(T, depth=5, require_dormant=False)
    assert result is not None
    assert result["pos"] == 5
    # The found collision should have at least one dormant.
    assert result["state_a"]["n_dormant"] >= 1
    assert result["state_b"]["n_dormant"] >= 1
    # And the two prefixes must have differing extendability.
    assert result["state_a"]["extendable"] != result["state_b"]["extendable"]
