from beziers.segment import Segment
from beziers.line import Line
from beziers.point import Point
from beziers.utils import quadraticRoots, isclose

my_epsilon = 2e-7

class QuadraticBezier(Segment):
  def __init__(self, start, c1,end):
    self.points = [start,c1,end]
    self._range = [0,1]

  def __repr__(self):
    return "B<%s-%s-%s>" % (self[0],self[1],self[2])

  def pointAtTime(self,t):
    """Returns the point at time t (0->1) along the curve."""
    x = (1 - t) * (1 - t) * self[0].x + 2 * (1 - t) * t * self[1].x + t * t * self[2].x;
    y = (1 - t) * (1 - t) * self[0].y + 2 * (1 - t) * t * self[1].y + t * t * self[2].y;
    return Point(x,y)

  def tOfPoint(self,p):
    """Returns the time t (0->1) of a point on the curve."""
    xroots = quadraticRoots(self[0].x - 2*self[1].x + self[2].x, 2 * (self[1].x-self[0].x), self[0].x - p.x)
    yroots = quadraticRoots(self[0].y - 2*self[1].y + self[2].y, 2 * (self[1].y-self[0].y), self[0].y - p.y)
    if not len(xroots) or not len(yroots):
      return -1
    for x in xroots:
      for y in yroots:
        if -my_epsilon < x - y < my_epsilon:
          return x
    return -1

  @property
  def length(self):
    """Returns the length of the quadratic bezier"""
    # Direct solution. There may be better ways From: https://math.stackexchange.com/questions/12186/arc-length-of-b%C3%A9zier-curves
    c = (self[1].x - self[0].x) ** 2 + (self[1].y - self[0].y) ** 2
    b = (self[1].x-self[0].x) * (self[2].x - 2*self[1].x + self[0].x) + (self[1].y-self[0].y) * (self[2].y - 2*self[1].y + self[0].y)
    a = (self[2].x - 2*self[1].x + self[0].x) ** 2 + (self[2].y - 2*self[1].y + self[0].y) ** 2
    return (1. + b / a) * sqrt(c + 2*b + a) + ((a*c - b*b)/(a * sqrt(a)))*asinh((a+b)/sqrt(a*c - b*b))

  def splitAtTime(self,t):
    """Returns two segments, dividing the given segment at a point t (0->1) along the curve."""
    p4 = self[0].lerp(self[1],t)
    p5 = self[1].lerp(self[2],t)
    p7 = p4.lerp(p5,t)
    return (QuadraticBezier(self[0],p4,p7), QuadraticBezier(p7,p5,self[2]))

  def derivative(self):
    """Returns a `Line` representing the derivative of this curve."""
    return Line(
      (self[1]-self[0])*2,
      (self[2]-self[1])*2
    )

  def _findRoots(self,dimension):
    if dimension == "x":
      return quadraticRoots(self[0].x - 2*self[1].x + self[2].x, 2 * (self[1].x-self[0].x), self[0].x)
    elif dimension == "y":
      return quadraticRoots(self[0].y - 2*self[1].y + self[2].y, 2 * (self[1].y-self[0].y), self[0].y)
    else:
      raise "Meh"

  def _findDRoots(self):
    roots = []
    d1 = self[0].x-2*self[1].x+self[2].x
    if not isclose(d1, 0.):
        roots.append((self[0].x-self[1].x)/d1)
    d2 = self[0].y-2*self[1].y+self[2].y
    if not isclose(d2, 0.):
        roots.append((self[0].y-self[1].y)/d2)
    return [ r for r in roots if r >= 0.01 and r <= 0.99 ]

  def findExtremes(self):
    """Returns a list of time `t` values for extremes of the curve."""
    return self._findDRoots()

  @property
  def area(self):
    """Returns the signed area between the curve and the y-axis"""
    return (2*(self[1].x*self[0].y - self[0].x*self[1].y - self[1].x*self[2].y + self[2].x*self[1].y) +
            3*(self[2].x*self[2].y - self[0].x*self[0].y) +
               self[2].x*self[0].y - self[0].x*self[2].y) / 6.
