"""Lesson 2 exercises: fixtures, using a closed-loop curtailment controller.

Fixtures live in tests/conftest.py. Complete the exercises in order and
run `pytest -v` after each one. Exercises 2-5 need you to add a fixture
to conftest.py first.
"""
import pytest

from pv_controls import ramp
from pv_controls.curtailment import (effective_limit, run_closed_loop,
                                     save_csv, settling_time)


# --- Example (already done) -------------------------------------------
def test_open_loop_output_shows_losses(plant):
    # Command 500 kW for 30 s with no controller: POI settles 2% low
    poi = None
    for _ in range(30):
        poi = plant.step(500, dt_s=1)
    assert poi == pytest.approx(490, rel=1e-3)


# --- Exercise 1 (warm-up, no fixtures) ---------------------------------
# Test effective_limit(). Use @pytest.mark.parametrize to show the most
# restrictive limit wins (rated, operator %, export limit). Then use
# pytest.raises for operator_pct = 120.
@pytest.mark.parametrize("rated_kw, operator_pct, export_limit_kw, expected", [
    (1000, 80, None, 800),      # operator_pct is most restrictive
    (1000, 120, None, ValueError),  # invalid operator_pct
    (1000, 90, 850, 850),       # export_limit_kw is most restrictive
    (1000, 100, None, 1000),    # rated_kw is most restrictive
    (500, 50, 300, 250),        # operator_pct is most restrictive
    (500, 60, None, 300),       # operator_pct is most restrictive
    (500, 70, 400, 350),        # operator_pct is most restrictive
])
def test_effective_limit(rated_kw, operator_pct, export_limit_kw, expected):
    if expected == ValueError:
        with pytest.raises(ValueError):
            effective_limit(rated_kw, operator_pct, export_limit_kw)
    else:
        result = effective_limit(rated_kw, operator_pct, export_limit_kw)
        assert result == expected


# --- Exercise 2 --------------------------------------------------------
# Using the `plant` and `controller` fixtures, hold a 600 kW limit for
# 120 s. Assert the final POI power is within 0.1% of 600 kW.
# (The integral term is what removes the 2% loss error.)
def test_closed_loop_600kw_limit(plant, controller):
    limits = [600.0] * 120
    result = run_closed_loop(plant, controller, limits)
    final_poi = result["poi"][-1]
    assert final_poi == pytest.approx(600, rel=1e-3)

# --- Exercise 3 --------------------------------------------------------
# Using make_plant and make_controller, show WHY the integral matters:
# with ki=0 (proportional only), the final POI error after 240 s at a
# 600 kW limit is MORE than 1% of the limit.
def test_closed_loop_no_integral(make_plant, make_controller):
    plant = make_plant()
    controller = make_controller(ki=0)  # override integral gain to 0
    limits = [600.0] * 240
    result = run_closed_loop(plant, controller, limits)
    final_poi = result["poi"][-1]
    assert abs(final_poi - 600) > 6  # more than 1% error


# --- Exercise 4 --------------------------------------------------------
# Using step_down_result (a fixture built from other fixtures), write
# TWO tests on the part after the step (index 60 onward):
#   a) POI settles within +/-1% of 600 kW in 30 s or less
#      (use settling_time())
#   b) POI never undershoots below 90% of 600 kW
def test_step_down_settling_time(step_down_result):
    poi_after_step = step_down_result["poi"][60:]  # after the step
    t_settle = settling_time(poi_after_step, target=600, tolerance=6)  # 1% of 600 kW
    assert (t_settle != None and t_settle <= 30.0)

def test_step_down_no_undershoot(step_down_result):
    poi_after_step = step_down_result["poi"][60:]  # after the step
    assert min(poi_after_step) >= 600 * 0.9


