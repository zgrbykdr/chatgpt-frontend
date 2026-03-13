from core.action_executor import ActionExecutor


class CardExecutor:
    def __init__(self, action_executor: ActionExecutor) -> None:
        self.action_executor = action_executor

    def execute_card(self, card, player) -> None:
        for action in card.get("actions", []):
            self.action_executor.execute(action, player)
