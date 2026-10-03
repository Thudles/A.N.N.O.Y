from dataclasses import dataclass
from .config import (ALERT_GRACE_S, ALERT_STEP_S, ALERT_MAX_LEVEL,
                     ALERT_CLEAR_HOLD_S, BUZZER_PIN, LED_PINS)

COLORS = {0: (0, 0, 0), 1: (1, 1, 0), 2: (1, 0.6, 0), 3: (1, 0.3, 0), 4: (1, 0, 0), 5: (1, 0, 0)}


@dataclass
class AlertOutput:
    level: int
    beep: bool
    color: tuple


class AlertStateMachine:
    """Quiet grace period, then each step makes the beeps faster and the light angrier."""

    def __init__(self):
        self._start = None
        self._clear_since = None

    def update(self, clutter, now):
        if clutter:
            self._clear_since = None
            if self._start is None:
                self._start = now
        elif self._start is not None:
            if self._clear_since is None:
                self._clear_since = now
            elif now - self._clear_since >= ALERT_CLEAR_HOLD_S:
                self._start = self._clear_since = None
        level = 0
        if self._start is not None and now - self._start >= ALERT_GRACE_S:
            level = min(ALERT_MAX_LEVEL, 1 + int((now - self._start - ALERT_GRACE_S) / ALERT_STEP_S))
        beep, color = False, COLORS[0]
        if level:
            period = max(0.2, 1.6 - 0.35 * level)
            beep = (now % period) < 0.1
            color = COLORS[level]
            if level == ALERT_MAX_LEVEL and (now % 0.4) >= 0.2:
                color = COLORS[0]
        return AlertOutput(level, beep, color)


class AlertDriver:
    def __init__(self, sim=False):
        self.sim = sim
        self._last_level = 0
        if not sim:
            from gpiozero import Buzzer, RGBLED
            self.buzzer = Buzzer(BUZZER_PIN)
            self.led = RGBLED(*LED_PINS)

    def apply(self, out, now):
        if self.sim:
            if out.level != self._last_level:
                print(f"[{now:5.1f}s] alert level {self._last_level} -> {out.level}")
                self._last_level = out.level
            return
        self.buzzer.value = 1 if out.beep else 0
        self.led.color = out.color

    def off(self):
        if not self.sim:
            self.buzzer.off()
            self.led.off()
