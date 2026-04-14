from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

from .models import KNOWN_INPUTS, KNOWN_OUTPUTS, VariableRecord


TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_]+")


class XMLDomainExtractor:
    def parse_xml_file(self, xml_path: Path, root: Path) -> list[VariableRecord]:
        rel = str(xml_path.relative_to(root)).replace("\\", "/")
        try:
            tree = ET.parse(xml_path)
        except ET.ParseError:
            return [VariableRecord(name="__parse_error__", source_file=rel, category="error", dtype="str", notes="Malformed XML", confidence=1.0)]
        records: dict[str, VariableRecord] = {}

        for elem in tree.iter():
            candidates = {elem.tag}
            candidates.update(elem.attrib.keys())
            candidates.update(TOKEN_RE.findall((elem.text or "")))
            for c in list(candidates):
                candidates.update(TOKEN_RE.findall(c))
            for name in candidates:
                if len(name) < 3:
                    continue
                cat, conf = self.categorize(name, rel)
                r = records.get(name)
                if not r:
                    r = VariableRecord(name=name, source_file=rel, category=cat, dtype=self.guess_dtype(name, elem.attrib.get(name)), confidence=conf)
                    records[name] = r
                val = elem.attrib.get(name)
                if val and r.default_value is None:
                    r.default_value = val
                if val and val.lower() in {"true", "false"}:
                    r.dtype = "bool"
                if val and "," in val and all(x.strip() for x in val.split(",")):
                    r.enum_values = [x.strip() for x in val.split(",")]
                if "min" in name.lower() or "max" in name.lower():
                    r.domain = "range-indicated"
        return list(records.values())

    def categorize(self, name: str, source_file: str) -> tuple[str, float]:
        if name in KNOWN_INPUTS:
            return "operating_input", 0.95
        if name in KNOWN_OUTPUTS:
            return "output", 0.95
        if "Error" in name:
            return "status", 0.8
        if "Fluid" in name:
            return "fluid_selection", 0.8
        if "CalcSettings" in name:
            return "calculation_settings", 0.8
        if "View" in source_file:
            return "output", 0.6
        if "application" in source_file.lower():
            return "configuration", 0.6
        return "unknown", 0.35

    def guess_dtype(self, name: str, value: str | None) -> str:
        v = (value or "").lower()
        if v in {"true", "false"} or name.lower().startswith("is"):
            return "bool"
        if v.replace(".", "", 1).isdigit():
            return "float"
        if "temp" in name.lower() or "pressure" in name.lower() or "duty" in name.lower():
            return "float"
        return "str"

    def parse_package(self, root: Path) -> list[VariableRecord]:
        results: list[VariableRecord] = []
        xml_paths = [*root.glob("Settings.xml"), *root.glob("AvqAddin.xml"), *root.glob("PHE/Application/*.xml"), *root.glob("PHE/Views/*.xml"), *root.glob("General/FLUID/*.xml")]
        for p in xml_paths:
            results.extend(self.parse_xml_file(p, root))
        return results
