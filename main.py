from ocp_viewer import show

from drawer_organizer import build_box

x = 19
y = 19
h = 60.0
radius = 2

unit = 24

import math

def adjust_to_half_unit(value, unit):
    # Find the smallest interval of 0.5 * unit >= value
    interval = 0.5 * unit
    n = math.ceil(value / interval)
    return n * interval

adj_x = adjust_to_half_unit(x, unit)
adj_y = adjust_to_half_unit(y, unit)



def main() -> None:
    box = build_box(adj_x, adj_y, h, radius)
    size = box.bounding_box().size
    print(f"x={adj_x} y={adj_y} h={h}")
    print(f"box X×Y×Z = {size.X}×{size.Y}×{size.Z}")
    show(box)


if __name__ == "__main__":
    main()
