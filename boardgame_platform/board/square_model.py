from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SquareAction:
    type: str
    params: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "SquareAction":
        action_type = payload.get("type", "custom_message")
        params = {k: v for k, v in payload.items() if k != "type"}
        return cls(type=action_type, params=params)


@dataclass
class Square:
    id: int
    name: str
    type: str
    price: int = 0
    group: Optional[str] = None
    rent: List[int] = field(default_factory=list)
    house_cost: int = 0
    hotel_cost: int = 0
    mortgage_value: int = 0
    deck: Optional[str] = None
    tax_amount: int = 0
    actions: List[SquareAction] = field(default_factory=list)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "Square":
        actions = [SquareAction.from_dict(a) for a in payload.get("actions", [])]
        return cls(
            id=payload["id"],
            name=payload["name"],
            type=payload["type"],
            price=payload.get("price", 0),
            group=payload.get("group"),
            rent=payload.get("rent", []),
            house_cost=payload.get("house_cost", 0),
            hotel_cost=payload.get("hotel_cost", 0),
            mortgage_value=payload.get("mortgage_value", 0),
            deck=payload.get("deck"),
            tax_amount=payload.get("tax_amount", 0),
            actions=actions,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "price": self.price,
            "group": self.group,
            "rent": self.rent,
            "house_cost": self.house_cost,
            "hotel_cost": self.hotel_cost,
            "mortgage_value": self.mortgage_value,
            "deck": self.deck,
            "tax_amount": self.tax_amount,
            "actions": [{"type": a.type, **a.params} for a in self.actions],
        }
