from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass
class Card:
    title: str
    description: str
    actions: List[Dict[str, Any]] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
