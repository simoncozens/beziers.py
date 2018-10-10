from beziers.path.representations.Segment import SegmentRepresentation
from beziers.path.representations.Nodelist import NodelistRepresentation, Node
from beziers.point import Point
from beziers.utils.samplemixin import SampleMixin
from beziers.segment import Segment
from beziers.line import Line
from beziers.cubicbezier import CubicBezier

import math

class BezierPath(SampleMixin,object):
  """`BezierPath` represents a collection of `Segment` objects - the
  curves and lines that make up a path.

  One of the really fiddly things about manipulating Bezier paths in
  a computer is that there are various ways to represent them.
  Different applications prefer different representations. For instance,
  when you're drawing a path on a canvas, you often want a list of nodes
  like so::

    { "x":255.0, "y":20.0, "type":"curve"},
    { "x":385.0, "y":20.0, "type":"offcurve"},
    { "x":526.0, "y":79.0, "type":"offcurve"},
    { "x":566.0, "y":135.0, "type":"curve"},
    { "x":585.0, "y":162.0, "type":"offcurve"},
    { "x":566.0, "y":260.0, "type":"offcurve"},
    { "x":484.0, "y":281.0, "type":"curve"},
    ...

  But when you're doing Clever Bezier Mathematics, you generally want
  a list of segments instead::

    [ (255.0,20.0), (385.0,20.0), (526.0,79.0), (566.0,135.0)],
    [ (566.0,135.0), (585.0,162.0), (566.0,260.0), (484.0,281.0)],

  The Beziers module is designed to allow you to move fluidly between these
  different representations depending on what you're wanting to do.

  """

  def __init__(self):
    self.activeRepresentation = None
    self.closed = True


  @classmethod
  def fromPoints(self, points, error = 50.0, cornerTolerance = 20.0, maxSegments = 20):
    """Fit a poly-bezier curve to the points given. This operation should be familiar
    from 'pencil' tools in a vector drawing application: the application samples points
    where your mouse pointer has been dragged, and then turns the sketch into a Bezier
    path. The goodness of fit can be controlled by tuning the `error` parameter. Corner
    detection can be controlled with `cornerTolerance`.

    Here are some points fit with `error=100.0`:

..  figure:: curvefit1.png
    :scale: 75 %
    :alt: curvefit1


    And with `error=10.0`:

..  figure:: curvefit2.png
    :scale: 75 %
    :alt: curvefit1

    """
    from beziers.utils.curvefitter import CurveFit
    segs = CurveFit.fitCurve(points, error, cornerTolerance, maxSegments)
    path = BezierPath()
    path.closed = False
    path.activeRepresentation = SegmentRepresentation(path,segs)
    return path

  @classmethod
  def fromSegments(klass, array):
    """Construct a path from an array of Segment objects."""
    self = klass()
    for a in array: assert(isinstance(a, Segment))
    self.activeRepresentation = SegmentRepresentation(self,array)
    return self

  @classmethod
  def fromFonttoolsGlyph(klass, glyph, glyphset):
    """Returns an *array of BezierPaths* from a FontTools glyph object.
    You must also provide the glyphset object to allow glyph decomposition."""

    from fontTools.pens.recordingPen import  DecomposingRecordingPen
    pen = DecomposingRecordingPen(glyphset)
    glyph.draw(pen)
    paths = []
    path = BezierPath()
    path.closed = False
    nodeList = []
    for seg in pen.value:
      if seg[0] == "moveTo":
        point = seg[1][0]
        nodeList = [Node(point[0],point[1],"move")]
      if seg[0] == "curveTo":
        p2,p3,p4 = seg[1]
        nodeList.append(Node(p2[0],p2[1],"offcurve"))
        nodeList.append(Node(p3[0],p3[1],"offcurve"))
        nodeList.append(Node(p4[0],p4[1],"curve"))
      if seg[0] == "lineTo":
        p2 = seg[1][0]
        nodeList.append(Node(p2[0],p2[1],"line"))
      if seg[0] == "closePath":
        path.closed = True
        ## Finish path
        path.activeRepresentation = NodelistRepresentation(path, nodeList)
        paths.append(path)
        path = BezierPath()
    return paths

  def asSegments(self):
    """Return the path as an array of segments (either Line, CubicBezier,
    or, if you are exceptionally unlucky, QuadraticBezier objects)."""
    if not isinstance(self.activeRepresentation, SegmentRepresentation):
      nl = self.activeRepresentation.toNodelist()
      assert isinstance(nl, list)
      self.activeRepresentation = SegmentRepresentation.fromNodelist(self,nl)
    return self.activeRepresentation.data()

  def asNodelist(self):
    """Return the path as an array of Node objects."""
    if not isinstance(self.activeRepresentation, NodelistRepresentation):
      nl = self.activeRepresentation.toNodelist()
      assert isinstance(nl, list)
      self.activeRepresentation = NodelistRepresentation(self,nl)
    return self.activeRepresentation.data()

  def asMatplot(self):
    from matplotlib.path import Path
    nl = self.asNodelist()
    verts = [(nl[0].x,nl[0].y)]
    codes = [Path.MOVETO]

    for n in nl[1::]:
      verts.append((n.x,n.y))
      if n.type == "offcurve" or n.type == "curve":
        codes.append(Path.CURVE4)
      elif n.type == "line":
        codes.append(Path.LINETO)
      else:
        raise "Unknown node type"
    if self.closed:
      verts.append((nl[0].x,nl[0].y))
      codes.append(Path.CLOSEPOLY)
    return Path(verts, codes)

  def plot(self,ax, **kwargs):
    """Plot the path on a Matplot subplot which you supply

    ::

          import matplotlib.pyplot as plt
          fig, ax = plt.subplots()
          path.plot(ax)

    """
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.path import Path
    import matplotlib.patches as patches
    path = self.asMatplot()
    if not "lw" in kwargs:
      kwargs["lw"] = 2
    patch = patches.PathPatch(path, fill = False, **kwargs)
    ax.add_patch(patch)
    (bl,tr) = self.bounds()
    bl = bl - Point(50,50)
    tr = tr + Point(50,50)
    ax.set_xlim(bl.x,tr.x)
    ax.set_ylim(bl.y,tr.y)
    if not("drawNodes" in kwargs) or kwargs["drawNodes"] != False:
      nl = self.asNodelist()
      for i in range(0,len(nl)):
        n = nl[i]
        if n.type =="offcurve":
          circle = plt.Circle((n.x, n.y), 1, fill=False)
          ax.add_artist(circle)
          if i+1 < len(nl) and nl[i+1].type != "offcurve":
            l = Line2D([n.x, nl[i+1].x], [n.y, nl[i+1].y])
            ax.add_artist(l)
          if i-0 >= 0 and nl[i-1].type != "offcurve":
            l = Line2D([n.x, nl[i-1].x], [n.y, nl[i-1].y])
            ax.add_artist(l)
        else:
          circle = plt.Circle((n.x, n.y), 2)
          ax.add_artist(circle)

  def bounds(self):
    """Determine the bounding box of the path, returned as two Point
    objects representing the lower left and upper right corners."""
    segs = self.asSegments()
    bl = segs[0][0].clone()
    tr = segs[0][0].clone()
    for seg in segs:
      t = 0.0
      while t <= 1.0:
        pt = seg.pointAtTime(t)
        if pt.x < bl.x: bl.x = pt.x
        if pt.y < bl.y: bl.y = pt.y
        if pt.x > tr.x: tr.x = pt.x
        if pt.y > tr.y: tr.y = pt.y
        t += 0.1
    return (bl,tr)

  def addExtremes(self):
    """Add extreme points to the path."""
    segs = self.asSegments()
    newsegs = []
    for seg in segs:
      count = 0
      while True:
        ex_t = seg.findExtremes()
        count = count + 1
        if len(ex_t) == 0 or count > 5:
          newsegs.append(seg)
          break
        seg1,seg2 = seg.splitAtTime(ex_t[0])
        newsegs.append(seg1)
        seg = seg2
    self.activeRepresentation = SegmentRepresentation(self,newsegs)

  @property
  def length(self):
    """Returns the length of the whole path."""
    segs = self.asSegments()
    length = 0
    for s in segs: length += s.length
    return length

  def pointAtTime(self,t):
    """Returns the point at time t (0->1) along the curve, where 1 is the end of the whole curve."""
    segs = self.asSegments()
    t *= len(segs)
    seg = segs[int(math.floor(t))]
    return seg.pointAtTime(t-math.floor(t))

  def lengthAtTime(self,t):
    """Returns the length of the subset of the path from the start
    up to the point t (0->1), where 1 is the end of the whole curve."""
    segs = self.asSegments()
    t *= len(segs)
    length = 0
    for s in segs[:int(math.floor(t))]: length += s.length
    seg = segs[int(math.floor(t))]
    s1,s2 = seg.splitAtTime(t-math.floor(t))
    length += s1.length
    return length

  def offset(self, vector, rotateVector = True):
    """Returns a new BezierPath which approximates offsetting the
    current Bezier path by the given vector. Note that the vector
    will be rotated around the normal of the curve so that the
    offsetting always happens on the same 'side' of the curve:

..  figure:: offset1.png
    :scale: 75 %
    :alt: offset1

    If you don't want that and you want 'straight' offsetting instead
    (which may intersect with the original curve), pass
    `rotateVector=False`:

..  figure:: offset2.png
    :scale: 75 %
    :alt: offset1

    """
    # Method 1 - curve fit
    newsegs = []
    for seg in self.asSegments():
      if isinstance(seg, Line):
        newsegs.append(Line(seg.start + vector, seg.end+vector))
      elif isinstance(seg, CubicBezier):
        t = 0.0
        points = []
        while t <1.0:
          if rotateVector:
            points.append( seg.pointAtTime(t) + vector.rotated(Point(0,0), seg.normalAtTime(t).angle))
          else:
            points.append( seg.pointAtTime(t) + vector)
          t = t + 0.01
        # points = [ p + vector for p in seg.sample(seg.length) ]
        bp = BezierPath.fromPoints(points, error=1, cornerTolerance= 1)
        for seg2 in bp.asSegments(): newsegs.append(seg2)
    newbp = BezierPath()
    newbp.activeRepresentation = SegmentRepresentation(newbp, newsegs)
    newbp.closed = self.closed
    return newbp

  def append(self, other):
    """Append another path to this one. If the end point of the first
    path is not the same as the start point of the other path, a line
    will be drawn between them."""
    segs1 = self.asSegments()
    segs2 = other.asSegments()
    # Add a line between if they don't match up
    if segs1[-1].end != segs2[0].start:
      segs1.append(Line(segs1[-1].end,segs2[0].start))
    segs1.extend(segs2)
    self.activeRepresentation = SegmentRepresentation(self, segs1)

  def reverse(self):
    """Reverse this path (mutates path)."""
    seg2 = [ x.reversed() for x in self.asSegments()]
    self.activeRepresentation = SegmentRepresentation(self, list(reversed(seg2)))

  def translate(self, vector):
    """Translates the path by a given vector."""
    seg2 = [ x.translate(vector) for x in self.asSegments()]
    self.activeRepresentation = SegmentRepresentation(self, seg2)

  def rotate(self, about, angle):
    """Rotate the path by a given vector."""
    seg2 = [ x.rotate(about, angle) for x in self.asSegments()]
    self.activeRepresentation = SegmentRepresentation(self, seg2)

  def balance(self):
    """Performs Tunni balancing on the path."""
    segs = self.asSegments()
    for x in segs:
      if isinstance(x, CubicBezier): x.balance()
    self.activeRepresentation = SegmentRepresentation(self, segs)