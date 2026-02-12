from __future__ import annotations
from pathlib import Path
import re
from typing import Dict, Any, List


def _split_row(row: str) -> List[str]:
    if "\t" in row:
        return [c.strip() for c in row.split("\t")]
    return [c.strip() for c in re.split(r"\s{2,}", row)]


def _norm_header(text: str) -> str:
    return re.sub(r"[^a-z]", "", text.lower())


def parse_feat_txt(raw: str, file_path: str = "import.txt") -> Dict[str, Any]:
    lines = [ln.rstrip() for ln in raw.replace("\ufeff", "").splitlines() if ln.strip()]
    if len(lines) < 2:
        return {"sourceFile": file_path, "rows": [], "errors": ["No data rows found"]}

    header = _split_row(lines[0])
    norm = [_norm_header(h) for h in header]
    name_idx = next((i for i, h in enumerate(norm) if "name" in h), 0)
    source_idx = next((i for i, h in enumerate(norm) if "source" in h), 1 if len(header) > 1 else 0)
    desc_idx = next((i for i, h in enumerate(norm) if any(k in h for k in ("description", "summary", "desc"))), 2 if len(header) > 2 else 0)

    rows = []
    errors = []
    dedupe = set()

    for idx, line in enumerate(lines[1:], start=2):
        cols = _split_row(line)
        name = cols[name_idx] if name_idx < len(cols) else ""
        source = cols[source_idx] if source_idx < len(cols) else "Unknown Source"
        summary = cols[desc_idx] if desc_idx < len(cols) else ""
        if not name:
            errors.append(f"Row {idx}: missing feat name")
            continue
        key = (name.lower(), source.lower())
        if key in dedupe:
            continue
        dedupe.add(key)
        rows.append({
            "id": f"imported_{re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')}_{idx}",
            "name": name,
            "source": source,
            "summary": summary,
            "mappingStatus": "Unmapped",
            "importedFrom": Path(file_path).name,
        })

    return {"sourceFile": file_path, "rows": rows, "errors": errors}
