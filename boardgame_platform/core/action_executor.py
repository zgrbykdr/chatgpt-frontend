from __future__ import annotations

from typing import Dict, Any


class ActionExecutor:
    def __init__(self, engine: "GameEngine") -> None:
        self.engine = engine

    def execute(self, action: Dict[str, Any], player) -> None:
        t = action.get("type")
        if t == "move_forward":
            self.engine.move_player(player, action.get("value", 0))
        elif t == "move_backward":
            self.engine.move_player(player, -action.get("value", 0))
        elif t == "move_to_square":
            self.engine.move_player_to(player, action.get("target", 0))
        elif t == "move_to_nearest_type":
            self.engine.move_to_nearest_type(player, action.get("target_type", "property"))
        elif t == "draw_card":
            self.engine.draw_card(player, action.get("deck"))
        elif t == "pay_money":
            self.engine.adjust_money(player, -action.get("value", 0))
        elif t == "receive_money":
            self.engine.adjust_money(player, action.get("value", 0))
        elif t == "pay_all_players":
            self.engine.pay_all_players(player, action.get("value", 0))
        elif t == "receive_from_all_players":
            self.engine.receive_from_all_players(player, action.get("value", 0))
        elif t == "go_to_jail":
            self.engine.send_to_jail(player)
        elif t == "leave_jail":
            player.in_jail = False
            player.jail_turns = 0
        elif t in {"skip_turns", "wait_turns"}:
            player.skipped_turns += action.get("value", 1)
        elif t == "custom_message":
            self.engine.push_message(action.get("text", ""))
        elif t == "grant_card":
            player.inventory.append(action.get("card", "special"))
        elif t == "remove_card":
            card = action.get("card")
            if card in player.inventory:
                player.inventory.remove(card)
        elif t == "gain_status":
            player.inventory.append(f"status:{action.get('status', 'boost')}")
        elif t == "lose_status":
            tag = f"status:{action.get('status', 'boost')}"
            if tag in player.inventory:
                player.inventory.remove(tag)
        elif t == "custom_event":
            self.engine.push_message(f"Custom event: {action.get('event', 'N/A')}")
