import json
import os
from .config import PCA_ADDRESSES, PULSE_RANGE_US, CALIBRATION_FILE


class Hexapod:
    """Writes joint angles (degrees) to 18 servos across two PCA9685 boards."""

    def __init__(self, sim=False):
        self.sim = sim
        self.offsets = [0.0] * 18
        self.signs = [1] * 18
        if os.path.exists(CALIBRATION_FILE):
            with open(CALIBRATION_FILE) as f:
                cal = json.load(f)
            self.offsets, self.signs = cal["offsets"], cal["signs"]
        self.last = [90.0] * 18
        if sim:
            return
        from adafruit_servokit import ServoKit
        self.kits = [ServoKit(channels=16, address=a) for a in PCA_ADDRESSES]
        for ch in range(18):
            self.kits[ch // 16].servo[ch % 16].set_pulse_width_range(*PULSE_RANGE_US)

    def _write(self, ch, angle):
        angle = max(0.0, min(180.0, angle))
        self.last[ch] = angle
        if not self.sim:
            self.kits[ch // 16].servo[ch % 16].angle = angle

    def set_leg(self, leg, ik_angles):
        coxa, femur, knee = ik_angles
        # Map IK angles to servo angles. Signs and offsets come from calibration.
        raw = (90 + coxa, 90 + femur, 90 + (knee - 90))
        for j, a in enumerate(raw):
            ch = leg * 3 + j
            self._write(ch, 90 + self.signs[ch] * (a - 90) + self.offsets[ch])

    def center_all(self):
        """Drive every servo to 90 so you can mount horns and check neutral."""
        for ch in range(18):
            self._write(ch, 90)
