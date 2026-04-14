from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


class ReportGenerator:
    @staticmethod
    def _safe_text(value: Any) -> str:
        return str(value).replace("\n", " ").replace("\r", " ").strip()

    @staticmethod
    def _wrap_line(line: str, width: int = 105) -> list[str]:
        words = line.split(" ")
        out: list[str] = []
        current = ""
        for word in words:
            if len(current) + len(word) + 1 <= width:
                current = (current + " " + word).strip()
            else:
                if current:
                    out.append(current)
                current = word
        if current:
            out.append(current)
        return out or [""]

    def export_json(self, payload: dict[str, Any], output_path: Path) -> Path:
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return output_path

    def export_html(self, payload: dict[str, Any], output_path: Path) -> Path:
        top_patterns = "".join(
            f"<li>{p['pattern']} (confidence: {p['confidence']}) - {p['evidence']}</li>" for p in payload.get("patterns", [])[:10]
        )
        html = f"""
        <html><head><title>DLL Insight Studio Report</title></head><body>
        <h1>DLL Insight Studio - Executive Report</h1>
        <h2>File Identity</h2><pre>{json.dumps(payload.get('identity', {}), indent=2)}</pre>
        <h2>Top Patterns</h2><ul>{top_patterns}</ul>
        <h2>Recommendations</h2><p>{payload.get('recommendations', 'Review guided decisions and validate with runtime workflow if available.')}</p>
        </body></html>
        """
        output_path.write_text(html, encoding="utf-8")
        return output_path

    def export_pdf(self, payload: dict[str, Any], output_path: Path) -> Path:
        c = canvas.Canvas(str(output_path), pagesize=letter)
        y = 760
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, y, "DLL Insight Studio - Technical Report")
        y -= 30
        c.setFont("Helvetica", 10)
        lines = [
            f"Project: {payload.get('project_name', 'Unknown')}",
            f"DLL Type: {payload.get('identity', {}).get('dll_type', 'Unknown')}",
            f"Architecture: {payload.get('identity', {}).get('architecture', 'Unknown')}",
            f"Confidence: {payload.get('identity', {}).get('confidence', 0)}",
            f"Imports: {len(payload.get('metadata', {}).get('imports', []))}  Exports: {len(payload.get('metadata', {}).get('exports', []))}",
            "Top Function Roles:",
        ]
        for fn in payload.get("functions", [])[:15]:
            name = self._safe_text(fn.get("name", "unknown_function"))
            role = self._safe_text(fn.get("role", {}).get("primary", "Unknown"))
            conf = fn.get("role", {}).get("confidence", 0)
            lines.append(f" - {name}: {role} ({conf})")
        lines.append("Top Pattern Candidates:")
        for p in payload.get("patterns", [])[:10]:
            lines.append(f" - {self._safe_text(p['pattern'])} ({p['confidence']}): {self._safe_text(p['evidence'])}")

        reverse = payload.get("reverse_engineering", {})
        lines.append("Dependency Highlights:")
        for dep in reverse.get("dependencies", [])[:8]:
            lines.append(f" - {dep['library']} ({dep['count']} symbols)")
        resolved = reverse.get("resolved_dependency_paths", {})
        if resolved:
            lines.append("Resolved Dependency Paths:")
            for lib, path in list(resolved.items())[:10]:
                lines.append(f" - {lib}: {self._safe_text(path)}")
        consts = reverse.get("constants", {})
        lines.append(
            f"Constants detected: numeric={len(consts.get('numeric_constants', []))}, scientific={len(consts.get('scientific_constants', []))}"
        )
        lines.append("FMU Lookup Table (top entries):")
        for row in reverse.get("fmu_lookup_table", [])[:10]:
            lines.append(f" - {self._safe_text(row['name'])} [{row['category']}] conf={row['confidence']}")
        lines.append("DOE Plan (parameter sensitivity):")
        for row in reverse.get("doe_plan", [])[:10]:
            lines.append(f" - {self._safe_text(row['parameter'])}: {row['low_step']} / {row['high_step']} priority={row['priority']}")
        lines.append("Parameter Ranges (heuristic):")
        for row in reverse.get("parameter_ranges", [])[:10]:
            lines.append(f" - {self._safe_text(row['name'])}: min={row['min']} max={row['max']} default={row['default']}")

        for line in lines:
            for wrapped in self._wrap_line(line):
                c.drawString(50, y, wrapped[:110])
                y -= 14
                if y < 60:
                    c.showPage()
                    y = 760
                    c.setFont("Helvetica", 10)
        c.save()
        return output_path
