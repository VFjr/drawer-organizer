"""Algebra-mode model.

Solids are ordinary values. Combine them with:

    +   union
    -   subtract
    &   intersect
    *   place, as in ``Pos(x, y, z) * shape``
"""

from build123d import Align, Axis, Box, Part, fillet


def build_box(x: float, y: float, h: float, radius: float) -> Part:
    """Box of width ``x / 2``, length ``y``, and height ``h``.

    ``Box(length, width, height)`` is sized along X, Y, and Z. The face at
    X = 0 sits on the drawer center. The two vertical edges on the outer
    face are filleted; the edges on the center face stay sharp.
    """
    box = Box(x / 2, y, h, align=(Align.MIN, Align.CENTER, Align.CENTER))
    outer_edges = box.edges().filter_by(Axis.Z).group_by(Axis.X)[-1]
    return fillet(outer_edges, radius)
