"""Ramp-rate limiter for a PV plant active-power controller.

Grid operators limit how fast plant output may change. The controller
moves the power setpoint toward a target no faster than that limit.
"""


def limit_ramp(current_kw: float, target_kw: float,
               max_ramp_kw_per_s: float, dt_s: float) -> float:
    """Return the next setpoint, moving toward target_kw without
    exceeding max_ramp_kw_per_s over a time step of dt_s seconds."""
    if max_ramp_kw_per_s < 0:
        raise ValueError("ramp limit must be non-negative")
    if dt_s <= 0:
        raise ValueError("time step must be positive")

    max_step = max_ramp_kw_per_s * dt_s
    delta = target_kw - current_kw

    if abs(delta) <= max_step:
        return target_kw
    if delta > 0:
        return current_kw + max_step
    return current_kw + max_step


def simulate_ramp(start_kw: float, target_kw: float,
                  max_ramp_kw_per_s: float, dt_s: float,
                  max_steps: int = 10_000) -> list[float]:
    """Run the limiter repeatedly and return every setpoint,
    starting with start_kw and ending when target_kw is reached
    (or after max_steps)."""
    history = [start_kw]
    current = start_kw
    for _ in range(max_steps):
        if current == target_kw:
            break
        current = limit_ramp(current, target_kw, max_ramp_kw_per_s, dt_s)
        history.append(current)
    return history
