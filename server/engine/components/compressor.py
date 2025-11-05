from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping
import math

from .base import EnergyBalancedComponent
from ..fluids.properties import FluidState


@dataclass
class Compressor(EnergyBalancedComponent):
  def initialize(self) -> None:
    super().initialize()
    self.state.setdefault('speed', float(self.params.get('speed', 45.0)))
    self.state.setdefault('isentropicEfficiency', float(self.params.get('eta_is', 0.75)))
    self.state.setdefault('heatDuty', 0.0)

  def step(self, fluids: Mapping[str, FluidState], dt: float) -> Dict[str, float]:
    fluid = fluids[self.params.get('fluid', 'R134a')]
    suction_p = float(self.params.get('suctionPressure', self.state.get('p', 400000)))
    discharge_p = float(self.params.get('dischargePressure', suction_p * 3.0))
    suction_T = float(self.params.get('suctionTemperature', 278.0))
    eta = float(self.state['isentropicEfficiency'])
    speed = self.state['speed']
    m_dot = float(self.params.get('massFlow', 0.12)) * (speed / 45.0)

    h_in = fluid.h_from_Tp(suction_T, suction_p)
    s_in = fluid.s_from_Tp(suction_T, suction_p)
    h_is = fluid.h_from_ps(discharge_p, s_in)
    work_is = h_is - h_in
    work = work_is / max(1e-6, eta)
    h_out = h_in + work
    residual = self.compute_energy_balance(h_in, h_out, m_dot, work)
    self.enforce_energy_balance(residual, relaxation=0.1)

    discharge_T = fluid.T_from_ph(discharge_p, h_out)
    power = m_dot * work
    cop = self.state.get('cop', 0.0)
    cop = (cop + (h_out - h_in) / max(1e-6, work)) * 0.5

    self.state.update(
      {
        'p': discharge_p,
        'h_in': h_in,
        'h_out': h_out,
        'T_out': discharge_T,
        'work': work,
        'power': power,
        'cop': cop,
        'm_dot': m_dot,
      }
    )
    return self.output()
