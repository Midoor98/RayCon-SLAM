import csv
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from trajectory import integrate


def sample(t, dx=0, dy=0, yaw=0):
    return dict(timestamp=t, dx_body_m=dx, dy_body_m=dy, dyaw_rad=yaw)


class TrajectoryTests(unittest.TestCase):
    def test_square_returns_to_origin(self):
        with (ROOT / "data/odometry.csv").open(newline="", encoding="utf-8") as stream:
            poses, distance = integrate(csv.DictReader(stream))
        self.assertEqual(len(poses), 9)
        self.assertAlmostEqual(distance, 8.0)
        self.assertAlmostEqual(poses[-1]["tx"], 0.0)
        self.assertAlmostEqual(poses[-1]["ty"], 0.0)
        for pose in poses:
            self.assertAlmostEqual(sum(pose[k] ** 2 for k in ("qx", "qy", "qz", "qw")), 1.0)

    def test_translation_uses_previous_body_orientation(self):
        poses, _ = integrate([sample(0), sample(1, 1, 0, math.pi / 2), sample(2, 2)])
        self.assertAlmostEqual(poses[1]["tx"], 1.0)
        self.assertAlmostEqual(poses[1]["ty"], 0.0)
        self.assertAlmostEqual(poses[2]["tx"], 1.0)
        self.assertAlmostEqual(poses[2]["ty"], 2.0)

    def test_sideways_translation(self):
        poses, distance = integrate([sample(0), sample(1, dy=2)])
        self.assertAlmostEqual(poses[-1]["tx"], 0)
        self.assertAlmostEqual(poses[-1]["ty"], 2)
        self.assertAlmostEqual(distance, 2)

    def test_invalid_timestamp_order(self):
        for t in (0, -1):
            with self.subTest(t=t), self.assertRaises(ValueError):
                integrate([sample(0), sample(t, 1)])

    def test_invalid_start_and_empty_input(self):
        for rows in ([], [sample(0, dx=1)], [sample(0, yaw=1)]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                integrate(rows)

    def test_nonfinite_input(self):
        for key in sample(0):
            with self.subTest(key=key), self.assertRaises(ValueError):
                integrate([sample(0), {**sample(1), key: math.nan}])


if __name__ == "__main__":
    unittest.main()
