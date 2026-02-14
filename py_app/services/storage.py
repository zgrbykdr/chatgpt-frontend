from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime
from typing import Tuple
try:
    from py_app.core.models import Campaign, migrate_campaign
except ModuleNotFoundError:
    from ..core.models import Campaign, migrate_campaign


def save_campaign(campaign: Campaign, path: Path) -> Campaign:
    path.parent.mkdir(parents=True, exist_ok=True)
    campaign.updatedAt = datetime.utcnow().isoformat()
    campaign.filePath = str(path)
    path.write_text(json.dumps(campaign.to_dict(), indent=2), encoding="utf-8")
    snapshot_backup(path)
    return campaign


def load_campaign(path: Path) -> Campaign:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return migrate_campaign(raw)


def snapshot_backup(path: Path, keep: int = 5) -> None:
    if not path.exists():
        return
    backup_dir = path.parent / ".backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.utcnow().isoformat().replace(":", "-").replace(".", "-")
    backup = backup_dir / f"{path.stem}-{stamp}{path.suffix}"
    backup.write_bytes(path.read_bytes())
    backups = sorted(backup_dir.glob(f"{path.stem}-*{path.suffix}"), reverse=True)
    for old in backups[keep:]:
        old.unlink(missing_ok=True)
