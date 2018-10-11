import sys
from beziers.point import Point

class IntersectionsMixin:
  # This isn't something we mix into different classes but I'm
  # just putting it here to keep the code tidy.

  def intersections(self, other):
    # Arrange by degree
    if len(other.points) > len(self.points): self,other = other,self
    if len(self.points) == 4:
      if len(other.points) == 4:
        return self._cubic_cubic_intersections(other)
      if len(other.points) == 2:
        return self._cubic_line_intersections(other)
    elif len(self.points) == 2 and len(other.points) == 2:
        return self._line_line_intersections(other)
    raise "Don't know how to compute intersections of a %s and a %s" % (type(self), type(other))

  def _bothPointsAreOnSameSideOfOrigin(self, a,b,c):
    xDiff = (a.x-c.x) * (b.x-c.x)
    yDiff = (a.y-c.y) * (b.y-c.y)
    return not (xDiff <= 0.0 and yDiff <= 0.0)

  def _line_line_intersections(self, other):
    a = self.start
    b = self.end
    c = other.start
    d = other.end
    if abs(b.x - a.x) < sys.float_info.epsilon:
      x = a.x
      slope34 = ( d.y - c.y) / ( d.x - c.x )
      y = slope34 * ( x - c.x ) + c.y
      return [ Point(x, y) ]
    if abs(d.x - c.x) < sys.float_info.epsilon:
      x = c.x
      slope12 = ( b.y - a.y) / ( b.x - a.x )
      y = slope12 * ( x - a.x ) + a.y
      return [ Point(x, y) ]

    slope12 = ( b.y - a.y) / ( b.x - a.x )
    slope34 = ( d.y - c.y) / ( d.x - c.x )
    if abs(slope12 - slope34) < sys.float_info.epsilon: return
    x = ( slope12 * a.x - a.y - slope34 * c.x + c.y ) / ( slope12 - slope34 )
    y = slope12 * ( x - a.x ) + a.y
    intersection = Point(x,y)
    if self._bothPointsAreOnSameSideOfOrigin(intersection, b, a) and self._bothPointsAreOnSameSideOfOrigin(intersection, c, d):
      return [ intersection ]
    return []

  def _cubic_line_intersections_t(self,line):
    t = line.alignmentTransformation()
    l1 = line.aligned()
    c1 = self.transformed(t)
    intersections = c1._findRoots("x")
    intersections.extend(c1._findRoots("y"))
    return sorted(intersections)

  def _cubic_line_intersections(self,line):
    return [self.pointAtTime(t) for t in self._cubic_line_intersections_t(line)]
