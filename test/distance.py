import unittest
from beziers.path.geometricshapes import Circle
from beziers.point import Point

class DistanceMethods(unittest.TestCase):
  def test_distance(self):
  	p1 = Circle(50)
  	p2 = Circle(50,origin=Point(200,0))
  	self.assertAlmostEqual(p1.distanceToPath(p2)[0], 100)