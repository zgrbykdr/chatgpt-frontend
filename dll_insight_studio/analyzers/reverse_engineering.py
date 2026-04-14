from __future__ import annotations

import re
from pathlib import Path
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
            {
                "library": lib,
                "count": len(symbols),
                "symbols": sorted(s for s in symbols if s)[:50],
                "is_system": self._is_system_library(lib),
            }
            for lib, symbols in sorted(grouped.items(), key=lambda kv: len(kv[1]), reverse=True)
        ]

    @staticmethod
    def _is_system_library(lib: str) -> bool:
        name = lib.lower()
        prefixes = ("api-ms-win-", "ext-ms-win-")
        common = {
            "kernel32.dll",
            "user32.dll",
            "advapi32.dll",
            "gdi32.dll",
            "ole32.dll",
            "oleaut32.dll",
            "ucrtbase.dll",
            "vcruntime140.dll",
            "msvcp140.dll",
            "ntdll.dll",
        }
        return name.startswith(prefixes) or name in common

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

    def infer_parameter_ranges(self, strings: list[dict[str, Any]], variables: list[dict[str, Any]]) -> list[dict[str, Any]]:
        corpus = "\n".join(s["value"] for s in strings[:5000])
        numeric_values = [float(v) for v in re.findall(r"[-+]?\d+(?:\.\d+)?", corpus)[:1000]]
        if numeric_values:
            baseline_min = min(numeric_values)
            baseline_max = max(numeric_values)
        else:
            baseline_min = 0.0
            baseline_max = 1.0

        ranges = []
        for var in variables[:80]:
            cat = var.get("category", "").lower()
            if cat not in {"parameter", "input"}:
                continue
            name = var["name"]
            factor = 0.1 if cat == "parameter" else 0.05
            min_val = baseline_min * (1 - factor)
            max_val = baseline_max * (1 + factor)
            ranges.append(
                {
                    "name": name,
                    "category": cat,
                    "min": round(min_val, 6),
                    "max": round(max_val, 6),
                    "default": round((min_val + max_val) / 2, 6),
                    "source": "heuristic_from_constants",
                }
            )
        return ranges

    def export_dymola_lookup_csv(self, rows: list[dict[str, Any]], output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        headers = ["name", "category", "region", "confidence", "min", "max", "default", "source"]
        with output_path.open("w", encoding="utf-8") as fh:
            fh.write(",".join(headers) + "\n")
            for row in rows:
                fh.write(
                    ",".join(
                        [
                            str(row.get("name", "")),
                            str(row.get("category", "")),
                            str(row.get("region", "")),
                            str(row.get("confidence", "")),
                            str(row.get("min", "")),
                            str(row.get("max", "")),
                            str(row.get("default", "")),
                            str(row.get("source", "")),
                        ]
                    )
                    + "\n"
                )
        return output_path
