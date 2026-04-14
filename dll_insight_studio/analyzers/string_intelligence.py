from __future__ import annotations

from typing import Any


CATEGORIES = {
    "Possible Inputs": ["input", "set", "source", "read"],
    "Possible Outputs": ["output", "result", "write", "export"],
    "Possible States": ["state", "cache", "history", "prev"],
    "Possible Parameters": ["param", "gain", "threshold", "coefficient"],
    "Possible Config Terms": ["config", "option", "setting", "profile"],
    "File Paths": ["\\", "/", ".ini", ".json", ".xml"],
    "Units": ["ms", "kg", "hz", "rpm", "volt", "amp"],
    "Error Messages": ["error", "failed", "invalid", "exception", "timeout"],
    "Solver Terms": ["solver", "integrator", "ode", "jacobian"],
    "FMI/FMU Terms": ["fmi", "fmu", "modeldescription", "co-simulation"],
    "Numeric/Scientific Terms": ["matrix", "vector", "fft", "sigma", "delta"],
}


class StringIntelligenceEngine:
    def classify(self, values: list[str], manual_labels: dict[str, str] | None = None) -> list[dict[str, Any]]:
        labels = manual_labels or {}
        output = []
        for value in values:
            if value in labels:
                output.append({"value": value, "category": labels[value], "confidence": 0.99, "source": "user"})
                continue
            lv = value.lower()
            best = "Unknown but important"
            best_score = 0.05
            for category, keywords in CATEGORIES.items():
                hits = sum(1 for kw in keywords if kw in lv)
                if hits:
                    score = min(0.9, 0.2 + (hits * 0.25))
                    if score > best_score:
                        best = category
                        best_score = score
            if len(value) > 40 and best == "Unknown but important":
                best_score = 0.35
            output.append({"value": value, "category": best, "confidence": round(best_score, 2), "source": "auto"})
        return output
