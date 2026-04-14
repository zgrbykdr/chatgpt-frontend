from pathlib import Path

from dll_insight_studio.persistence.database import Database
from dll_insight_studio.persistence.repository import ProjectRepository


def test_repository_roundtrip(tmp_path: Path) -> None:
    db = Database(tmp_path / "project.db")
    repo = ProjectRepository(db)
    project_id = repo.create_project(
        {
            "name": "test",
            "workspace": str(tmp_path),
            "dll_path": "sample.dll",
            "mode": "Guided",
            "depth": "Standard",
        }
    )
    repo.save_strings(project_id, [{"value": "input_1", "category": "Possible Inputs", "confidence": 0.7}])
    rows = db.fetch_all("SELECT * FROM strings WHERE project_id=?", (project_id,))
    assert len(rows) == 1
    assert rows[0]["category"] == "Possible Inputs"
