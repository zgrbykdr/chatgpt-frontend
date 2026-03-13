from core.game_state import GameState


class TurnManager:
    def __init__(self, state: GameState) -> None:
        self.state = state
        self.doubles_streak = 0

    def advance(self) -> None:
        alive = [idx for idx, p in enumerate(self.state.players) if not p.bankrupt]
        if len(alive) <= 1:
            self.state.winner_id = alive[0] if alive else None
            return
        i = self.state.current_turn
        for _ in range(len(self.state.players)):
            i = (i + 1) % len(self.state.players)
            if not self.state.players[i].bankrupt:
                self.state.current_turn = i
                return
