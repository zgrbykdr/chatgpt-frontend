from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from core.boundary import BoundaryCondition
from core.interface import Interface
from core.material import material_by_name
from core.project import Project
from core.thermal_network import ThermalNetwork


@dataclass
class SolverResult:
    success: bool
    message: str
    temperatures: dict[str, float] = field(default_factory=dict)
    energy_in: float = 0.0
    energy_out: float = 0.0
    energy_error_percent: float = 0.0
    warnings: list[str] = field(default_factory=list)
    heat_flows: list[dict[str, Any]] = field(default_factory=list)


class ThermalResistanceSolver:
    def solve(self, project: Project) -> SolverResult:
        warnings = project.validate_project()
        fatal = [w for w in warnings if w.startswith(("Invalid geometry", "Invalid h value", "Invalid thermal conductivity", "No boundary condition", "No fixed"))]
        if fatal:
            return SolverResult(False, "; ".join(fatal), warnings=warnings)
        if not project.parts:
            return SolverResult(False, "Modelde parça yok.", warnings=warnings)
        network = ThermalNetwork([part.id for part in project.parts])
        try:
            self._add_parts(project, network)
            self._add_boundaries(project, network)
            self._add_interfaces(project, network)
            temps_array = network.solve()
        except np.linalg.LinAlgError:
            return SolverResult(False, "Model çözülemedi. En az bir fixed temperature veya convection boundary tanımlayın.", warnings=warnings)
        except Exception as exc:
            return SolverResult(False, f"Solver hatası: {exc}", warnings=warnings)
        temperatures = {part.id: float(temps_array[i]) for i, part in enumerate(project.parts)}
        heat_flows, energy_out = self._calculate_heat_flows(project, network, temperatures)
        energy_in = sum(max(part.heat_power, 0.0) for part in project.parts) + sum(max(b.value, 0.0) for b in project.boundaries if b.type == "heat_power")
        error = abs(energy_in - energy_out) / max(abs(energy_in), 1e-9) * 100.0 if energy_in > 0 else 0.0
        if error > 5:
            warnings.append("Energy balance error percent exceeds 5%")
        for part in project.parts:
            part.temperature_result = temperatures[part.id]
        result = SolverResult(True, "Solver başarıyla tamamlandı.", temperatures, energy_in, energy_out, error, warnings, heat_flows)
        project.results = {
            "solver_status": result.message,
            "temperatures": temperatures,
            "energy_in": energy_in,
            "energy_out": energy_out,
            "energy_error_percent": error,
            "warnings": warnings,
            "heat_flows": heat_flows,
        }
        project.touch()
        return result

    def _add_parts(self, project: Project, network: ThermalNetwork) -> None:
        for part in project.parts:
            material = material_by_name(project.materials, part.material_name)
            if material.thermal_conductivity <= 0 or part.area() <= 0:
                raise ValueError(f"Geçersiz malzeme veya alan: {part.name}")
            if part.heat_power:
                network.add_heat_source(part.id, part.heat_power)

    def _add_boundaries(self, project: Project, network: ThermalNetwork) -> None:
        for boundary in project.boundaries:
            part = project.get_part_by_id(boundary.part_id)
            if not part or boundary.type == "adiabatic":
                continue
            if boundary.type == "fixed_temperature":
                network.add_fixed_temperature(part.id, boundary.value)
            elif boundary.type == "heat_power":
                network.add_heat_source(part.id, boundary.value)
            elif boundary.type == "heat_flux":
                area = part.area()
                if area <= 0:
                    raise ValueError(f"Alan geçersiz: {part.name}")
                network.add_heat_source(part.id, boundary.value * area)
            elif boundary.type == "convection":
                area = self._face_area(part, boundary)
                if boundary.h_value <= 0 or area <= 0:
                    raise ValueError("h değeri ve alan pozitif olmalıdır.")
                network.add_ambient_resistance(part.id, 1.0 / (boundary.h_value * area), boundary.ambient_temperature, f"convection:{boundary.id}")

    def _add_interfaces(self, project: Project, network: ThermalNetwork) -> None:
        for interface in project.interfaces:
            if interface.type == "adiabatic":
                continue
            resistance = self._interface_resistance(project, interface)
            network.add_between_resistance(interface.part_a_id, interface.part_b_id, resistance, f"interface:{interface.id}")

    def _interface_resistance(self, project: Project, interface: Interface) -> float:
        if interface.type == "perfect_contact":
            return 1e-9
        if interface.type == "contact_resistance":
            return max(interface.contact_resistance, 1e-12)
        area = max(interface.contact_area, 1e-12)
        material_name = "Air Gap Equivalent" if interface.type == "air_gap" else interface.material_name
        material = material_by_name(project.materials, material_name)
        if material.thermal_conductivity <= 0:
            raise ValueError(f"Invalid thermal conductivity: {material.name}")
        return max(interface.thickness, 1e-12) / (material.thermal_conductivity * area)

    def _face_area(self, part, boundary: BoundaryCondition) -> float:
        if boundary.face in {"front", "back", "all"}:
            return part.area()
        if boundary.face in {"left", "right"}:
            return max(part.height * part.thickness, 0.0)
        return max(part.width * part.thickness, 0.0)

    def _calculate_heat_flows(self, project: Project, network: ThermalNetwork, temperatures: dict[str, float]) -> tuple[list[dict[str, Any]], float]:
        flows: list[dict[str, Any]] = []
        out_total = 0.0
        fixed_nodes = {link["node"] for link in network.heat_links if link["type"] == "fixed_temperature"}
        fixed_balance = {node: self._node_heat_source(project, node) for node in fixed_nodes}

        for link in network.heat_links:
            if link["type"].startswith("convection"):
                node = link["node"]
                q = (temperatures[node] - link["ambient"]) / link["resistance"]
                flows.append({"label": link["type"], "heat_flow_w": q})
                if node in fixed_balance:
                    fixed_balance[node] -= q
                if q > 0:
                    out_total += q
            elif link["type"].startswith("interface"):
                node_a = link["node_a"]
                node_b = link["node_b"]
                qa = (temperatures[node_a] - temperatures[node_b]) / link["resistance"]
                flows.append({"label": link["type"], "heat_flow_w": qa})
                if node_a in fixed_balance:
                    fixed_balance[node_a] -= qa
                if node_b in fixed_balance:
                    fixed_balance[node_b] += qa

        for node, heat_flow in fixed_balance.items():
            flows.append({"label": f"fixed_temperature:{node}", "heat_flow_w": heat_flow})
            if heat_flow > 0:
                out_total += heat_flow
        return flows, out_total

    def _node_heat_source(self, project: Project, node_id: str) -> float:
        part = project.get_part_by_id(node_id)
        heat_source = part.heat_power if part else 0.0
        for boundary in project.boundaries:
            if boundary.part_id != node_id:
                continue
            if boundary.type == "heat_power":
                heat_source += boundary.value
            elif boundary.type == "heat_flux" and part:
                heat_source += boundary.value * self._face_area(part, boundary)
        return heat_source
