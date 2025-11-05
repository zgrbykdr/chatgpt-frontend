from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping

from .base import EnergyBalancedComponent
from ..fluids.properties import FluidState


@dataclass
class Pump(EnergyBalancedComponent):
  def initialize(self) -> None:
    super().initialize()
    self.state.setdefault('speed', float(self.params.get('speed', 2900.0)))
    self.state.setdefault('efficiency', float(self.params.get('efficiency', 0.7)))
    self.state.setdefault('head', float(self.params.get('head', 20.0)))

  def step(self, fluids: Mapping[str, FluidState], dt: float) -> Dict[str, float]:
    fluid = fluids[self.params.get('fluid', 'Water')]
    rho = fluid.density(self.state.get('p', 200000), self.state.get('T', 285.0))
    g = 9.81
    head = self.state['head'] * (self.state['speed'] / float(self.params.get('speed', 2900.0))) ** 2
    dp = rho * g * head
    m_dot = float(self.params.get('massFlow', 0.5))
    power = m_dot * dp / max(rho, 1.0)
    h_in = fluid.h_from_Tp(self.state.get('T', 285.0), self.state.get('p', 200000))
    h_out = h_in + power / max(m_dot, 1e-6)
    residual = self.compute_energy_balance(h_in, h_out, m_dot, power)
    self.enforce_energy_balance(residual, relaxation=0.2)
    self.state.update(
      {
        'dp': dp,
        'power': power,
        'h_in': h_in,
        'h_out': h_out,
        'm_dot': m_dot,
      }
    )
    return self.output()
