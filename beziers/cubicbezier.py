from beziers.segment import Segment
from beziers.line import Line
from beziers.point import Point
from beziers.quadraticbezier import QuadraticBezier
import math
from beziers.utils.legendregauss import Tvalues, Cvalues

class CubicBezier(Segment):
  def __init__(self, start, c1,c2,end):
    self.points = [start,c1,c2,end]


  def __repr__(self):
    return "B<%s-%s-%s-%s>" % (self[0],self[1],self[2],self[3])

  def pointAtTime(self,t):
    """Returns the point at time t (0->1) along the curve."""
    x = (1 - t) * (1 - t) * (1 - t) * self[0].x + 3 * (1 - t) * (1 - t) * t * self[1].x + 3 * (1 - t) * t * t * self[2].x + t * t * t * self[3].x;
    y = (1 - t) * (1 - t) * (1 - t) * self[0].y + 3 * (1 - t) * (1 - t) * t * self[1].y + 3 * (1 - t) * t * t * self[2].y + t * t * t * self[3].y;
    return Point(x,y)

  @property
  def length(self):
    """Returns the length of the cubic Bezier using the Legendre-Gauss approximation."""
    d = self.derivative()
    z = 0.5
    _sum = 0
    for i in range(0,len(Tvalues)):
      t = z * Tvalues[i] + z
      p = d.pointAtTime(t)
      arc = math.sqrt(p.x * p.x + p.y * p.y)
      _sum += Cvalues[i] * arc
    return _sum * z

  def splitAtTime(self,t):
    """Returns two segments, dividing the given segment at a point t (0->1) along the curve."""
    t = 1-t
    p4 = self[0].lerp(self[1],t)
    p5 = self[1].lerp(self[2],t)
    p6 = self[2].lerp(self[3],t)
    p7 = p4.lerp(p5,t)
    p8 = p5.lerp(p6,t)
    p9 = p7.lerp(p8,t)
    return (CubicBezier(self[0],p4,p7,p9), CubicBezier(p9,p8,p6,self[3]))

  def join(self,other):
    """Not currently implemented: join two `CubicBezier` together."""
    raise "Not implemented"

  def toQuadratic(self):
    """Not currently implemented: reduce this to a `QuadraticBezier`."""
    raise "Not implemented"

  def derivative(self):
    """Returns a `QuadraticBezier` representing the derivative of this curve."""
    return QuadraticBezier(
      (self[1]-self[0])*3,
      (self[2]-self[1])*3,
      (self[3]-self[2])*3
    )

  def tangentAtTime(self,t):
    """Returns a `Point` representing the unit vector of tangent at time `t`."""
    return self.derivative().pointAtTime(t).toUnitVector()

  def normalAtTime(self,t):
    """Returns a `Point` representing the normal (rotated tangent) at time `t`."""
    tan = self.tangentAtTime(t)
    return Point(-tan.y,tan.x)

  def _findRoots(self):
    d = self.derivative()
    roots = []

    # We have f(t) = w1 (1-t)^2 + 2 w2 (1-t) t + w3 t^2
    # We want f(t) = a t^2 + b^t + c to solve with the quadratic formula
    w1,w2,w3 = d[0].x,d[1].x,d[2].x
    a,b,c = w1 - 2*w2 + w3, 2 * (w2-w1), w1
    if a != 0.0 and b*b-4*a*c > 0.0:
      t1 = (-b + math.sqrt(b*b-4*a*c)) / (2*a)
      if t1 >= 0.0 and t1 <= 1.0:
        roots.append(t1)
      t2 = (-b - math.sqrt(b*b-4*a*c)) / (2*a)
      if t2 >= 0.0 and t2 <= 1.0:
        roots.append(t2)
    w1,w2,w3 = d[0].y,d[1].y,d[2].y
    a,b,c = w1 - 2*w2 + w3, 2 * (w2-w1), w1
    if a != 0.0 and b*b-4*a*c > 0.0:
      t1 = (-b + math.sqrt(b*b-4*a*c)) / (2*a)
      if t1 >= 0.0 and t1 <= 1.0:
        roots.append(t1)
      t2 = (-b - math.sqrt(b*b-4*a*c)) / (2*a)
      if t2 >= 0.0 and t2 <= 1.0:
        roots.append(t2)

    return roots

  def findExtremes(self):
    """Returns a list of time `t` values for extremes of the curve."""
    r = self._findRoots()
    r.sort()
    return [ root for root in r if root >= 0.01 and root <= 0.99 ]

  def curvatureAtTime(self,t):
    """Returns the C curvature at time `t`.."""
    d = self.derivative()
    d2 = d.derivative()
    return d.pointAtTime(t).x * d2.pointAtTime(t).y - d.pointAtTime(t).y * d2.pointAtTime(t).x

  @property
  def tunniPoint(self):
    """Returns the Tunni point of this Bezier (the intersection of
    the handles)."""
    h1 = Line(self[0], self[1])
    h2 = Line(self[2], self[3])
    i = h1.intersection(h2)
    if i.distanceFrom(self[0]) > 5 * self.length:
      return
    else:
      return i

  def balance(self):
    """Perform Tunni balancing on this Bezier."""
    p = self.tunniPoint
    if not p: return
    fraction1 = self[0].distanceFrom(self[1]) / self[0].distanceFrom(p)
    fraction2 = self[3].distanceFrom(self[2]) / self[3].distanceFrom(p)
    avg = (fraction2 + fraction1) / 2.0
    self[1] = self[0].lerp(p, avg)
    self[2] = self[3].lerp(p, avg)
