from core.boundary import BoundaryCondition
from core.interface import Interface
from core.project import Project


def test_project_save_load(tmp_path):
    project = Project.new_project()
    first = project.parts[0]
    second = project.add_part()
    boundary = BoundaryCondition(part_id=first.id, type="convection", h_value=15.0)
    interface = Interface(part_a_id=first.id, part_b_id=second.id, type="perfect_contact")
    project.add_boundary(boundary)
    project.add_interface(interface)
    path = tmp_path / "project.json"
    project.save_to_file(path)
    loaded = Project.load_from_file(path)
    assert len(loaded.parts) == 2
    assert loaded.parts[0].name == first.name
    assert len(loaded.boundaries) == 1
    assert len(loaded.interfaces) == 1
