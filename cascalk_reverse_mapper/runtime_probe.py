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

    def host_assisted_record(self, before: dict, after: dict, notes: str) -> dict:
        deltas = {}
        for k, v in after.items():
            if k in before and isinstance(v, (int, float)) and isinstance(before[k], (int, float)):
                deltas[k] = v - before[k]
        return {"status": "recorded", "error": "", "outputs": after, "deltas": deltas, "notes": notes}
