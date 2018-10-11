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

  def findExtremes(self):
    return []