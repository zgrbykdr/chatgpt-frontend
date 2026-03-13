from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Dict

if TYPE_CHECKING:
    from core.game_engine import GameEngine
    from players.player_model import Player


class ActionExecutor:
    def __init__(self, engine: "GameEngine"):
        self.engine = engine
        self.handlers: Dict[str, Callable[["Player", dict], None]] = {
            "move_forward": self._move_forward,
            "move_backward": self._move_backward,
            "move_to_square": self._move_to_square,
            "draw_card": self._draw_card,
            "pay_money": self._pay_money,
            "receive_money": self._receive_money,
            "pay_all_players": self._pay_all,
            "receive_from_all_players": self._receive_all,
            "go_to_jail": self._go_to_jail,
            "leave_jail": self._leave_jail,
            "skip_turns": self._skip_turns,
            "wait_turns": self._skip_turns,
            "custom_message": self._custom_message,
            "custom_event": self._custom_event,
        }

    def execute(self, player: "Player", action: dict) -> None:
        action_type = action.get("type")
        handler = self.handlers.get(action_type, self._custom_event)
        handler(player, action)

    def _move_forward(self, player: "Player", action: dict) -> None:
        self.engine.move_player_steps(player, action.get("value", 0))

    def _move_backward(self, player: "Player", action: dict) -> None:
        self.engine.move_player_steps(player, -action.get("value", 0))

    def _move_to_square(self, player: "Player", action: dict) -> None:
        self.engine.move_player_to(player, action.get("target", 0), collect_go=False)

    def _draw_card(self, player: "Player", action: dict) -> None:
        self.engine.draw_and_apply_card(player, action.get("deck", "Chance"))

    def _pay_money(self, player: "Player", action: dict) -> None:
        self.engine.charge_player(player, action.get("value", 0), "Card/Square payment")

    def _receive_money(self, player: "Player", action: dict) -> None:
        player.money += action.get("value", 0)

    def _pay_all(self, player: "Player", action: dict) -> None:
        value = action.get("value", 0)
        for other in self.engine.state.players:
            if other is player or not other.active:
                continue
            self.engine.transfer_money(player, other, value)

    def _receive_all(self, player: "Player", action: dict) -> None:
        value = action.get("value", 0)
        for other in self.engine.state.players:
            if other is player or not other.active:
                continue
            self.engine.transfer_money(other, player, value)

    def _go_to_jail(self, player: "Player", action: dict) -> None:
        self.engine.send_player_to_jail(player)

    def _leave_jail(self, player: "Player", action: dict) -> None:
        player.in_jail = False
        player.jail_turns = 0

    def _skip_turns(self, player: "Player", action: dict) -> None:
        player.skip_turns += action.get("value", 1)

    def _custom_message(self, player: "Player", action: dict) -> None:
        self.engine.state.messages.append(action.get("message", f"{player.name}: custom action"))

    def _custom_event(self, player: "Player", action: dict) -> None:
        self.engine.state.messages.append(f"Custom event triggered: {action}")
