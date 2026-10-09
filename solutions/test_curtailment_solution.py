"""Reference solutions for Lesson 2. Try the exercises first!

Run with: pytest solutions/
"""
import pytest

from pv_controls.curtailment import (effective_limit, run_closed_loop,
                                     save_csv, settling_time)


def test_open_loop_output_shows_losses(plant):
    for _ in range(30):
        poi = plant.step(500, dt_s=1)
    assert poi == pytest.approx(490, rel=1e-3)


# Exercise 1
@pytest.mark.parametrize(
    "rated, pct, export, expected",
    [
        (1000, 100, None, 1000),   # no curtailment
        (1000, 60, None, 600),     # operator command wins
        (1000, 80, 500, 500),      # export limit wins
        (1000, 30, 500, 300),      # operator command wins
    ],
)
def test_effective_limit(rated, pct, export, expected):
    assert effective_limit(rated, pct, export) == expected


def test_effective_limit_rejects_bad_percent():
    with pytest.raises(ValueError):
        effective_limit(1000, operator_pct=120)


# Exercise 2
def test_pi_removes_steady_state_error(plant, controller):
    result = run_closed_loop(plant, controller, [600] * 120)
    assert result["poi"][-1] == pytest.approx(600, rel=1e-3)


# Exercise 3
def test_proportional_only_leaves_error(make_plant, make_controller):
    result = run_closed_loop(make_plant(), make_controller(ki=0),
                             [600] * 240)
    error = abs(600 - result["poi"][-1])
    assert error > 0.01 * 600


# Exercise 4
def test_step_down_settles_within_30_s(step_down_result):
    after_step = step_down_result["poi"][60:]
    t_settle = settling_time(after_step, target=600, tolerance=6)
    assert t_settle is not None and t_settle <= 30


def test_step_down_undershoot_is_limited(step_down_result):
    after_step = step_down_result["poi"][60:]
    assert min(after_step) >= 0.9 * 600


# Exercise 5
def test_tracks_60_percent_for_any_plant_size(rated_kw, make_plant,
                                              make_controller):
    limit = 0.6 * rated_kw
    result = run_closed_loop(make_plant(rated_kw=rated_kw),
                             make_controller(rated_kw=rated_kw),
                             [limit] * 120)
    assert result["poi"][-1] == pytest.approx(limit, rel=1e-3)


# Exercise 6
CLOUD_LIMITS = [600] * 240
CLOUD_AVAILABLE = [1000] * 60 + [400] * 60 + [1000] * 120


def test_anti_windup_limits_overshoot_after_cloud(make_plant,
                                                  make_controller):
    result = run_closed_loop(make_plant(), make_controller(),
                             CLOUD_LIMITS, CLOUD_AVAILABLE)
    assert max(result["poi"][120:]) <= 1.05 * 600


def test_without_anti_windup_overshoot_is_large(make_plant,
                                                make_controller):
    result = run_closed_loop(make_plant(),
                             make_controller(integral_limit_kw=1e9),
                             CLOUD_LIMITS, CLOUD_AVAILABLE)
    assert max(result["poi"][120:]) > 1.20 * 600


# Exercise 7
def test_command_respects_ramp_limit(make_plant, make_controller):
    result = run_closed_loop(make_plant(),
                             make_controller(max_ramp_kw_per_s=20),
                             [600] * 120)
    commands = [0.0] + result["command"]
    steps = [abs(b - a) for a, b in zip(commands, commands[1:])]
    assert max(steps) <= 20 + 1e-9   # tiny tolerance for float rounding


# Exercise 8
def test_save_csv_writes_header_and_rows(tmp_path, plant, controller):
    result = run_closed_loop(plant, controller, [600] * 10)
    path = tmp_path / "run.csv"

    save_csv(result, path)

    lines = path.read_text().splitlines()
    assert lines[0] == "t,limit,command,poi"
    assert len(lines) == 1 + 10
