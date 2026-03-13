from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class Square:
    id: int
    name: str
    type: str
    actions: List[Dict[str, Any]] = field(default_factory=list)
    price: Optional[int] = None
    group: Optional[str] = None
    rent: Optional[List[int]] = None
    house_cost: Optional[int] = None
    hotel_cost: Optional[int] = None
    deck: Optional[str] = None
    tax: Optional[int] = None

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Square":
        return Square(**data)
