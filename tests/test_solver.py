from thermal2d.io.project_io import load_project
from thermal2d.mesher import StructuredMesher
from thermal2d.solver import HeatSolver


def test_steady_runs():
    p = load_project("samples/simple_wall_steady.json")
    mesh = StructuredMesher().generate(p)
    r = HeatSolver(p, mesh).solve_steady()
    assert r.temperature.shape == (p.mesh.ny, p.mesh.nx)
    assert r.temperature.min() >= -1
    assert r.temperature.max() <= 21


def test_transient_runs():
    p = load_project("samples/transient_outdoor_schedule.json")
    p.solver.t_end = 7200
    p.solver.output_interval = 3600
    mesh = StructuredMesher().generate(p)
    r = HeatSolver(p, mesh).solve_transient()
    assert len(r.history) >= 2
    assert "c" in r.probe_history
