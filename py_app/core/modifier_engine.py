from __future__ import annotations
from typing import Dict, List, Any
from .models import Character, ABILITY_KEYS

STACKING_RULES = {
    "default": "max",
    "dodge": "stack",
    "circumstance": "stack",
    "untyped": "stack",
    "penalty": "stack",
}


def ability_mod(score: int) -> int:
    return (score - 10) // 2


def _sum_target(mods: List[Dict[str, Any]], target: str) -> int:
    return sum(int(m.get("value", 0)) for m in mods if m.get("target") == target and m.get("active", True))


def _stack(mods: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    buckets: Dict[str, List[Dict[str, Any]]] = {}
    for mod in mods:
        if mod.get("active", True) is False:
            continue
        btype = str(mod.get("bonusType", "untyped")).lower()
        key = f"{mod.get('target')}|{btype}"
        buckets.setdefault(key, []).append(mod)

    resolved: List[Dict[str, Any]] = []
    for key, entries in buckets.items():
        btype = key.split("|", 1)[1]
        mode = STACKING_RULES.get(btype, STACKING_RULES["default"])
        if mode == "stack":
            resolved.extend(entries)
        else:
            resolved.append(max(entries, key=lambda x: int(x.get("value", 0))))
    return resolved


def _collect_modifiers(c: Character) -> List[Dict[str, Any]]:
    base = list(c.modifiers or [])
    feats = [m for feat in (c.featChoices or []) if feat.get("active", True) for m in feat.get("modifiers", [])]
    effects = [m for fx in (c.effects or []) if fx.get("active", True) for m in fx.get("modifiers", [])]
    return base + feats + effects


def recalc_character(c: Character) -> Character:
    mods = _stack(_collect_modifiers(c))

    abilities = {}
    for key in ABILITY_KEYS:
        score = sum(int(v) for v in c.abilities[key].values()) + _sum_target(mods, f"ability.{key}")
        abilities[key] = {"score": score, "mod": ability_mod(score)}

    dex_mod = abilities["DEX"]["mod"]
    dex_cap = c.combat["ac"].get("dexCap")
    dex_for_ac = min(dex_mod, dex_cap) if dex_cap is not None else dex_mod

    initiative = dex_mod + int(c.combat.get("initiativeMisc", 0)) + _sum_target(mods, "initiative")

    ac_total = (
        10 + int(c.combat["ac"].get("armor", 0)) + int(c.combat["ac"].get("shield", 0)) + dex_for_ac
        + int(c.combat["ac"].get("size", 0)) + int(c.combat["ac"].get("natural", 0))
        + int(c.combat["ac"].get("deflection", 0)) + int(c.combat["ac"].get("dodge", 0))
        + int(c.combat["ac"].get("misc", 0)) + _sum_target(mods, "ac.total")
    )
    ac_touch = 10 + dex_for_ac + int(c.combat["ac"].get("size", 0)) + int(c.combat["ac"].get("deflection", 0)) + int(c.combat["ac"].get("dodge", 0)) + _sum_target(mods, "ac.touch")
    ac_flat = ac_total - dex_for_ac - int(c.combat["ac"].get("dodge", 0))

    saves = {
        "Fort": int(c.saves["Fort"].get("base", 0)) + abilities["CON"]["mod"] + int(c.saves["Fort"].get("misc", 0)) + _sum_target(mods, "save.Fort"),
        "Ref": int(c.saves["Ref"].get("base", 0)) + abilities["DEX"]["mod"] + int(c.saves["Ref"].get("misc", 0)) + _sum_target(mods, "save.Ref"),
        "Will": int(c.saves["Will"].get("base", 0)) + abilities["WIS"]["mod"] + int(c.saves["Will"].get("misc", 0)) + _sum_target(mods, "save.Will"),
    }

    c.derived = {
        "abilities": abilities,
        "initiative": initiative,
        "armorClass": {"total": ac_total, "touch": ac_touch, "flatFooted": ac_flat},
        "saves": saves,
    }
    return c
