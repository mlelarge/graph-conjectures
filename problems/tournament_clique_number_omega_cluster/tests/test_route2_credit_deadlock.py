import os
import sys


SCRIPTS = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPTS))

from route2_credit_deadlock import (  # noqa: E402
    analyse_triple,
    cyclic_wait_cycles,
    gold_triple,
)
from route2_append_partners import (  # noqa: E402
    ac_target,
    demand_signature,
    is_full_raiser,
    qr19_gold_target,
)


def test_qr19_gold_demand_relief_maps_are_cycle_free():
    profs = gold_triple()
    maps, cycles = cyclic_wait_cycles(profs, 19, 4)

    assert cycles == []
    assert {
        t: maps[0][t]["successor_level"] for t in range(2, 5)
    } == {2: 2, 3: 3, 4: 3}
    assert {
        t: maps[1][t]["successor_level"] for t in range(2, 5)
    } == {2: 2, 3: 4, 4: 4}
    assert {
        t: maps[2][t]["successor_level"] for t in range(2, 5)
    } == {2: 3, 3: 4, 4: 5}


def test_cyclic_wait_cycles_equal_safe_dead_ends():
    gold = gold_triple()

    gold_result = analyse_triple(gold, 19, 4)
    assert gold_result["cycle_states_equal_all_safe_dead_ends"]
    assert gold_result["cyclic_wait_cycles"] == []
    assert gold_result["n_dead_ends"] == 0

    shared_result = analyse_triple([gold[0], gold[0], gold[0]], 19, 4)
    assert shared_result["cycle_states_equal_all_safe_dead_ends"]
    assert shared_result["cyclic_wait_cycles"]
    assert shared_result["n_dead_ends"] > 0


def test_gold_escaper_repeated_is_a_shared_order_solution():
    gold = gold_triple()
    result = analyse_triple([gold[2], gold[2], gold[2]], 19, 4)

    assert demand_signature(gold[2], 19, 4) == (3, 4, 5)
    assert is_full_raiser((3, 4, 5))
    assert result["feasible_no_deadlock"]
    assert result["n_dead_ends"] == 0


def test_append_partner_certificates_on_ac7_and_qr19():
    ac7 = ac_target(7)
    qr19 = qr19_gold_target()

    assert ac7["full_raiser_witness"]["demand_signature"] == [3, 4]
    assert ac7["cycle_free_triple"]["n_distinct_maps"] == 1
    assert qr19["full_raiser_witness"]["demand_signature"] == [3, 4, 5]
    assert qr19["cycle_free_triple"]["n_distinct_maps"] == 1
