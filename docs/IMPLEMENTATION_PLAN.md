# D&D 3E DM Desktop Manager - Implementation Plan

## 1) Tech Stack
1. **Desktop shell**: Electron (Node.js + Chromium desktop app).
2. **UI**: Vanilla HTML/CSS/JavaScript with responsive DM dashboard layout.
3. **Storage**: Local JSON campaign files with snapshot backups (`.backups` keep last N).
4. **Validation**: JSON Schemas for data packs and campaign entities.
5. **Testing**: Node test runner using assertion scripts (`tests/run-tests.js`).

## 2) File Structure
- `main.js`: Electron main process and file dialogs.
- `preload.js`: IPC bridge.
- `index.html`, `styles.css`, `src/renderer.js`: GUI and interactions.
- `src/lib/models.js`: canonical campaign/character model and migration.
- `src/lib/modifierEngine.js`: stacking rules and derived stat recomputation.
- `src/lib/txtFeatParser.js`: robust TXT feat parsing and deduping.
- `src/lib/storage.js`: save/load + backups.
- `data/schemas/*.schema.json`: JSON schemas for data packs.
- `data/packs/*.json`: starter/OGL-safe sample data packs.
- `tests/*.js`: unit tests for calculations and import parsing.

## 3) Data Model (implementation-ready)
Core entities inside campaign JSON:
- Campaign, Character, ClassLevel, AbilityScore, Skill, Feat, Spell, Item, Effect, Modifier, Note, AttackProfile.
- Import entities: ImportedSourceFile, FeatImportRow, FeatMechanicsMapping.

All totals are derived via `modifierEngine` at runtime.

## 4) GUI Layout Plan
- **Left Sidebar**: searchable character list with PC/NPC tags.
- **Main Panels**:
  - Overview (identity + HP + AC + initiative + derived line).
  - Feats & Features (library, selected feats, mapping wizard).
  - Effects/Conditions (timers + active toggle + end-round decrement).
  - Combat Dashboard (initiative order, HP, AC, saves, quick +/- buttons).
  - Notes (character/session/campaign notes).
- Keyboard shortcuts for damage/heal/end round/add fatigued.

## 5) Rule/Modifier Engine Design
- Modifier fields: `target`, `value`, `bonusType`, activation flag/conditions.
- Stacking table configurable in engine:
  - default typed bonuses: keep highest.
  - dodge/circumstance/untyped/penalties: stack.
- Recompute pipeline:
  1. Gather base + feat + effect modifiers.
  2. Apply stacking.
  3. Compute ability totals/mods.
  4. Compute initiative, AC breakdown, saves.

## 6) TXT Import + Mapping Workflow
1. User imports TXT (`Name`, `Source`, `Description` tolerant parser).
2. Parser reads tab or multi-space columns, dedupes by (Name+Source).
3. Imported rows become feats with mapping status `Unmapped` by default.
4. If feat name = Improved Initiative, auto-map +4 initiative demonstration.
5. Rules Mapper wizard lets user define modifier target/value/type and stores mapping.
6. External feat mechanics JSON can be imported and merged.

## 7) Import/Export Design
- Export characters JSON from current campaign.
- Save/load campaigns via dialogs.
- Save mapping entries in campaign-private import area.
- Provide starter schemas + pack templates for feats/spells/conditions/items.

## 8) Migration Strategy
- `schemaVersion` on campaign root.
- `migrateCampaign` merges existing files with current defaults.
- New fields auto-initialized during load.

## 9) Testing Strategy
- Unit tests:
  - Ability mod formula and initiative mapping (+4 feat).
  - Fatigued condition penalties.
  - TXT parser dedupe/header handling robustness.
- Smoke tests:
  - JSON save/load roundtrip.

