import unittest
from annoy.config import XSHUT_PINS, BUZZER_PIN, LED_PINS

# 0/1: HAT ID EEPROM (ID_SD/ID_SC), 2/3: I2C1 SDA/SCL used by the PCA9685s and VL53L0Xs
RESERVED = {0, 1, 2, 3}


class PinTest(unittest.TestCase):
    def test_pins_are_valid_unique_and_not_reserved(self):
        pins = list(XSHUT_PINS) + [BUZZER_PIN] + list(LED_PINS)
        self.assertEqual(len(pins), len(set(pins)), f"duplicate GPIO in {pins}")
        for p in pins:
            self.assertIn(p, range(28), f"GPIO {p} is not a Pi header pin")
            self.assertNotIn(p, RESERVED, f"GPIO {p} is reserved")


if __name__ == "__main__":
    unittest.main()
