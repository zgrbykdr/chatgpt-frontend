from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


class ReportGenerator:
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
            "Top Function Roles:",
        ]
        for fn in payload.get("functions", [])[:15]:
            lines.append(f" - {fn['name']}: {fn.get('role', {}).get('primary', 'Unknown')} ({fn.get('role', {}).get('confidence', 0)})")
        lines.append("Top Pattern Candidates:")
        for p in payload.get("patterns", [])[:10]:
            lines.append(f" - {p['pattern']} ({p['confidence']}): {p['evidence']}")
        for line in lines:
            c.drawString(50, y, line[:110])
            y -= 14
            if y < 60:
                c.showPage()
                y = 760
                c.setFont("Helvetica", 10)
        c.save()
        return output_path
