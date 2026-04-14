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


def is_meaningful_text(value: str) -> bool:
    if len(value.strip()) < 3:
        return False
    letters = sum(ch.isalpha() for ch in value)
    digits = sum(ch.isdigit() for ch in value)
    spaces = sum(ch.isspace() for ch in value)
    visible = sum(ch.isprintable() for ch in value)
    punctuation = len(value) - letters - digits - spaces
    if visible < max(3, int(len(value) * 0.9)):
        return False
    if letters == 0 and digits < 2:
        return False
    punct_ratio = punctuation / max(1, len(value))
    if punct_ratio > 0.45 and letters < 4:
        return False
    return True


class StringIntelligenceEngine:
    def classify(self, values: list[str], manual_labels: dict[str, str] | None = None) -> list[dict[str, Any]]:
        labels = manual_labels or {}
        output = []
        for value in values:
            if not is_meaningful_text(value):
                output.append({"value": value, "category": "Noise/Encoded", "confidence": 0.05, "source": "auto"})
                continue
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
