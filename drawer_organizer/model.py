"""Algebra-mode model.

Solids are ordinary values. Combine them with:

    +   union
    -   subtract
    &   intersect
    *   place, as in ``Pos(x, y, z) * shape``
"""

import math

from build123d import (
    Align,
    Axis,
    Box,
    Cylinder,
    Edge,
    Face,
    GeomType,
    Kind,
    Part,
    Plane,
    Polygon,
    Pos,
    Rectangle,
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

    box = box - cavity

    # Fillet where the floor meets the walls. The lip on the open face stays sharp.
    inside_edges = [
        edge
        for edge in box.edges()
        if abs(edge.bounding_box().min.Z - floor_z) <= 1e-6
        and abs(edge.bounding_box().max.Z - floor_z) <= 1e-6
        and edge.bounding_box().max.X > 1e-6
    ]

    box = fillet(inside_edges, 1)

    # Lip on the +Y end, sketched on the center plane (Y, Z) and extruded
    # across to the outer face.
    y_end = y / 2
    reach = 4
    slope_length = 5.5
    under_angle = 50
    rise = math.sqrt(slope_length**2 - reach**2)
    drop = (reach - wall_thickness) / math.tan(math.radians(under_angle))
    sketch = Plane.YZ * Polygon(
        (y_end, top + rise),
        (y_end - reach, top),
        (y_end - wall_thickness, top - drop),
        (y_end, top - drop),
        align=None,
    )
    lip = extrude(sketch, amount=width)

    # Trim to the outer outline so the lip keeps the outer corner fillet.
    # Built like the main box, not extruded from top_face: the extruded arc
    # gives a cylinder with a reversed axis, which clean() won't merge with
    # the main fillet, so the fillet would be split into two faces.
    envelope = Box(width, y, h + rise, align=(Align.MIN, Align.CENTER, Align.MIN))
    envelope = fillet(envelope.edges().filter_by(Axis.Z).group_by(Axis.X)[-1], radius)
    envelope = Pos(0, 0, bottom) * envelope
    box =  ((box + lip) & envelope).clean()

    # Soften the edges of the lip's sloped top, before the lip is hollowed:
    # afterwards the ridge sits on a wall too thin to fillet. Skip the edge on
    # the open face and the short stretch of the tip over the back wall, which
    # fails to fillet.
    slope = box.faces().filter_by(GeomType.PLANE).sort_by(Axis.Z)[-1]
    slope_edges = [
        edge
        for edge in slope.edges()
        if edge.bounding_box().max.X > 1e-6
        and not (
            edge.bounding_box().max.Z <= top + 1e-6
            and edge.bounding_box().min.X > 1e-6
        )
    ]
    box = fillet(slope_edges, 0.3)

    # Hollow out the lip, open on the center face and on the outer end face,
    # leaving wall_thickness on the slope, the underside, the outer face and
    # the corner. offset() on the solid with both faces as openings silently
    # returns the lip unchanged, so the hollow is built from 2D profiles
    # instead.
    #
    # The lip is split along the underside, carried on through the end wall,
    # rather than at the flat bottom of the sketch. Shelling that flat bottom
    # leaves a ledge at the end face.
    past = 2  # How far the profiles run past the open faces.
    under_slope = drop / (reach - wall_thickness)
    cross = Plane.YZ * Polygon(
        (y_end - reach, top),
        (y_end + past, top + rise + past * rise / reach),
        (y_end + past, top - (reach + past) * under_slope),
        align=None,
    )
    cross = offset(cross, amount=-wall_thickness, kind=Kind.INTERSECTION)
    along = extrude(Pos(-1, 0, 0) * cross, amount=width + 1, dir=(1, 0, 0))

    plan = Pos(width - wall_thickness, y_end - wall_thickness) * Rectangle(
        width - wall_thickness + 1, y_end + past, align=(Align.MAX, Align.MAX)
    )
    plan = fillet(
        plan.vertices().group_by(Axis.X)[-1].group_by(Axis.Y)[-1],
        radius - wall_thickness,
    )
    plan += Pos(-1, y_end - radius) * Rectangle(
        width - radius + 1, radius + past, align=(Align.MIN, Align.MIN)
    )
    cross_bottom = cross.bounding_box().min.Z
    around = extrude(
        Pos(0, 0, cross_bottom - 1) * plan,
        amount=cross.bounding_box().max.Z - cross_bottom + 2,
    )

    box = (box - (along & around)).clean()

    return box

