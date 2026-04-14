from __future__ import annotations

import re
from pathlib import Path

from .models import API_STRING_CLUES


STR_RE = re.compile(rb"[ -~]{4,}")


class DLLAnalyzer:
    def _read_arch(self, data: bytes) -> str:
        if data[:2] != b"MZ":
            return "unknown"
        pe_off = int.from_bytes(data[0x3C:0x40], "little")
        machine = int.from_bytes(data[pe_off + 4:pe_off + 6], "little")
        return {0x8664: "x64", 0x14C: "x86"}.get(machine, f"machine_{machine:x}")

    def _strings(self, data: bytes) -> list[str]:
        vals = [m.decode("latin1", errors="ignore") for m in STR_RE.findall(data)]
        return vals

    def analyze_dll(self, dll_path: Path) -> dict:
        data = dll_path.read_bytes()
        all_strings = self._strings(data)
        clue_hits = [s for s in all_strings if any(k in s for k in API_STRING_CLUES)]
        lower = dll_path.name.lower()
        probable = "candidate_binary"
        why = "heuristic"
        conf = 0.5
        if lower == "alfacalcinterface.dll":
            probable, conf, why = "interface_api_facade", 0.95, "known interface naming + clues"
        elif lower == "cascalc.dll":
            probable, conf, why = "core_orchestrator", 0.9, "core package naming"
        elif lower == "refprp64.dll":
            probable, conf, why = "property_backend", 0.95, "known property backend naming"
        elif lower in {"phecalc.dll", "hecalc.dll", "shecalc.dll", "p3calc.dll", "nips.dll"}:
            probable, conf, why = "domain_compute_support", 0.78, "domain solver candidate"
        return {
            "dll_name": dll_path.name,
            "architecture": self._read_arch(data),
            "export_count": 0,
            "import_count": 0,
            "exports": [],
            "imports": [],
            "strings": all_strings[:5000],
            "string_clue_count": len(clue_hits),
            "probable_role": probable,
            "confidence": conf,
            "why": why,
        }

    def analyze_package(self, root: Path) -> list[dict]:
        results: list[dict] = []
        for p in root.glob("*.dll"):
            results.append(self.analyze_dll(p))
        return results
