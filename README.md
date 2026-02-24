# Thermal2D Studio

Production-oriented 2D thermal simulation desktop application with integrated pre/post workflow.

## Features
- Rectangle geometry editor model with overlap/priority.
- Structured automesher (uniform + non-uniform edge arrays).
- Explicit transient solver with stability criterion and SOR steady solver.
- Temperature-dependent properties + phase change via apparent heat capacity.
- BCs: fixed temperature, heat flux, convective (h or R) with constant/sinus/step schedules.
- Probes, CSV export, HTML reporting, batch CLI.
- DXF + SVG rectangle import pipeline.
- Material libraries (200 default, 1200 optional import list + DIN-like format template).

## Install
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Run GUI
```bash
thermal2d-gui
```

## Batch mode
```bash
simulate --project samples/simple_wall_steady.json --outdir out/wall --mode steady
```

## Windows build
Use PyInstaller:
```bash
pip install pyinstaller
pyinstaller -n Thermal2D --onefile -w -m thermal2d.gui.app
```

## Limitations
- DWG import is not included; DXF is the primary CAD pathway.
- Cavity radiation module structure is prepared for iterative extension; not fully modeled in this release.
