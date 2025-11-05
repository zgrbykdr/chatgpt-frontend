from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Callable
import math

try:
  from CoolProp.CoolProp import PropsSI  # type: ignore
except Exception:  # pragma: no cover - fallback when CoolProp not available
  def PropsSI(output: str, input1: str, value1: float, input2: str, value2: float, fluid: str) -> float:
    if output == 'T' and {input1, input2} == {'P', 'Q'}:
      pressure = value1 if input1 == 'P' else value2
      return 273.15 + 0.0001 * pressure
    if output == 'H' and {input1, input2} == {'P', 'Q'}:
      pressure = value1 if input1 == 'P' else value2
      quality = value2 if input2 == 'Q' else value1
      return 1e3 * quality + 1.5 * pressure * 1e-3
    if output == 'H' and {input1, input2} == {'P', 'T'}:
      temperature = value1 if input1 == 'T' else value2
      return 4.2e3 * (temperature - 273.15)
    if output == 'S' and {input1, input2} == {'P', 'T'}:
      temperature = value1 if input1 == 'T' else value2
      return 4.0 * math.log(max(1.0, temperature))
    if output == 'D' and {input1, input2} == {'P', 'T'}:
      pressure = value1 if input1 == 'P' else value2
      return max(1.0, pressure / (287.0 * (value2 if input2 == 'T' else value1)))
    if output == 'C' and {input1, input2} == {'P', 'T'}:
      return 4200.0
    if output == 'T' and {input1, input2} == {'P', 'H'}:
      enthalpy = value1 if input1 == 'H' else value2
      return 273.15 + enthalpy / 4200.0
    return 0.0


@dataclass
class FluidState:
  name: str

  def h_from_Tp(self, temperature: float, pressure: float) -> float:
    return float(PropsSI('H', 'T', temperature, 'P', pressure, self.name))

  def h_from_px(self, pressure: float, quality: float) -> float:
    return float(PropsSI('H', 'P', pressure, 'Q', quality, self.name))

  def h_from_ps(self, pressure: float, entropy: float) -> float:
    return float(PropsSI('H', 'P', pressure, 'S', entropy, self.name))

  def s_from_Tp(self, temperature: float, pressure: float) -> float:
    return float(PropsSI('S', 'T', temperature, 'P', pressure, self.name))

  def T_from_ph(self, pressure: float, enthalpy: float) -> float:
    return float(PropsSI('T', 'P', pressure, 'H', enthalpy, self.name))

  def cp(self, pressure: float, temperature: float) -> float:
    return max(1000.0, float(PropsSI('C', 'T', temperature, 'P', pressure, self.name)))

  def density(self, pressure: float, temperature: float) -> float:
    return max(0.1, float(PropsSI('D', 'T', temperature, 'P', pressure, self.name)))

  def saturation_temperature(self, pressure: float) -> float:
    return float(PropsSI('T', 'P', pressure, 'Q', 0.5, self.name))


@lru_cache(maxsize=32)
def get_fluid(name: str) -> FluidState:
  return FluidState(name)


AVAILABLE_FLUIDS = [
  'R134a',
  'R410A',
  'R32',
  'R290',
  'Water',
  'MEG30',
]
