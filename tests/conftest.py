"""Shared fixtures for Lesson 2.

pytest automatically loads conftest.py. Any test in this folder can use
these fixtures just by naming them as function arguments - no import.
"""
import pytest

from pv_controls.curtailment import PlantController, run_closed_loop
from pv_controls.plant import PVPlant


# --- Example fixture (already done) -----------------------------------
@pytest.fixture
def plant():
    """A fresh 1000 kW plant, starting at 0 kW, for each test."""
    return PVPlant(rated_kw=1000, tau_s=2.0, loss_fraction=0.02)


# --- Exercise 2 fixture -----------------------------------------------
# Write a `controller` fixture returning PlantController(rated_kw=1000).


# --- Exercise 3 fixtures ----------------------------------------------
# Write two FACTORY fixtures. Each returns an inner function, so a test
# can build objects with custom settings:
#
#     make_plant(initial_kw=1000)       -> PVPlant, 1000 kW rated
#     make_controller(ki=0)             -> PlantController, 1000 kW rated
#
# Pattern:
#     @pytest.fixture
#     def make_thing():
#         def _make(**overrides):
#             settings = {"rated_kw": 1000, **overrides}
#             return Thing(**settings)
#         return _make


# --- Exercise 4 fixture -----------------------------------------------
# Write a `step_down_result` fixture that USES make_plant and
# make_controller. Start the plant at 1000 kW, hold the limit at
# 1000 kW for 60 s, then step it to 600 kW for 120 s (dt = 1 s).
# Return the run_closed_loop() result.


# --- Exercise 5 fixture -----------------------------------------------
# Write a PARAMETRIZED fixture `rated_kw` with params=[500, 1000, 5000].
# Return request.param. Optional: ids=lambda kw: f"{kw}kW"
