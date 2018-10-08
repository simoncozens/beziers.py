import unittest
from beziers.quadraticbezier import QuadraticBezier
from beziers.point import Point

class QuadraticMethods(unittest.TestCase):
  def test_extremes(self):
    q = QuadraticBezier(
      Point(70,250), Point(13,187), Point(209,58))
    r = q.findExtremes()
    self.assertEqual(len(r), 1)
    self.assertAlmostEqual(r[0], 127/532.0)

  def test_extremes2(self):
    q = QuadraticBezier(
      Point(70,250), Point(10,14), Point(209,58))
    r = q.findExtremes()
    self.assertEqual(len(r), 2)
    self.assertAlmostEqual(r[0], 65/269.0)
    self.assertAlmostEqual(r[1], 81/98.0)

