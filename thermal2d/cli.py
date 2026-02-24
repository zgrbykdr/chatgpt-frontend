from __future__ import annotations

import argparse
from pathlib import Path

from thermal2d.io.project_io import load_project
from thermal2d.mesher import StructuredMesher
from thermal2d.post.exports import export_field_csv, export_probe_csv
from thermal2d.post.report import build_html_report
from thermal2d.solver import HeatSolver


def main() -> None:
    parser = argparse.ArgumentParser(prog="simulate")
    parser.add_argument("--project", required=True)
    parser.add_argument("--outdir", required=True)
    parser.add_argument("--mode", choices=["steady", "transient"], default=None)
    args = parser.parse_args()

    p = load_project(args.project)
    if args.mode:
        p.solver.mode = args.mode
    mesh = StructuredMesher().generate(p)
    solver = HeatSolver(p, mesh)
    result = solver.solve_steady() if p.solver.mode == "steady" else solver.solve_transient()

    out = Path(args.outdir)
    export_field_csv(result, out)
    export_probe_csv(result, out)
    build_html_report(p, result, out)
    print(f"Done. Outputs: {out}")


if __name__ == "__main__":
    main()
