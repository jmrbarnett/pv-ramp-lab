"""Reference solutions for Lesson 1. Try the exercises first!

Not run by default. To run: pytest solutions/
"""
import pytest

from pv_controls.ramp import limit_ramp, simulate_ramp


def test_ramp_up_is_limited():
    assert limit_ramp(500, 800, 10, 1) == 510


# Exercise 1
def test_ramp_down_is_limited():
    assert limit_ramp(800, 500, 10, 1) == 790


# Exercise 2
def test_small_change_reaches_target_without_overshoot():
    assert limit_ramp(500, 505, 10, 1) == 505


# Exercise 3
def test_at_target_stays_at_target():
    assert limit_ramp(500, 500, 10, 1) == 500


# Exercise 4
def test_negative_ramp_limit_raises():
    with pytest.raises(ValueError):
        limit_ramp(500, 800, -10, 1)


@pytest.mark.parametrize("bad_dt", [0, -1])
def test_non_positive_time_step_raises(bad_dt):
    with pytest.raises(ValueError):
        limit_ramp(500, 800, 10, bad_dt)


# Exercise 5
@pytest.mark.parametrize(
    "current, target, ramp, dt, expected",
    [
        (0, 1000, 10, 1, 10),       # ramp up
        (1000, 0, 10, 1, 990),      # ramp down
        (0, 1000, 10, 0.5, 5),      # half-second step
        (995, 1000, 10, 1, 1000),   # within one step
        (700, 700, 10, 1, 700),     # already at target
    ],
)
def test_limit_ramp_cases(current, target, ramp, dt, expected):
    assert limit_ramp(current, target, ramp, dt) == pytest.approx(expected)


# Exercise 6
def test_full_ramp_simulation():
    history = simulate_ramp(0, 1000, 10, 1)

    assert history[-1] == 1000
    assert len(history) - 1 == 100

    steps = [abs(b - a) for a, b in zip(history, history[1:])]
    assert max(steps) <= 10
