from __future__ import annotations

import sqlite3
import threading
from pathlib import Path
from typing import Iterable


SCHEMA = """
CREATE TABLE IF NOT EXISTS projects(id INTEGER PRIMARY KEY, name TEXT, root_path TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS files(id INTEGER PRIMARY KEY, project_id INTEGER, rel_path TEXT, kind TEXT, role TEXT, size INTEGER, sha256 TEXT);
CREATE TABLE IF NOT EXISTS xml_variables(id INTEGER PRIMARY KEY, project_id INTEGER, name TEXT, source_file TEXT, category TEXT, dtype TEXT, default_value TEXT, enum_values TEXT, domain TEXT, notes TEXT, confidence REAL);
CREATE TABLE IF NOT EXISTS dll_findings(id INTEGER PRIMARY KEY, project_id INTEGER, dll_name TEXT, architecture TEXT, export_count INTEGER, import_count INTEGER, string_clue_count INTEGER, probable_role TEXT, confidence REAL, why TEXT);
CREATE TABLE IF NOT EXISTS dll_exports(id INTEGER PRIMARY KEY, project_id INTEGER, dll_name TEXT, symbol TEXT);
CREATE TABLE IF NOT EXISTS dll_imports(id INTEGER PRIMARY KEY, project_id INTEGER, dll_name TEXT, symbol TEXT);
CREATE TABLE IF NOT EXISTS dll_strings(id INTEGER PRIMARY KEY, project_id INTEGER, dll_name TEXT, value TEXT);
CREATE TABLE IF NOT EXISTS interface_candidates(id INTEGER PRIMARY KEY, project_id INTEGER, dll_name TEXT, function_name TEXT, probable_purpose TEXT, call_order_guess INTEGER, parameter_semantics TEXT, confidence REAL, evidence TEXT);
CREATE TABLE IF NOT EXISTS variable_mappings(id INTEGER PRIMARY KEY, project_id INTEGER, canonical_name TEXT, aliases TEXT, category TEXT, confidence REAL, related_dll TEXT, related_functions TEXT, data_type TEXT, domain TEXT, sweepable INTEGER);
CREATE TABLE IF NOT EXISTS guided_decisions(id INTEGER PRIMARY KEY, project_id INTEGER, step_name TEXT, decision TEXT, notes TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS runtime_sessions(id INTEGER PRIMARY KEY, project_id INTEGER, mode TEXT, base_case_json TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS runtime_observations(id INTEGER PRIMARY KEY, session_id INTEGER, inputs_json TEXT, outputs_json TEXT, status TEXT, error_text TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS sensitivity_results(id INTEGER PRIMARY KEY, project_id INTEGER, input_var TEXT, output_var TEXT, influence REAL, evidence_source TEXT, notes TEXT);
CREATE TABLE IF NOT EXISTS lookup_builds(id INTEGER PRIMARY KEY, project_id INTEGER, name TEXT, axes_json TEXT, outputs_json TEXT, status TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS export_records(id INTEGER PRIMARY KEY, project_id INTEGER, export_type TEXT, path TEXT, metadata_json TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS logs(id INTEGER PRIMARY KEY, project_id INTEGER, level TEXT, message TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
"""


class Persistence:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        # GUI actions and background import workers both access persistence.
        # check_same_thread=False allows this, and the lock serializes access.
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._lock = threading.RLock()
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def execute(self, sql: str, params: tuple = ()):
        with self._lock:
            cur = self.conn.cursor()
            cur.execute(sql, params)
            self.conn.commit()
            return cur

    def executemany(self, sql: str, rows: Iterable[tuple]):
        with self._lock:
            cur = self.conn.cursor()
            cur.executemany(sql, list(rows))
            self.conn.commit()
            return cur
