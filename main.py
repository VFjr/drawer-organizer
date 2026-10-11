from ocp_viewer import show

from drawer_organizer import build_box
from drawer_organizer.units import adjust_to_half_unit

## Editable parameters
x = 19
y = 19
h = 60.0

## Non-editable parameters
radius = 2
chamfer_length = 1.5
side_clearance = 0.3
unit = 24

adj_x = adjust_to_half_unit(x, unit)
adj_y = adjust_to_half_unit(y, unit)

wall_thickness = (
    0.6 if adj_x < 60 or adj_y < 60 else
    0.7 if adj_x < 120 or adj_y < 120 else
    0.8
)

mag_hole_diameter = 10.3
mag_hole_h = 1.3
mag_bottom_thickness = 0.2
mag_top_thickness = 1.4



def main() -> None:
    box = build_box( 
        x=adj_x,
        y=adj_y,
        h=h,
        radius=radius,
        chamfer_length=chamfer_length,
        mag_hole_diameter=mag_hole_diameter,
        mag_hole_h=mag_hole_h,
        mag_bottom_thickness=mag_bottom_thickness,
        mag_top_thickness=mag_top_thickness,
        wall_thickness=wall_thickness,
    )
    show(box)


if __name__ == "__main__":
    main()
