class RuleEngine:
    def __init__(self, rules: dict):
        self.rules = rules

    @property
    def go_reward(self) -> int:
        return self.rules.get("go_reward", 200)

    @property
    def jail_square(self) -> int:
        return self.rules.get("jail_square", 10)

    @property
    def go_to_jail_square(self) -> int:
        return self.rules.get("go_to_jail_square", 30)

    @property
    def max_players(self) -> int:
        return self.rules.get("max_players", 8)
