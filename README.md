# D&D 3E DM Desktop Manager (Electron)

A local-first desktop GUI for running D&D 3.0/3.5 style sessions with fast combat tracking, full character model coverage, modifier-driven rules, and private feat TXT imports.

## Content Policy
- Rules/content are separated from code in `data/packs` and imported files.
- This project ships only minimal starter/SRD-style sample entries.
- You can privately import additional content as TXT/JSON data packs.

## Install (non-programmer)
1. Install Node.js LTS (18+).
2. Open terminal in this folder.
3. Run:
   ```bash
   npm install
   ```

## Run the App
```bash
npm start
```

## Build an Executable
You can package using Electron Forge or Electron Builder.

Example quick setup:
```bash
npm install --save-dev @electron-forge/cli
npx electron-forge import
npm run make
```

Build outputs will be in `out/` or `dist/` depending on toolchain.

## Test
```bash
npm test
```

## What is implemented
- Campaign + character create/edit/save/load/export.
- Modifier engine with stacking rules.
- Derived calculations: ability mods, initiative, AC, saves.
- Combat dashboard with quick damage/heal.
- Effects with durations and end-round decrement.
- Fatigued condition demo (`-2 STR`, `-2 DEX`, duration 10 rounds).
- Feat TXT importer (dedupe by Name+Source, preserve source).
- Rules mapping status (`Mapped` / `Unmapped`) and mapper wizard.
- Improved Initiative demonstration mapping (`initiative +4`).

## Data packs and schemas
- Starter packs: `data/packs/*.json`.
- JSON schemas: `data/schemas/*.schema.json`.

