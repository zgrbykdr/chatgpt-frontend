from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable, List


@dataclass
class Animation:
    duration: float
    update_fn: Callable[[float], None]
    start_time: float = 0.0


class AnimationManager:
    def __init__(self):
        self.animations: List[Animation] = []

    def add(self, duration: float, update_fn: Callable[[float], None]):
        self.animations.append(Animation(duration=duration, update_fn=update_fn, start_time=time.time()))

    def tick(self):
        now = time.time()
        alive = []
        for anim in self.animations:
            p = min(1.0, (now - anim.start_time) / max(anim.duration, 1e-3))
            anim.update_fn(p)
            if p < 1.0:
                alive.append(anim)
        self.animations = alive
