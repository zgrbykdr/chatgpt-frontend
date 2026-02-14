# D&D 3E DM Desktop Manager - Python Implementation Plan

## 1) Tech Stack
1. Desktop GUI: **Python + PySide6**.
2. Data model + rules engine: Python dataclasses and services.
3. Storage: local JSON campaigns with snapshot backups.
4. Validation: JSON schemas under `data/schemas`.
5. Testing: Python `unittest`.

## 2) File Structure
- `py_app/main.py`: app entry point.
- `py_app/ui/main_window.py`: desktop GUI.
- `py_app/core/models.py`: campaign and character entities.
- `py_app/core/modifier_engine.py`: stacking and derived calculations.
- `py_app/services/txt_feat_parser.py`: TXT feat import parser.
- `py_app/services/storage.py`: load/save/backup.
- `tests_py/`: rule engine and import tests.

## 3) Data Model Coverage
Campaign contains:
- Character list (PC/NPC), notes, round tracker, initiative order, import metadata.
- Libraries: feats, spells, conditions, items, import mappings.

Character contains:
- Identity, abilities, HP system, combat/AC, saves, skills, feats, spells, equipment,
  special abilities, effects, notes, modifiers, derived stats.

## 4) Rules/Modifier Engine
- Modifiers are structured as: `target`, `value`, `bonusType`, `active`.
- Stacking rules:
  - default typed bonus: highest only
  - dodge/circumstance/untyped/penalty: stack
- Derived formulas:
  - ability mod `(score - 10) // 2`
  - initiative = DEX mod + misc + modifiers
  - AC total/touch/flat-footed
  - Fort/Ref/Will from base + ability + misc + modifiers

## 5) TXT Feat Import + Mapping
- Parser supports tab or multi-space separated rows.
- Detects Name/Source/Description headers robustly.
- Dedupe: `(Name + Source)`.
- Imported feats marked `Unmapped` by default.
- Mapping editor writes modifiers/prereqs into campaign private mappings.
- External JSON mapping import supported.
- Demo: Improved Initiative mapped to `initiative +4`.

## 6) Effects/Conditions
- Structured effect entries with source, start round, remaining rounds, modifiers.
- End-round action decrements durations and expires effects.
- Demo condition: Fatigued `-2 STR`, `-2 DEX`.

## 7) Testing Strategy
- Unit tests for:
  - Improved Initiative application
  - Fatigued condition penalties
  - TXT parsing + dedupe + source preservation
