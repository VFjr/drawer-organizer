from ocp_viewer import show

from drawer_organizer import build_box

x = 24
y = 24
h = 60.0


def main() -> None:
    box = build_box(x, y, h)
    size = box.bounding_box().size
    print(f"x={x} y={y} h={h}")
    print(f"box X×Y×Z = {size.X}×{size.Y}×{size.Z}")
    show(box)


if __name__ == "__main__":
    main()
