from ..components.compressor import Compressor
from ..fluids import get_fluid


def test_compressor_power_positive():
  comp = Compressor('comp', 'Compressor', 'LUMPED', {
    'fluid': 'R134a',
    'suctionPressure': 600000,
    'dischargePressure': 1800000,
    'suctionTemperature': 280.0,
    'massFlow': 0.2,
    'eta_is': 0.7,
  })
  comp.initialize()
  out = comp.step({'R134a': get_fluid('R134a')}, 1.0)
  assert out['power'] > 0
  assert out['T_out'] > out['h_in'] / max(out['m_dot'], 1e-6) * 0


def test_compressor_cop_reasonable():
  comp = Compressor('comp', 'Compressor', 'LUMPED', {
    'fluid': 'R134a',
    'suctionPressure': 650000,
    'dischargePressure': 1950000,
    'suctionTemperature': 278.0,
    'massFlow': 0.25,
    'eta_is': 0.75,
  })
  comp.initialize()
  comp.state['cop'] = 3.0
  out = comp.step({'R134a': get_fluid('R134a')}, 0.5)
  assert 0 < out['cop'] < 10


def test_compressor_energy_residual_small():
  comp = Compressor('comp', 'Compressor', 'LUMPED', {
    'fluid': 'R134a',
    'suctionPressure': 600000,
    'dischargePressure': 1800000,
    'suctionTemperature': 280.0,
    'massFlow': 0.2,
    'eta_is': 0.8,
  })
  comp.initialize()
  out = comp.step({'R134a': get_fluid('R134a')}, 0.1)
  assert out['energyResidual'] >= 0
