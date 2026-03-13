from typing import Dict, Any


class RuleEngine:
    def __init__(self, rules: Dict[str, Any]) -> None:
        self.rules = rules

    def get(self, key: str, default=None):
        return self.rules.get(key, default)
