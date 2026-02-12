from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from uuid import uuid4
from datetime import datetime


def uid(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:10]}"


def now_iso() -> str:
    return datetime.utcnow().isoformat()


ABILITY_KEYS = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]


def default_ability_block() -> Dict[str, int]:
    return {
        "base": 10,
        "racial": 0,
        "level": 0,
        "enhancement": 0,
        "circumstance": 0,
        "morale": 0,
        "misc": 0,
    }


@dataclass
class Character:
    id: str = field(default_factory=lambda: uid("char"))
    type: str = "PC"
    archived: bool = False
    tags: List[str] = field(default_factory=lambda: ["party"])
    identity: Dict[str, Any] = field(default_factory=lambda: {
        "name": "New Character",
        "player": "",
        "race": "",
        "classLevels": [{"classId": "fighter", "level": 1}],
        "alignment": "",
        "deity": "",
        "size": "Medium",
        "age": "",
        "gender": "",
        "heightWeight": "",
        "appearance": "",
        "homeland": "",
        "languages": [],
    })
    abilities: Dict[str, Dict[str, int]] = field(default_factory=lambda: {k: default_ability_block() for k in ABILITY_KEYS})
    hp: Dict[str, Any] = field(default_factory=lambda: {
        "max": 10,
        "current": 10,
        "temp": 0,
        "nonlethal": 0,
        "damageReduction": "",
        "energyResistances": [],
        "immunities": [],
        "fastHealing": 0,
        "regeneration": 0,
        "stableAtNegative": True,
        "log": [],
    })
    combat: Dict[str, Any] = field(default_factory=lambda: {
        "baseAttackBonus": 1,
        "grappleMisc": 0,
        "initiativeMisc": 0,
        "speed": {"land": 30, "fly": 0, "swim": 0, "climb": 0, "burrow": 0},
        "ac": {"armor": 0, "shield": 0, "size": 0, "natural": 0, "deflection": 0, "dodge": 0, "misc": 0, "dexCap": None},
        "attacks": [],
    })
    saves: Dict[str, Any] = field(default_factory=lambda: {
        "Fort": {"base": 2, "misc": 0},
        "Ref": {"base": 0, "misc": 0},
        "Will": {"base": 0, "misc": 0},
        "conditional": [],
    })
    skills: List[Dict[str, Any]] = field(default_factory=list)
    feats: List[Dict[str, Any]] = field(default_factory=list)
    featChoices: List[Dict[str, Any]] = field(default_factory=list)
    spells: Dict[str, Any] = field(default_factory=lambda: {
        "classes": [], "prepared": {}, "expended": {}, "known": {}, "spontaneous": False,
        "concentration": 0, "spellFailure": 0, "spellPenetrationNotes": "", "notes": ""
    })
    equipment: Dict[str, Any] = field(default_factory=lambda: {"inventory": [], "currency": {"cp": 0, "sp": 0, "gp": 0, "pp": 0}})
    specialAbilities: List[Dict[str, Any]] = field(default_factory=list)
    effects: List[Dict[str, Any]] = field(default_factory=list)
    notes: Dict[str, str] = field(default_factory=lambda: {"persistent": "", "session": ""})
    modifiers: List[Dict[str, Any]] = field(default_factory=list)
    derived: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Campaign:
    schemaVersion: int = 1
    id: str = field(default_factory=lambda: uid("camp"))
    name: str = "New Campaign"
    createdAt: str = field(default_factory=now_iso)
    updatedAt: str = field(default_factory=now_iso)
    globalNotes: str = ""
    sessionNotes: str = ""
    currentRound: int = 1
    currentTurnCharacterId: Optional[str] = None
    initiativeOrder: List[str] = field(default_factory=list)
    filePath: Optional[str] = None
    libraries: Dict[str, Any] = field(default_factory=lambda: {
        "feats": [], "spells": [], "conditions": [], "items": [],
        "imports": {"sourceFiles": [], "featRows": [], "mappings": []}
    })
    characters: List[Character] = field(default_factory=lambda: [Character()])

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["characters"] = [asdict(c) for c in self.characters]
        return payload


def migrate_campaign(raw: Dict[str, Any]) -> Campaign:
    base = Campaign()
    if not raw:
        return base
    data = base.to_dict()
    data.update(raw)
    chars = []
    for ch in raw.get("characters", []):
        merged = asdict(Character())
        merged.update(ch)
        chars.append(Character(**merged))
    if not chars:
        chars = [Character()]
    data["characters"] = chars
    return Campaign(**{k: v for k, v in data.items() if k != "characters"}, characters=chars)
