from math import floor


def ability_modifier(score: int) -> int:
    return floor((score - 10) / 2)


def estimate_encounter_difficulty(avg_party_level: int, encounter_el: int) -> str:
    delta = encounter_el - avg_party_level
    if delta <= -2:
        return "Easy"
    if delta <= 1:
        return "Moderate"
    if delta <= 3:
        return "Hard"
    return "Deadly"


def d20_outcome_text(roll: int) -> str:
    if roll == 1:
        return "Natural 1"
    if roll == 20:
        return "Natural 20"
    return ""
