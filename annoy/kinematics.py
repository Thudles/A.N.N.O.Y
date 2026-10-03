import math
from .config import COXA, FEMUR, TIBIA


def _clamp(v, lo=-1.0, hi=1.0):
    return max(lo, min(hi, v))


def leg_ik(x, y, z):
    """Foot target in leg frame (m, x outward, z up) -> (coxa, femur, knee) degrees.

    femur: angle of the femur above horizontal.
    knee: interior angle between femur and tibia (180 = straight).
    """
    coxa = math.atan2(y, x)
    r = math.hypot(x, y) - COXA
    d = min(math.hypot(r, z), FEMUR + TIBIA - 1e-6)
    a1 = math.atan2(z, r)
    a2 = math.acos(_clamp((FEMUR**2 + d**2 - TIBIA**2) / (2 * FEMUR * d)))
    knee = math.acos(_clamp((FEMUR**2 + TIBIA**2 - d**2) / (2 * FEMUR * TIBIA)))
    return math.degrees(coxa), math.degrees(a1 + a2), math.degrees(knee)
