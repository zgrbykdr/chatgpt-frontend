from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping

from .base import ComponentModel
from ..fluids.properties import FluidState


@dataclass
class Sensor(ComponentModel):
  def initialize(self) -> None:
    super().initialize()
    self.state.setdefault('measurement', 0.0)

  def step(self, fluids: Mapping[str, FluidState], dt: float) -> Dict[str, float]:
    quantity = self.params.get('quantity', 'temperature')
    if quantity == 'temperature':
      self.state['measurement'] = self.state.get('T', self.params.get('temperature', 285.0))
    elif quantity == 'pressure':
      self.state['measurement'] = self.state.get('p', self.params.get('pressure', 500000))
    elif quantity == 'massFlow':
      self.state['measurement'] = self.state.get('m_dot', self.params.get('massFlow', 0.2))
    else:
      self.state['measurement'] = 0.0
    return self.output()
