from __future__ import annotations

from pathlib import Path
from typing import Any

from dll_insight_studio.persistence.database import Database


class ProjectRepository:
    def __init__(self, db: Database):
        self.db = db

    def create_project(self, payload: dict[str, Any]) -> int:
        return self.db.insert_project(payload)

    def save_file_record(self, project_id: int, path: Path, sha256: str, metadata: dict[str, Any]) -> None:
        self.db.replace_rows(
            "DELETE FROM files WHERE project_id=?",
            "INSERT INTO files(project_id, path, sha256, metadata_json) VALUES(?,?,?,?)",
            (project_id,),
            [(project_id, str(path), sha256, Database.encode_json(metadata))],
        )

    def save_metadata(self, project_id: int, exports: list[dict[str, Any]], imports: list[dict[str, Any]]) -> None:
        self.db.replace_rows(
            "DELETE FROM exports WHERE project_id=?",
            "INSERT INTO exports(project_id, symbol, ordinal) VALUES(?,?,?)",
            (project_id,),
            [(project_id, e.get("name", ""), e.get("ordinal", 0)) for e in exports],
        )
        self.db.replace_rows(
            "DELETE FROM imports WHERE project_id=?",
            "INSERT INTO imports(project_id, library, symbol) VALUES(?,?,?)",
            (project_id,),
            [(project_id, i.get("library", ""), i.get("name", "")) for i in imports],
        )

    def save_strings(self, project_id: int, strings: list[dict[str, Any]]) -> None:
        rows = [(project_id, s["value"], s.get("category", "Unknown"), s.get("confidence", 0.0)) for s in strings]
        self.db.replace_rows(
            "DELETE FROM strings WHERE project_id=?",
            "INSERT INTO strings(project_id, value, category, confidence) VALUES(?,?,?,?)",
            (project_id,),
            rows,
        )

    def save_functions(self, project_id: int, functions: list[dict[str, Any]]) -> None:
        self.db.replace_rows(
            "DELETE FROM functions WHERE project_id=?",
            "INSERT INTO functions(project_id, name, address, size) VALUES(?,?,?,?)",
            (project_id,),
            [(project_id, f["name"], str(f.get("address", "")), int(f.get("size", 0))) for f in functions],
        )
        metric_rows: list[tuple[Any, ...]] = []
        role_rows: list[tuple[Any, ...]] = []
        for fn in functions:
            for metric, value in fn.get("metrics", {}).items():
                metric_rows.append((project_id, fn["name"], metric, float(value)))
            role = fn.get("role", {})
            role_rows.append(
                (
                    project_id,
                    fn["name"],
                    role.get("primary", "Unknown"),
                    role.get("secondary", "Unknown"),
                    float(role.get("confidence", 0.0)),
                    role.get("explanation", ""),
                )
            )
        self.db.replace_rows(
            "DELETE FROM function_metrics WHERE project_id=?",
            "INSERT INTO function_metrics(project_id, function_name, metric, value) VALUES(?,?,?,?)",
            (project_id,),
            metric_rows,
        )
        self.db.replace_rows(
            "DELETE FROM function_roles WHERE project_id=?",
            "INSERT INTO function_roles(project_id, function_name, primary_role, secondary_role, confidence, explanation) VALUES(?,?,?,?,?,?)",
            (project_id,),
            role_rows,
        )

    def save_variables(self, project_id: int, variables: list[dict[str, Any]]) -> None:
        self.db.replace_rows(
            "DELETE FROM variables WHERE project_id=?",
            "INSERT INTO variables(project_id, name, category, confidence, region) VALUES(?,?,?,?,?)",
            (project_id,),
            [
                (project_id, v["name"], v.get("category", "Unknown"), float(v.get("confidence", 0.0)), v.get("region", "global"))
                for v in variables
            ],
        )

    def save_patterns(self, project_id: int, patterns: list[dict[str, Any]]) -> None:
        self.db.replace_rows(
            "DELETE FROM pattern_candidates WHERE project_id=?",
            "INSERT INTO pattern_candidates(project_id, pattern, confidence, evidence) VALUES(?,?,?,?)",
            (project_id,),
            [
                (project_id, p["pattern"], float(p.get("confidence", 0.0)), p.get("evidence", ""))
                for p in patterns
            ],
        )

    def add_guidance_decision(self, project_id: int, step_key: str, prompt: str, choice: str, notes: str) -> None:
        self.db.conn.execute(
            "INSERT INTO guidance_decisions(project_id, step_key, prompt, choice, notes, created_at) VALUES(?,?,?,?,?,datetime('now'))",
            (project_id, step_key, prompt, choice, notes),
        )
        self.db.conn.commit()

    def add_runtime_session(self, project_id: int, exe_path: str, run_label: str, notes: str, observed_changes: str) -> None:
        self.db.conn.execute(
            "INSERT INTO runtime_sessions(project_id, exe_path, run_label, notes, observed_changes, created_at) VALUES(?,?,?,?,?,datetime('now'))",
            (project_id, exe_path, run_label, notes, observed_changes),
        )
        self.db.conn.commit()

    def add_report_history(self, project_id: int, report_type: str, output_path: str) -> None:
        self.db.conn.execute(
            "INSERT INTO report_history(project_id, report_type, output_path, created_at) VALUES(?,?,?,datetime('now'))",
            (project_id, report_type, output_path),
        )
        self.db.conn.commit()

    def load_dashboard_data(self, project_id: int) -> dict[str, list[dict[str, Any]]]:
        data = {}
        for table in [
            "exports",
            "imports",
            "strings",
            "functions",
            "function_roles",
            "variables",
            "pattern_candidates",
            "guidance_decisions",
            "runtime_sessions",
            "analysis_logs",
            "app_logs",
        ]:
            rows = [dict(r) for r in self.db.fetch_all(f"SELECT * FROM {table} WHERE project_id=? ORDER BY id DESC", (project_id,))]
            data[table] = rows
        return data
