"""Lesson 1 exercises: tests for the ramp-rate limiter.

One example test is provided. Complete exercises 1-6 below.
Run `pytest -v` after each one.
"""
import pytest

from pv_controls.ramp import limit_ramp, simulate_ramp


# --- Example (already done) -------------------------------------------
def test_ramp_up_is_limited():
    # 500 kW -> 800 kW target, 10 kW/s limit, 1 s step: only +10 kW allowed
    assert limit_ramp(current_kw=500, target_kw=800,
                      max_ramp_kw_per_s=10, dt_s=1) == 510


# --- Exercise 1 --------------------------------------------------------
# Ramp DOWN is limited too. Write a test where the target is below
# the current value and check the result drops by exactly one step.
def test_ramp_down_is_limited():
    # 800 kW -> 500 kW target, 10 kW/s limit, 1 s step: only -10 kW allowed
    assert limit_ramp(current_kw=800, target_kw=500,
                      max_ramp_kw_per_s=10, dt_s=1) == 790


# --- Exercise 2 --------------------------------------------------------
# No overshoot: when the target is closer than one step away, the
# limiter should return the target exactly.
def test_no_overshoot():
    # 500 kW -> 505 kW target, 10 kW/s limit, 1 s step: only +5 kW allowed
    assert limit_ramp(current_kw=500, target_kw=505,
                      max_ramp_kw_per_s=10, dt_s=1) == 505

# --- Exercise 3 --------------------------------------------------------
# Already at target: the output should equal the target.
def test_already_at_target():
    assert limit_ramp(current_kw=500, target_kw=500,
                      max_ramp_kw_per_s=10, dt_s=1) == 500


# --- Exercise 4 --------------------------------------------------------
# Invalid inputs must raise ValueError. Use:
#     with pytest.raises(ValueError):
#         limit_ramp(...)
# Cover both a negative ramp limit and a zero (or negative) time step.
def test_invalid_inputs():
    with pytest.raises(ValueError):
        limit_ramp(current_kw=500, target_kw=800,
                   max_ramp_kw_per_s=-10, dt_s=1)

    with pytest.raises(ValueError):
        limit_ramp(current_kw=500, target_kw=800,
                   max_ramp_kw_per_s=10, dt_s=0)

    with pytest.raises(ValueError):
        limit_ramp(current_kw=500, target_kw=800,
                   max_ramp_kw_per_s=10, dt_s=-1)


# --- Exercise 5 --------------------------------------------------------
# Combine several cases into ONE test with @pytest.mark.parametrize.
# Columns: current, target, ramp, dt, expected.
# Include a case with dt = 0.5 s.
def test_parametrized_ramp():
    test_cases = [
        (500, 800, 10, 1, 510),   # ramp up
        (800, 500, 10, 1, 790),   # ramp down
        (500, 505, 10, 1, 505),   # no overshoot
        (500, 500, 10, 1, 500),   # already at target
        (500, 800, 20, 0.5, 510), # ramp up with dt=0.5s
    ]
    
    for current_kw, target_kw, max_ramp_kw_per_s, dt_s, expected in test_cases:
        assert limit_ramp(current_kw=current_kw,
                          target_kw=target_kw,
                          max_ramp_kw_per_s=max_ramp_kw_per_s,
                          dt_s=dt_s) == expected


# --- Exercise 6 --------------------------------------------------------
# Simulation test: ramp 0 -> 1000 kW at 10 kW/s with dt = 1 s.
# Using simulate_ramp(), check that:
#   a) the final setpoint equals the target
#   b) it took 100 steps (hint: history includes the starting value)
#   c) no step-to-step change exceeds 10 kW
def test_simulate_ramp():
    target_kw = 1000
    max_ramp_kw_per_s = 10
    dt_s = 1

    history = simulate_ramp(start_kw=0.0, target_kw=target_kw,
                            max_ramp_kw_per_s=max_ramp_kw_per_s,
                            dt_s=dt_s)

    # a) final setpoint equals the target
    assert history[-1] == target_kw

    # b) it took 100 steps (including starting value)
    assert len(history) == 101

    # c) no step-to-step change exceeds 10 kW
    for i in range(1, len(history)):
        assert abs(history[i] - history[i - 1]) <= max_ramp_kw_per_s * dt_s
