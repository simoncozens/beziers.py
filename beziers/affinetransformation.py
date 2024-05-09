import math
from typing import Optional

from beziers.point import Point
from beziers.utils import isclose


class AffineTransformation(object):
    """A 2D affine transformation represented as a 3x3 matrix."""

    def __init__(self, matrix=None):
        if not matrix:
            self.matrix = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        else:
            self.matrix = matrix

    def __str__(self):
        m = self.matrix
        return "[ {:> 8.3f} {:> 8.3f} {:> 8.3f} ],\n[ {:> 8.3f} {:> 8.3f} {:> 8.3f} ],\n[ {:> 8.3f} {:> 8.3f} {:> 8.3f} ]".format(
            m[0][0],
            m[0][1],
            m[0][2],
            m[1][0],
            m[1][1],
            m[1][2],
            m[2][0],
            m[2][1],
            m[2][2],
        )

    def apply(self, other: "AffineTransformation") -> None:
        """Modify this transformation to have the effect of self x other."""
        m1 = self.matrix
        m2 = other.matrix
        self.matrix = [
            [
                m1[0][0] * m2[0][0] + m1[0][1] * m2[1][0] + m1[0][2] * m2[2][0],
                m1[0][0] * m2[0][1] + m1[0][1] * m2[1][1] + m1[0][2] * m2[2][1],
                m1[0][0] * m2[0][2] + m1[0][1] * m2[1][2] + m1[0][2] * m2[2][2],
            ],
            [
                m1[1][0] * m2[0][0] + m1[1][1] * m2[1][0] + m1[1][2] * m2[2][0],
                m1[1][0] * m2[0][1] + m1[1][1] * m2[1][1] + m1[1][2] * m2[2][1],
                m1[1][0] * m2[0][2] + m1[1][1] * m2[1][2] + m1[1][2] * m2[2][2],
            ],
            [
                m1[2][0] * m2[0][0] + m1[2][1] * m2[1][0] + m1[2][2] * m2[2][0],
                m1[2][0] * m2[0][1] + m1[2][1] * m2[1][1] + m1[2][2] * m2[2][1],
                m1[2][0] * m2[0][2] + m1[2][1] * m2[1][2] + m1[2][2] * m2[2][2],
            ],
        ]

    def apply_backwards(self, other: "AffineTransformation") -> None:
        """Modify this transformation to have the effect of other x self."""
        m2 = self.matrix
        m1 = other.matrix
        self.matrix = [
            [
                m1[0][0] * m2[0][0] + m1[0][1] * m2[1][0] + m1[0][2] * m2[2][0],
                m1[0][0] * m2[0][1] + m1[0][1] * m2[1][1] + m1[0][2] * m2[2][1],
                m1[0][0] * m2[0][2] + m1[0][1] * m2[1][2] + m1[0][2] * m2[2][2],
            ],
            [
                m1[1][0] * m2[0][0] + m1[1][1] * m2[1][0] + m1[1][2] * m2[2][0],
                m1[1][0] * m2[0][1] + m1[1][1] * m2[1][1] + m1[1][2] * m2[2][1],
                m1[1][0] * m2[0][2] + m1[1][1] * m2[1][2] + m1[1][2] * m2[2][2],
            ],
            [
                m1[2][0] * m2[0][0] + m1[2][1] * m2[1][0] + m1[2][2] * m2[2][0],
                m1[2][0] * m2[0][1] + m1[2][1] * m2[1][1] + m1[2][2] * m2[2][1],
                m1[2][0] * m2[0][2] + m1[2][1] * m2[1][2] + m1[2][2] * m2[2][2],
            ],
        ]

    @classmethod
    def translation(klass, vector: Point) -> "AffineTransformation":
        """Create a transformation that translates by the given vector."""
        return klass([[1, 0, vector.x], [0, 1, vector.y], [0, 0, 1]])

    def translate(self, vector: Point):
        """Modify this transformation to include a translation by the given vector."""
        self.apply_backwards(type(self).translation(vector))

    @classmethod
    def scaling(
        klass, factor_x: float, factor_y: Optional[float] = None
    ) -> "AffineTransformation":
        """Create a transformation that scales by the given factor(s)."""
        if not factor_y:
            factor_y = factor_x
        return klass([[factor_x, 0, 0], [0, factor_y, 0], [0, 0, 1]])

    def scale(self, factor_x: float, factor_y: Optional[float] = None) -> None:
        """Modify this transformation to include a scaling by the given factor(s)."""
        self.apply_backwards(type(self).scaling(factor_x, factor_y))

    @classmethod
    def reflection(klass) -> "AffineTransformation":
        """Create a transformation that reflects across the x-axis."""
        return klass([[-1, 0, 0], [0, 1, 0], [0, 0, 1]])

    def reflect(self) -> None:
        """Modify this transformation to include a reflection across the x-axis."""
        self.apply_backwards(type(self).reflection)

    @classmethod
    def rotation(klass, angle: float) -> "AffineTransformation":
        """Create a transformation that rotates by the given angle (in radians)."""
        return klass(
            [
                [math.cos(-angle), math.sin(-angle), 0],
                [-math.sin(-angle), math.cos(-angle), 0],
                [0, 0, 1],
            ]
        )

    def rotate(self, angle: float):
        """Modify this transformation to include a rotation by the given angle (in radians)."""
        self.apply_backwards(type(self).rotation(angle))

    def invert(self) -> None:
        """Modify this transformation to be its inverse."""
        m = self.matrix
        det = (
            m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
            - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
            + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
        )
        if isclose(det, 0.0):
            return None
        adj = [
            [
                (m[1][1] * m[2][2] - m[2][1] * m[1][2]) / det,
                (m[2][1] * m[0][2] - m[0][1] * m[2][2]) / det,
                (m[0][1] * m[1][2] - m[1][1] * m[0][2]) / det,
            ],
            [
                (m[1][2] * m[2][0] - m[1][0] * m[2][2]) / det,
                (m[0][0] * m[2][2] - m[0][2] * m[2][0]) / det,
                (m[0][2] * m[1][0] - m[0][0] * m[1][2]) / det,
            ],
            [
                (m[1][0] * m[2][1] - m[1][1] * m[2][0]) / det,
                (m[0][1] * m[2][0] - m[0][0] * m[2][1]) / det,
                (m[0][0] * m[1][1] - m[0][1] * m[1][0]) / det,
            ],
        ]
        self.matrix = adj
