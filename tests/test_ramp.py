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


# --- Exercise 2 --------------------------------------------------------
# No overshoot: when the target is closer than one step away, the
# limiter should return the target exactly.


# --- Exercise 3 --------------------------------------------------------
# Already at target: the output should equal the target.


# --- Exercise 4 --------------------------------------------------------
# Invalid inputs must raise ValueError. Use:
#     with pytest.raises(ValueError):
#         limit_ramp(...)
# Cover both a negative ramp limit and a zero (or negative) time step.


# --- Exercise 5 --------------------------------------------------------
# Combine several cases into ONE test with @pytest.mark.parametrize.
# Columns: current, target, ramp, dt, expected.
# Include a case with dt = 0.5 s.


# --- Exercise 6 --------------------------------------------------------
# Simulation test: ramp 0 -> 1000 kW at 10 kW/s with dt = 1 s.
# Using simulate_ramp(), check that:
#   a) the final setpoint equals the target
#   b) it took 100 steps (hint: history includes the starting value)
#   c) no step-to-step change exceeds 10 kW
