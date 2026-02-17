"""Run configured LES demo case."""

from __future__ import annotations

import argparse
from pathlib import Path

from cfdles.config import load_config
from cfdles.timestepper import run_simulation


def main() -> None:
    parser = argparse.ArgumentParser(description="Run CFD LES demo")
    parser.add_argument("config", nargs="?", default="demos/cavity.json", help="Path to JSON config")
    args = parser.parse_args()
    cfg = load_config(Path(args.config))
    run_simulation(cfg)


if __name__ == "__main__":
    main()
