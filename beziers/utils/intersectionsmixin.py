import sys
from beziers.point import Point

class IntersectionsMixin:
  # This isn't something we mix into different classes but I'm
  # just putting it here to keep the code tidy.

  def intersections(self, other):
    """Returns an array of `Point` objects representing the intersections
    between this Segment and another Segment."""
    # Arrange by degree
    if len(other.points) > len(self.points): self,other = other,self
    if len(self.points) == 4 or len(self.points)==3:
      if len(other.points) == 4 or len(self.points)==3:
        return self._curve_curve_intersections(other)
      if len(other.points) == 2:
        return self._curve_line_intersections(other)
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

  def _curve_line_intersections_t(self,line):
    t = line.alignmentTransformation()
    l1 = line.aligned()
    c1 = self.transformed(t)
    intersections = c1._findRoots("x")
    intersections.extend(c1._findRoots("y"))
    return sorted(intersections)

  def _curve_line_intersections(self,line):
    return [self.pointAtTime(t) for t in self._curve_line_intersections_t(line)]

  def _curve_curve_intersections_t(self,other, precision=1e-6):
    if not (self.bounds().overlaps(other.bounds())): return []
    if self.bounds().area < precision and other.bounds().area < precision:
      return [ [
      0.5*(self._range[0] + self._range[1]),
      0.5*(other._range[0] + other._range[1]),
     ] ]
    def xmap(v,ts,te): return ts+(te-ts)*v
    c11, c12 = self.splitAtTime(0.5)
    c11._range = [ self._range[0], xmap(0.5,self._range[0],self._range[1])]
    c12._range = [ xmap(0.5,self._range[0],self._range[1]), self._range[1]]
    c21, c22 = other.splitAtTime(0.5)
    c21._range = [ other._range[0], xmap(0.5,other._range[0],other._range[1])]
    c22._range = [xmap(0.5,other._range[0],other._range[1]), other._range[1]]
    assert(c11._range[0] < c11._range[1])
    assert(c12._range[0] < c12._range[1])
    assert(c21._range[0] < c21._range[1])
    assert(c22._range[0] < c22._range[1])

    found = []
    for this in [c11,c12]:
      for that in [c21,c22]:
        if this.bounds().overlaps(that.bounds()):
          found.extend(this._curve_curve_intersections_t(that, precision))
    seen = {}
    def filterSeen(n):
      key = '%.5f' % n[0]
      if key in seen: return False
      seen[key] = 1
      return True
    found = filter(filterSeen, found)
    return found

  def _curve_curve_intersections(self,other):
    return [self.pointAtTime(t[0]) for t in self._curve_curve_intersections_t(other)]
