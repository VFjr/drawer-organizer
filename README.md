# drawer-organizer

Parametric drawer organizer containers with embedded magnets, built with [build123d](https://github.com/gumyr/build123d) and exported as STEP.

`x` and `y` are the inside space you need; the container is rounded up to the next half-unit (12 mm) grid size that fits. `z` is the outer height of the box.

## Usage

One container:

```bash
uv run drawer-organizer size 19 100 50 --name pens [--show]
```

Many containers from a CSV (`name,x,y,z`). Copy the example to your own, gitignored list:

```bash
cp containers.example.csv containers.csv
uv run drawer-organizer csv containers.csv [--out output] [--show]
```

With the venv active (`source .venv/bin/activate`), drop the `uv run`.

STEP files are written to `output/` as `<name>_<grid x>x<grid y>x<z>.step`. `--show` also sends the parts to the OCP viewer (start it with `uv run ocp-viewer`); CSV containers appear side by side as separate, named objects.

Shared settings (wall thickness, clearance, magnet pocket, grid unit) live in `drawer_organizer/standard.py`.
