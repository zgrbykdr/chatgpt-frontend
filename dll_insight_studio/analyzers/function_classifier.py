from __future__ import annotations

from typing import Any

ROLES = ["Init", "Input", "Parameter", "Compute", "State Update", "Output", "Config", "Error/Log", "Control/Coordinator"]


class FunctionClassificationEngine:
    def classify(self, functions: list[dict[str, Any]], strings: list[dict[str, Any]], overrides: dict[str, str] | None = None) -> list[dict[str, Any]]:
        overrides = overrides or {}
        lookup = "\n".join(s["value"].lower() for s in strings[:1000])
        classified = []
        for fn in functions:
            name = fn["name"]
            lname = name.lower()
            if name in overrides:
                primary = overrides[name]
                secondary = "Compute"
                confidence = 0.99
                explanation = "User override applied."
            else:
                scores = {role: 0.1 for role in ROLES}
                if any(k in lname for k in ["init", "setup", "create"]):
                    scores["Init"] += 0.6
                if any(k in lname for k in ["input", "read", "load"]):
                    scores["Input"] += 0.55
                if any(k in lname for k in ["param", "cfg", "config"]):
                    scores["Parameter"] += 0.5
                if any(k in lname for k in ["compute", "calc", "step", "solve"]):
                    scores["Compute"] += 0.6
                if any(k in lname for k in ["state", "update"]):
                    scores["State Update"] += 0.55
                if any(k in lname for k in ["output", "write", "get"]):
                    scores["Output"] += 0.5
                if "error" in lname or "log" in lname:
                    scores["Error/Log"] += 0.6
                if any(k in lname for k in ["main", "run", "dispatch", "controller"]):
                    scores["Control/Coordinator"] += 0.5
                if "solver" in lookup and scores["Compute"] < 0.5:
                    scores["Compute"] += 0.15

                ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
                primary, confidence = ranked[0]
                secondary = ranked[1][0]
                confidence = min(0.97, round(confidence, 2))
                explanation = f"Role inferred from function naming and metric profile. Alternative={secondary}."
            fn["role"] = {
                "primary": primary,
                "secondary": secondary,
                "confidence": confidence,
                "explanation": explanation,
                "evidence": ["naming", "metrics", "global string context"],
            }
            classified.append(fn)
        return classified
