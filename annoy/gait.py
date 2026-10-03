import math
from .config import (LEG_MOUNT_DEG, TRIPOD_A, REACH, STAND_HEIGHT,
                     STRIDE, BASE_LIFT, BASE_PERIOD, SLOW_FACTOR,
                     LIFT_MARGIN, MAX_LIFT, CLUTTER_MM, MAX_STEP_MM)


def adapt(heights_mm):
    """Clutter heights -> (per-leg lifts, gait period, blocked).

    Lift each foot above clutter near it, slow down when any is seen, and report
    blocked when something is too tall to step over.
    """
    lifts = [min(MAX_LIFT, max(BASE_LIFT, h / 1000 + LIFT_MARGIN)) if h >= CLUTTER_MM else BASE_LIFT
             for h in heights_mm]
    clutter = any(h >= CLUTTER_MM for h in heights_mm)
    blocked = any(h > MAX_STEP_MM for h in heights_mm)
    return lifts, BASE_PERIOD * (SLOW_FACTOR if clutter else 1.0), blocked


class TripodGait:
    """Two groups of three legs alternate swing and stance (50% duty)."""

    def __init__(self):
        self.phase = 0.0
        self.period = BASE_PERIOD
        self.heading = (1.0, 0.0)  # unit vector in body frame
        self._swing_lift = [BASE_LIFT] * 6
        self._swinging = [False] * 6

    def update(self, dt):
        self.phase = (self.phase + dt / self.period) % 1.0

    def foot_targets(self, lifts=None):
        lifts = lifts or [BASE_LIFT] * 6
        out = []
        for leg in range(6):
            local = (self.phase + (0.0 if leg in TRIPOD_A else 0.5)) % 1.0
            if local < 0.5:  # swing: foot moves forward, lifted
                # Latch lift at lift-off so the foot doesn't jump; it may still rise for
                # clutter seen mid-swing, but never drops onto it.
                if self._swinging[leg]:
                    self._swing_lift[leg] = max(self._swing_lift[leg], lifts[leg])
                else:
                    self._swing_lift[leg] = lifts[leg]
                self._swinging[leg] = True
                s = local / 0.5
                fwd = -STRIDE / 2 + STRIDE * s
                lift = self._swing_lift[leg] * math.sin(math.pi * s)
            else:            # stance: foot slides back on the floor
                self._swinging[leg] = False
                s = (local - 0.5) / 0.5
                fwd = STRIDE / 2 - STRIDE * s
                lift = 0.0
            m = math.radians(LEG_MOUNT_DEG[leg])
            bx, by = self.heading[0] * fwd, self.heading[1] * fwd
            lx = math.cos(m) * bx + math.sin(m) * by
            ly = -math.sin(m) * bx + math.cos(m) * by
            out.append((REACH + lx, ly, -STAND_HEIGHT + lift))
        return out
