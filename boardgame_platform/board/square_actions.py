from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.game_engine import GameEngine
    from players.player_model import Player


def execute_square_type(engine: "GameEngine", player: "Player", square_idx: int) -> None:
    square = engine.state.board.get_square(square_idx)
    if square is None:
        return

    if square.type in {"property", "railroad", "utility"}:
        engine.handle_property_landing(player, square)
    elif square.type == "tax":
        engine.charge_player(player, square.tax_amount or 100, reason=f"Tax: {square.name}")
    elif square.type == "go_to_jail":
        engine.send_player_to_jail(player)
    elif square.type == "draw_card":
        if square.deck:
            engine.draw_and_apply_card(player, square.deck)
