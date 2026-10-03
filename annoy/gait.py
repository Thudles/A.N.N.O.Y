import math
from .config import (LEG_MOUNT_DEG, TRIPOD_A, REACH, STAND_HEIGHT,
                     STRIDE, BASE_LIFT, BASE_PERIOD)


class TripodGait:
    """Two groups of three legs alternate swing and stance (50% duty)."""

    def __init__(self):
        self.phase = 0.0
        self.period = BASE_PERIOD
        self.heading = (1.0, 0.0)  # unit vector in body frame

    def update(self, dt):
        self.phase = (self.phase + dt / self.period) % 1.0

    def foot_targets(self, lifts=None):
        lifts = lifts or [BASE_LIFT] * 6
        out = []
        for leg in range(6):
            local = (self.phase + (0.0 if leg in TRIPOD_A else 0.5)) % 1.0
            if local < 0.5:  # swing: foot moves forward, lifted
                s = local / 0.5
                fwd = -STRIDE / 2 + STRIDE * s
                lift = lifts[leg] * math.sin(math.pi * s)
            else:            # stance: foot slides back on the floor
                s = (local - 0.5) / 0.5
                fwd = STRIDE / 2 - STRIDE * s
                lift = 0.0
            m = math.radians(LEG_MOUNT_DEG[leg])
            bx, by = self.heading[0] * fwd, self.heading[1] * fwd
            lx = math.cos(m) * bx + math.sin(m) * by
            ly = -math.sin(m) * bx + math.cos(m) * by
            out.append((REACH + lx, ly, -STAND_HEIGHT + lift))
        return out
