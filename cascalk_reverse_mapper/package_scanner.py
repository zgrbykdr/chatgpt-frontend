from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path

from .models import PRIORITY_DLLS, SUPPORT_DLLS


class PackageScanner:
    def extract_if_zip(self, source: Path, workspace: Path) -> Path:
        source = Path(source)
        if source.suffix.lower() == ".zip":
            target = workspace / source.stem
            target.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(source) as zf:
                zf.extractall(target)
            return target
        return source

    def _sha256(self, path: Path) -> str:
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    def classify(self, rel_path: str) -> tuple[str, str]:
        lower = rel_path.lower()
        name = Path(rel_path).name
        if lower.endswith(".dll") or lower.endswith(".lib"):
            if name in PRIORITY_DLLS:
                return "binary", "core_or_interface"
            if name in SUPPORT_DLLS:
                return "binary", "runtime_dependency"
            if name.lower() == "alfacalcinterface.dll":
                return "binary", "interface_candidate"
            return "binary", "candidate_binary"
        if lower.endswith(".xml"):
            if "phe/views/totalview" in lower:
                return "xml", "view_result_definition"
            if "phe/application" in lower:
                return "xml", "application_schema"
            if "general/fluid" in lower:
                return "xml", "fluid_definition"
            return "xml", "config"
        if lower.endswith(".fld") or lower.endswith(".bnc") or lower.endswith(".bnr"):
            return "refdata", "reference_property"
        if lower.endswith(".pdf"):
            return "doc", "documentation"
        return "other", "misc"

    def scan(self, root: Path) -> list[dict]:
        root = Path(root)
        records: list[dict] = []
        for p in root.rglob("*"):
            if p.is_file():
                rel = str(p.relative_to(root)).replace("\\", "/")
                kind, role = self.classify(rel)
                records.append(
                    {
                        "path": rel,
                        "kind": kind,
                        "role": role,
                        "size": p.stat().st_size,
                        "sha256": self._sha256(p),
                    }
                )
        return records
