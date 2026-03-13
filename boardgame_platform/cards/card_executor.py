from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.game_engine import GameEngine
    from players.player_model import Player
    from cards.card_model import Card


class CardExecutor:
    def __init__(self, engine: "GameEngine"):
        self.engine = engine

    def apply(self, player: "Player", card: "Card") -> None:
        self.engine.state.messages.append(f"{player.name} drew: {card.title}")
        for action in card.actions:
            self.engine.action_executor.execute(player, action)
