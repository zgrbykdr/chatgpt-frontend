from ..components.heat_exchanger import FiniteVolumeHX
from ..fluids import get_fluid


def make_map():
  return {'R134a': get_fluid('R134a')}


def test_fvm_temperature_monotonic():
  hx = FiniteVolumeHX('evap', 'Evaporator', 'FVM', {
    'fluid': 'R134a',
    'massFlow': 0.28,
    'cells': 8,
    'area': 12.0,
    'inletTemperature': 278.0,
    'pressure': 640000,
  })
  hx.initialize()
  out = hx.step(make_map(), 0.5)
  temps = out['cellTemperatures']
  assert temps[-1] != temps[0]
  assert all(isinstance(t, float) for t in temps)


def test_fvm_heat_duty_scaling():
  hx = FiniteVolumeHX('evap', 'Evaporator', 'FVM', {
    'fluid': 'R134a',
    'massFlow': 0.2,
    'cells': 6,
    'area': 8.0,
    'inletTemperature': 275.0,
    'pressure': 600000,
  })
  hx.initialize()
  baseline = hx.step(make_map(), 1.0)['heatDuty']
  hx.params['hCoeff'] = 4500.0
  hx.initialize()
  higher = hx.step(make_map(), 1.0)['heatDuty']
  assert higher > baseline


def test_fvm_energy_residual_present():
  hx = FiniteVolumeHX('evap', 'Evaporator', 'FVM', {
    'fluid': 'R134a',
    'massFlow': 0.3,
    'cells': 10,
    'area': 10.0,
    'inletTemperature': 278.0,
    'pressure': 650000,
  })
  hx.initialize()
  out = hx.step(make_map(), 0.2)
  assert out['energyResidual'] >= 0