# --- Exercise 5 --------------------------------------------------------
# Using the parametrized `rated_kw` fixture with make_plant and
# make_controller, run a limit of 60% of rated for 120 s and assert the
# final POI is within 0.1% of that limit. pytest -v should show THREE
# test runs from this one function.
pytest.mark.parametrize("rated_kw", [500, 1000, 5000], ids=lambda kw: f"{kw}kW")
def test_rated_kw_limits(make_plant, make_controller, rated_kw):
    plant = make_plant(rated_kw=rated_kw)
    controller = make_controller(rated_kw=rated_kw)
    limit = 0.6 * rated_kw
    limits = [limit] * 120
    result = run_closed_loop(plant, controller, limits)
    final_poi = result["poi"][-1]
    assert final_poi == pytest.approx(limit, rel=1e-3)


# --- Exercise 6 --------------------------------------------------------
# Cloud event and anti-windup. Limit 600 kW for 240 s. Available power:
# 1000 kW for 60 s, 400 kW for 60 s (cloud), then 1000 kW for 120 s.
# Pass available_kw=... to run_closed_loop().
#   a) With the default controller, POI after the cloud (index 120
#      onward) never exceeds 600 kW by more than 5%.
#   b) With anti-windup effectively disabled
#      (make_controller(integral_limit_kw=1e9)), the overshoot is
#      MORE than 20%. This proves the guard matters.
def test_cloud_event_anti_windup(make_plant, make_controller):
    plant = make_plant()
    controller = make_controller()  # default anti-windup
    limits = [600.0] * 240
    available_kw = [1000.0] * 60 + [400.0] * 60 + [1000.0] * 120
    result = run_closed_loop(plant, controller, limits, available_kw)
    poi_after_cloud = result["poi"][120:]  # after the cloud
    print(f"Max poi after cloud: {max(poi_after_cloud)}")
    assert max(poi_after_cloud) <= 600 * 1.05, f"Max poi after cloud: {max(poi_after_cloud)}"  # no more than 5% overshoot

    # Now disable anti-windup and check for overshoot >20%
    controller_no_windup = make_controller(integral_limit_kw=1e9)
    result_no_windup = run_closed_loop(plant, controller_no_windup, limits, available_kw)
    poi_after_cloud_no_windup = result_no_windup["poi"][120:]
    assert max(poi_after_cloud_no_windup) > 600 * 1.2, f"Max poi after cloud (no windup): {max(poi_after_cloud_no_windup)}"  # more than 20% overshoot


# --- Exercise 7 --------------------------------------------------------
# Ramp limit (Lesson 1 reused). With make_controller(max_ramp_kw_per_s=20),
# run a 600 kW limit from 0 kW for 120 s. Assert no change between
# consecutive commands exceeds 20 kW (include the starting 0 kW).  
def test_ramp_limit(make_plant, make_controller):
    plant = make_plant()
    controller = make_controller(max_ramp_kw_per_s=20)
    limits = ramp.simulate_ramp(start_kw=0, target_kw=600, max_ramp_kw_per_s=20, dt_s=1, max_steps=120)
    result = run_closed_loop(plant, controller, limits)
    commands = result["command"]
    for i in range(1, len(commands)):
        assert abs(commands[i] - commands[i - 1]) <= 20, f"Ramp exceeded at step {i}: {commands[i]} vs {commands[i-1]}"


# --- Exercise 8 --------------------------------------------------------
# Built-in fixture tmp_path: pytest gives each test a fresh temporary
# folder. Run a short simulation, save_csv() it to tmp_path / "run.csv",
# then assert the header is "t,limit,command,poi" and there is one data
# row per time step.
def test_save_csv_writes_header_rows(tmp_path, plant, controller):
    limits = [600.0] * 10
    result = run_closed_loop(plant, controller, limits)
    csv_path = tmp_path / "run.csv"
    save_csv(result, csv_path)

    with open(csv_path, 'r') as f:
        lines = f.readlines()
    
    # Check header
    assert lines[0].strip() == "t,limit,command,poi"

    # Check number of data rows matches number of time steps
    assert len(lines) - 1 == len(limits)  # subtract 1 for header