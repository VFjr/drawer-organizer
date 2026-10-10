"""Algebra-mode model.

Solids are ordinary values. Combine them with:

    +   union
    -   subtract
    &   intersect
    *   place, as in ``Pos(x, y, z) * shape``
"""

from build123d import Align, Axis, Box, Part, chamfer, fillet


def build_box(x: float, y: float, h: float, radius: float, chamfer_length: float) -> Part:
    """Box of width ``x / 2``, length ``y``, and height ``h``.

    ``Box(length, width, height)`` is sized along X, Y, and Z. The face at
    X = 0 sits on the drawer center. The two vertical edges on the outer
    face are filleted. Every bottom edge is chamfered except the one that
    lies on that center plane.
    """
    box = Box(x / 2, y, h, align=(Align.MIN, Align.CENTER, Align.CENTER))
    outer_edges = box.edges().filter_by(Axis.Z).group_by(Axis.X)[-1]
    box = fillet(outer_edges, radius)

    bottom = box.bounding_box().min.Z
    bottom_edges = [
        edge
        for edge in box.edges()
        if edge.bounding_box().max.Z <= bottom + 1e-6
        and edge.bounding_box().max.X > 1e-6
    ]
    return chamfer(bottom_edges, chamfer_length)
