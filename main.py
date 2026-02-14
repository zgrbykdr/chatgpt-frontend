from __future__ import annotations

# Supports both: python -m main  and  python -m main.py
from py_app.main import main

if __name__ == "__main__":
    raise SystemExit(main())
