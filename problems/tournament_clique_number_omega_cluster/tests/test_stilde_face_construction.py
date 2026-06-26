import os
import sys


SCRIPTS = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPTS))

from stilde_face_construction import build  # noqa: E402


def test_bounded_frontier_construction_stalls_at_2k():
    # The bounded-frontier q_0=1 construction reproduces F_2=4, F_3=8 but yields
    # 16 = 2^4 at depth 4, above the true F_4=15.  NOTE (docs sec. 16): the cause is
    # NOT the M_2 schedule -- a clean 2-cut over all s reaches 15 with the right
    # modules -- but module-shape GENERATION: the bounded frontier drops the
    # complementary depth-3 modules (e.g. (1,3,5), suboptimal at depth 3 but needed
    # as a depth-4 module).  This persists even with all-s 2-cuts + a larger cap.
    res, _ = build(4, cap_per_shape=2, max_shapes=30)
    assert res[2] == 4
    assert res[3] == 8
    assert res[4] == 16  # = 2^4; the sub-2^k regime needs the dropped modules
