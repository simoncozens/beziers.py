from beziers.point import Point
from beziers.utils.samplemixin import SampleMixin

class Segment(SampleMixin,object):

  """A segment is part of a path. Although this package is called
  `beziers.py`, it's really for font people, and paths in the font
  world are made up of cubic Bezier curves, lines and (if you're
  dealing with TrueType) quadratic Bezier curves. Each of these
  things is represented as an object derived from the Segment base
  class. So, when you inspect the path in the segment representation,
  you will get a list of CubicBezier, Line and QuadraticBezier objects,
  all of which derive from Segment.

  Because of this, a Segment can have two, three or four elements:
  lines have two end points; quadratic Beziers have a start, a control
  point and an end point; cubic have a start, two control points and
  an end point.

  You can pretend that a Segment object is an array and index it like
  one::

      q = CubicBezier(
        Point(122,102), Point(35,200), Point(228,145), Point(190,46)
      )

      start, cp1, cp2, end = q[0],q[1],q[2],q[3]

  You can also access the start and end points like so::

      start = q.start
      end = q.end

  """

  def __getitem__(self, item):
    return self.points[item]
  def __setitem__(self, key, item):
      self.points[key] = item
  def __len__(self):
    return len(self.points)

  @property
  def start(self):
    """Returns a Point object representing the start of this segment."""
    return self.points[0]

  @property
  def end(self):
    """Returns a Point object representing the end of this segment."""
    return self.points[-1]

  def translate(self,vector):
    """Returns a *new Segment object* representing the translation of
    this segment by the given vector. i.e.::

      >>> l = Line(Point(0,0), Point(10,10))
      >>> l.translate(Point(5,5))
      L<<5.0,5.0>--<15.0,15.0>>
      >>> l
      L<<0.0,0.0>--<10.0,10.0>>

    """

    klass = self.__class__
    return klass(*[ p+vector for p in self.points ])

  def rotate(self,around, by):
    """Returns a *new Segment object* representing the rotation of
    this segment around the given point and by the given angle. i.e.::

      >>> l = Line(Point(0,0), Point(10,10))
      >>> l.rotate(Point(5,5), math.pi/2)
      L<<10.0,-8.881784197e-16>--<-8.881784197e-16,10.0>>

    """

    klass = self.__class__
    pNew = [ p.clone() for p in self.points]
    for p in pNew: p.rotate(around,by)
    return klass(*pNew)

  def align(self):
    """Returns a *new Segment object* aligned to the origin. i.e.
    with the first point translated to the origin (0,0) and the
    last point with y=0. Obviously, for a `Line` this is a bit pointless,
    but it's quite handy for higher-order curves."""
    t1 = self.translate(self.start * -1)
    t2 = t1.rotate(Point(0,0),t1.end.angle * -1)
    return t2

  def lengthAtTime(self, t):
    """Returns the length of the subset of the path from the start
    up to the point t (0->1), where 1 is the end of the whole curve."""
    s1,_ = self.splitAtTime(t)
    return s1.length

  def reversed(self):
    """Returns a new segment with the points reversed."""
    klass = self.__class__
    return klass(*list(reversed(self.points)))

