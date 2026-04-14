from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class RuntimeObservation:
    run_label: str
    notes: str
    changed_regions: str


class RuntimeValidationAssistant:
    def readiness_message(self, exe_path: Path | None) -> str:
        if exe_path and exe_path.exists():
            return "Host EXE is available. You can run guided repeated-run validation to strengthen confidence."
        return "No host EXE selected. Static-only analysis remains fully available; runtime evidence is skipped."

    def compare_runs(self, baseline: RuntimeObservation, changed: RuntimeObservation) -> dict[str, str]:
        clues = []
        if baseline.changed_regions != changed.changed_regions:
            clues.append("Observed changed memory/behavior regions differ between runs.")
        if baseline.notes != changed.notes:
            clues.append("User observations changed after controlled input modification.")
        return {
            "summary": " ".join(clues) or "No clear delta observed.",
            "confidence_impact": "high" if clues else "low",
        }
