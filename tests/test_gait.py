import unittest
from annoy.config import TRIPOD_A, TRIPOD_B, STAND_HEIGHT, BASE_PERIOD
from annoy.gait import TripodGait


class TripodGaitTest(unittest.TestCase):
    def test_tripods_alternate(self):
        gait = TripodGait()
        for _ in range(100):
            gait.update(BASE_PERIOD / 100)
            feet = gait.foot_targets()
            down = {leg for leg, (_, _, z) in enumerate(feet) if abs(z + STAND_HEIGHT) < 1e-9}
            # One full tripod is always on the floor
            self.assertTrue(set(TRIPOD_A) <= down or set(TRIPOD_B) <= down)

    def test_phase_wraps(self):
        gait = TripodGait()
        gait.update(BASE_PERIOD * 2.25)
        self.assertAlmostEqual(gait.phase, 0.25)


if __name__ == "__main__":
    unittest.main()
