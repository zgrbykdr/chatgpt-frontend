# CasCalc Reverse Mapper

A production-style desktop app focused on reverse engineering **CasCalc.zip** package structure and generating practical lookup tables.

## Tech stack
- Python 3
- PySide6 GUI desktop application
- SQLite persistence
- pandas/numpy data workflows

## Run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Test
```bash
pip install pytest
pytest -q
```

## Key implemented workflow
1. Import `CasCalc.zip` or extracted folder.
2. Scan and classify binaries/XML/refdata with package-specific priorities.
3. Parse priority XMLs + fluid XMLs and extract variable catalog.
4. Analyze DLL metadata/strings with CasCalc-priority role inference.
5. Discover interface hypotheses (Create/Calculate/Get/Delete style lifecycle).
6. Build XML-to-binary variable mapping candidates.
7. Run direct probe attempt or host-assisted observation recording.
8. Perform sensitivity matrix generation.
9. Build lookup datasets and export CSV/JSON/NPZ/HDF5.
10. Export executive/technical reports in HTML/JSON/PDF.

## Guidance included in-app
- Start with interface DLL first.
- Prefer one-phase + common fluid initially.
- One-variable-at-a-time sensitivity changes.
- Keep failed samples as invalid evidence.
- Use XML as first source of truth, then binary/runtime refine.
