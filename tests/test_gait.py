import math
import unittest
from annoy.config import (TRIPOD_A, TRIPOD_B, STAND_HEIGHT, BASE_PERIOD, BASE_LIFT,
                          MAX_LIFT, MAX_STEP_MM, LIFT_MARGIN, CLUTTER_MM)
from annoy.gait import TripodGait, adapt


class AdaptTest(unittest.TestCase):
    def test_clear_floor(self):
        lifts, period, blocked = adapt([0.0] * 6)
        self.assertEqual(lifts, [BASE_LIFT] * 6)
        self.assertEqual(period, BASE_PERIOD)
        self.assertFalse(blocked)

    def test_steps_over_low_clutter(self):
        lifts, period, blocked = adapt([MAX_STEP_MM, 0, 0, 0, 0, 0])
        self.assertAlmostEqual(lifts[0], MAX_STEP_MM / 1000 + LIFT_MARGIN)
        self.assertEqual(lifts[1:], [BASE_LIFT] * 5)
        self.assertGreater(period, BASE_PERIOD)
        self.assertFalse(blocked)

    def test_tall_clutter_blocks_and_lift_is_capped(self):
        lifts, _, blocked = adapt([0, 0, 120.0, 0, 0, 0])
        self.assertEqual(lifts[2], MAX_LIFT)
        self.assertTrue(blocked)

    def test_max_step_is_detectable(self):
        self.assertGreater(MAX_STEP_MM, CLUTTER_MM)


class TripodGaitTest(unittest.TestCase):
    def test_tripods_alternate(self):
        gait = TripodGait()
        for _ in range(100):
            gait.update(BASE_PERIOD / 100)
            feet = gait.foot_targets()
            down = {leg for leg, (_, _, z) in enumerate(feet) if abs(z + STAND_HEIGHT) < 1e-9}
            # One full tripod is always on the floor
            self.assertTrue(set(TRIPOD_A) <= down or set(TRIPOD_B) <= down)

    def _swing_z(self, gait, lifts):
        gait.update(BASE_PERIOD / 20)
        leg = TRIPOD_A[0]  # TRIPOD_A swings during the first half cycle
        return gait.foot_targets(lifts)[leg][2] + STAND_HEIGHT

    def test_lift_does_not_drop_mid_swing(self):
        gait = TripodGait()
        self._swing_z(gait, [MAX_LIFT] * 6)
        z = self._swing_z(gait, [BASE_LIFT] * 6)  # clutter vanished mid-swing
        self.assertAlmostEqual(z, MAX_LIFT * math.sin(math.pi * 0.2))

    def test_lift_can_rise_mid_swing(self):
        gait = TripodGait()
        self._swing_z(gait, [BASE_LIFT] * 6)
        z = self._swing_z(gait, [MAX_LIFT] * 6)
        self.assertAlmostEqual(z, MAX_LIFT * math.sin(math.pi * 0.2))

    def test_lift_relatches_on_next_swing(self):
        gait = TripodGait()
        self._swing_z(gait, [MAX_LIFT] * 6)
        gait.update(BASE_PERIOD * 0.9)  # through stance, back to the start of the next swing
        gait.foot_targets([BASE_LIFT] * 6)
        z = self._swing_z(gait, [BASE_LIFT] * 6)
        self.assertLess(z, MAX_LIFT * math.sin(math.pi * 0.2))

    def test_phase_wraps(self):
        gait = TripodGait()
        gait.update(BASE_PERIOD * 2.25)
        self.assertAlmostEqual(gait.phase, 0.25)


if __name__ == "__main__":
    unittest.main()
