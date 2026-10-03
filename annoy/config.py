"""All tunables in one place. Measure your own frame and edit these."""

LOOP_HZ = 50

# Leg link lengths in meters (measure yours)
COXA, FEMUR, TIBIA = 0.045, 0.075, 0.110
STAND_HEIGHT = 0.08   # body height above floor
REACH = 0.12          # neutral foot distance outward from coxa axis

# Leg order: 0 front-right, 1 mid-right, 2 rear-right, 3 rear-left, 4 mid-left, 5 front-left
# Direction each leg points outward in the body frame (x forward, y left), degrees
LEG_MOUNT_DEG = [-45, -90, -135, 135, 90, 45]
TRIPOD_A = (0, 2, 4)
TRIPOD_B = (1, 3, 5)

# Servo mapping: leg*3 + joint (0 coxa, 1 femur, 2 tibia) -> channel 0-31
# Board 0 at 0x40 (ch 0-15), board 1 at 0x41 (ch 16-31)
PCA_ADDRESSES = (0x40, 0x41)
PULSE_RANGE_US = (500, 2500)
CALIBRATION_FILE = "calibration.json"  # {"offsets": [18 floats], "signs": [18 of +1/-1]}

# Gait
STRIDE = 0.05
BASE_LIFT = 0.025
BASE_PERIOD = 0.8     # seconds per full cycle
SLOW_FACTOR = 1.6     # gait slows by this much near clutter
LIFT_MARGIN = 0.02    # extra clearance above clutter height
MAX_LIFT = 0.05       # keeps femur under +90 deg and feet below the belly; measure yours
MAX_STEP_MM = (MAX_LIFT - LIFT_MARGIN) * 1000  # taller clutter blocks instead of being stepped over

# Time-of-flight sensors (one per leg, mounted ahead of the foot, pointing down)
XSHUT_PINS = [5, 6, 13, 19, 26, 20]  # BCM GPIO numbers, edit to match wiring
BASE_I2C_ADDR = 0x30
CLUTTER_MM = 15       # height above baseline that counts as clutter

# Alerts
BUZZER_PIN = 21
LED_PINS = (16, 12, 1)  # R, G, B (BCM)
ALERT_GRACE_S = 5
ALERT_STEP_S = 10
ALERT_MAX_LEVEL = 5
ALERT_CLEAR_HOLD_S = 2
