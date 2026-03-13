from collections import defaultdict
from typing import Callable, Dict, List, Any


class EventBus:
    def __init__(self) -> None:
        self._handlers: Dict[str, List[Callable[..., None]]] = defaultdict(list)

    def subscribe(self, event: str, handler: Callable[..., None]) -> None:
        self._handlers[event].append(handler)

    def emit(self, event: str, **payload: Any) -> None:
        for handler in self._handlers[event]:
            handler(**payload)
