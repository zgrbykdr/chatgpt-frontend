from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pefile


class MetadataExtractor:
    STRING_RE = re.compile(rb"[\x20-\x7E]{4,}")

    def extract(self, dll_path: Path) -> dict[str, Any]:
        pe = pefile.PE(str(dll_path), fast_load=False)
        exports = []
        imports = []

        if hasattr(pe, "DIRECTORY_ENTRY_EXPORT"):
            for exp in pe.DIRECTORY_ENTRY_EXPORT.symbols:
                exports.append({"name": (exp.name or b"ordinal").decode(errors="ignore"), "ordinal": exp.ordinal})

        if hasattr(pe, "DIRECTORY_ENTRY_IMPORT"):
            for imp in pe.DIRECTORY_ENTRY_IMPORT:
                lib = imp.dll.decode(errors="ignore")
                for symbol in imp.imports:
                    imports.append({"library": lib, "name": (symbol.name or b"").decode(errors="ignore")})

        raw = dll_path.read_bytes()
        raw_strings = sorted({m.group().decode(errors="ignore") for m in self.STRING_RE.finditer(raw)})

        numeric_constants = sorted(set(re.findall(r"\b\d+(?:\.\d+)?\b", "\n".join(raw_strings))))[:200]

        return {
            "exports": exports,
            "imports": imports,
            "strings": raw_strings[:5000],
            "resources": self._extract_resources(pe),
            "version_info": self._extract_version(pe),
            "manifests": [s for s in raw_strings if "assembly" in s.lower()][:20],
            "file_paths": [s for s in raw_strings if "\\" in s or "/" in s][:100],
            "numeric_constants": numeric_constants,
            "external_references": sorted({item["library"] for item in imports}),
        }

    def _extract_resources(self, pe: pefile.PE) -> list[str]:
        if not hasattr(pe, "DIRECTORY_ENTRY_RESOURCE"):
            return []
        names: list[str] = []
        for entry in pe.DIRECTORY_ENTRY_RESOURCE.entries:
            name = str(entry.name) if entry.name else f"ID_{entry.struct.Id}"
            names.append(name)
        return names

    def _extract_version(self, pe: pefile.PE) -> dict[str, str]:
        version: dict[str, str] = {}
        if not hasattr(pe, "FileInfo"):
            return version
        for file_info in pe.FileInfo:
            if file_info.Key == b"StringFileInfo":
                for st in file_info.StringTable:
                    for key, value in st.entries.items():
                        version[key.decode(errors="ignore")] = value.decode(errors="ignore")
        return version
