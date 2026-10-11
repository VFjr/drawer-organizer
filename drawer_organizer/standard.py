"""Parameters shared by every container."""

from dataclasses import dataclass


@dataclass(frozen=True)
class StandardParameters:
    radius: float = 2
    chamfer_length: float = 1.5
    side_clearance: float = 0.3
    unit: float = 24
    mag_hole_diameter: float = 10.3
    mag_hole_h: float = 1.3
    mag_bottom_thickness: float = 0.2
    mag_top_thickness: float = 1.4

    @property
    def floor_thickness(self) -> float:
        return self.mag_bottom_thickness + self.mag_hole_h + self.mag_top_thickness

    def wall_thickness(self, grid_x: float, grid_y: float) -> float:
        """Walls thicken as the container grows, judged on its longer side."""
        longest = max(grid_x, grid_y)
        if longest < 60:
            return 0.6
        if longest < 120:
            return 0.7
        return 0.8


def standard_parameters() -> StandardParameters:
    return StandardParameters()
