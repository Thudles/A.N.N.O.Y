import math
import unittest
from annoy.config import COXA, FEMUR, TIBIA
from annoy.kinematics import leg_ik


def leg_fk(coxa, femur, knee):
    """Inverse of leg_ik: (coxa, femur, knee) degrees -> foot (x, y, z) in leg frame."""
    c, f, k = (math.radians(a) for a in (coxa, femur, knee))
    tibia_dir = f - (math.pi - k)
    r = FEMUR * math.cos(f) + TIBIA * math.cos(tibia_dir)
    z = FEMUR * math.sin(f) + TIBIA * math.sin(tibia_dir)
    return (COXA + r) * math.cos(c), (COXA + r) * math.sin(c), z


class LegIKTest(unittest.TestCase):
    def test_round_trip(self):
        for target in [(0.12, 0.0, -0.08), (0.10, 0.03, -0.06), (0.14, -0.025, -0.05),
                       (0.12, 0.0, -0.055)]:
            got = leg_fk(*leg_ik(*target))
            for a, b in zip(got, target):
                self.assertAlmostEqual(a, b, places=6, msg=f"target {target}")

    def test_unreachable_target_is_clamped_not_crashing(self):
        coxa, femur, knee = leg_ik(1.0, 0.0, 0.0)
        self.assertAlmostEqual(knee, 180.0, delta=1.0)


if __name__ == "__main__":
    unittest.main()
