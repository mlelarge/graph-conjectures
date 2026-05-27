import os
import sys
import unittest


SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPT_DIR))

from sleeping_bound_refutation import count_toggle_signatures  # noqa: E402


class SleepingBoundRefutationTest(unittest.TestCase):
    def test_toggle_family_has_exponentially_many_signatures(self):
        for k in range(1, 7):
            with self.subTest(k=k):
                out = count_toggle_signatures(k)
                self.assertEqual(out["valid_prefixes"], 1 << k)
                self.assertEqual(out["ff_surviving_prefixes"], 1 << k)
                self.assertEqual(out["distinct_sleeping_signatures"], 1 << k)
                self.assertEqual(out["collisions"], 0)
                self.assertEqual(out["invalid"], [])

    def test_toggle_family_gives_two_to_n_over_four_lower_bound(self):
        out = count_toggle_signatures(6)
        self.assertEqual(out["n"], 24)
        self.assertEqual(out["distinct_sleeping_signatures"], 2 ** (out["n"] // 4))

    def test_all_toggle_prefixes_have_same_extendability(self):
        """The 2^k sleeping-block signatures of the toggle family all
        encode extendable states. This is the regression target for any
        future quotient theorem: a sound quotient must identify these
        signatures, since they share the same extendability.

        Confirms that the polynomial-bound refutation is genuinely
        about state-counting, not extension-equivalence."""
        from itertools import product

        from ff_signature_probe import has_completion_ff, valid_prefix_state_ff
        from sleeping_bound_refutation import toggle_prefix, toggle_tournament

        for k in range(1, 6):
            with self.subTest(k=k):
                T = toggle_tournament(k)
                cut = 2 * k
                extendabilities = set()
                for bits in product((0, 1), repeat=k):
                    prefix = toggle_prefix(k, bits)
                    state = valid_prefix_state_ff(T, prefix)
                    self.assertIsNotNone(state)
                    pm, deg, par, flex, win = state
                    ext = has_completion_ff(
                        T, cut, pm, deg, par, tuple(flex), tuple(win)
                    )
                    extendabilities.add(ext)
                # All toggle prefixes share the same extendability verdict.
                self.assertEqual(len(extendabilities), 1)
                self.assertEqual(extendabilities, {True})


if __name__ == "__main__":
    unittest.main()
