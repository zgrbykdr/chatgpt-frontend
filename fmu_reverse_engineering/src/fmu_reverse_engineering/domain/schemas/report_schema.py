from pydantic import BaseModel


class ReportSchema(BaseModel):
    run_id: str
    summary_path: str
    html_path: str | None = None
    pdf_path: str | None = None
