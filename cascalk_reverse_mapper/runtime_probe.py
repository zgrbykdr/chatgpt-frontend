from __future__ import annotations

import ctypes
import json
from pathlib import Path


class RuntimeProbeEngine:
    def direct_probe(self, root: Path, inputs: dict[str, float | str | bool]) -> dict:
        dll = root / "AlfaCalcInterface.dll"
        if not dll.exists():
            return {"status": "failed", "error": "AlfaCalcInterface.dll missing", "outputs": {}}
        try:
            lib = ctypes.WinDLL(str(dll))  # type: ignore[attr-defined]
        except Exception as e:
            return {"status": "failed", "error": f"load failure: {e}", "outputs": {}}
        found = {name: hasattr(lib, name) for name in ["CreateItem", "Calculate", "CalculateEx", "DeleteItem"]}
        return {
            "status": "partial",
            "error": "Direct invocation requires manual signature setup",
            "outputs": {"interface_presence": json.dumps(found), "echo_input_count": len(inputs)},
        }

    def semi_auto_probe(self, root: Path, inputs: dict[str, float | str | bool]) -> dict:
        """
        Try direct probing first; if signatures are unknown, fall back to
        a deterministic heuristic output model so the workflow can continue.
        """
        res = self.direct_probe(root, inputs)
        if res.get("status") == "failed":
            res = {"status": "inferred", "error": res.get("error", ""), "outputs": {}}
        if res.get("status") == "partial":
            cold = float(inputs.get("InTempSide1", 20.0))
            hot = float(inputs.get("InTempSide2", 40.0))
            dp1 = float(inputs.get("PressureSide1", 2.0))
            dp2 = float(inputs.get("PressureSide2", 2.0))
            heat_load = max(0.0, (hot - cold) * 12.5)
            effective_area = 0.8 * (hot + cold) / 2.0
            inferred = {
                "HeatLoad": heat_load,
                "EffectiveArea": effective_area,
                "InPressSide1": dp1,
                "InPressSide2": dp2,
                "Error": "",
                "InferenceMode": "semi_auto_heuristic",
            }
            return {"status": "semi_auto", "error": "Function signatures unresolved; heuristic continuation applied.", "outputs": inferred}
        return res

    def host_assisted_record(self, before: dict, after: dict, notes: str) -> dict:
        deltas = {}
        for k, v in after.items():
            if k in before and isinstance(v, (int, float)) and isinstance(before[k], (int, float)):
                deltas[k] = v - before[k]
        return {"status": "recorded", "error": "", "outputs": after, "deltas": deltas, "notes": notes}
