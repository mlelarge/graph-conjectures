import os
import sys


SCRIPTS = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPTS))

from stilde_growth_bounds import (  # noqa: E402
    build_report,
    ceil_cuberoot,
    next_transitive_counts,
)


def test_exact_dichromatic_recurrence_and_forced_h19_failure():
    report = build_report(max_n=24, count_max_n=3, count_cap=10)
    rows = report["bounds"]

    assert [row["dichromatic_exact"] for row in rows[:10]] == [
        1, 2, 3, 5, 8, 12, 18, 27, 41, 62
    ]
    assert rows[23]["dichromatic_exact"] == 18206
    assert ceil_cuberoot(18206) == 27
    assert report["first_n_where_pod_lower_exceeds_h19_iterated_upper_n"] == 24
    assert rows[4]["omega_exact_known"] == 5
    assert report["proved_growth_constant"]["upper"] == 5 ** (1 / 4)


def test_transitive_subtournament_polynomial_recurrence():
    # S~_1 = one vertex: F_1 = 1+x.
    s1 = [1, 1]
    # S~_2 = C3: empty set, three vertices, three pairs, no transitive triple.
    s2 = next_transitive_counts(s1, 10)
    assert s2 == [1, 3, 3]
    # S~_3 has 9 vertices and maximum transitive subtournament order 4.
    s3 = next_transitive_counts(s2, 10)
    assert s3 == [1, 9, 36, 54, 27]
