"""Command line: fit one container from given sizes, or a batch from a CSV.

    uv run python main.py size 19 100 50 --name pens --show
    uv run python main.py csv containers.csv --out output --show

The CSV needs a header row with ``name``, ``x``, ``y`` and ``z`` (``h`` is
accepted for ``z``). ``x`` and ``y`` are the required inside sizes and ``z``
is the outer height of the box, as for ``fit_container``.
"""

import argparse
import csv
import re
from pathlib import Path

from build123d import Pos, export_step

from drawer_organizer.fit import FittedContainer, fit_container

DEFAULT_OUT = Path("output")


def _file_stem(name: str, container: FittedContainer) -> str:
    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", name.strip()).strip("_") or "container"
    return f"{safe}_{container.grid_x:g}x{container.grid_y:g}x{container.h:g}"


def _report(name: str, container: FittedContainer, path: Path) -> None:
    inside = container.inside
    print(
        f"{name}: grid {container.grid_x:g} x {container.grid_y:g}, h {container.h:g}"
        f" | inside {inside['x']:.2f} x {inside['y']:.2f} x {inside['h']:.2f}"
        f" -> {path}"
    )


def _export(name: str, x: float, y: float, z: float, out: Path) -> FittedContainer:
    container = fit_container(x, y, z)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{_file_stem(name, container)}.step"
    export_step(container.part, path)
    _report(name, container, path)
    return container


def _read_rows(csv_path: Path) -> list[tuple[str, float, float, float]]:
    with csv_path.open(newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None:
            raise SystemExit(f"{csv_path}: empty file")
        columns = {field.strip().lower(): field for field in reader.fieldnames}
        if "z" not in columns and "h" in columns:
            columns["z"] = columns["h"]
        missing = [key for key in ("name", "x", "y", "z") if key not in columns]
        if missing:
            raise SystemExit(f"{csv_path}: missing column(s) {', '.join(missing)}")

        rows = []
        for line, record in enumerate(reader, start=2):
            if not any((value or "").strip() for value in record.values()):
                continue
            try:
                rows.append((
                    record[columns["name"]].strip(),
                    float(record[columns["x"]]),
                    float(record[columns["y"]]),
                    float(record[columns["z"]]),
                ))
            except (TypeError, ValueError) as error:
                raise SystemExit(f"{csv_path}:{line}: {error}") from error

    names = [row[0] for row in rows]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        raise SystemExit(f"{csv_path}: duplicate name(s) {', '.join(duplicates)}")
    return rows


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)

    size = commands.add_parser("size", help="one container from sizes given here")
    size.add_argument("x", type=float, help="required inside x")
    size.add_argument("y", type=float, help="required inside y")
    size.add_argument("z", type=float, help="outer height of the box")
    size.add_argument("--name", default="container")
    size.add_argument("--out", type=Path, default=DEFAULT_OUT)
    size.add_argument("--show", action="store_true", help="also send it to the OCP viewer")

    batch = commands.add_parser("csv", help="every container listed in a CSV")
    batch.add_argument("file", type=Path)
    batch.add_argument("--out", type=Path, default=DEFAULT_OUT)
    batch.add_argument(
        "--show", action="store_true", help="also send them to the OCP viewer, side by side"
    )

    args = parser.parse_args(argv)

    if args.command == "size":
        container = _export(args.name, args.x, args.y, args.z, args.out)
        if args.show:
            from ocp_viewer import show

            show(container.part)
        return

    shown = []
    for name, x, y, z in _read_rows(args.file):
        shown.append((name, _export(name, x, y, z, args.out)))

    if args.show and shown:
        from ocp_viewer import show

        # Side by side along X, so each can be hidden on its own in the viewer.
        gap = 10
        placed = []
        cursor = 0.0
        for _, container in shown:
            width = container.part.bounding_box().size.X
            placed.append(Pos(cursor + width / 2, 0, 0) * container.part)
            cursor += width + gap
        show(*placed, names=[name for name, _ in shown])
