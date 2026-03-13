from core.game_state import GameState
from board.square_model import Square


class PropertyLogic:
    @staticmethod
    def can_buy(player, square: Square, state: GameState) -> bool:
        return square.price is not None and state.property_state[square.id].owner_id is None and player.money >= square.price

    @staticmethod
    def buy(player, square: Square, state: GameState) -> None:
        player.money -= square.price or 0
        state.property_state[square.id].owner_id = player.player_id

    @staticmethod
    def rent_due(square: Square, houses: int = 0) -> int:
        if square.rent:
            idx = min(houses, len(square.rent) - 1)
            return square.rent[idx]
        if square.type == "railroad":
            return 25
        if square.type == "utility":
            return 30
        return 0
