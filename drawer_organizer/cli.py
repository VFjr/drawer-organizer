"""Command line: fit one container from given sizes, or a batch from a CSV.

    uv run python main.py size 19 100 50 --name pens --show
    uv run python main.py csv containers.csv --out output --show

The CSV needs a header row with ``name``, ``x``, ``y`` and ``z`` (``h`` is
accepted for ``z``). ``x`` and ``y`` are the required inside sizes and ``z``
is the outer height of the box, as for ``fit_container``.
"""

import csv
import re
from pathlib import Path
from typing import Annotated

import typer
from build123d import Pos, export_step

from drawer_organizer.fit import FittedContainer, fit_container

DEFAULT_OUT = Path("output")

app = typer.Typer(
    help="Fit drawer organizer containers and export them as STEP.",
    no_args_is_help=True,
)

OutOption = Annotated[Path, typer.Option(help="Folder for the STEP files.")]


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


@app.command()
def size(
    x: Annotated[float, typer.Argument(help="Required inside x.")],
    y: Annotated[float, typer.Argument(help="Required inside y.")],
    z: Annotated[float, typer.Argument(help="Outer height of the box.")],
    name: Annotated[str, typer.Option(help="Name used for the STEP file.")] = "container",
    out: OutOption = DEFAULT_OUT,
    show: Annotated[bool, typer.Option(help="Also send it to the OCP viewer.")] = False,
) -> None:
    """One container from sizes given here."""
    container = _export(name, x, y, z, out)
    if show:
        from ocp_viewer import show as show_in_viewer

        show_in_viewer(container.part)


@app.command("csv")
def from_csv(
    file: Annotated[
        Path, typer.Argument(exists=True, dir_okay=False, help="CSV with name,x,y,z.")
    ],
    out: OutOption = DEFAULT_OUT,
    show: Annotated[
        bool, typer.Option(help="Also send them to the OCP viewer, side by side.")
    ] = False,
) -> None:
    """Every container listed in a CSV."""
    shown = []
    for name, x, y, z in _read_rows(file):
        shown.append((name, _export(name, x, y, z, out)))

    if show and shown:
        from ocp_viewer import show as show_in_viewer

        # Side by side along X, so each can be hidden on its own in the viewer.
        gap = 10
        placed = []
        cursor = 0.0
        for _, container in shown:
            width = container.part.bounding_box().size.X
            placed.append(Pos(cursor + width / 2, 0, 0) * container.part)
            cursor += width + gap
        show_in_viewer(*placed, names=[name for name, _ in shown])


def main() -> None:
    app()
