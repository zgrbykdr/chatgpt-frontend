import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

from modules.shared.utils import safe_json_read, safe_json_write, now_iso


class CampaignManager:
    def __init__(self, data_manager) -> None:
        self.data = data_manager
        self.active_meta_path = self.data.save_dir / "active_campaign.json"
        self._ensure_sample_campaign()

    def _campaign_path(self, campaign_id: str) -> Path:
        return self.data.save_dir / f"{campaign_id}.json"

    def _default_campaign_payload(self, campaign_id: str, name: str) -> Dict[str, Any]:
        timestamp = now_iso()
        return {
            "id": campaign_id,
            "name": name,
            "created": timestamp,
            "updated": timestamp,
            "session_notes": ["Session 1: Add your first session note here."],
            "lore": [],
            "story_state": {
                "kingdom_unstable": False,
                "cult_active": False,
                "war_ongoing": False,
                "party_reputation": "local",
            },
            "battle_state": {"round": 1, "tokens": [], "log": []},
            "atmosphere": {"last_preset": "tavern"},
            "generator_history": [],
        }

    def _ensure_sample_campaign(self) -> None:
        sample_id = "sample_campaign"
        sample_path = self._campaign_path(sample_id)
        if not sample_path.exists():
            sample = self._default_campaign_payload(sample_id, "Shadows over Emberfall")
            sample["session_notes"] = [
                "Session 1: Party entered Emberfall and discovered missing caravans.",
                "Session 2: Cult traces found beneath the old shrine district.",
            ]
            safe_json_write(sample_path, sample)

        active_meta = safe_json_read(self.active_meta_path, {})
        if not active_meta.get("active_campaign_id"):
            safe_json_write(self.active_meta_path, {"active_campaign_id": sample_id})

    def list_campaigns(self) -> List[Dict[str, str]]:
        campaigns: List[Dict[str, str]] = []
        for file_path in sorted(self.data.save_dir.glob("*.json")):
            if file_path.name == "active_campaign.json":
                continue
            payload = safe_json_read(file_path, {})
            campaigns.append({
                "id": payload.get("id", file_path.stem),
                "name": payload.get("name", file_path.stem),
                "path": str(file_path),
            })
        return campaigns

    def get_active_campaign_id(self) -> str:
        meta = safe_json_read(self.active_meta_path, {})
        return meta.get("active_campaign_id", "sample_campaign")

    def set_active_campaign(self, campaign_id: str) -> None:
        safe_json_write(self.active_meta_path, {"active_campaign_id": campaign_id})

    def load_active_campaign(self) -> Dict[str, Any]:
        active_id = self.get_active_campaign_id()
        payload = safe_json_read(self._campaign_path(active_id), {})
        if not payload:
            payload = self._default_campaign_payload(active_id, active_id.replace("_", " ").title())
            safe_json_write(self._campaign_path(active_id), payload)
        return payload

    def load_campaign(self, campaign_id: str) -> Dict[str, Any]:
        payload = safe_json_read(self._campaign_path(campaign_id), {})
        if not payload:
            raise FileNotFoundError(f"Campaign not found: {campaign_id}")
        self.set_active_campaign(campaign_id)
        return payload

    def create_campaign(self, name: str) -> Dict[str, Any]:
        normalized = "_".join(name.lower().strip().split())
        campaign_id = normalized or f"campaign_{now_iso().replace(':', '-') }"
        candidate = campaign_id
        idx = 1
        while self._campaign_path(candidate).exists():
            idx += 1
            candidate = f"{campaign_id}_{idx}"
        payload = self._default_campaign_payload(candidate, name.strip() or candidate)
        safe_json_write(self._campaign_path(candidate), payload)
        self.set_active_campaign(candidate)
        return payload

    def rename_campaign(self, campaign: Dict[str, Any], new_name: str) -> Dict[str, Any]:
        campaign["name"] = new_name.strip() or campaign.get("name", "Unnamed Campaign")
        self.save_campaign(campaign)
        return campaign

    def save_campaign(self, campaign: Dict[str, Any]) -> None:
        campaign_id = campaign.get("id", "sample_campaign")
        campaign["updated"] = now_iso()
        safe_json_write(self._campaign_path(campaign_id), campaign)

    def export_campaign(self, campaign: Dict[str, Any], export_path: Path) -> None:
        export_path.parent.mkdir(parents=True, exist_ok=True)
        safe_json_write(export_path, campaign)

    def import_campaign(self, import_path: Path) -> Dict[str, Any]:
        payload = safe_json_read(import_path, {})
        if not payload:
            raise ValueError("Invalid campaign file")
        campaign_id = payload.get("id") or import_path.stem
        payload["id"] = campaign_id
        payload["updated"] = now_iso()
        safe_json_write(self._campaign_path(campaign_id), payload)
        self.set_active_campaign(campaign_id)
        return payload
