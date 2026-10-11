"""Algebra-mode model.

Solids are ordinary values. Combine them with:

    +   union
    -   subtract
    &   intersect
    *   place, as in ``Pos(x, y, z) * shape``
"""

from build123d import (
    Align,
    Axis,
    Box,
    Cylinder,
    Edge,
    Face,
    Part,
    Pos,
    Side,
    Wire,
    chamfer,
    extrude,
    fillet,
    offset,
)


def build_box(
    x: float,
    y: float,
    h: float,
    radius: float,
    chamfer_length: float,
    mag_hole_diameter: float,
    mag_hole_h: float,
    mag_bottom_thickness: float,
    mag_top_thickness: float,
    wall_thickness: float,
) -> Part:
    """Box of width ``x / 2``, length ``y``, and height ``h``.

    ``Box(length, width, height)`` is sized along X, Y, and Z. The face at
    X = 0 sits on the drawer center. The two vertical edges on the outer
    face are filleted. Every bottom edge is chamfered except the one that
    lies on that center plane.

    """
    
    # main box
    width = x / 2
    box = Box(width, y, h, align=(Align.MIN, Align.CENTER, Align.CENTER))
    outer_edges = box.edges().filter_by(Axis.Z).group_by(Axis.X)[-1]

    # outer filler
    box = fillet(outer_edges, radius)

    # bottom chamfer
    bottom = box.bounding_box().min.Z
    top = box.bounding_box().max.Z
    bottom_edges = [
        edge
        for edge in box.edges()
        if edge.bounding_box().max.Z <= bottom + 1e-6
        and edge.bounding_box().max.X > 1e-6
    ]
    box = chamfer(bottom_edges, chamfer_length)

    # magnet pocket
    pocket = Pos(
        mag_hole_h / 2,
        0,
        bottom + mag_bottom_thickness,
    ) * Cylinder(mag_hole_diameter / 2, mag_hole_h, align=(Align.CENTER, Align.CENTER, Align.MIN))
    box = box - pocket

    # inner cavity
    floor_z = bottom + mag_bottom_thickness + mag_hole_h + mag_top_thickness
    top_face = box.faces().sort_by(Axis.Z)[-1]
    center = [edge for edge in top_face.edges() if abs(edge.center().X) < 1e-6]
    walls = [edge for edge in top_face.edges() if edge not in center]
    curve = offset(walls, amount=-wall_thickness, side=Side.LEFT, closed=False)
    opening = [vertex for vertex in curve.vertices() if abs(vertex.X) < 1e-6]
    face = Face(Wire(list(curve.edges()) + [Edge.make_line(opening[0], opening[1])]))
    cavity = extrude(Pos(0, 0, floor_z - top) * face, amount=top - floor_z)
    return box - cavity

