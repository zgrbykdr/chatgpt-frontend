import json
from pathlib import Path


class RuleEditor:
    def __init__(self, rules_path: str | Path):
        self.rules_path = Path(rules_path)

    def load(self) -> dict:
        with self.rules_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def save(self, rules_payload: dict) -> None:
        with self.rules_path.open("w", encoding="utf-8") as handle:
            json.dump(rules_payload, handle, indent=2)

    def set_rule(self, key: str, value):
        payload = self.load()
        payload[key] = value
        self.save(payload)
