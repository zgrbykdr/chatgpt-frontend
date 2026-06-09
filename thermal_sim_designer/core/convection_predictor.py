from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.fluid import Fluid


@dataclass
class ConvectionPrediction:
    h_value: float
    correlation_name: str
    Re: float
    Pr: float
    Nu: float
    Ra: float
    Gr: float
    validity_message: str
    confidence: str

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


class ConvectionPredictor:
    def predict(
        self,
        fluid: Fluid,
        flow_type: str,
        geometry_type: str = "plate",
        velocity: float = 1.0,
        characteristic_length: float = 0.1,
        surface_temperature: float = 60.0,
        ambient_temperature: float = 25.0,
        diameter: float = 0.01,
        pressure: float = 101325.0,
    ) -> ConvectionPrediction:
        del geometry_type, pressure
        if fluid.thermal_conductivity <= 0 or fluid.kinematic_viscosity <= 0 or fluid.prandtl_number <= 0:
            raise ValueError("Akışkan özellikleri pozitif olmalıdır.")
        if flow_type == "forced_external_flat_plate":
            return self._forced_flat_plate(fluid, velocity, characteristic_length)
        if flow_type == "natural_vertical_plate":
            return self._natural_vertical_plate(fluid, characteristic_length, surface_temperature, ambient_temperature)
        if flow_type == "internal_pipe_flow":
            return self._internal_pipe_flow(fluid, velocity, diameter)
        raise ValueError("Desteklenmeyen taşınım senaryosu.")

    def _forced_flat_plate(self, fluid: Fluid, velocity: float, length: float) -> ConvectionPrediction:
        length = max(length, 1e-9)
        velocity = max(velocity, 1e-9)
        re = velocity * length / fluid.kinematic_viscosity
        pr = fluid.prandtl_number
        if re < 5e5:
            nu = 0.664 * re**0.5 * pr ** (1 / 3)
            name = "Forced external flat plate laminar"
            confidence = "medium"
        else:
            nu = 0.037 * re**0.8 * pr ** (1 / 3)
            name = "Forced external flat plate turbulent"
            confidence = "medium"
        h = nu * fluid.thermal_conductivity / length
        return ConvectionPrediction(h, name, re, pr, nu, 0.0, 0.0, "Düz plaka korelasyonu yaklaşık MVP tahminidir.", confidence)

    def _natural_vertical_plate(self, fluid: Fluid, length: float, surface_temperature: float, ambient_temperature: float) -> ConvectionPrediction:
        length = max(length, 1e-9)
        delta_t = max(abs(surface_temperature - ambient_temperature), 1e-9)
        gr = 9.81 * fluid.thermal_expansion_coefficient * delta_t * length**3 / (fluid.kinematic_viscosity**2)
        pr = fluid.prandtl_number
        ra = gr * pr
        if ra < 1e9:
            nu = 0.59 * ra**0.25
            name = "Natural vertical plate laminar"
        else:
            nu = 0.1 * ra ** (1 / 3)
            name = "Natural vertical plate turbulent"
        h = nu * fluid.thermal_conductivity / length
        return ConvectionPrediction(h, name, 0.0, pr, nu, ra, gr, "Dikey plaka doğal taşınım korelasyonu kullanıldı.", "medium")

    def _internal_pipe_flow(self, fluid: Fluid, velocity: float, diameter: float) -> ConvectionPrediction:
        diameter = max(diameter, 1e-9)
        velocity = max(velocity, 1e-9)
        re = velocity * diameter / fluid.kinematic_viscosity
        pr = fluid.prandtl_number
        if re < 2300:
            nu = 3.66
            name = "Internal pipe laminar constant wall temperature"
            confidence = "medium"
        else:
            nu = 0.023 * re**0.8 * pr**0.4
            name = "Internal pipe turbulent Dittus-Boelter"
            confidence = "medium"
        h = nu * fluid.thermal_conductivity / diameter
        return ConvectionPrediction(h, name, re, pr, nu, 0.0, 0.0, "Boru içi akış için temel korelasyon kullanıldı.", confidence)
