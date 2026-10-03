import math
import random
import statistics
from collections import deque
from .config import XSHUT_PINS, BASE_I2C_ADDR


class ToFArray:
    """Six VL53L0X sensors. Reports clutter height (mm) above each sensor's floor baseline."""

    def __init__(self, sim=False):
        self.sim = sim
        self.hist = [deque(maxlen=3) for _ in range(6)]
        if sim:
            self.baseline = [100.0] * 6
            return
        import board, busio, adafruit_vl53l0x
        from gpiozero import DigitalOutputDevice
        i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)
        xshut = [DigitalOutputDevice(p, initial_value=False) for p in XSHUT_PINS]
        self.sensors = []
        for i, pin in enumerate(xshut):  # wake one at a time, give each a unique address
            pin.on()
            s = adafruit_vl53l0x.VL53L0X(i2c)
            s.set_address(BASE_I2C_ADDR + i)
            self.sensors.append(s)
        self.baseline = self._measure_baseline()

    def _raw(self, i, now):
        if self.sim:
            reading = 100.0 + random.gauss(0, 1.0)
            if i == 0 and 5.0 <= now <= 25.0:  # fake sock under sensor 0
                reading -= 25.0
            return reading
        return float(self.sensors[i].range)

    def _measure_baseline(self):
        base = []
        for i in range(6):
            vals = [self._raw(i, 0) for _ in range(20)]
            base.append(statistics.median(vals))
        return base

    def heights_mm(self, now=0.0):
        out = []
        for i in range(6):
            self.hist[i].append(self._raw(i, now))
            filt = statistics.median(self.hist[i])
            out.append(max(0.0, self.baseline[i] - filt))
        return out
