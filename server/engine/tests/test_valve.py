from ..components.valve import ExpansionValve
from ..fluids import get_fluid


def test_valve_mass_flow_limits():
  valve = ExpansionValve('valve', 'ExpansionValve', 'LUMPED', {
    'fluid': 'R134a',
    'upstreamPressure': 1500000,
    'downstreamPressure': 500000,
    'Cv': 1.0,
    'opening': 0.2,
  })
  valve.initialize()
  out = valve.step({'R134a': get_fluid('R134a')}, 0.1)
  assert out['m_dot'] >= 0


def test_valve_opening_clamp():
  valve = ExpansionValve('valve', 'ExpansionValve', 'LUMPED', {
    'fluid': 'R134a',
    'upstreamPressure': 1500000,
    'downstreamPressure': 500000,
    'Cv': 1.0,
    'opening': -10.0,
  })
  valve.initialize()
  out = valve.step({'R134a': get_fluid('R134a')}, 0.1)
  assert out['m_dot'] >= 0
