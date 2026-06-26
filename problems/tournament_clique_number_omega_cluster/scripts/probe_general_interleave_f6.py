"""Does the GENERAL interleaving of depth-5 modules beat the portfolio's F_6<=45?

§29/§30 show the portfolio (one floating M_2, companions as blocks) and the
two-cut extension both plateau at product 45.  §28's lesson: only structured
modules (with a simultaneous cut) reproduce the optimum; arbitrary witnesses do
not.  This probe takes the STRUCTURED portfolio modules and asks whether a FULL
lattice-path interleaving (sec 10 closure) -- where the companions also contribute
staircases, not just scalars -- can reach a face product below 45.

A product < 45 would prove F_6 < 45 (portfolio suboptimal -> toward pod-tight).
A clean 45 floor hardens "45 is a robust barrier across construction families".

Result (2026-06-21): structured modules reach exactly 45, nothing below; arbitrary
witnesses cannot even reach 45 (min 50) -- confirming structure matters AND that
general interleaving does not beat the 2-cut.
"""

from __future__ import annotations

from decide_simultaneous_cut import decide_simultaneous_cut
from decide_layer_labeling import decide_caps_labeling
from stilde_profile_closure import reachable_under_caps, step_profile


def structured_portfolio_modules():
    """M_2 with a simultaneous (2,4) cut (=> the 45 witness) plus companions."""
    m2 = step_profile(decide_simultaneous_cut(5, 5, 9, 2, 4)["witness_order"], 5)
    m0 = step_profile(decide_caps_labeling(5, (1, 5, 5))["witness_order"], 5)
    m1 = step_profile(decide_caps_labeling(5, (1, 3, 9))["witness_order"], 5)
    return m0, m1, m2


def min_general_product(profiles, lo=25, hi=44):
    """Smallest face product (q0=1) any interleaving of these modules achieves."""
    best = None
    for q1 in range(2, hi + 1):
        for q2 in range(2, hi + 1):
            if not (lo <= q1 * q2 <= hi):
                continue
            if reachable_under_caps(profiles, (1, q1, q2))["reachable"]:
                if best is None or q1 * q2 < best[0]:
                    best = (q1 * q2, q1, q2)
    return best


def run():
    m0, m1, m2 = structured_portfolio_modules()
    print(f"structured M2={m2.heights} M0={m0.heights} M1={m1.heights}", flush=True)
    # closure must see the 2-cut path achieving 45
    r45 = reachable_under_caps([m0, m1, m2], (1, 5, 9))
    print(f"closure sees (1,5,9)=45 reachable: {r45['reachable']} "
          f"(visited {r45['visited']})", flush=True)
    below = min_general_product([m0, m1, m2], lo=25, hi=44)
    print(f"min general-interleaving product < 45: {below}", flush=True)
    verdict = "BEATS 45" if below else "does NOT beat 45 (floor holds)"
    print(f"general interleaving of structured modules {verdict}", flush=True)
    return below


if __name__ == "__main__":
    run()
