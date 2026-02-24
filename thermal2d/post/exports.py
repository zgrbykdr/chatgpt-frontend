from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from thermal2d.solver import SolverResult


def export_probe_csv(result: SolverResult, outdir: str | Path) -> None:
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    for pid, series in result.probe_history.items():
        with (out / f"probe_{pid}.csv").open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["time_s", "temperature_C"])
            w.writerows(series)


def export_field_csv(result: SolverResult, outdir: str | Path) -> Path:
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / "temperature_field.csv"
    np.savetxt(path, result.temperature, delimiter=",")
    return path
