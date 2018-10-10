from beziers.segment import Segment
from beziers.point import Point

import math
import sys

class Line(Segment):
  """Represents a line segment within a Bezier path."""
  def __init__(self, start, end):
    self.points = [start,end]

  def __repr__(self):
    return "L<%s--%s>" % (self.points[0], self.points[1])

  def pointAtTime(self,t):
    """Returns the point at time t (0->1) along the line."""
    return self.start.lerp(self.end, t)

  def splitAtTime(self,t):
    """Returns two segments, dividing the given segment at a point t (0->1) along the line."""
    return (Line(self.start, self.pointAtTime(t)), Line(self.pointAtTime(t), self.end))

  def bothPointsAreOnSameSideOfOrigin(self, a,b,c):
    xDiff = (a.x-c.x) * (b.x-c.x)
    yDiff = (a.y-c.y) * (b.y-c.y)
    return not (xDiff <= 0.0 and yDiff <= 0.0)

  @property
  def slope(self):
    v = self[1]-self[0]
    return v.y / v.x

  @property
  def intercept(self):
    return self[1].y - self.slope * self[1].x

  @property
  def length(self):
    return self[0].distanceFrom(self[1])

  def intersection(self,other):
    a = self.start
    b = self.end
    c = other.start
    d = other.end
    if abs(b.x - a.x) < sys.float_info.epsilon:
      x = a.x
      slope34 = ( d.y - c.y) / ( d.x - c.x )
      y = slope34 * ( x - c.x ) + c.y
      return Point(x, y)
    if abs(d.x - c.x) < sys.float_info.epsilon:
      x = c.x
      slope12 = ( b.y - a.y) / ( b.x - a.x )
      y = slope12 * ( x - a.x ) + a.y
      return Point(x, y)

    slope12 = ( b.y - a.y) / ( b.x - a.x )
    slope34 = ( d.y - c.y) / ( d.x - c.x )
    if abs(slope12 - slope34) < sys.float_info.epsilon: return
    x = ( slope12 * a.x - a.y - slope34 * c.x + c.y ) / ( slope12 - slope34 )
    y = slope12 * ( x - a.x ) + a.y
    intersection = Point(x,y)
    if self.bothPointsAreOnSameSideOfOrigin(intersection, b, a) and self.bothPointsAreOnSameSideOfOrigin(intersection, c, d):
      return intersection
    return nil

  def findExtremes(self):
    return []
