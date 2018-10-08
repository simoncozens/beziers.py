import math

class Point(object):
  """A representation of a point within the Beziers world."""

  def __init__(self, x,y):
    self.x = float(x)
    self.y = float(y)

  def __repr__(self):
    return "<%s,%s>" % (self.x,self.y)

  def __mul__(self, other):
    """Multiply a point by a scalar."""
    return Point(self.x * other, self.y * other)

  def __truediv__(self, other):
    return Point(self.x / other, self.y / other)

  def __add__(self, other):
    return Point(self.x + other.x, self.y + other.y)

  def __sub__(self, other):
    return Point(self.x - other.x, self.y - other.y)

  def __iadd__(self, other):
    self.x += other.x
    self.y += other.y

  def __isub__(self, other):
    self.x -= other.x
    self.y -= other.y

  def __matmul__(self,other): # Dot protect. Abusing overloading. Sue me.
    return self.x * other.x + self.y * other.y

  def clone(self):
    """Clone a point, returning a new object with the same co-ordinates."""
    return Point(self.x,self.y)

  def lerp(self, other, t):
    """Interpolate between two points, at time t."""
    return self * t + other * (1-t)

  @property
  def squareMagnitude(self):
    """Interpreting this point as a vector, returns the squared magnitude (Euclidean length) of the vector."""
    return self.x*self.x + self.y*self.y

  @property
  def magnitude(self):
    """Interpreting this point as a vector, returns the magnitude (Euclidean length) of the vector."""
    return math.sqrt(self.squareMagnitude)

  def toUnitVector(self):
    return Point(self.x/self.magnitude, self.y/self.magnitude)

  @property
  def angle(self):
    """Interpreting this point as a vector, returns the angle in radians of the vector."""
    return math.atan2(self.y,self.x)

  @classmethod
  def fromAngle(self,angle):
    """Given an angle in radians, return a unit vector representing that angle."""
    return Point(math.cos(angle), math.sin(angle)).toUnitVector()

  def rotate(self,around,by):
    """Rotate a point around another point, by an angle given in radians."""
    delta = around - self
    oldangle = delta.angle
    newangle = oldangle + by
    unitvector = Point.fromAngle(newangle)
    new = around - unitvector * delta.magnitude
    self.x = new.x
    self.y = new.y

  def squareDistanceFrom(self,other):
    """Returns the squared Euclidean distance between this point and another."""
    return (self.x - other.x) * (self.x - other.x) + (self.y - other.y) * (self.y - other.y)

  def distanceFrom(self,other):
    """Returns the Euclidean distance between this point and another."""
    return math.sqrt(self.squareDistanceFrom(other))
