import os
import sys

SCRIPTS = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPTS))

from stilde_profile_closure import reachable_under_caps  # noqa: E402
from probe_general_interleave_f6 import (  # noqa: E402
    min_general_product, structured_portfolio_modules,
)


def test_general_interleaving_does_not_beat_45():
    m0, m1, m2 = structured_portfolio_modules()
    # the closure sees the 2-cut path reach 45 ...
    assert reachable_under_caps([m0, m1, m2], (1, 5, 9))["reachable"]
    # ... but no full interleaving reaches a face product below 45
    assert min_general_product([m0, m1, m2], lo=25, hi=44) is None
