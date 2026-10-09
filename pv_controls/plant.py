"""Simple PV plant model for closed-loop controller testing.

The plant does not jump instantly to the commanded power. Its inverter
output follows a first-order lag toward the command, and it can never
produce more than the power available from the sun (available_kw) or
its nameplate rating (rated_kw). Collection-system losses mean the
power measured at the point of interconnection (POI) is slightly lower
than the inverter output.
"""


class PVPlant:
    def __init__(self, rated_kw: float, tau_s: float = 2.0,
                 loss_fraction: float = 0.02, initial_kw: float = 0.0):
        if rated_kw <= 0:
            raise ValueError("rated_kw must be positive")
        if tau_s <= 0:
            raise ValueError("tau_s must be positive")
        if not 0 <= loss_fraction < 1:
            raise ValueError("loss_fraction must be in [0, 1)")

        self.rated_kw = rated_kw
        self.tau_s = tau_s
        self.loss_fraction = loss_fraction
        self.inverter_kw = float(initial_kw)
        self.available_kw = float(rated_kw)

    def set_available(self, available_kw: float) -> None:
        """Set solar resource (e.g., drops during a passing cloud)."""
        self.available_kw = min(max(available_kw, 0.0), self.rated_kw)

    @property
    def poi_kw(self) -> float:
        """Power measured at the point of interconnection."""
        return self.inverter_kw * (1 - self.loss_fraction)

    def step(self, command_kw: float, dt_s: float) -> float:
        """Advance the model by dt_s seconds and return POI power."""
        if dt_s <= 0:
            raise ValueError("time step must be positive")
        target = min(max(command_kw, 0.0), self.available_kw)
        alpha = dt_s / (self.tau_s + dt_s)
        self.inverter_kw += alpha * (target - self.inverter_kw)
        return self.poi_kw
