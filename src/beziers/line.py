import math
import sys
from typing import List, Tuple

from beziers.point import Point
from beziers.segment import Segment
from beziers.utils import isclose


class Line(Segment):
    """Represents a line segment within a Bezier path."""

    def __init__(self, start: Point, end: Point):
        """Create a new line segment.

        Args:
            start (Point): The starting point of the line.
            end (Point): The ending point of the line.
        """
        self.points = [start, end]
        self._orig = None

    def __repr__(self):
        return "L<%s--%s>" % (self.points[0], self.points[1])

    @classmethod
    def fromRepr(klass, text: str) -> "Line":
        """Create a new line segment from a string representation."""
        import re

        p = re.compile("^L<(<.*?>)--(<.*?>)>$")
        m = p.match(text)
        return klass(Point.fromRepr(m.group(1)), Point.fromRepr(m.group(2)))

    def pointAtTime(self, t: float) -> Point:
        """Returns the point at time t (0->1) along the line."""
        return self.start.lerp(self.end, t)

    # XXX One of these is wrong
    def tangentAtTime(self, t: float) -> Point:
        """Returns the tangent at time t (0->1) along the line."""
        return Point.fromAngle(
            math.atan2(self.end.y - self.start.y, self.end.x - self.start.x)
        )

    def normalAtTime(self, t: float) -> Point:
        """Returns the normal at time t (0->1) along the line."""
        return self.tangentAtTime(t).rotated(Point(0, 0), math.pi / 2)

    def curvatureAtTime(self, _t: float) -> float:
        """Returns the C curvature at time `t`."""
        return sys.float_info.epsilon  # Avoid divide-by-zero

    def splitAtTime(self, t: float) -> Tuple["Line", "Line"]:
        """Returns two segments, dividing the given segment at a point t (0->1) along the line."""
        return (
            Line(self.start, self.pointAtTime(t)),
            Line(self.pointAtTime(t), self.end),
        )

    def _findRoots(self, dimension: str) -> List[float]:
        if dimension == "x":
            t = (
                self[0].x / (self[0].x - self[1].x)
                if not isclose(self[0].x, self[1].x)
                else 100.0
            )
        elif dimension == "y":
            t = (
                self[0].y / (self[0].y - self[1].y)
                if not isclose(self[0].y, self[1].y)
                else 100.0
            )
        else:
            raise SyntaxError("Meh")
        if 0.0 <= t <= 1.0:
            return [t]
        return []

    def tOfPoint(self, point: Point, its_on_the_line_i_swear=False) -> float:
        """Returns the t (0->1) value of the given point, assuming it lies on the line, or -1 if it does not."""
        # Just find one and hope the other fits
        # point = self.start * (1-t) + self.end * t
        if not isclose(self.end.x, self.start.x):
            t = (point.x - self.start.x) / (self.end.x - self.start.x)
        elif not isclose(self.end.y, self.start.y):
            t = (point.y - self.start.y) / (self.end.y - self.start.y)
        else:
            print("! Line %s is actually a point..." % self)
            return -1
        if its_on_the_line_i_swear or self.pointAtTime(t).distanceFrom(point) < 2e-7:
            return t
        return -1

    def flatten(self, _degree=8) -> List["Line"]:
        return [self]

    @property
    def slope(self) -> float:
        """Returns the slope of the line."""
        v = self[1] - self[0]
        if v.x == 0:
            return 0
        return v.y / v.x

    @property
    def intercept(self) -> float:
        """Returns the y-intercept of the line."""
        return self[1].y - self.slope * self[1].x

    @property
    def length(self) -> float:
        """Returns the length of the line."""
        return self[0].distanceFrom(self[1])

    def findExtremes(self) -> List[Point]:
        """Returns the extrema of the line."""
        return []

    @property
    def area(self) -> float:
        """Returns the signed area of the line."""
        return 0.5 * (self[1].x - self[0].x) * (self[0].y + self[1].y)
