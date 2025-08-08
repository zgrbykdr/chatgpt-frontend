import json
from pathlib import Path

from monopoly.engine.game import Game
from monopoly.gui.app_window import run_gui
from monopoly.io.config_io import load_config_from_folder


def main():
    root = Path(__file__).parent
    default_data_dir = root / "monopoly" / "data"
    config = load_config_from_folder(default_data_dir)

    game = Game(config=config)
    run_gui(game)


if __name__ == "__main__":
    main()