from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping

from .base import ComponentModel
from ..fluids.properties import FluidState


def smooth_clamp(value: float, lower: float, upper: float) -> float:
  import math

  return lower + (upper - lower) / (1 + math.exp(-(value - lower) / max(1e-6, upper - lower)))


@dataclass
class ExpansionValve(ComponentModel):
  def initialize(self) -> None:
    super().initialize()
    self.state.setdefault('opening', float(self.params.get('opening', 0.5)))

  def step(self, fluids: Mapping[str, FluidState], dt: float) -> Dict[str, float]:
    fluid = fluids[self.params.get('fluid', 'R134a')]
    upstream_p = float(self.params.get('upstreamPressure', 1200000))
    downstream_p = float(self.params.get('downstreamPressure', 400000))
    cv = float(self.params.get('Cv', 0.9))
    opening = smooth_clamp(self.state['opening'], 0.05, 0.95)
    rho = fluid.density(upstream_p, self.params.get('temperature', 280.0))
    m_dot = cv * opening * (upstream_p - downstream_p) / max(1e-3, rho)
    m_dot = max(0.0, m_dot)
    h_in = fluid.h_from_Tp(self.params.get('temperature', 280.0), upstream_p)
    h_out = h_in
    self.state.update(
      {
        'm_dot': m_dot,
        'upstream_p': upstream_p,
        'downstream_p': downstream_p,
        'h_in': h_in,
        'h_out': h_out,
      }
    )
    return self.output()
