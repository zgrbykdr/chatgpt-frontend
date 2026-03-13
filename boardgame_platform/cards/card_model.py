from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class Card:
    title: str
    description: str
    actions: List[Dict[str, Any]] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "Card":
        return cls(
            title=payload["title"],
            description=payload.get("description", ""),
            actions=payload.get("actions", []),
            conditions=payload.get("conditions", {}),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "description": self.description,
            "actions": self.actions,
            "conditions": self.conditions,
        }
