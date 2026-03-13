import json
import random
import tempfile
from pathlib import Path
from typing import Any, Dict


def safe_json_read(path: Path, default: Any) -> Any:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def safe_json_write(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, dir=path.parent, encoding="utf-8") as tmp:
        json.dump(payload, tmp, indent=2, ensure_ascii=False)
        temp_path = Path(tmp.name)
    temp_path.replace(path)


def roll_die(sides: int) -> int:
    return random.randint(1, sides)


def now_iso() -> str:
    from datetime import datetime
    return datetime.now().isoformat(timespec="seconds")


def parse_dice_expression(expr: str) -> Dict[str, int]:
    expr = expr.lower().replace(" ", "")
    if "d" not in expr:
        raise ValueError("Expression must include d, e.g. 2d6+3")
    n_part, tail = expr.split("d", 1)
    count = int(n_part or "1")
    mod = 0
    if "+" in tail:
        sides_part, mod_part = tail.split("+", 1)
        mod = int(mod_part)
    elif "-" in tail:
        sides_part, mod_part = tail.split("-", 1)
        mod = -int(mod_part)
    else:
        sides_part = tail
    return {"count": count, "sides": int(sides_part), "mod": mod}
