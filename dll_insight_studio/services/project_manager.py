from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from dll_insight_studio.models.entities import ProjectConfig
from dll_insight_studio.persistence.database import Database
from dll_insight_studio.persistence.repository import ProjectRepository
from dll_insight_studio.utilities.file_utils import sha256_file


class ProjectManager:
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.workspace_root.mkdir(parents=True, exist_ok=True)

    def create_project(self, config: ProjectConfig) -> tuple[int, Database, ProjectRepository, Path]:
        stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        project_dir = self.workspace_root / f"{config.name}_{stamp}"
        project_dir.mkdir(parents=True, exist_ok=True)
        copied_dll = project_dir / config.dll_path.name
        shutil.copy2(config.dll_path, copied_dll)
        copied_exe = None
        if config.exe_path:
            copied_exe = project_dir / config.exe_path.name
            shutil.copy2(config.exe_path, copied_exe)

        db = Database(project_dir / "project.db")
        repo = ProjectRepository(db)
        project_id = repo.create_project(
            {
                "name": config.name,
                "workspace": str(project_dir),
                "dll_path": str(copied_dll),
                "exe_path": str(copied_exe) if copied_exe else None,
                "related_dir": str(config.related_dir) if config.related_dir else None,
                "mode": config.mode,
                "depth": config.depth,
            }
        )
        repo.save_file_record(project_id, copied_dll, sha256_file(copied_dll), {"copied": True})
        return project_id, db, repo, project_dir

    def open_project(self, db_path: Path) -> tuple[Database, ProjectRepository]:
        db = Database(db_path)
        return db, ProjectRepository(db)

    def autosave_marker(self, project_dir: Path, state: dict[str, Any]) -> None:
        (project_dir / "autosave.json").write_text(str(state), encoding="utf-8")
