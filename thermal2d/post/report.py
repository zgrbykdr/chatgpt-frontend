from __future__ import annotations

from pathlib import Path

from thermal2d.models import Project
from thermal2d.solver import SolverResult


def build_html_report(project: Project, result: SolverResult, outdir: str | Path) -> Path:
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    avg = result.temperature.mean()
    tmin = result.temperature.min()
    tmax = result.temperature.max()
    html = f"""
    <html><head><title>{project.name} report</title></head>
    <body>
    <h1>{project.name}</h1>
    <h2>Inputs</h2>
    <p>Domain: {project.width}m x {project.height}m</p>
    <p>Mesh: {project.mesh.nx} x {project.mesh.ny}</p>
    <p>Solver mode: {project.solver.mode}</p>
    <h2>Summary</h2>
    <table border='1'>
      <tr><th>Min T</th><th>Mean T</th><th>Max T</th></tr>
      <tr><td>{tmin:.3f}</td><td>{avg:.3f}</td><td>{tmax:.3f}</td></tr>
    </table>
    <p>L2D and psi structure: compute total heat flow from boundary fluxes and subtract 1D references per EN ISO 10211 assumptions.</p>
    </body></html>
    """
    path = out / "report.html"
    path.write_text(html)
    return path
