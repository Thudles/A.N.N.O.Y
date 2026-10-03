import contextlib
import csv
import io
import os
import tempfile
import unittest
from annoy.main import run


class SimSmokeTest(unittest.TestCase):
    def test_sock_raises_then_clears_alert(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "run.csv")
            with contextlib.redirect_stdout(io.StringIO()):
                run(sim=True, seconds=40, log_path=path)
            with open(path) as f:
                levels = [int(r["alert_level"]) for r in csv.DictReader(f)]
        self.assertGreaterEqual(max(levels), 2)
        self.assertEqual(levels[-1], 0)


if __name__ == "__main__":
    unittest.main()
