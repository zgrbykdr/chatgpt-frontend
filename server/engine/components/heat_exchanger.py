from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping
import math

from .base import EnergyBalancedComponent
from ..fluids.properties import FluidState


@dataclass
class MovingBoundaryHX(EnergyBalancedComponent):
  def initialize(self) -> None:
    super().initialize()
    self.state.setdefault('region_sc', self.params.get('region_sc', 0.2))
    self.state.setdefault('region_tp', self.params.get('region_tp', 0.5))
    self.state.setdefault('region_sh', self.params.get('region_sh', 0.3))
    self.state.setdefault('heatDuty', self.params.get('heatDuty', 15.0))

  def step(self, fluids: Mapping[str, FluidState], dt: float) -> Dict[str, float]:
    fluid = fluids[self.params.get('fluid', 'R134a')]
    m_dot = self.state.get('m_dot', self.params.get('massFlow', 0.3))
    quality_in = float(self.params.get('qualityIn', 0.2))
    pressure = self.state.get('p', self.params.get('pressure', 700000))
    hx_area = float(self.params.get('area', 12.0))
    wall_temp = float(self.params.get('wallTemperature', 290.0))

    h_in = fluid.h_from_px(pressure, quality_in)
    saturation = fluid.saturation_temperature(pressure)
    delta_t = max(1.0, wall_temp - saturation)
    h_tp = fluid.h_from_Tp(saturation + delta_t * 0.1, pressure)
    h_out = h_tp + delta_t * 100.0

    residual = self.compute_energy_balance(h_in, h_out, m_dot)
    self.enforce_energy_balance(residual)

    total_length = float(self.params.get('length', 5.0))
    total_fraction = self.state['region_sc'] + self.state['region_tp'] + self.state['region_sh']
    if total_fraction <= 0:
      sc = tp = sh = total_length / 3
    else:
      sc = total_length * self.state['region_sc'] / total_fraction
      tp = total_length * self.state['region_tp'] / total_fraction
      sh = total_length * self.state['region_sh'] / total_fraction

    capacity = hx_area * delta_t * 0.8
    outlet_temp = saturation + delta_t * math.tanh(capacity / max(1e-6, m_dot))

    self.state.update(
      {
        'p': pressure,
        'h_in': h_in,
        'h_out': h_out,
        'T_out': outlet_temp,
        'region_sc': sc / total_length,
        'region_tp': tp / total_length,
        'region_sh': sh / total_length,
        'heatDuty': capacity,
      }
    )
    return self.output()


@dataclass
class FiniteVolumeHX(EnergyBalancedComponent):
  cells: int = 10

  def initialize(self) -> None:
    super().initialize()
    self.cells = int(self.params.get('cells', self.cells))
    self.state['cellTemperatures'] = [self.params.get('temperature', 280.0)] * self.cells
    self.state.setdefault('heatDuty', self.params.get('heatDuty', 18.0))

  def step(self, fluids: Mapping[str, FluidState], dt: float) -> Dict[str, float]:
    fluid = fluids[self.params.get('fluid', 'R134a')]
    pressure = self.state.get('p', self.params.get('pressure', 650000))
    m_dot = self.state.get('m_dot', self.params.get('massFlow', 0.25))
    cp = fluid.cp(pressure, self.state['cellTemperatures'][0])
    q_cells = []
    inlet_temp = self.params.get('inletTemperature', 273.15 + 5)
    previous_temp = inlet_temp
    total_heat = 0.0
    for idx in range(self.cells):
      cell_temp = self.state['cellTemperatures'][idx]
      delta = previous_temp - cell_temp
      h_transfer = self.params.get('hCoeff', 3500.0)
      area = self.params.get('area', 10.0) / self.cells
      q = h_transfer * area * delta
      total_heat += q
      new_temp = cell_temp + dt * q / max(1e-6, m_dot * cp)
      q_cells.append(new_temp)
      previous_temp = new_temp
    self.state['cellTemperatures'] = q_cells
    outlet_temp = q_cells[-1]
    h_in = fluid.h_from_Tp(inlet_temp, pressure)
    h_out = fluid.h_from_Tp(outlet_temp, pressure)
    residual = self.compute_energy_balance(h_in, h_out, m_dot)
    self.enforce_energy_balance(residual, relaxation=0.2)
    self.state.update(
      {
        'T_out': outlet_temp,
        'heatDuty': total_heat,
        'p': pressure,
        'h_in': h_in,
        'h_out': h_out,
      }
    )
    return self.output()
