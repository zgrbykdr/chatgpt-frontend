import json
from pathlib import Path


class RuleEditor:
    @staticmethod
    def set_rule(rules, key, value):
        rules[key] = value

    @staticmethod
    def save(path: str, rules):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with Path(path).open("w", encoding="utf-8") as f:
            json.dump(rules, f, indent=2)
