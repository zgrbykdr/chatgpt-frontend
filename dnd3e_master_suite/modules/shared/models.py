from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class LoreRecord:
    id: str
    title: str
    category: str
    summary: str = ""
    tags: List[str] = field(default_factory=list)
    related_records: List[str] = field(default_factory=list)
    notes: str = ""
    status: str = "active"
    created_date: str = ""
    updated_date: str = ""
    favorite: bool = False
    dnd3e: Dict[str, str] = field(default_factory=dict)


@dataclass
class TokenState:
    name: str
    side: str
    color: str
    hp: int
    ac: int
    initiative: int
    init_mod: int = 0
    speed: int = 30
    conditions: List[str] = field(default_factory=list)
    bab: str = "+0"
    saves: Dict[str, str] = field(default_factory=lambda: {"Fort": "+0", "Ref": "+0", "Will": "+0"})
    size: str = "Medium"
    spellcaster: bool = False
    caster_level: str = ""
    attack_notes: str = ""
    ac_breakdown: str = ""
    xp_note: str = ""
