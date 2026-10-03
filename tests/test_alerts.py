import unittest
from annoy.alerts import AlertStateMachine
from annoy.config import ALERT_GRACE_S, ALERT_STEP_S, ALERT_MAX_LEVEL, ALERT_CLEAR_HOLD_S


class AlertStateMachineTest(unittest.TestCase):
    def test_quiet_during_grace(self):
        sm = AlertStateMachine()
        self.assertEqual(sm.update(True, 0.0).level, 0)
        self.assertEqual(sm.update(True, ALERT_GRACE_S - 0.01).level, 0)
        self.assertEqual(sm.update(True, ALERT_GRACE_S).level, 1)

    def test_escalates_and_caps(self):
        sm = AlertStateMachine()
        sm.update(True, 0.0)
        self.assertEqual(sm.update(True, ALERT_GRACE_S + ALERT_STEP_S).level, 2)
        self.assertEqual(sm.update(True, 1000.0).level, ALERT_MAX_LEVEL)

    def test_resets_after_clear_hold(self):
        sm = AlertStateMachine()
        sm.update(True, 0.0)
        t = ALERT_GRACE_S + 1
        self.assertEqual(sm.update(True, t).level, 1)
        sm.update(False, t + 0.1)
        self.assertEqual(sm.update(False, t + 0.1 + ALERT_CLEAR_HOLD_S).level, 0)

    def test_brief_clear_does_not_reset(self):
        sm = AlertStateMachine()
        sm.update(True, 0.0)
        t = ALERT_GRACE_S + 1
        sm.update(False, t)
        self.assertEqual(sm.update(True, t + ALERT_CLEAR_HOLD_S / 2).level, 1)


if __name__ == "__main__":
    unittest.main()
