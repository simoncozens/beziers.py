import unittest
from beziers.path.representations.GSPath import GSPathRepresentation
from beziers.path.representations.Segment import SegmentRepresentation
from beziers.path.representations.Nodelist import Node
from beziers.point import Point
from beziers.cubicbezier import CubicBezier
from beziers.line import Line
from beziers.path import BezierPath
from dotmap import DotMap

import matplotlib.pyplot as plt

class PathTests(unittest.TestCase):
  def test_representations(self):
    b = DotMap({ "closed": True,
    "nodes": [
    {"x":385.0, "y":20.0, "type":"offcurve"},
    { "x":526.0, "y":79.0, "type":"offcurve"},
    { "x":566.0, "y":135.0, "type":"curve"},
    { "x":585.0, "y":162.0, "type":"offcurve"},
    { "x":566.0, "y":260.0, "type":"offcurve"},
    { "x":484.0, "y":281.0, "type":"curve"},
    { "x":484.0, "y":407.0, "type":"offcurve"},
    { "x":381.0, "y":510.0, "type":"offcurve"},
    { "x":255.0, "y":510.0, "type":"curve"},
    { "x":26.0, "y":281.0, "type":"line"},
    { "x":26.0, "y":155.0, "type":"offcurve"},
    { "x":129.0, "y":20.0, "type":"offcurve"},
    { "x":255.0, "y":20.0, "type":"curve"}
    ]})

    path = BezierPath()
    path.activeRepresentation = GSPathRepresentation(path,b)
    nl = path.asNodelist()
    self.assertEqual(len(nl), 13)
    self.assertIsInstance(nl[1], Node)
    self.assertEqual(nl[1].type,"offcurve")
    self.assertAlmostEqual(nl[1].x,526.0)

    segs = path.asSegments()
    self.assertEqual(len(segs), 5)
    self.assertIsInstance(segs[1], CubicBezier)
    self.assertIsInstance(segs[2], Line)

  def test_addextremes(self):
    q = CubicBezier(
      Point(42,135), Point(129,242), Point(167,77), Point(65,59)
    )
    ex = q.findExtremes()
    self.assertEqual(len(ex),2)
    path = BezierPath()
    path.closed = False
    path.activeRepresentation = SegmentRepresentation(path,[q])
    path.addExtremes()
    path.balance()
    segs = path.asSegments()
    self.assertEqual(len(segs), 3)
    # import matplotlib.pyplot as plt
    # fig, ax = plt.subplots()
    # path.plot(ax)
    # plt.show()