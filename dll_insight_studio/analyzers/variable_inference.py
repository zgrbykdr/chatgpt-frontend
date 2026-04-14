from __future__ import annotations

from typing import Any


class VariableInferenceEngine:
    def infer(self, functions: list[dict[str, Any]], strings: list[dict[str, Any]], identity: dict[str, Any]) -> list[dict[str, Any]]:
        variables = []
        candidates = [s for s in strings if s["category"] in {"Possible Inputs", "Possible Outputs", "Possible States", "Possible Parameters", "Units"}]
        for idx, s in enumerate(candidates[:200]):
            cat_map = {
                "Possible Inputs": "input",
                "Possible Outputs": "output",
                "Possible States": "state",
                "Possible Parameters": "parameter",
                "Units": "temporary intermediates",
            }
            name = s["value"][:48].replace(" ", "_")
            if not name.isidentifier():
                name = f"var_{idx:04d}"
            variables.append(
                {
                    "name": name,
                    "category": cat_map.get(s["category"], "unknowns"),
                    "confidence": round(min(0.95, s["confidence"] + 0.1), 2),
                    "region": "managed_field" if identity.get("is_dotnet") else f"offset_group_{idx % 5}",
                    "linked_functions": [f["name"] for f in functions[idx % max(1, len(functions)):][:2]],
                }
            )
        if not variables:
            for i in range(min(25, len(functions))):
                variables.append({
                    "name": f"synthetic_var_{i:03d}",
                    "category": ["inputs", "outputs", "states", "parameters", "flags", "buffers"][i % 6],
                    "confidence": 0.4,
                    "region": f"offset_{hex(0x10 + i * 4)}",
                    "linked_functions": [functions[i]["name"]],
                })
        return variables
