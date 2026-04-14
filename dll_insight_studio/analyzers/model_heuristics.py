from __future__ import annotations

from typing import Any


class ModelHeuristicEngine:
    PATTERNS = [
        "discrete step simulation",
        "state-space model",
        "continuous-time approximated solver",
        "controller",
        "rule-based decision model",
        "lookup-table model",
        "optimization or iterative solver",
        "signal-processing pipeline",
        "FMU-style wrapper",
        "config-driven engine",
    ]

    def rank_patterns(self, functions: list[dict[str, Any]], strings: list[dict[str, Any]], identity: dict[str, Any]) -> list[dict[str, Any]]:
        corpus = "\n".join(s["value"].lower() for s in strings[:2000])
        out = []
        for pattern in self.PATTERNS:
            score = 0.2
            evidence = []
            if "solver" in corpus and "solver" in pattern:
                score += 0.45
                evidence.append("solver-like strings detected")
            if "state" in corpus and "state" in pattern:
                score += 0.35
                evidence.append("state-related strings detected")
            if "fmu" in corpus and "fmu" in pattern.lower():
                score += 0.55
                evidence.append("FMI/FMU identifiers present")
            if any(fn["role"]["primary"] == "Control/Coordinator" for fn in functions) and "controller" in pattern:
                score += 0.3
                evidence.append("control/coordinator functions detected")
            if identity.get("is_dotnet") and "config-driven" in pattern:
                score += 0.15
                evidence.append("managed metadata usually accompanies config-oriented wrappers")
            out.append({"pattern": pattern, "confidence": round(min(score, 0.98), 2), "evidence": "; ".join(evidence) or "generic structural indicators"})
        out.sort(key=lambda x: x["confidence"], reverse=True)
        return out
