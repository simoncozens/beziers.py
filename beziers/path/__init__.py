from beziers.path.representations.Segment import SegmentRepresentation
from beziers.path.representations.Nodelist import NodelistRepresentation
from beziers.point import Point

class BezierPath(object):
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
  a list of segments instead:

    [ (255.0,20.0), (385.0,20.0), (526.0,79.0), (566.0,135.0)],
    [ (566.0,135.0), (585.0,162.0), (566.0,260.0), (484.0,281.0)],

  The Beziers module is designed to allow you to move fluidly between these
  different representations depending on what you're wanting to do.

  """

  def __init__(self):
    self.activeRepresentation = None
    self.closed = True

  def fromSegments(array):
    # XXX sanity check here
    self.activeRepresentation = SegmentRepresentation(self,array)

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

  def plot(self,ax):
    """Plot the path on a Matplot subplot which you supply."""
    import matplotlib.pyplot as plt
    from matplotlib.path import Path
    import matplotlib.patches as patches
    path = self.asMatplot()
    patch = patches.PathPatch(path, lw=2, fill = False)
    ax.add_patch(patch)
    (bl,tr) = self.bounds()
    bl = bl - Point(50,50)
    tr = tr + Point(50,50)
    ax.set_xlim(bl.x,tr.x)
    ax.set_ylim(bl.y,tr.y)
    for n in self.asNodelist():
      if n.type =="offcurve":
        circle = plt.Circle((n.x, n.y), 1, fill=False)
        ax.add_artist(circle)
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
