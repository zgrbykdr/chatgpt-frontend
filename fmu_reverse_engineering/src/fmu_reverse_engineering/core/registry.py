from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Registry:
    items: dict[str, Callable[..., Any]] = field(default_factory=dict)

    def register(self, name: str, factory: Callable[..., Any]) -> None:
        self.items[name] = factory

    def create(self, name: str, **kwargs: Any) -> Any:
        if name not in self.items:
            raise KeyError(f"Unknown registration: {name}")
        return self.items[name](**kwargs)

    def list(self) -> list[str]:
        return sorted(self.items.keys())
