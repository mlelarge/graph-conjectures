"""Pin the negative results for the asymmetric external wiring search.

These tests record:
  - strict single-external wiring (no inactive hits) yields 0
    orientations;
  - relaxed single-external wiring (any LFO with active hits in both
    states) yields exactly 1 orientation, the (0,0,0,1,1,0,0) wiring;
  - two-external composition requiring active hits at both externals
    yields 0 orientations.

If any future change to the underlying 7-block changes these counts,
these tests fire.
"""
from __future__ import annotations
import itertools, os, sys, unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from external_wiring_search import (  # noqa: E402
    BLOCK_N, L_ORDER, R_ORDER, N_PORTS, Y_PORTS,
    build_combined, back_arc_data, insertions, classify_external_hits,
    search,
)
from external_wiring_two import (  # noqa: E402
    build_combined_two, insertions2,
)


class StrictSingleExternalTest(unittest.TestCase):

    def test_strict_search_empty(self):
        records = search()
        self.assertEqual(records, [])


class RelaxedSingleExternalTest(unittest.TestCase):

    def test_unique_relaxed_candidate(self):
        candidates = []
        for bits in itertools.product((0, 1), repeat=BLOCK_N):
            T = build_combined(bits)
            c = BLOCK_N
            l_active = False
            r_active = False
            for combined in insertions(L_ORDER):
                d = back_arc_data(T, combined)
                if d is None:
                    continue
                if classify_external_hits(d["arcs"], c, Y_PORTS)["active_hits"]:
                    l_active = True
                    break
            for combined in insertions(R_ORDER):
                d = back_arc_data(T, combined)
                if d is None:
                    continue
                if classify_external_hits(d["arcs"], c, N_PORTS)["active_hits"]:
                    r_active = True
                    break
            if l_active and r_active:
                candidates.append(bits)
        self.assertEqual(candidates, [(0, 0, 0, 1, 1, 0, 0)])


class TwoExternalCompositionTest(unittest.TestCase):

    def test_both_externals_active_in_both_states_impossible(self):
        found = 0
        for c1_bits in itertools.product((0, 1), repeat=BLOCK_N):
            for c2_bits in itertools.product((0, 1), repeat=BLOCK_N):
                for c12 in (0, 1):
                    T = build_combined_two(c1_bits, c2_bits, c12)
                    c1, c2 = BLOCK_N, BLOCK_N + 1
                    l_ok = False
                    for combined in insertions2(L_ORDER):
                        d = back_arc_data(T, combined)
                        if d is None:
                            continue
                        cls1 = classify_external_hits(d["arcs"], c1, Y_PORTS)
                        cls2 = classify_external_hits(d["arcs"], c2, Y_PORTS)
                        if cls1["active_hits"] and cls2["active_hits"]:
                            l_ok = True
                            break
                    if not l_ok:
                        continue
                    r_ok = False
                    for combined in insertions2(R_ORDER):
                        d = back_arc_data(T, combined)
                        if d is None:
                            continue
                        cls1 = classify_external_hits(d["arcs"], c1, N_PORTS)
                        cls2 = classify_external_hits(d["arcs"], c2, N_PORTS)
                        if cls1["active_hits"] and cls2["active_hits"]:
                            r_ok = True
                            break
                    if l_ok and r_ok:
                        found += 1
                        return self.fail(
                            f"unexpected candidate: c1={c1_bits} c2={c2_bits} c12={c12}"
                        )
        self.assertEqual(found, 0)


if __name__ == "__main__":
    unittest.main()
