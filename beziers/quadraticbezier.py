from beziers.segment import Segment
from beziers.line import Line
from beziers.point import Point

class QuadraticBezier(Segment):
  def __init__(self, start, c1,end):
    self.points = [start,c1,end]

  def __repr__(self):
    return "B<%s-%s-%s>" % (self[0],self[1],self[2])

  def pointAtTime(self,t):
    """Returns the point at time t (0->1) along the curve."""
    x = (1 - t) * (1 - t) * self[0].x + 2 * (1 - t) * t * self[1].x + t * t * self[2].x;
    y = (1 - t) * (1 - t) * self[0].y + 2 * (1 - t) * t * self[1].y + t * t * self[2].y;
    return Point(x,y)

  def derivative(self):
    """Returns a `Line` representing the derivative of this curve."""
    return Line(
      (self[1]-self[0])*2,
      (self[2]-self[1])*2
    )

  def _findRoots(self):
    # Thanks to Mathematica for
    # Solve[D[(1 - t) (1 - t) a + (1 - t) t *b + t*t*c, t] == 0, t]
    r1 = (2*self[0].x-self[1].x)/(2*(self[0].x-self[1].x+self[2].x))
    r2 = (2*self[0].y-self[1].y)/(2*(self[0].y-self[1].y+self[2].y))
    roots = [r1,r2]
    return [ r for r in roots if r >= 0.01 and r <= 0.99 ]

  def findExtremes(self):
    """Returns a list of time `t` values for extremes of the curve."""
    return self._findRoots()
