import pytest

from core.convection_predictor import ConvectionPredictor
from core.fluid import Fluid, default_fluids, fluid_by_name


def test_air_forced_flat_plate_laminar_matches_correlation():
    air = fluid_by_name(default_fluids(), "Air")
    velocity = 2.0
    length = 0.2
    result = ConvectionPredictor().predict(
        air,
        "forced_external_flat_plate",
        velocity=velocity,
        characteristic_length=length,
    )
    expected_re = velocity * length / air.kinematic_viscosity
    expected_nu = 0.664 * expected_re**0.5 * air.prandtl_number ** (1 / 3)
    expected_h = expected_nu * air.thermal_conductivity / length
    assert result.correlation_name == "Forced external flat plate laminar"
    assert result.Re == pytest.approx(expected_re)
    assert result.Nu == pytest.approx(expected_nu)
    assert result.h_value == pytest.approx(expected_h)
    assert result.Pr == pytest.approx(air.prandtl_number)


def test_forced_flat_plate_turbulent_branch_matches_correlation():
    air = fluid_by_name(default_fluids(), "Air")
    velocity = 100.0
    length = 0.2
    result = ConvectionPredictor().predict(
        air,
        "forced_external_flat_plate",
        velocity=velocity,
        characteristic_length=length,
    )
    expected_re = velocity * length / air.kinematic_viscosity
    expected_nu = 0.037 * expected_re**0.8 * air.prandtl_number ** (1 / 3)
    assert expected_re >= 5e5
    assert result.correlation_name == "Forced external flat plate turbulent"
    assert result.Re == pytest.approx(expected_re)
    assert result.Nu == pytest.approx(expected_nu)


def test_water_internal_pipe_laminar_uses_constant_nusselt():
    water = fluid_by_name(default_fluids(), "Water")
    diameter = 0.001
    velocity = 0.1
    result = ConvectionPredictor().predict(
        water,
        "internal_pipe_flow",
        velocity=velocity,
        diameter=diameter,
    )
    expected_re = velocity * diameter / water.kinematic_viscosity
    expected_h = 3.66 * water.thermal_conductivity / diameter
    assert expected_re < 2300
    assert result.correlation_name == "Internal pipe laminar constant wall temperature"
    assert result.Re == pytest.approx(expected_re)
    assert result.Nu == pytest.approx(3.66)
    assert result.h_value == pytest.approx(expected_h)


def test_water_internal_pipe_turbulent_matches_dittus_boelter():
    water = fluid_by_name(default_fluids(), "Water")
    diameter = 0.02
    velocity = 1.0
    result = ConvectionPredictor().predict(
        water,
        "internal_pipe_flow",
        velocity=velocity,
        diameter=diameter,
    )
    expected_re = velocity * diameter / water.kinematic_viscosity
    expected_nu = 0.023 * expected_re**0.8 * water.prandtl_number**0.4
    assert expected_re >= 2300
    assert result.correlation_name == "Internal pipe turbulent Dittus-Boelter"
    assert result.Re == pytest.approx(expected_re)
    assert result.Nu == pytest.approx(expected_nu)
    assert result.h_value == pytest.approx(expected_nu * water.thermal_conductivity / diameter)


def test_natural_convection_matches_vertical_plate_correlation():
    air = fluid_by_name(default_fluids(), "Air")
    length = 0.5
    surface_temperature = 60.0
    ambient_temperature = 25.0
    result = ConvectionPredictor().predict(
        air,
        "natural_vertical_plate",
        characteristic_length=length,
        surface_temperature=surface_temperature,
        ambient_temperature=ambient_temperature,
    )
    expected_gr = (
        9.81
        * air.thermal_expansion_coefficient
        * abs(surface_temperature - ambient_temperature)
        * length**3
        / air.kinematic_viscosity**2
    )
    expected_ra = expected_gr * air.prandtl_number
    expected_nu = 0.59 * expected_ra**0.25
    assert expected_ra < 1e9
    assert result.correlation_name == "Natural vertical plate laminar"
    assert result.Gr == pytest.approx(expected_gr)
    assert result.Ra == pytest.approx(expected_ra)
    assert result.Nu == pytest.approx(expected_nu)
    assert result.h_value == pytest.approx(expected_nu * air.thermal_conductivity / length)


def test_predictor_rejects_invalid_fluid_properties():
    invalid = Fluid(
        name="Invalid",
        density=1.0,
        dynamic_viscosity=1.0,
        kinematic_viscosity=0.0,
        thermal_conductivity=0.026,
        specific_heat=1000.0,
        prandtl_number=0.7,
        thermal_expansion_coefficient=0.003,
        valid_temperature_min=-50.0,
        valid_temperature_max=200.0,
    )
    with pytest.raises(ValueError, match="pozitif"):
        ConvectionPredictor().predict(invalid, "forced_external_flat_plate")


def test_predictor_rejects_unsupported_flow_type():
    air = fluid_by_name(default_fluids(), "Air")
    with pytest.raises(ValueError, match="Desteklenmeyen"):
        ConvectionPredictor().predict(air, "unsupported_flow")
