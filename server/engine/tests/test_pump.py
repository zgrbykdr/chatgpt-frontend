from ..components.pump import Pump
from ..fluids import get_fluid


def test_pump_pressure_gain_positive():
  pump = Pump('pump', 'Pump', 'LUMPED', {
    'fluid': 'Water',
    'massFlow': 0.4,
    'speed': 2900.0,
    'head': 18.0,
  })
  pump.initialize()
  out = pump.step({'Water': get_fluid('Water')}, 1.0)
  assert out['dp'] > 0
  assert out['power'] > 0


def test_pump_energy_balance():
  pump = Pump('pump', 'Pump', 'LUMPED', {
    'fluid': 'Water',
    'massFlow': 0.5,
    'speed': 3000.0,
    'head': 22.0,
  })
  pump.initialize()
  out = pump.step({'Water': get_fluid('Water')}, 0.5)
  assert out['energyResidual'] >= 0
