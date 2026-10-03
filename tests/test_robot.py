import json
import os
import tempfile
import unittest
from annoy.config import BASE_PERIOD, MAX_LIFT
from annoy.gait import TripodGait
from annoy.kinematics import leg_ik
from annoy.robot import Hexapod, load_calibration


class CalibrationTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "calibration.json")

    def tearDown(self):
        self.dir.cleanup()

    def _write(self, cal):
        with open(self.path, "w") as f:
            json.dump(cal, f)

    def test_missing_file_is_neutral(self):
        self.assertEqual(load_calibration(self.path), ([0.0] * 18, [1] * 18))

    def test_valid_file_loads(self):
        self._write({"offsets": [2] * 18, "signs": [1, -1] * 9})
        offsets, signs = load_calibration(self.path)
        self.assertEqual(offsets, [2.0] * 18)
        self.assertEqual(signs, [1, -1] * 9)

    def test_rejects_bad_files(self):
        bad = [
            {"offsets": [0] * 17, "signs": [1] * 18},       # too few offsets
            {"offsets": [0] * 18, "signs": [1] * 18 + [1]},  # too many signs
            {"offsets": ["0"] * 18, "signs": [1] * 18},      # offsets not numbers
            {"offsets": [0] * 18, "signs": [2] * 18},        # sign not +/-1
            {"offsets": [0] * 18},                           # signs missing
        ]
        for cal in bad:
            self._write(cal)
            with self.assertRaises(ValueError, msg=str(cal)):
                load_calibration(self.path)


class HexapodTest(unittest.TestCase):
    def setUp(self):
        self.robot = Hexapod(sim=True, calibration_file="/nonexistent/calibration.json")

    def test_out_of_range_is_clamped_and_counted(self):
        self.robot.set_leg(0, (100.0, 0.0, 90.0))  # coxa servo 190
        self.assertEqual(self.robot.last[0], 180.0)
        self.assertEqual(self.robot.clamp_counts, [1] + [0] * 17)

    def test_normal_gait_never_clamps(self):
        gait = TripodGait()
        for _ in range(200):
            gait.update(BASE_PERIOD / 100)
            for leg, target in enumerate(gait.foot_targets([MAX_LIFT] * 6)):
                self.robot.set_leg(leg, leg_ik(*target))
        self.assertEqual(self.robot.clamp_counts, [0] * 18)


if __name__ == "__main__":
    unittest.main()
