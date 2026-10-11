"""Find the smallest container on the half-unit grid with enough room inside."""

from dataclasses import dataclass

from build123d import Part

from drawer_organizer.measure import internal_dimensions
from drawer_organizer.model import build_container
from drawer_organizer.standard import StandardParameters, standard_parameters
from drawer_organizer.units import adjust_to_half_unit


@dataclass
class FittedContainer:
    part: Part
    grid_x: float
    grid_y: float
    h: float
    inside: dict[str, float]


def make_container(
    grid_x: float, grid_y: float, h: float, params: StandardParameters
) -> Part:
    """Container that occupies ``grid_x`` by ``grid_y`` on the grid, ``h`` tall."""
    return build_container(
        x=grid_x - params.side_clearance,
        y=grid_y - params.side_clearance,
        h=h,
        radius=params.radius,
        chamfer_length=params.chamfer_length,
        mag_hole_diameter=params.mag_hole_diameter,
        mag_hole_h=params.mag_hole_h,
        mag_bottom_thickness=params.mag_bottom_thickness,
        mag_top_thickness=params.mag_top_thickness,
        wall_thickness=params.wall_thickness(grid_x, grid_y),
    )


def fit_container(
    inside_x: float,
    inside_y: float,
    h: float,
    params: StandardParameters | None = None,
) -> FittedContainer:
    """Smallest container whose measured inside is at least ``inside_x`` by
    ``inside_y``. ``h`` is the outer height of the box, before the lip.

    ``grid_x`` and ``grid_y`` are multiples of half a unit. Each candidate is
    built and measured, so walls, clearance and the lip are all accounted
    for; whichever side is short grows by half a unit until both fit.
    """
    params = params or standard_parameters()
    step = params.unit / 2
    tolerance = 1e-6

    grid_x = adjust_to_half_unit(inside_x, params.unit)
    grid_y = adjust_to_half_unit(inside_y, params.unit)

    while True:
        part = make_container(grid_x, grid_y, h, params)
        inside = internal_dimensions(part)
        x_short = inside["x"] < inside_x - tolerance
        y_short = inside["y"] < inside_y - tolerance
        if not (x_short or y_short):
            return FittedContainer(part, grid_x, grid_y, h, inside)
        if x_short:
            grid_x += step
        if y_short:
            grid_y += step
