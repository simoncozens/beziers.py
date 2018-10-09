import unittest
from beziers.cubicbezier import CubicBezier
from beziers.point import Point

class CubicMethods(unittest.TestCase):
  def test_extremes(self):
    q = CubicBezier(
      Point(122,102), Point(35,200), Point(228,145), Point(190,46)
    )
    r = q.findExtremes()
    self.assertEqual(len(r), 3)
    self.assertAlmostEqual(r[0], 0.18740457659443518)
    self.assertAlmostEqual(r[1], 0.368678841994204)
    self.assertAlmostEqual(r[2], 0.9084858343644688)

  def test_extremes2(self):
    q = CubicBezier(
      Point(75,147), Point(147,32), Point(184,114), Point(190,46)
    )
    r = q.findExtremes()
    self.assertEqual(len(r), 0)

  def test_length(self):
    q = CubicBezier(
      Point(120,160), Point(35,200), Point(220,260), Point(220,40)
    )
    self.assertAlmostEqual(q.length,272.87003168)

  def test_align(self):
    q = CubicBezier(
      Point(120,160), Point(35,200), Point(220,260), Point(220,40)
    )
    s = q.align()
    self.assertAlmostEqual(s[0].x,0.0)
    self.assertAlmostEqual(s[0].y,0.0)
    self.assertAlmostEqual(s[1].x,-85.14452515537582)
    self.assertAlmostEqual(s[1].y,-39.69143277919774)
    self.assertAlmostEqual(s[2].x,-12.803687993289572)
    self.assertAlmostEqual(s[2].y,140.84056792618557)
    self.assertAlmostEqual(s[3].x,156.2049935181331)
    self.assertAlmostEqual(s[3].y,0.0)

  def test_curvature(self):
    q = CubicBezier(
      Point(122,102), Point(35,200), Point(228,145), Point(190,46)
    )
    self.assertAlmostEqual(q.curvatureAtTime(0.5),-103450.5)