from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import PySimpleGUI as sg

from monopoly.engine.game import Game
from monopoly.io.config_io import load_config_from_folder, save_config_to_folder


def _format_cash(game: Game, amount: int) -> str:
    return f"{game.currency}{amount}"


def run_gui(game: Game) -> None:
    sg.theme("DarkBlue3")

    board_table = [[sg.Text("Board Preview (index : name / type)")],
                   [sg.Listbox(values=_board_preview(game), size=(40, 24), key="-BOARD-LB-")]]

    players_col = [
        [sg.Text("Players")],
        [sg.Text("Current:"), sg.Text("", key="-CURRENT-")],
        [sg.Text("P1 name"), sg.Input(game.players[0].name, key="-P1NAME-", size=(16,1)),
         sg.Text("P2 name"), sg.Input(game.players[1].name, key="-P2NAME-", size=(16,1)), sg.Button("Apply Names")],
        [sg.HorizontalSeparator()],
        [sg.Text("P1 Cash:"), sg.Text(_format_cash(game, game.players[0].cash), key="-P1C-")],
        [sg.Text("P2 Cash:"), sg.Text(_format_cash(game, game.players[1].cash), key="-P2C-")],
        [sg.Text("P1 Pos:"), sg.Text("0", key="-P1POS-")],
        [sg.Text("P2 Pos:"), sg.Text("0", key="-P2POS-")],
        [sg.HorizontalSeparator()],
        [sg.Button("Roll"), sg.Button("End Turn"), sg.Button("Buy"), sg.Button("Pay Tax Flat"), sg.Button("Pay Tax %")],
        [sg.Button("Pay Jail Fine"), sg.Button("Use Jail Card")],
        [sg.Multiline(size=(48, 12), key="-LOG-", disabled=True)]
    ]

    # Editor Tab
    editor_layout = [
        [sg.Text("Editor: Squares")],
        [sg.Text("Index"), sg.Input("", key="-ED-INDEX-", size=(5,1)), sg.Button("Load Square"), sg.Button("Save Square")],
        [sg.Text("Type"), sg.Input("", key="-ED-TYPE-", size=(12,1)),
         sg.Text("Name"), sg.Input("", key="-ED-NAME-", size=(28,1))],
        [sg.Text("Description"), sg.Input("", key="-ED-DESC-", size=(46,1))],
        [sg.Text("Color"), sg.Input("", key="-ED-COLOR-", size=(12,1)),
         sg.Text("Price"), sg.Input("", key="-ED-PRICE-", size=(10,1))],
        [sg.Text("Rent [base,1,2,3,4,hotel]"), sg.Input("", key="-ED-RENT-", size=(46,1))],
        [sg.HorizontalSeparator()],
        [sg.Text("Editor: Decks"), sg.Button("Reload Decks View"), sg.Button("Save Decks")],
        [sg.Text("Chance"), sg.Multiline(json.dumps(game.config["chance"], indent=2), key="-ED-CHANCE-", size=(50, 12))],
        [sg.Text("Community Chest"), sg.Multiline(json.dumps(game.config["community_chest"], indent=2), key="-ED-COMM-", size=(50, 12))],
        [sg.HorizontalSeparator()],
        [sg.Text("Config Folder"), sg.Input(str(Path.cwd() / "monopoly" / "data"), key="-CFG-PATH-", size=(50,1)),
         sg.Button("Load Config"), sg.Button("Save Config")]
    ]

    layout = [
        [sg.Menu([["File", ["Load Config", "Save Config", "Exit"]]])],
        [sg.Column(board_table), sg.VSeparator(), sg.Column(players_col)],
        [sg.TabGroup([[sg.Tab("Editor", editor_layout)]])]
    ]

    window = sg.Window("Monopoly - 2P Custom", layout, finalize=True)

    def refresh_all():
        window["-BOARD-LB-"].update(values=_board_preview(game))
        window["-P1C-"].update(_format_cash(game, game.players[0].cash))
        window["-P2C-"].update(_format_cash(game, game.players[1].cash))
        window["-P1POS-"].update(str(game.players[0].position))
        window["-P2POS-"].update(str(game.players[1].position))
        window["-CURRENT-"].update(game.players[game.current_player_index].name)
        window["-LOG-"].update("\n".join(game.log[-200:]))

    refresh_all()

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Exit"):
            break
        if event == "Apply Names":
            game.players[0].name = values["-P1NAME-"] or game.players[0].name
            game.players[1].name = values["-P2NAME-"] or game.players[1].name
            refresh_all()
        if event == "Roll":
            result = game.take_turn()
            refresh_all()
        if event == "End Turn":
            game.end_turn()
            refresh_all()
        if event == "Buy":
            idx = game.players[game.current_player_index].position
            if game.squares[idx]["type"] in {"property", "railroad", "utility"}:
                game.buy_property(idx)
            refresh_all()
        if event == "Pay Tax Flat":
            game.choose_tax("flat")
            refresh_all()
        if event == "Pay Tax %":
            game.choose_tax("percent")
            refresh_all()
        if event == "Pay Jail Fine":
            game.pay_jail_fine()
            refresh_all()
        if event == "Use Jail Card":
            game.use_get_out_of_jail()
            refresh_all()
        if event == "Load Square":
            try:
                idx = int(values["-ED-INDEX-"])
                sq = game.squares[idx]
                window["-ED-TYPE-"].update(sq.get("type", ""))
                window["-ED-NAME-"].update(sq.get("name", ""))
                window["-ED-DESC-"].update(sq.get("description", ""))
                window["-ED-COLOR-"].update(sq.get("color", ""))
                window["-ED-PRICE-"].update(str(sq.get("price", "")))
                window["-ED-RENT-"].update(json.dumps(sq.get("rent", [])))
            except Exception:
                sg.popup_error("Invalid index")
        if event == "Save Square":
            try:
                idx = int(values["-ED-INDEX-"])
                sq = game.squares[idx]
                sq["type"] = values["-ED-TYPE-"] or sq.get("type", "")
                sq["name"] = values["-ED-NAME-"] or sq.get("name", "")
                desc = values["-ED-DESC-"]
                if desc:
                    sq["description"] = desc
                color = values["-ED-COLOR-"]
                if color:
                    sq["color"] = color
                price = values["-ED-PRICE-"]
                if price:
                    sq["price"] = int(price)
                rent_txt = values["-ED-RENT-"]
                if rent_txt:
                    sq["rent"] = json.loads(rent_txt)
                refresh_all()
            except Exception as e:
                sg.popup_error(f"Save failed: {e}")
        if event == "Reload Decks View":
            window["-ED-CHANCE-"].update(json.dumps(game.config["chance"], indent=2))
            window["-ED-COMM-"].update(json.dumps(game.config["community_chest"], indent=2))
        if event == "Save Decks":
            try:
                game.config["chance"] = json.loads(values["-ED-CHANCE-"])
                game.config["community_chest"] = json.loads(values["-ED-COMM-"])
                game.chance_deck = list(game.config["chance"])  # reset deck
                game.community_deck = list(game.config["community_chest"])  # reset deck
                sg.popup("Decks updated")
            except Exception as e:
                sg.popup_error(f"Deck save failed: {e}")
        if event in ("Load Config", "Save Config") or event in ("-menu-Load Config-", "-menu-Save Config-"):
            # Menu tied to same handlers below
            pass
        if event == "Load Config":
            try:
                folder = Path(values["-CFG-PATH-"])
                game.config = load_config_from_folder(folder)
                game.squares = game.config["board"]["squares"]
                game.chance_deck = list(game.config["chance"])  # reset
                game.community_deck = list(game.config["community_chest"])  # reset
                sg.popup("Config loaded")
                refresh_all()
            except Exception as e:
                sg.popup_error(f"Load failed: {e}")
        if event == "Save Config":
            try:
                folder = Path(values["-CFG-PATH-"])
                # ensure board config mirrors runtime changes
                game.config["board"]["squares"] = game.squares
                save_config_to_folder(folder, game.config)
                sg.popup("Config saved")
            except Exception as e:
                sg.popup_error(f"Save failed: {e}")

    window.close()


def _board_preview(game: Game) -> List[str]:
    out = []
    for idx, s in enumerate(game.squares):
        name = s.get("name", s["type"]).strip()
        out.append(f"{idx:02d}: {name} / {s['type']}")
    return out