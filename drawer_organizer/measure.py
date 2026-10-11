"""Internal dimensions, measured on the finished part rather than computed
from the inputs, so fillets and the lip are accounted for as built."""

from build123d import Align, Box, Part, Pos

# Thickness of the slices used to probe the part.
_PROBE = 0.01


def _pieces(part: Part, probe: Part):
    return (part & probe).solids()


def internal_dimensions(part: Part) -> dict[str, float]:
    """Free space inside the bin.

    ``x`` is between the inner faces of the side walls, at mid height.
    ``y`` is from the inner face of the -Y end wall to the tip of the lip,
    fillet included. ``h`` is from the top of the floor to the top of the
    side walls.
    """
    bb = part.bounding_box()
    span_x = bb.size.X + 2
    span_y = bb.size.Y + 2
    span_z = bb.size.Z + 2

    walls = sorted(_pieces(part, Box(span_x, _PROBE, _PROBE)), key=lambda s: s.center().X)
    x = walls[-1].bounding_box().min.X - walls[0].bounding_box().max.X
    side_wall_mid_x = walls[-1].bounding_box().center().X

    column = Pos(0, 0, bb.min.Z - 1) * Box(
        _PROBE, _PROBE, span_z, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )
    floor_top = max(s.bounding_box().max.Z for s in _pieces(part, column))

    wall_column = Pos(side_wall_mid_x, 0, bb.min.Z - 1) * Box(
        _PROBE, _PROBE, span_z, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )
    rim_top = max(s.bounding_box().max.Z for s in _pieces(part, wall_column))
    h = rim_top - floor_top

    # Start well above the floor so the floor fillets don't count.
    above_floor = floor_top + 2
    lengthwise = Pos(0, 0, above_floor) * Box(
        _PROBE, span_y, bb.max.Z - above_floor + 1, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )
    ends = sorted(_pieces(part, lengthwise), key=lambda s: s.center().Y)
    y = ends[-1].bounding_box().min.Y - ends[0].bounding_box().max.Y

    return {"x": x, "y": y, "h": h}
