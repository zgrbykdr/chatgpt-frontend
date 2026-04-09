from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

from .enums import WorkflowMode


class WorkflowConfig(BaseModel):
    mode: WorkflowMode = WorkflowMode.AUTOMATIC
    target_outputs: list[str] = Field(default_factory=list)


class AppConfig(BaseModel):
    project: dict[str, Any] = Field(default_factory=dict)
    workflow: WorkflowConfig = Field(default_factory=WorkflowConfig)
    model_search: dict[str, Any] = Field(default_factory=dict)
    evaluation: dict[str, Any] = Field(default_factory=dict)
    execution: dict[str, Any] = Field(default_factory=dict)
    exports: dict[str, Any] = Field(default_factory=dict)


def load_config(path: str | Path) -> AppConfig:
    with Path(path).open("r", encoding="utf-8") as f:
        payload = yaml.safe_load(f) or {}
    return AppConfig.model_validate(payload)
