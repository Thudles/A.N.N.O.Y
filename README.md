# A.N.N.O.Y: Autonomous Nagging Navigator Observing Your clutter

Python hexapod for a Raspberry Pi. Two PCA9685 boards drive 18 servos, six VL53L0X
sensors point down ahead of each foot, and an adaptive tripod gait steps over clutter
while escalating beeps and lights nag until the floor is clear.

## Try it without hardware
    python -m annoy.main --sim --seconds 40
Simulates a sock under sensor 0 from t=5s to t=25s. Watch the alert level climb, then check `logs/run.csv`.

Run the tests (no hardware or extra packages needed):
    python -m unittest

## Hardware setup
1. Enable I2C on the Pi (`sudo raspi-config`), `pip install -r requirements.txt`.
2. PCA9685 boards at 0x40 and 0x41 (solder the A0 jumper on the second). Servo power from a 6V 10A+ buck, shared ground only with the Pi, and power the Pi from its own 5V supply.
3. Wire each VL53L0X XSHUT pin to the GPIOs in `config.py` (`XSHUT_PINS`); addresses are assigned at boot.
4. Measure link lengths and set `COXA/FEMUR/TIBIA` in `config.py`.
5. `python -m annoy.main --center`, attach horns at neutral, then create `calibration.json` next to this README with 18 `offsets` and 18 `signs` (+1 or -1) until each leg moves the right way. Bring up one leg at a time.
6. Run `python -m annoy.main` with the robot on a stand first.

## Testing for the resume claim
Log trials per obstacle type (socks, shoe, book, cable, box, bag): detected, cleared, success rate.
`logs/run.csv` has timestamps, alert level, and per-sensor clutter height to back this up.

## Known limits
- ServoKit writes one channel per I2C call; if the 50 Hz loop lags, switch to PCA9685 auto-increment batch writes.
- Gait is open loop and heads straight; no turning or body leveling yet.
- Clutter taller than `MAX_STEP_MM` (derived from `MAX_LIFT` in `config.py`) stops the robot in place; it can't route around it yet.
