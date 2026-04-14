from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


def _simple_pdf(text: str, out_path: Path):
    safe = text.replace("(", "[").replace(")", "]")
    content = f"BT /F1 10 Tf 40 780 Td ({safe[:3000]}) Tj ET"
    obj1 = "1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
    obj2 = "2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n"
    obj3 = "3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj\n"
    obj4 = f"4 0 obj << /Length {len(content)} >> stream\n{content}\nendstream endobj\n"
    obj5 = "5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n"
    body = obj1 + obj2 + obj3 + obj4 + obj5
    xref_start = len("%PDF-1.4\n") + len(body)
    pdf = "%PDF-1.4\n" + body + "xref\n0 6\n0000000000 65535 f \n"
    offset = len("%PDF-1.4\n")
    for obj in [obj1, obj2, obj3, obj4, obj5]:
        pdf += f"{offset:010d} 00000 n \n"
        offset += len(obj)
    pdf += f"trailer << /Size 6 /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF"
    out_path.write_bytes(pdf.encode("latin1", errors="ignore"))


class ReportGenerator:
    def build_reports(self, project_name: str, findings: dict, out_dir: Path) -> dict[str, Path]:
        out_dir.mkdir(parents=True, exist_ok=True)
        now = datetime.utcnow().isoformat()
        executive = {
            "package": project_name,
            "main_dll_roles": findings.get("dll_roles", [])[:8],
            "likely_inputs": findings.get("inputs", [])[:40],
            "likely_outputs": findings.get("outputs", [])[:40],
            "interface_candidates": findings.get("interfaces", [])[:20],
            "sensitivity_summary": findings.get("sensitivity", [])[:30],
            "generated_at": now,
        }
        technical = {"generated_at": now, **findings}

        html_path = out_dir / "report.html"
        html_path.write_text(f"<html><body><h1>CasCalc Reverse Mapper</h1><pre>{json.dumps(technical, indent=2)}</pre></body></html>", encoding="utf-8")

        json_path = out_dir / "report.json"
        json_path.write_text(json.dumps({"executive": executive, "technical": technical}, indent=2), encoding="utf-8")

        pdf_path = out_dir / "report.pdf"
        _simple_pdf(json.dumps(executive, indent=2), pdf_path)
        return {"html": html_path, "json": json_path, "pdf": pdf_path}
