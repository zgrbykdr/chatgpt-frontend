import pytest

from core.boundary import BoundaryCondition
from core.interface import Interface
from core.project import Project
from core.solver import ThermalResistanceSolver


def test_contact_resistance_between_heat_source_and_fixed_sink_matches_delta_t():
    project = Project.new_project()
    hot = project.parts[0]
    hot.name = "Hot"
    hot.heat_power = 10.0
    cold = project.add_part()
    cold.name = "Cold"
    project.add_interface(
        Interface(
            part_a_id=hot.id,
            part_b_id=cold.id,
            type="contact_resistance",
            contact_resistance=2.0,
            contact_area=1.0,
        )
    )
    project.add_boundary(BoundaryCondition(part_id=cold.id, type="fixed_temperature", value=25.0))
    result = ThermalResistanceSolver().solve(project)
    assert result.success, result.message
    assert hot.temperature_result - cold.temperature_result == pytest.approx(20.0, abs=0.05)
    assert result.energy_in == pytest.approx(10.0)
    assert result.energy_out == pytest.approx(10.0, abs=0.05)
    assert result.energy_error_percent == pytest.approx(0.0, abs=0.5)


def test_single_part_convection_temperature_and_energy_balance_are_analytic():
    project = Project.new_project()
    part = project.parts[0]
    part.name = "Convection cooled plate"
    part.width = 1.0
    part.height = 1.0
    part.thickness = 0.1
    part.heat_power = 10.0
    project.add_boundary(
        BoundaryCondition(
            part_id=part.id,
            face="all",
            type="convection",
            ambient_temperature=20.0,
            h_value=5.0,
        )
    )
    result = ThermalResistanceSolver().solve(project)
    assert result.success, result.message
    assert part.temperature_result == pytest.approx(22.0)
    assert result.energy_in == pytest.approx(10.0)
    assert result.energy_out == pytest.approx(10.0)
    assert result.energy_error_percent == pytest.approx(0.0)
    assert any(flow["label"].startswith("convection") for flow in result.heat_flows)


def test_heat_flux_boundary_is_added_as_area_scaled_heat_source():
    project = Project.new_project()
    part = project.parts[0]
    part.width = 2.0
    part.height = 0.5
    part.thickness = 0.1
    project.add_boundary(BoundaryCondition(part_id=part.id, face="all", type="heat_flux", value=8.0))
    project.add_boundary(
        BoundaryCondition(
            part_id=part.id,
            face="all",
            type="convection",
            ambient_temperature=25.0,
            h_value=4.0,
        )
    )
    result = ThermalResistanceSolver().solve(project)
    assert result.success, result.message
    assert part.area() == pytest.approx(1.0)
    assert part.temperature_result == pytest.approx(27.0)
    assert result.energy_out == pytest.approx(8.0)


def test_thermal_pad_interface_uses_thickness_conductivity_and_area():
    project = Project.new_project()
    hot = project.parts[0]
    hot.heat_power = 12.0
    cold = project.add_part()
    area = 0.02
    thickness = 0.003
    conductivity = 3.0
    expected_resistance = thickness / (conductivity * area)
    project.add_interface(
        Interface(
            part_a_id=hot.id,
            part_b_id=cold.id,
            type="thermal_pad",
            contact_area=area,
            thickness=thickness,
            material_name="Thermal Pad 3 W/mK",
        )
    )
    project.add_boundary(BoundaryCondition(part_id=cold.id, type="fixed_temperature", value=30.0))
    result = ThermalResistanceSolver().solve(project)
    assert result.success, result.message
    assert hot.temperature_result - cold.temperature_result == pytest.approx(12.0 * expected_resistance, abs=0.05)


def test_air_gap_interface_uses_air_gap_equivalent_material():
    project = Project.new_project()
    hot = project.parts[0]
    hot.heat_power = 1.0
    cold = project.add_part()
    project.add_interface(
        Interface(
            part_a_id=hot.id,
            part_b_id=cold.id,
            type="air_gap",
            contact_area=0.1,
            thickness=0.0026,
            material_name="This should be ignored for air_gap",
        )
    )
    project.add_boundary(BoundaryCondition(part_id=cold.id, type="fixed_temperature", value=25.0))
    result = ThermalResistanceSolver().solve(project)
    assert result.success, result.message
    assert hot.temperature_result - cold.temperature_result == pytest.approx(1.0, abs=0.05)


def test_solver_rejects_invalid_convection_h_before_solving():
    project = Project.new_project()
    part = project.parts[0]
    part.heat_power = 10.0
    project.add_boundary(BoundaryCondition(part_id=part.id, type="convection", h_value=0.0))
    result = ThermalResistanceSolver().solve(project)
    assert not result.success
    assert "Invalid h value" in result.message
    assert part.temperature_result is None


def test_solver_singular_matrix_does_not_crash():
    project = Project.new_project()
    project.boundaries.clear()
    project.parts[0].heat_power = 10.0
    result = ThermalResistanceSolver().solve(project)
    assert not result.success
    assert "fixed temperature" in result.message or "boundary" in result.message
