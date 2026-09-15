import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "assets/implementations"))
from motion_math import smootherstep, progress, hermite, damped_step


class MotionTests(unittest.TestCase):
    def test_smootherstep_is_monotonic_and_bounded(self):
        values = [smootherstep(i/100) for i in range(-10, 111)]
        self.assertEqual(values, sorted(values))
        self.assertEqual(values[0], 0)
        self.assertEqual(values[-1], 1)

    def test_endpoint_velocity_is_near_zero(self):
        epsilon = 0.0001
        self.assertLess(smootherstep(epsilon)/epsilon, 1e-5)
        self.assertLess((1-smootherstep(1-epsilon))/epsilon, 1e-5)

    def test_time_behavior_independent_of_frame_rate(self):
        self.assertEqual(progress(30/30, 0.5, 1), progress(60/60, 0.5, 1))

    def test_hermite_honors_endpoint_velocities(self):
        dt = 0.00001
        self.assertAlmostEqual((hermite(0,2,10,3,dt,2)-hermite(0,2,10,3,0,2))/dt, 2, places=3)
        self.assertAlmostEqual((hermite(0,2,10,3,2,2)-hermite(0,2,10,3,2-dt,2))/dt, 3, places=3)

    def test_spring_settles_and_rejects_invalid_parameters(self):
        self.assertAlmostEqual(damped_step(0), 0)
        self.assertAlmostEqual(damped_step(5), 1, places=6)
        with self.assertRaises(ValueError): damped_step(1, damping=0)


if __name__ == "__main__":
    unittest.main()
