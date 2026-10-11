from ocp_viewer import show

from drawer_organizer import fit_container

## Required inside x and y, and the outer height of the box
x = 19
y = 100
h = 50.0


def main() -> None:
    container = fit_container(x, y, h)
    inside = container.inside
    print(f"grid x={container.grid_x} y={container.grid_y} h={container.h:.2f}")
    print(f"internal x={inside['x']:.2f} y={inside['y']:.2f} h={inside['h']:.2f}")
    show(container.part)


if __name__ == "__main__":
    main()
