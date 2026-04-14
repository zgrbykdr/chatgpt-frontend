from __future__ import annotations

from .models import API_STRING_CLUES, InterfaceCandidate


class InterfaceDiscoveryEngine:
    def discover(self, dll_findings: list[dict]) -> list[InterfaceCandidate]:
        candidates: list[InterfaceCandidate] = []
        order_map = {"CreateItem": 1, "CheckFluid": 2, "Calculate": 3, "CalculateEx": 3, "GetAltStringValue": 4, "DeleteItem": 5}
        for finding in dll_findings:
            dll_name = finding["dll_name"]
            for s in finding.get("strings", []):
                for clue in API_STRING_CLUES:
                    if clue in s:
                        candidates.append(
                            InterfaceCandidate(
                                dll_name=dll_name,
                                function_name=clue,
                                probable_purpose=self._purpose(clue),
                                call_order_guess=order_map.get(clue, 3),
                                parameter_semantics="likely handle + variable name + value",
                                confidence=0.6 if dll_name.lower() != "alfacalcinterface.dll" else 0.9,
                                evidence=f"string clue in {dll_name}: {s[:80]}",
                            )
                        )
        # dedupe
        dedup: dict[tuple[str, str], InterfaceCandidate] = {}
        for c in candidates:
            dedup[(c.dll_name, c.function_name)] = c
        return sorted(dedup.values(), key=lambda x: (x.dll_name, x.call_order_guess, x.function_name))

    def _purpose(self, fn: str) -> str:
        if "Create" in fn:
            return "create calculation object"
        if "Delete" in fn:
            return "destroy/free object"
        if "Calculate" in fn:
            return "execute calculation"
        if "Fluid" in fn:
            return "fluid handling"
        if fn.startswith("Get"):
            return "read value"
        return "unknown API role"
