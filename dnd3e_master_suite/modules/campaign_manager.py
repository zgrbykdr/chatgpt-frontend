from pathlib import Path
from typing import Any, Dict

from modules.shared.utils import safe_json_read, safe_json_write, now_iso


class CampaignManager:
    def __init__(self, data_manager) -> None:
        self.data = data_manager
        self.active_campaign_path = self.data.save_dir / "sample_campaign.json"
        self._ensure_sample_campaign()

    def _ensure_sample_campaign(self) -> None:
        if self.active_campaign_path.exists():
            return
        sample = {
            "id": "sample_campaign",
            "name": "Shadows over Emberfall",
            "created": now_iso(),
            "updated": now_iso(),
            "session_notes": ["Session 1: Party entered Emberfall and discovered missing caravans."],
            "lore": [],
            "story_state": {"kingdom_unstable": True, "cult_active": True, "undead_sightings": "rising"},
            "battle_state": {"round": 1, "tokens": [], "log": []},
            "atmosphere": {"last_preset": "tavern"},
            "generator_history": [],
        }
        safe_json_write(self.active_campaign_path, sample)

    def load_active_campaign(self) -> Dict[str, Any]:
        return safe_json_read(self.active_campaign_path, {})

    def save_campaign(self, campaign: Dict[str, Any]) -> None:
        campaign["updated"] = now_iso()
        safe_json_write(self.active_campaign_path, campaign)
