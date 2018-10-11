from beziers.point import Point

class BoundingBox:
  """A representation of a rectangle within the Beziers world,
  used to store bounding boxes."""

  def __init__(self):
    self.bl = None
    self.tr = None

  def __str__(self):
    return "BB[%s -> %s]" % (self.bl,self.tr)

  @property
  def area(self):
    vec = self.tr-self.bl
    return vec.x * vec.y

  @property
  def left(self):
    return self.bl.x

  @property
  def right(self):
    return self.tr.x

  @property
  def top(self):
    return self.tr.y

  @property
  def bottom(self):
    return self.bl.y

  def extend(self,other):
    """Add an object to the bounding box. Object can be a `Point`,
    another `BoundingBox`, or something which has a `bounds()` method."""
    if isinstance(other, Point):
      if not(self.bl): self.bl = other.clone()
      if not(self.tr): self.tr = other.clone()
      if other.x < self.bl.x: self.bl.x = other.x
      if other.y < self.bl.y: self.bl.y = other.y
      if other.x > self.tr.x: self.tr.x = other.x
      if other.y > self.tr.y: self.tr.y = other.y
    elif isinstance(other, BoundingBox):
      self.extend(other.bl)
      self.extend(other.tr)
    else:
      # Try getting its bb
      self.extend(other.bounds())

  def includes(self, point):
    """Returns True if the point is included in this bounding box."""
    return self.bl.x >= point.x and self.tr.x <= point.x and self.bl.y >= point.y and self.tr.y <= point.y

  def overlaps(self,other):
    """Returns True if the given bounding box overlaps with this bounding box."""
    if other.left > self.right:
      return False
    if other.right < self.left:
      return False
    if other.bottom > self.top:
      return False
    if other.top < self.bottom:
      return False
    return True

