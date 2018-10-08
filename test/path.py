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
      Point(122,102), Point(35,200), Point(228,145), Point(190,46)
    )
    path = BezierPath()
    path.closed = False
    path.activeRepresentation = SegmentRepresentation(path,[q])
    path.addExtremes()
    segs = path.asSegments()
    self.assertEqual(len(segs), 4)

  def test_curvature(self):
    q = CubicBezier(
      Point(122,102), Point(35,200), Point(228,145), Point(190,46)
    )
    path = BezierPath()
    path.closed = False
    fig = plt.figure()
    ax = fig.add_subplot(111)
    path.activeRepresentation = SegmentRepresentation(path,[q])
    t = 0
    from matplotlib.path import Path
    import matplotlib.patches as patches
    verts, codes = [],[]
    path.addExtremes()
    while t < 1.0:
      p = q.pointAtTime(t)
      p2 = p + q.normalAtTime(t) * (q.curvatureAtTime(t) * 0.0001)
      verts.append((p.x,p.y))
      verts.append((p2.x,p2.y))
      codes.append(Path.MOVETO)
      codes.append(Path.LINETO)
      t+= 0.01
    patch = patches.PathPatch(Path(verts,codes), lw=2, fill = False)
    ax.add_patch(patch)
    path.plot(ax)
    plt.show()
