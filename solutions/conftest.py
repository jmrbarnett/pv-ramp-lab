"""Reference fixtures for Lesson 2 (used by `pytest solutions/`)."""
import pytest

from pv_controls.curtailment import PlantController, run_closed_loop
from pv_controls.plant import PVPlant


@pytest.fixture
def plant():
    return PVPlant(rated_kw=1000, tau_s=2.0, loss_fraction=0.02)


# Exercise 2
@pytest.fixture
def controller():
    return PlantController(rated_kw=1000)


# Exercise 3
@pytest.fixture
def make_plant():
    def _make(**overrides):
        settings = {"rated_kw": 1000, **overrides}
        return PVPlant(**settings)
    return _make


@pytest.fixture
def make_controller():
    def _make(**overrides):
        settings = {"rated_kw": 1000, **overrides}
        return PlantController(**settings)
    return _make


# Exercise 4
@pytest.fixture
def step_down_result(make_plant, make_controller):
    plant = make_plant(initial_kw=1000)
    limits = [1000] * 60 + [600] * 120
    return run_closed_loop(plant, make_controller(), limits)


# Exercise 5
@pytest.fixture(params=[500, 1000, 5000], ids=lambda kw: f"{kw}kW")
def rated_kw(request):
    return request.param
