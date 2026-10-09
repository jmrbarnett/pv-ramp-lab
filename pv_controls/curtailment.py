"""Power plant controller (PPC) for curtailment / setpoint tracking.

The PPC compares the curtailment limit with the power measured at the
point of interconnection (POI) and adjusts the command sent to the
inverters so that POI power tracks the limit.

    command = limit + kp * error + integral      (error = limit - POI)

* The proportional term reacts quickly to error.
* The integral term removes steady-state error caused by plant losses.
* Anti-windup clamps the integral to +/- integral_limit_kw so it cannot
  grow without bound when the limit is unreachable (e.g., a cloud).
* An optional ramp limit (from Lesson 1) slows command changes.
"""
from pv_controls.ramp import limit_ramp


def effective_limit(rated_kw: float, operator_pct: float = 100.0,
                    export_limit_kw: float | None = None) -> float:
    """Most restrictive of: rated power, the grid operator's curtailment
    command (percent of rated), and an optional export limit."""
    if not 0 <= operator_pct <= 100:
        raise ValueError("operator_pct must be between 0 and 100")
    if export_limit_kw is not None and export_limit_kw < 0:
        raise ValueError("export_limit_kw must be non-negative")

    limits = [rated_kw, rated_kw * operator_pct / 100]
    if export_limit_kw is not None:
        limits.append(export_limit_kw)
    return min(limits)


class PlantController:
    def __init__(self, rated_kw: float, kp: float = 0.3, ki: float = 0.2,
                 max_ramp_kw_per_s: float | None = None,
                 integral_limit_kw: float | None = None):
        if rated_kw <= 0:
            raise ValueError("rated_kw must be positive")
        if kp < 0 or ki < 0:
            raise ValueError("gains must be non-negative")

        self.rated_kw = rated_kw
        self.kp = kp
        self.ki = ki
        self.max_ramp_kw_per_s = max_ramp_kw_per_s
        # Default: integral may correct up to 5% of rated power
        self.integral_limit_kw = (0.05 * rated_kw if integral_limit_kw is None
                                  else integral_limit_kw)
        self.integral = 0.0
        self.command_kw = 0.0

    def update(self, limit_kw: float, measured_kw: float,
               dt_s: float) -> float:
        """Return the next inverter command in kW."""
        error = limit_kw - measured_kw

        # Integrate, then clamp (anti-windup)
        self.integral += self.ki * error * dt_s
        self.integral = min(max(self.integral, -self.integral_limit_kw),
                            self.integral_limit_kw)

        command = limit_kw + self.kp * error + self.integral
        command = min(max(command, 0.0), self.rated_kw)

        if self.max_ramp_kw_per_s is not None:
            command = limit_ramp(self.command_kw, command,
                                 self.max_ramp_kw_per_s, dt_s)

        self.command_kw = command
        return command


def run_closed_loop(plant, controller, limits_kw: list[float],
                    available_kw: list[float] | None = None,
                    dt_s: float = 1.0) -> dict[str, list[float]]:
    """Simulate one controller update and one plant step per entry in
    limits_kw. Returns time series keyed by 't', 'limit', 'command',
    'poi'. available_kw (same length) changes the solar resource."""
    if available_kw is not None and len(available_kw) != len(limits_kw):
        raise ValueError("available_kw must match limits_kw length")

    result = {"t": [], "limit": [], "command": [], "poi": []}
    for i, limit in enumerate(limits_kw):
        if available_kw is not None:
            plant.set_available(available_kw[i])
        command = controller.update(limit, plant.poi_kw, dt_s)
        poi = plant.step(command, dt_s)

        result["t"].append(round((i + 1) * dt_s, 9))
        result["limit"].append(limit)
        result["command"].append(command)
        result["poi"].append(poi)
    return result


def settling_time(values: list[float], target: float, tolerance: float,
                  dt_s: float = 1.0) -> float | None:
    """Seconds until values enter target +/- tolerance and stay there.
    Returns None if they never settle."""
    for i in range(len(values)):
        if all(abs(v - target) <= tolerance for v in values[i:]):
            return round((i + 1) * dt_s, 9)
    return None


def save_csv(result: dict[str, list[float]], path) -> None:
    """Write a run_closed_loop result to CSV for ploting or review."""
    keys = list(result)
    with open(path, "w", newline="") as f:
        f.write(",".join(keys) + "\n")
        for row in zip(*(result[k] for k in keys)):
            f.write(",".join(f"{v:g}" for v in row) + "\n")
