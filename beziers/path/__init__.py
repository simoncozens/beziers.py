from beziers.path.representations.Segment import SegmentRepresentation
from beziers.path.representations.Nodelist import NodelistRepresentation, Node
from beziers.point import Point
from beziers.boundingbox import BoundingBox
from beziers.utils.samplemixin import SampleMixin
from beziers.utils.booleanoperationsmixin import BooleanOperationsMixin
from beziers.segment import Segment
from beziers.line import Line
from beziers.cubicbezier import CubicBezier

import math

class BezierPath(BooleanOperationsMixin,SampleMixin,object):
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
  def fromNodelist(klass, array, closed=True):
    """Construct a path from an array of Node objects."""
    self = klass()
    for a in array: assert(isinstance(a, Node))
    self.closed = closed
    self.activeRepresentation = NodelistRepresentation(self,array)
    self.asSegments() # Resolves a few problems
    return self

  @classmethod
  def fromFonttoolsGlyph(klass,font,glyphname):
    """Returns an *array of BezierPaths* from a FontTools font object and glyph name."""
    glyphset = font.getGlyphSet()
    glyfTable = font["glyf"]
    glyph = glyfTable[glyphname]

    from fontTools.pens.basePen import BasePen
    class MyPen(BasePen):
      def __init__(self, glyphSet=None):
        super(MyPen, self).__init__(glyphSet)
        self.paths = []
        self.path = BezierPath()
        self.nodeList = []
      def _moveTo(self, p):
        self.nodeList = [Node(p[0], p[1], "move")]
      def _lineTo(self, p):
        self.nodeList.append(Node(p[0], p[1], "line"))
      def _curveToOne(self, p1, p2, p3):
        self.nodeList.append(Node(p1[0], p1[1], "offcurve"))
        self.nodeList.append(Node(p2[0], p2[1], "offcurve"))
        self.nodeList.append(Node(p3[0], p3[1], "curve"))
      def _qCurveToOne(self, p1, p2):
        self.nodeList.append(Node(p1[0], p1[1], "offcurve"))
        self.nodeList.append(Node(p2[0], p2[1], "curve"))
      def _closePath(self):
        self.path.closed = True
        self.path.activeRepresentation = NodelistRepresentation(self.path, self.nodeList)
        self.paths.append(self.path)
        self.path = BezierPath()
    pen = MyPen(glyphset)
    glyph.draw(pen, glyfTable)
    return pen.paths

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

    for i in range(1,len(nl)):
      n = nl[i]
      verts.append((n.x,n.y))
      if n.type == "offcurve":
        if nl[i+1].type == "offcurve" or nl[i-1].type == "offcurve":
          codes.append(Path.CURVE4)
        else:
          codes.append(Path.CURVE3)
      elif n.type == "curve":
        if nl[i-1].type == "offcurve" and i >2 and nl[i-2].type == "offcurve":
          codes.append(Path.CURVE4)
        else:
          codes.append(Path.CURVE3)
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
    if not "fill" in kwargs:
      kwargs["fill"] = False
    drawNodes = (not("drawNodes" in kwargs) or kwargs["drawNodes"] != False)
    if "drawNodes" in kwargs:
      kwargs.pop("drawNodes")
    patch = patches.PathPatch(path, **kwargs)
    ax.add_patch(patch)
    left, right = ax.get_xlim()
    top, bottom = ax.get_ylim()
    bounds = self.bounds()
    bounds.addMargin(50)
    if not (left == 0.0 and right == 1.0 and top == 0.0 and bottom == 1.0):
      bounds.extend(Point(left,top))
      bounds.extend(Point(right,bottom))
    ax.set_xlim(bounds.left,bounds.right)
    ax.set_ylim(bounds.bottom,bounds.top)
    if drawNodes:
      nl = self.asNodelist()
      for i in range(0,len(nl)):
        n = nl[i]
        if n.type =="offcurve":
          circle = plt.Circle((n.x, n.y), 2, fill=True,color="black",alpha=0.5)
          ax.add_artist(circle)
          if i+1 < len(nl) and nl[i+1].type != "offcurve":
            l = Line2D([n.x, nl[i+1].x], [n.y, nl[i+1].y], linewidth=2,color="black",alpha=0.3)
            ax.add_artist(l)
          if i-0 >= 0 and nl[i-1].type != "offcurve":
            l = Line2D([n.x, nl[i-1].x], [n.y, nl[i-1].y], linewidth=2,color="black",alpha=0.3)
            ax.add_artist(l)
        else:
          circle = plt.Circle((n.x, n.y), 3,color="black",alpha=0.3)
          ax.add_artist(circle)

  def clone(self):
    """Return a new path which is an exact copy of this one"""
    p = BezierPath.fromSegments(self.asSegments())
    p.closed = self.closed
    return p

  def round(self):
    """Rounds the points of this path to integer coordinates."""
    segs = self.asSegments()
    for s in segs: s.round()
    self.activeRepresentation = SegmentRepresentation(self,segs)

  def bounds(self):
    """Determine the bounding box of the path, returned as a
    `BoundingBox` object."""
    bbox = BoundingBox()
    for seg in self.asSegments():
      bbox.extend(seg)
    return bbox

  def splitAtPoints(self,splitlist):
    def mapx(v,ds): return (v-ds)/(1-ds)
    segs = self.asSegments()
    newsegs = []
    # Cluster splitlist by seg
    newsplitlist = {}
    for (seg,t) in splitlist:
      if not seg in newsplitlist: newsplitlist[seg] = []
      newsplitlist[seg].append(t)
    for k in newsplitlist:
      newsplitlist[k] = sorted(newsplitlist[k])
    # Now walk the path
    for seg in segs:
      if seg in newsplitlist:
        tList = newsplitlist[seg]
        while len(tList) > 0:
          t = tList.pop(0)
          if t < 1e-8: continue
          seg1,seg2 = seg.splitAtTime(t)
          newsegs.append(seg1)
          seg = seg2
          for i in range(0,len(tList)): tList[i] = mapx(tList[i],t)
      newsegs.append(seg)
    self.activeRepresentation = SegmentRepresentation(self,newsegs)


  def addExtremes(self):
    """Add extreme points to the path."""
    def mapx(v,ds): return (v-ds)/(1-ds)
    segs = self.asSegments()
    splitlist = []
    for seg in segs:
      for t in seg.findExtremes():
        splitlist.append((seg,t))
    self.splitAtPoints(splitlist)

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
    if t == 1.0:
      return segs[-1].pointAtTime(1)
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
    points = []
    def finishPoints(newsegs, points):
      if len(points) > 0:
        bp = BezierPath.fromPoints(points, error=0.1, cornerTolerance= 1)
        newsegs.extend(bp.asSegments())
      while len(points)>0:points.pop()

    for seg in self.asSegments():
      if isinstance(seg,Line):
        finishPoints(newsegs,points)
        newsegs.append(seg.translated(vector))
      else:
        t = 0.0
        while t <1.0:
          if rotateVector:
            points.append( seg.pointAtTime(t) + vector.rotated(Point(0,0), seg.normalAtTime(t).angle))
          else:
            points.append( seg.pointAtTime(t) + vector)
          step = max(abs(seg.curvatureAtTime(t)),0.1)
          t = t + min(seg.length / step,0.1)
    finishPoints(newsegs,points)
    newpath = BezierPath()
    newpath.activeRepresentation = SegmentRepresentation(newpath, newsegs)
    return newpath

  def append(self, other, joinType="line"):
    """Append another path to this one. If the end point of the first
    path is not the same as the start point of the other path, a line
    will be drawn between them."""
    segs1 = self.asSegments()
    segs2 = other.asSegments()
    if len(segs1) < 1:
      self.activeRepresentation = SegmentRepresentation(self, segs2)
      return
    if len(segs2) < 1:
      self.activeRepresentation = SegmentRepresentation(self, segs1)
      return

    # Which way around should they go?
    dist1 = segs1[-1].end.distanceFrom(segs2[0].start)
    dist2 = segs1[-1].end.distanceFrom(segs2[-1].end)
    if dist2 > 2 * dist1:
      segs2 = list(reversed([ x.reversed() for x in segs2]))

    # Add a line between if they don't match up
    if segs1[-1].end != segs2[0].start:
      segs1.append(Line(segs1[-1].end,segs2[0].start))

    # XXX Check for discontinuities and harmonize if needed

    segs1.extend(segs2)
    self.activeRepresentation = SegmentRepresentation(self, segs1)
    return self

  def reverse(self):
    """Reverse this path (mutates path)."""
    seg2 = [ x.reversed() for x in self.asSegments()]
    self.activeRepresentation = SegmentRepresentation(self, list(reversed(seg2)))
    return self

  def translate(self, vector):
    """Translates the path by a given vector."""
    seg2 = [ x.translated(vector) for x in self.asSegments()]
    self.activeRepresentation = SegmentRepresentation(self, seg2)
    return self

  def rotate(self, about, angle):
    """Rotate the path by a given vector."""
    seg2 = [ x.rotated(about, angle) for x in self.asSegments()]
    self.activeRepresentation = SegmentRepresentation(self, seg2)
    return self

  def scale(self, by):
    """Scales the path by a given magnitude."""
    seg2 = [ x.scaled(by) for x in self.asSegments()]
    self.activeRepresentation = SegmentRepresentation(self, seg2)
    return self

  def balance(self):
    """Performs Tunni balancing on the path."""
    segs = self.asSegments()
    for x in segs:
      if isinstance(x, CubicBezier): x.balance()
    self.activeRepresentation = SegmentRepresentation(self, segs)
    return self

  def findDiscontinuities(self):
    """Not implemented yet"""

  def harmonize(self):
    """Not implemented yet"""

  def roundCorners(self):
    """Not implemented yet"""

  def dash(self, lineLength = 50, gapLength = None):
    """Returns a list of BezierPath objects created by chopping
    this path into a dashed line::

      paths = path.dash(lineLength = 20, gapLength = 50)

..  figure:: dash.png
    :scale: 75 %
    :alt: path.dash(lineLength = 20, gapLength = 50)

"""
    if not gapLength:
      gapLength = lineLength
    granularity = self.length
    newpaths = []
    points = []
    for t in self.regularSampleTValue(granularity):
      lenSoFar = self.lengthAtTime(t) # Super inefficient. But simple!
      lenSoFar = lenSoFar % (lineLength + gapLength)
      if lenSoFar >= lineLength and len(points) > 0:
        # When all you have is a hammer...
        bp = BezierPath.fromPoints(points, error=1, cornerTolerance= 1)
        points = []
        if len(bp.asSegments()) > 0: newpaths.append(bp)
      elif lenSoFar <= lineLength:
        points.append(self.pointAtTime(t))
    return newpaths

  def segpairs(self):
    segs = self.asSegments()
    for i in range(0,len(segs)-1):
      yield (segs[i],segs[i+1])

  def harmonize(self, seg1, seg2):
    if seg1.end.x != seg2.start.x or seg1.end.y != seg2.start.y: return
    a1, a2 = seg1[1], seg1[2]
    b1, b2 = seg2[1], seg2[2]
    intersections = Line(a1,a2).intersections(Line(b1,b2),limited=False)
    if not intersections[0]: return
    p0 = a1.distanceFrom(a2) / a2.distanceFrom(intersections[0].point)
    p1 = b1.distanceFrom(intersections[0].point) / b1.distanceFrom(b2)
    r = math.sqrt(p0 * p1)
    t = r / (r+1)
    newA3 = a2.lerp(b1, t)
    fixup = seg2.start - newA3
    seg1[2] += fixup
    seg2[1] += fixup

  def flatten(self,degree=8):
    segs = []
    for s in self.asSegments():
      segs.extend(s.flatten(degree))
    return BezierPath.fromSegments(segs)

  def windingNumberOfPoint(self,pt):
    bounds = self.bounds()
    bounds.addMargin(10)
    ray1 = Line(Point(bounds.left,pt.y),pt)
    ray2 = Line(Point(bounds.right,pt.y),pt)
    leftIntersections = {}
    rightIntersections = {}
    leftWinding = 0
    rightWinding = 0
    for s in self.asSegments():
      for i in s.intersections(ray1):
        # print("Found left intersection with %s: %s" % (ray1, i.point))
        leftIntersections[i.point] = i

      for i in s.intersections(ray2):
        rightIntersections[i.point] = i

    for i in leftIntersections.values():
      # XXX tangents here are all positive? Really?
      # print(i.seg1, i.t1, i.point)
      tangent = s.tangentAtTime(i.t1)
      # print("Tangent at left intersection %s is %f" % (i.point,tangent.y))
      leftWinding += int(math.copysign(1,tangent.y))

    for i in rightIntersections.values():
      tangent = s.tangentAtTime(i.t1)
      # print("Tangent at right intersection %s is %f" % (i.point,tangent.y))
      rightWinding += int(math.copysign(1,tangent.y))

    # print("Left winding: %i right winding: %i " % (leftWinding,rightWinding))
    return max(abs(leftWinding),abs(rightWinding))

  def pointIsInside(self,pt):
    """Returns true if the given point lies on the "inside" of the path,
    assuming an 'even-odd' winding rule where self-intersections are considered
    outside."""
    li = self.windingNumberOfPoint(pt)
    return li % 2 == 1

  @property
  def area(self):
    """Approximates the area under a closed path by flattening and treating as a polygon."""
    flat = self.flatten()
    area = 0
    for s in flat.asSegments():
      area = area + (s.start.x+s.end.x) * (s.end.y - s.start.y)
    area = area / 2.0
    return abs(area)

  @property
  def centroid(self):
    if not self.closed: return None
    return self.bounds().centroid # Really?

  def drawWithBrush(self, other, pathSmoothness = 50, brushSmoothness = 20, alpha = 0.15):
    """Assuming that `other` is a closed Bezier path representing a pen or
    brush of a certain shape and that `self` is an open path, this method
    traces the brush along the path, returning an array of Bezier paths.

    `other` may also be a function which, given a time `t` (0-1), returns a closed
    path representing the shape of the brush at the given time.

    This requires the `shapely` and `scipy` libraries to be installed, and is very,
    very slow.
    """

    samples = self.sample(int(self.length*(pathSmoothness/100.0)))
    self.closed = False

    def constantBrush(t):
      return other

    brush = other
    if not callable(brush):
      brush = constantBrush

    c = brush(0).centroid

    points = []
    from shapely.geometry import Point as ShapelyPoint

    t = 0
    for n in samples:
      brushHere = brush(t).clone()
      brushHere.translate(n-brushHere.centroid)
      brushsamples = brushHere.sample(int(brushHere.length*(brushSmoothness/100.0)))
      points.extend( [ ShapelyPoint(s.x, s.y) for s in brushsamples] )
      t = t + 1.0/len(samples)

    from beziers.utils.alphashape import alpha_shape
    concave_hull, edge_points = alpha_shape(points,
                                        alpha=alpha)
    points = [ Point(p[0],p[1]) for p in concave_hull.exterior.coords ]
    path = BezierPath.fromPoints(points,error=5,maxSegments=100)
    return path
