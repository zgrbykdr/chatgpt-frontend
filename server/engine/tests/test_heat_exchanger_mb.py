import pytest

from ..components.heat_exchanger import MovingBoundaryHX
from ..fluids import get_fluid


def make_fluid_map():
  return {'R134a': get_fluid('R134a')}


def test_mb_regions_normalized():
  model = MovingBoundaryHX(
    id='evap',
    type='Evaporator',
    modeling='MB',
    params={
      'fluid': 'R134a',
      'massFlow': 0.3,
      'area': 12.0,
      'length': 5.0,
      'qualityIn': 0.2,
      'pressure': 650000,
      'wallTemperature': 280.0,
    },
  )
  model.initialize()
  out = model.step(make_fluid_map(), dt=1.0)
  assert pytest.approx(out['region_sc'] + out['region_tp'] + out['region_sh'], rel=1e-5) == 1.0


def test_mb_heat_duty_positive():
  model = MovingBoundaryHX('cond', 'Condenser', 'MB', {
    'fluid': 'R134a',
    'massFlow': 0.35,
    'area': 14.0,
    'length': 6.0,
    'qualityIn': 0.8,
    'pressure': 900000,
    'wallTemperature': 310.0,
  })
  model.initialize()
  out = model.step(make_fluid_map(), dt=0.5)
  assert out['heatDuty'] > 0
  assert out['T_out'] > 0


def test_mb_energy_residual_reduces_with_iteration():
  model = MovingBoundaryHX('evap', 'Evaporator', 'MB', {
    'fluid': 'R134a',
    'massFlow': 0.25,
    'area': 11.0,
    'length': 4.5,
    'qualityIn': 0.3,
    'pressure': 550000,
    'wallTemperature': 290.0,
  })
  model.initialize()
  out1 = model.step(make_fluid_map(), 1.0)
  residual1 = out1.get('energyResidual', 0.0)
  out2 = model.step(make_fluid_map(), 1.0)
  residual2 = out2.get('energyResidual', 0.0)
  assert residual2 <= residual1 + 1e-6
