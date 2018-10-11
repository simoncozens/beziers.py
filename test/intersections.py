import unittest
from beziers.cubicbezier import CubicBezier
from beziers.line import Line
from beziers.point import Point
from beziers.path import BezierPath
from beziers.path.representations.Segment import SegmentRepresentation

class IntersectionMethods(unittest.TestCase):
  def test_cubic_line(self):
    q = CubicBezier(
      Point(100,240), Point(30,60), Point(210,230), Point(160,30))
    l = Line(Point(25,260), Point(230,20))
    path = BezierPath()
    path.closed = False
    path.activeRepresentation = SegmentRepresentation(path,[q])
    i = q.intersections(l)
    self.assertEqual(len(i),3)
    self.assertEqual(i[0],q.pointAtTime(0.117517031451))
    self.assertEqual(i[1],q.pointAtTime(0.518591792307))
    self.assertEqual(i[2],q.pointAtTime(0.867886610031))
    # print q.intersections(l)
    # import matplotlib.pyplot as plt
    # fig, ax = plt.subplots()
    # path.plot(ax)

    # path = BezierPath()
    # path.closed = False
    # path.activeRepresentation = SegmentRepresentation(path,[l])
    # path.plot(ax)

    # for n in q.intersections(l):
    #   circle = plt.Circle((n.x, n.y), 1, fill=False)
    #   ax.add_artist(circle)


    # plt.show()