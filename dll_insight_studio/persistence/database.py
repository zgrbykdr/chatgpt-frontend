from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1


class Database:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._initialize()

    def _initialize(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS schema_version(version INTEGER NOT NULL)"
        )
        if cur.execute("SELECT COUNT(*) AS c FROM schema_version").fetchone()["c"] == 0:
            cur.execute("INSERT INTO schema_version(version) VALUES(?)", (SCHEMA_VERSION,))
        self._create_tables()
        self.conn.commit()

    def _create_tables(self) -> None:
        statements = [
            """
            CREATE TABLE IF NOT EXISTS projects(
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                workspace TEXT NOT NULL,
                dll_path TEXT NOT NULL,
                exe_path TEXT,
                related_dir TEXT,
                mode TEXT,
                depth TEXT,
                created_at TEXT,
                updated_at TEXT
            )
            """,
            "CREATE TABLE IF NOT EXISTS files(id INTEGER PRIMARY KEY, project_id INTEGER, path TEXT, sha256 TEXT, metadata_json TEXT)",
            "CREATE TABLE IF NOT EXISTS sessions(id INTEGER PRIMARY KEY, project_id INTEGER, started_at TEXT, state TEXT)",
            "CREATE TABLE IF NOT EXISTS exports(id INTEGER PRIMARY KEY, project_id INTEGER, symbol TEXT, ordinal INTEGER)",
            "CREATE TABLE IF NOT EXISTS imports(id INTEGER PRIMARY KEY, project_id INTEGER, library TEXT, symbol TEXT)",
            "CREATE TABLE IF NOT EXISTS strings(id INTEGER PRIMARY KEY, project_id INTEGER, value TEXT, category TEXT, confidence REAL)",
            "CREATE TABLE IF NOT EXISTS string_labels(id INTEGER PRIMARY KEY, project_id INTEGER, string_id INTEGER, label TEXT, source TEXT)",
            "CREATE TABLE IF NOT EXISTS functions(id INTEGER PRIMARY KEY, project_id INTEGER, name TEXT, address TEXT, size INTEGER)",
            "CREATE TABLE IF NOT EXISTS function_metrics(id INTEGER PRIMARY KEY, project_id INTEGER, function_name TEXT, metric TEXT, value REAL)",
            "CREATE TABLE IF NOT EXISTS function_roles(id INTEGER PRIMARY KEY, project_id INTEGER, function_name TEXT, primary_role TEXT, secondary_role TEXT, confidence REAL, explanation TEXT)",
            "CREATE TABLE IF NOT EXISTS variables(id INTEGER PRIMARY KEY, project_id INTEGER, name TEXT, category TEXT, confidence REAL, region TEXT)",
            "CREATE TABLE IF NOT EXISTS variable_evidence(id INTEGER PRIMARY KEY, project_id INTEGER, variable_name TEXT, evidence TEXT)",
            "CREATE TABLE IF NOT EXISTS pattern_candidates(id INTEGER PRIMARY KEY, project_id INTEGER, pattern TEXT, confidence REAL, evidence TEXT)",
            "CREATE TABLE IF NOT EXISTS guidance_decisions(id INTEGER PRIMARY KEY, project_id INTEGER, step_key TEXT, prompt TEXT, choice TEXT, notes TEXT, created_at TEXT)",
            "CREATE TABLE IF NOT EXISTS runtime_sessions(id INTEGER PRIMARY KEY, project_id INTEGER, exe_path TEXT, run_label TEXT, notes TEXT, observed_changes TEXT, created_at TEXT)",
            "CREATE TABLE IF NOT EXISTS report_history(id INTEGER PRIMARY KEY, project_id INTEGER, report_type TEXT, output_path TEXT, created_at TEXT)",
            "CREATE TABLE IF NOT EXISTS app_logs(id INTEGER PRIMARY KEY, project_id INTEGER, level TEXT, message TEXT, created_at TEXT)",
            "CREATE TABLE IF NOT EXISTS analysis_logs(id INTEGER PRIMARY KEY, project_id INTEGER, stage TEXT, message TEXT, created_at TEXT)",
        ]
        for sql in statements:
            self.conn.execute(sql)

    def insert_project(self, payload: dict[str, Any]) -> int:
        now = datetime.utcnow().isoformat()
        cur = self.conn.execute(
            """
            INSERT INTO projects(name, workspace, dll_path, exe_path, related_dir, mode, depth, created_at, updated_at)
            VALUES(?,?,?,?,?,?,?,?,?)
            """,
            (
                payload["name"],
                payload["workspace"],
                payload["dll_path"],
                payload.get("exe_path"),
                payload.get("related_dir"),
                payload.get("mode", "Guided"),
                payload.get("depth", "Standard"),
                now,
                now,
            ),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def update_project_timestamp(self, project_id: int) -> None:
        self.conn.execute(
            "UPDATE projects SET updated_at=? WHERE id=?",
            (datetime.utcnow().isoformat(), project_id),
        )
        self.conn.commit()

    def save_json_rows(self, table: str, project_id: int, rows: list[dict[str, Any]]) -> None:
        if table == "analysis_logs":
            for row in rows:
                self.conn.execute(
                    "INSERT INTO analysis_logs(project_id, stage, message, created_at) VALUES(?,?,?,?)",
                    (project_id, row["stage"], row["message"], datetime.utcnow().isoformat()),
                )
            self.conn.commit()
            return
        raise ValueError(f"Unsupported table '{table}'")

    def replace_rows(self, sql_delete: str, sql_insert: str, delete_args: tuple[Any, ...], rows: list[tuple[Any, ...]]) -> None:
        self.conn.execute(sql_delete, delete_args)
        if rows:
            self.conn.executemany(sql_insert, rows)
        self.conn.commit()

    def fetch_project(self, project_id: int) -> sqlite3.Row | None:
        return self.conn.execute("SELECT * FROM projects WHERE id=?", (project_id,)).fetchone()

    def fetch_all(self, query: str, params: tuple[Any, ...]) -> list[sqlite3.Row]:
        return list(self.conn.execute(query, params).fetchall())

    def add_log(self, project_id: int | None, level: str, message: str) -> None:
        self.conn.execute(
            "INSERT INTO app_logs(project_id, level, message, created_at) VALUES(?,?,?,?)",
            (project_id, level, message, datetime.utcnow().isoformat()),
        )
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    @staticmethod
    def encode_json(payload: Any) -> str:
        return json.dumps(payload, ensure_ascii=False)
