from typing import Dict, Any


def make_tax_action(amount: int) -> Dict[str, Any]:
    return {"type": "pay_money", "value": amount}
