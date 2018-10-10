import math

class Point(object):
  """A representation of a point within the Beziers world.

  Here are some things you can do with points. You can interpret
  them as vectors, and add them together::

    >>> a = Point(5,5)
    >>> b = Point(10,10)
    >>> a + b
    <15.0,15.0>

  You can multiply them by a scalar to scale them::

    >>> a * 2
    <10.0,10.0>

  You can adjust them::

    >>> a += b
    >>> a
    <15.0,15.0>

  If you're using Python 3, you can abuse operator overloading
  and compute the dot product of two vectors:

    >>> a = Point(5,5)
    >>> b = Point(10,10)
    >>> a @ b
    100.0

"""

  def __init__(self, x,y):
    self.x = float(x)
    self.y = float(y)

  def __repr__(self):
    return "<%s,%s>" % (self.x,self.y)

  def __eq__(self, other):
    def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
      return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)
    return isclose(self.x, other.x) and isclose(self.y, other.y)

  def __hash__(self):
    return  hash(self.x) << 32 ^ hash(self.y)

  def __mul__(self, other):
    """Multiply a point by a scalar."""
    return Point(self.x * other, self.y * other)

  def __div__(self, other):
    return Point(self.x / other, self.y / other)

  def __truediv__(self, other):
    return Point(self.x / other, self.y / other)

  def __add__(self, other):
    return Point(self.x + other.x, self.y + other.y)

  def __sub__(self, other):
    return Point(self.x - other.x, self.y - other.y)

  def __iadd__(self, other):
    self.x += other.x
    self.y += other.y
    return self

  def __isub__(self, other):
    self.x -= other.x
    self.y -= other.y
    return self

  def __matmul__(self,other): # Dot product. Abusing overloading. Sue me.
    return self.x * other.x + self.y * other.y

  def clone(self):
    """Clone a point, returning a new object with the same co-ordinates."""
    return Point(self.x,self.y)

  def lerp(self, other, t):
    """Interpolate between two points, at time t."""
    return self * (1-t) + other * (t)

  @property
  def squareMagnitude(self):
    """Interpreting this point as a vector, returns the squared magnitude (Euclidean length) of the vector."""
    return self.x*self.x + self.y*self.y

  @property
  def magnitude(self):
    """Interpreting this point as a vector, returns the magnitude (Euclidean length) of the vector."""
    return math.sqrt(self.squareMagnitude)

  def toUnitVector(self):
    """Divides this point by its magnitude, returning a vector of length 1."""
    return Point(self.x/self.magnitude, self.y/self.magnitude)

  @property
  def angle(self):
    """Interpreting this point as a vector, returns the angle in radians of the vector."""
    return math.atan2(self.y,self.x)

  @classmethod
  def fromAngle(self,angle):
    """Given an angle in radians, return a unit vector representing that angle."""
    return Point(math.cos(angle), math.sin(angle)).toUnitVector()

  def rotated(self,around,by):
    """Return a new point found by rotating this point around another point, by an angle given in radians."""
    delta = around - self
    oldangle = delta.angle
    newangle = oldangle + by
    unitvector = Point.fromAngle(newangle)
    new = around - unitvector * delta.magnitude
    return new

  def rotate(self,around,by):
    """Mutate this point by rotating it around another point, by an angle given in radians."""
    new = self.rotated(around, by)
    self.x = new.x
    self.y = new.y

  def squareDistanceFrom(self,other):
    """Returns the squared Euclidean distance between this point and another."""
    return (self.x - other.x) * (self.x - other.x) + (self.y - other.y) * (self.y - other.y)

  def distanceFrom(self,other):
    """Returns the Euclidean distance between this point and another."""
    return math.sqrt(self.squareDistanceFrom(other))
