from __future__ import annotations

import re
from typing import Any


class ReverseEngineeringEnhancer:
    FMU_HINTS = ("fmi", "fmu", "modeldescription", "valueReference", "scalarvariable")

    def build_dependency_map(self, metadata: dict[str, Any]) -> list[dict[str, Any]]:
        grouped: dict[str, set[str]] = {}
        for imp in metadata.get("imports", []):
            lib = imp.get("library", "unknown")
            symbol = imp.get("name", "")
            grouped.setdefault(lib, set()).add(symbol)
        return [
            {"library": lib, "count": len(symbols), "symbols": sorted(s for s in symbols if s)[:50]}
            for lib, symbols in sorted(grouped.items(), key=lambda kv: len(kv[1]), reverse=True)
        ]

    def extract_constants(self, metadata: dict[str, Any], strings: list[dict[str, Any]]) -> dict[str, list[str]]:
        numeric = set(metadata.get("numeric_constants", []))
        scientific = set()
        for item in strings:
            val = item["value"]
            for hit in re.findall(r"[-+]?\d+(?:\.\d+)?(?:e[-+]?\d+)?", val.lower()):
                if len(hit) <= 24:
                    scientific.add(hit)
        return {
            "numeric_constants": sorted(numeric)[:300],
            "scientific_constants": sorted(scientific)[:300],
        }

    def build_fmu_lookup_table(self, strings: list[dict[str, Any]], variables: list[dict[str, Any]]) -> list[dict[str, Any]]:
        table: list[dict[str, Any]] = []
        seen: set[str] = set()
        for var in variables:
            name = var.get("name", "")
            if not name or name in seen:
                continue
            seen.add(name)
            source = "variable_inference"
            if any(h in name.lower() for h in self.FMU_HINTS):
                source = "fmu_hint"
            table.append(
                {
                    "name": name,
                    "category": var.get("category", "unknown"),
                    "region": var.get("region", "unknown"),
                    "confidence": var.get("confidence", 0.0),
                    "source": source,
                }
            )
        for s in strings:
            text = s["value"]
            ltext = text.lower()
            if any(h in ltext for h in self.FMU_HINTS):
                candidate = re.sub(r"[^a-zA-Z0-9_]+", "_", text).strip("_")[:64]
                if candidate and candidate not in seen:
                    seen.add(candidate)
                    table.append(
                        {
                            "name": candidate,
                            "category": "fmu_related",
                            "region": "string_derived",
                            "confidence": s.get("confidence", 0.3),
                            "source": "fmu_string",
                        }
                    )
        return table[:800]

    def build_doe_plan(self, variables: list[dict[str, Any]]) -> list[dict[str, Any]]:
        doables = [v for v in variables if v.get("category", "").lower() in {"parameter", "input"}]
        plan = []
        for var in doables[:40]:
            name = var["name"]
            plan.append(
                {
                    "parameter": name,
                    "baseline": "current",
                    "low_step": "-10%",
                    "high_step": "+10%",
                    "objective": "Measure change in output/state confidence linkage",
                    "priority": "high" if var.get("confidence", 0) > 0.75 else "medium",
                }
            )
        return plan
