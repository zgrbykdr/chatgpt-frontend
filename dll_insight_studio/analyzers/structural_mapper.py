from __future__ import annotations

from typing import Any


class StructuralMapper:
    def map_structure(self, identity: dict[str, Any], metadata: dict[str, Any]) -> dict[str, Any]:
        if identity.get("is_dotnet"):
            return self._dotnet_structure(metadata)
        return self._native_structure(metadata)

    def _dotnet_structure(self, metadata: dict[str, Any]) -> dict[str, Any]:
        method_like = [s for s in metadata.get("strings", []) if "::" in s or "." in s and "(" in s]
        methods = [{"name": m[:80], "size": len(m), "cluster": "ManagedMethod"} for m in method_like[:200]]
        return {
            "branch": ".NET",
            "namespaces": sorted({m.split(".")[0] for m in method_like if "." in m})[:100],
            "classes": sorted({m.split(".")[-2] for m in method_like if m.count(".") >= 2})[:100],
            "functions": methods,
            "call_graph": [{"from": methods[i]["name"], "to": methods[i + 1]["name"]} for i in range(0, max(0, len(methods) - 1), 2)],
        }

    def _native_structure(self, metadata: dict[str, Any]) -> dict[str, Any]:
        functions = []
        for idx, exp in enumerate(metadata.get("exports", [])):
            name = exp.get("name") or f"sub_{idx:04X}"
            metrics = {
                "branch_density": (idx % 7) / 7,
                "arithmetic_density": (idx % 5) / 5,
                "memory_access_density": (idx % 3) / 3,
                "fan_in": (idx % 9),
                "fan_out": (idx % 6),
                "constant_usage": (idx % 11),
            }
            functions.append({"name": name, "address": hex(0x1000 + idx * 0x20), "size": 32 + (idx % 20) * 8, "metrics": metrics})
        if not functions:
            for i, s in enumerate(metadata.get("strings", [])[:40]):
                functions.append({"name": f"sub_{i:04X}", "address": hex(0x2000 + i * 0x30), "size": 64, "metrics": {"branch_density": 0.3, "arithmetic_density": 0.3, "memory_access_density": 0.4, "fan_in": 1, "fan_out": 1, "constant_usage": len(s) % 10}})
        return {
            "branch": "Native",
            "functions": functions,
            "call_graph": [{"from": functions[i]["name"], "to": functions[(i + 1) % len(functions)]["name"]} for i in range(min(len(functions), 100))],
            "offset_clusters": [
                {"region": "region_A", "offsets": [hex(0x10 + i * 4) for i in range(6)]},
                {"region": "region_B", "offsets": [hex(0x80 + i * 8) for i in range(4)]},
            ],
        }
