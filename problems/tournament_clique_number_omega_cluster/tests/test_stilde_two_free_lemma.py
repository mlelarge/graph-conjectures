import os
import sys


SCRIPTS = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPTS))

from stilde_two_free_lemma import (  # noqa: E402
    forced_missing_colour_chain,
    is_colour_chain,
)


def test_forced_chain_has_size_2_to_k_and_correct_colour():
    for depth in range(1, 6):
        chain = forced_missing_colour_chain(depth, missing_colour=2)
        assert len(chain) == 2**depth
        assert is_colour_chain(chain, depth, colour=2)
