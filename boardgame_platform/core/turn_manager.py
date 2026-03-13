import random


class TurnManager:
    def __init__(self):
        self.last_roll = (0, 0)

    def roll_dice(self) -> tuple[int, int]:
        self.last_roll = (random.randint(1, 6), random.randint(1, 6))
        return self.last_roll

    def is_double(self) -> bool:
        return self.last_roll[0] == self.last_roll[1]
