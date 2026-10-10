"""Algebra-mode model.

Solids are ordinary values. Combine them with:

    +   union
    -   subtract
    &   intersect
    *   place, as in ``Pos(x, y, z) * shape``
"""

from build123d import Box, Part


def build_box(x: float, y: float, h: float) -> Part:
    """Box of width ``x / 2``, length ``y``, and height ``h``.

    ``Box(length, width, height)`` is sized along X, Y, and Z.
    """
    return Box(x / 2, y, h)
