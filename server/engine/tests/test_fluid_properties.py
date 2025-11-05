import math
import pytest

from ..fluids import get_fluid, AVAILABLE_FLUIDS


def test_fluid_list_contains_common_refrigerants():
  assert 'R134a' in AVAILABLE_FLUIDS
  assert 'Water' in AVAILABLE_FLUIDS


def test_fluid_enthalpy_temperature_relation():
  fluid = get_fluid('Water')
  h1 = fluid.h_from_Tp(280.0, 101325)
  h2 = fluid.h_from_Tp(310.0, 101325)
  assert h2 > h1


def test_fluid_density_positive():
  fluid = get_fluid('R134a')
  density = fluid.density(700000, 280.0)
  assert density > 0


def test_fluid_saturation_monotonic():
  fluid = get_fluid('R134a')
  t_low = fluid.saturation_temperature(500000)
  t_high = fluid.saturation_temperature(1000000)
  assert t_high >= t_low


def test_fluid_cp_minimum():
  fluid = get_fluid('Water')
  cp = fluid.cp(101325, 300.0)
  assert cp >= 1000.0


def test_fluid_entropy_variation():
  fluid = get_fluid('R134a')
  s1 = fluid.s_from_Tp(280.0, 500000)
  s2 = fluid.s_from_Tp(300.0, 500000)
  assert s2 != pytest.approx(s1)


def test_fluid_temperature_from_ph_inverse():
  fluid = get_fluid('Water')
  T = 305.0
  h = fluid.h_from_Tp(T, 101325)
  T_back = fluid.T_from_ph(101325, h)
  assert T_back == pytest.approx(T, rel=1e-2, abs=1e-2)


def test_fluid_caching_identity():
  fluid1 = get_fluid('Water')
  fluid2 = get_fluid('Water')
  assert fluid1 is fluid2
