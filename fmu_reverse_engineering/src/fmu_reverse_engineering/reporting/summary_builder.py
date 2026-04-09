from pathlib import Path

from fmu_reverse_engineering.domain.schemas.report_schema import ReportSchema


class SummaryBuilder:
    def build(self, run_id: str, output_dir: str, payload: dict) -> ReportSchema:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        summary_path = out / "summary.json"
        summary_path.write_text(__import__("json").dumps(payload, indent=2), encoding="utf-8")
        return ReportSchema(run_id=run_id, summary_path=str(summary_path))
