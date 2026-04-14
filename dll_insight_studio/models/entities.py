from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class ProjectConfig:
    name: str
    dll_path: Path
    exe_path: Path | None = None
    related_dir: Path | None = None
    mode: str = "Guided"
    depth: str = "Standard"


@dataclass
class Evidence:
    source: str
    weight: float
    details: str


@dataclass
class ScoredItem:
    label: str
    confidence: float
    evidence: list[Evidence] = field(default_factory=list)
    alternative: str | None = None


@dataclass
class AnalysisSummary:
    project_id: int
    file_identity: dict[str, Any]
    metadata: dict[str, Any]
    strings: list[dict[str, Any]]
    functions: list[dict[str, Any]]
    variables: list[dict[str, Any]]
    patterns: list[dict[str, Any]]
    runtime_notes: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class GuidanceDecision:
    project_id: int
    step_key: str
    prompt: str
    choice: str
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
