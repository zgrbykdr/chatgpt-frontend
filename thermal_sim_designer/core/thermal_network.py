from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass
class ThermalNetwork:
    node_ids: list[str]
    matrix: np.ndarray = field(init=False)
    vector: np.ndarray = field(init=False)
    heat_links: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        n = len(self.node_ids)
        self.matrix = np.zeros((n, n), dtype=float)
        self.vector = np.zeros(n, dtype=float)

    def index(self, node_id: str) -> int:
        return self.node_ids.index(node_id)

    def add_heat_source(self, node_id: str, power: float) -> None:
        self.vector[self.index(node_id)] += power

    def add_fixed_temperature(self, node_id: str, temperature: float) -> None:
        idx = self.index(node_id)
        penalty = 1e12
        self.matrix[idx, idx] += penalty
        self.vector[idx] += penalty * temperature
        self.heat_links.append({"type": "fixed_temperature", "node": node_id, "temperature": temperature})

    def add_ambient_resistance(self, node_id: str, resistance: float, ambient: float, label: str) -> None:
        if resistance <= 0:
            raise ValueError("Direnç pozitif olmalıdır.")
        idx = self.index(node_id)
        conductance = 1.0 / resistance
        self.matrix[idx, idx] += conductance
        self.vector[idx] += conductance * ambient
        self.heat_links.append({"type": label, "node": node_id, "resistance": resistance, "ambient": ambient})

    def add_between_resistance(self, node_a: str, node_b: str, resistance: float, label: str) -> None:
        if resistance <= 0:
            raise ValueError("Interface direnci pozitif olmalıdır.")
        ia = self.index(node_a)
        ib = self.index(node_b)
        conductance = 1.0 / resistance
        self.matrix[ia, ia] += conductance
        self.matrix[ib, ib] += conductance
        self.matrix[ia, ib] -= conductance
        self.matrix[ib, ia] -= conductance
        self.heat_links.append({"type": label, "node_a": node_a, "node_b": node_b, "resistance": resistance})

    def solve(self) -> np.ndarray:
        return np.linalg.solve(self.matrix, self.vector)
