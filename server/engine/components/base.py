from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, Mapping


@dataclass
class ComponentModel:
  id: str
  type: str
  modeling: str
  params: Dict[str, Any]
  state: Dict[str, float] = field(default_factory=dict)

  def initialize(self) -> None:
    """Initialize component state from parameters."""
    if 'pressure' in self.params:
      self.state.setdefault('p', float(self.params['pressure']))
    if 'temperature' in self.params:
      self.state.setdefault('T', float(self.params['temperature']))
    if 'massFlow' in self.params:
      self.state.setdefault('m_dot', float(self.params['massFlow']))

  def step(self, fluids: Mapping[str, Any], dt: float) -> Dict[str, float]:
    """Advance component state. Must be implemented by subclass."""
    raise NotImplementedError

  def output(self) -> Dict[str, float]:
    return dict(self.state)


class EnergyBalancedComponent(ComponentModel):
  def compute_energy_balance(self, inlet_h: float, outlet_h: float, mass_flow: float, work: float = 0.0) -> float:
    return mass_flow * (outlet_h - inlet_h) - work

  def enforce_energy_balance(self, residual: float, relaxation: float = 0.5) -> None:
    self.state['energyResidual'] = abs(residual)
    if 'heatDuty' in self.state:
      self.state['heatDuty'] -= relaxation * residual
