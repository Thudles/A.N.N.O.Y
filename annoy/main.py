import argparse
import csv
import os
import time
from . import config as C
from .kinematics import leg_ik
from .gait import TripodGait
from .sensors import ToFArray
from .alerts import AlertStateMachine, AlertDriver
from .robot import Hexapod


def run(sim, seconds, log_path):
    robot, tof = Hexapod(sim), ToFArray(sim)
    driver, sm, gait = AlertDriver(sim), AlertStateMachine(), TripodGait()
    dt = 1.0 / C.LOOP_HZ
    os.makedirs(os.path.dirname(log_path) or ".", exist_ok=True)
    start = time.monotonic()
    step = 0
    with open(log_path, "w", newline="") as f:
        log = csv.writer(f)
        log.writerow(["t", "alert_level"] + [f"h{i}_mm" for i in range(6)])
        try:
            while True:
                now = step * dt if sim else time.monotonic() - start
                if seconds and now > seconds:
                    break
                heights = tof.heights_mm(now)
                clutter = any(h >= C.CLUTTER_MM for h in heights)
                # Adaptive gait: lift each foot above clutter near it, slow down when any is seen
                lifts = [max(C.BASE_LIFT, h / 1000 + C.LIFT_MARGIN) if h >= C.CLUTTER_MM else C.BASE_LIFT
                         for h in heights]
                gait.period = C.BASE_PERIOD * (C.SLOW_FACTOR if clutter else 1.0)
                gait.update(dt)
                for leg, target in enumerate(gait.foot_targets(lifts)):
                    robot.set_leg(leg, leg_ik(*target))
                out = sm.update(clutter, now)
                driver.apply(out, now)
                if step % 5 == 0:
                    log.writerow([f"{now:.2f}", out.level] + [f"{h:.1f}" for h in heights])
                step += 1
                if not sim:
                    time.sleep(max(0.0, start + step * dt - time.monotonic()))
        finally:
            driver.off()


def main():
    p = argparse.ArgumentParser(description="ANNOY hexapod")
    p.add_argument("--sim", action="store_true", help="run without hardware (fast, simulated time)")
    p.add_argument("--center", action="store_true", help="set all servos to 90 degrees and exit")
    p.add_argument("--seconds", type=float, default=0, help="stop after N seconds (0 = forever)")
    p.add_argument("--log", default="logs/run.csv")
    a = p.parse_args()
    if a.center:
        Hexapod(a.sim).center_all()
        return
    run(a.sim, a.seconds, a.log)


if __name__ == "__main__":
    main()
