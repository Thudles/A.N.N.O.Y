import json
import os
import sys
from .config import PCA_ADDRESSES, PULSE_RANGE_US, CALIBRATION_FILE


def load_calibration(path):
    """Read and check calibration.json -> (offsets, signs). Missing file -> neutral values."""
    if not os.path.exists(path):
        return [0.0] * 18, [1] * 18
    with open(path) as f:
        cal = json.load(f)
    offsets, signs = cal.get("offsets"), cal.get("signs")
    if not isinstance(offsets, list) or len(offsets) != 18 \
            or not all(isinstance(o, (int, float)) and not isinstance(o, bool) for o in offsets):
        raise ValueError(f"{path}: 'offsets' must be a list of 18 numbers")
    if not isinstance(signs, list) or len(signs) != 18 or not all(s in (1, -1) for s in signs):
        raise ValueError(f"{path}: 'signs' must be a list of 18 values, each +1 or -1")
    return [float(o) for o in offsets], [int(s) for s in signs]


class Hexapod:
    """Writes joint angles (degrees) to 18 servos across two PCA9685 boards."""

    def __init__(self, sim=False, calibration_file=CALIBRATION_FILE):
        self.sim = sim
        if not sim and not os.path.exists(calibration_file):
            print(f"warning: no calibration at {calibration_file}, using neutral offsets", file=sys.stderr)
        self.offsets, self.signs = load_calibration(calibration_file)
        self.last = [90.0] * 18
        self.clamp_counts = [0] * 18  # writes outside 0-180: bad IK target or calibration
        if sim:
            return
        from adafruit_servokit import ServoKit
        self.kits = [ServoKit(channels=16, address=a) for a in PCA_ADDRESSES]
        for ch in range(18):
            self.kits[ch // 16].servo[ch % 16].set_pulse_width_range(*PULSE_RANGE_US)

    def _write(self, ch, angle):
        if not 0.0 <= angle <= 180.0:
            self.clamp_counts[ch] += 1
            angle = max(0.0, min(180.0, angle))
        self.last[ch] = angle
        if not self.sim:
            self.kits[ch // 16].servo[ch % 16].angle = angle

    def set_leg(self, leg, ik_angles):
        coxa, femur, knee = ik_angles
        # Map IK angles to servo angles: coxa and femur are centered on 90, the knee's
        # interior angle maps directly. Signs and offsets come from calibration.
        raw = (90 + coxa, 90 + femur, knee)
        for j, a in enumerate(raw):
            ch = leg * 3 + j
            self._write(ch, 90 + self.signs[ch] * (a - 90) + self.offsets[ch])

    def center_all(self):
        """Drive every servo to 90 so you can mount horns and check neutral."""
        for ch in range(18):
            self._write(ch, 90)
