class AnimationManager:
    def __init__(self):
        self.floaters = []

    def spawn_money(self, text, pos, color):
        self.floaters.append({"text": text, "x": pos[0], "y": pos[1], "ttl": 60, "color": color})

    def update(self):
        for f in self.floaters:
            f["y"] -= 0.6
            f["ttl"] -= 1
        self.floaters = [f for f in self.floaters if f["ttl"] > 0]
