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
        [sg.Button("Roll"), sg.Button("Roll in Jail"), sg.Button("End Turn")],
        [sg.Button("Buy"), sg.Button("Auction"), sg.Button("Build"), sg.Button("Sell")],
        [sg.Button("Mortgage"), sg.Button("Unmortgage"), sg.Button("Trade")],
        [sg.Button("Pay Tax Flat"), sg.Button("Pay Tax %")],
        [sg.Button("Pay Jail Fine"), sg.Button("Use Jail Card")],
        [sg.Multiline(size=(48, 12), key="-LOG-", disabled=True)]
    ]

    # Editor Tab
    editor_layout = [
        [sg.Text("Editor: Board Settings")],
        [sg.Text("GO Salary"), sg.Input(str(game.go_salary), key="-ED-GO-", size=(8,1)),
         sg.Text("Jail Fine"), sg.Input(str(game.config['board'].get('jail_fine',50)), key="-ED-JF-", size=(8,1)),
         sg.Text("Bank Houses"), sg.Input(str(game.bank_houses), key="-ED-BH-", size=(6,1)),
         sg.Text("Bank Hotels"), sg.Input(str(game.bank_hotels), key="-ED-BT-", size=(6,1))],
        [sg.Text("House Costs (color->cost JSON)"), sg.Input(json.dumps(game.house_costs), key='-ED-HC-', size=(60,1))],
        [sg.Button("Save Board Settings")],
        [sg.HorizontalSeparator()],
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
        window["End Turn"].update(disabled=game.must_roll_again)

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
        if event == "Roll in Jail":
            game.jail_roll()
            refresh_all()
        if event == "Buy":
            idx = game.players[game.current_player_index].position
            if game.squares[idx]["type"] in {"property", "railroad", "utility"}:
                game.buy_property(idx)
            refresh_all()
        if event == "Auction":
            idx = game.players[game.current_player_index].position
            if game.squares[idx]["type"] in {"property", "railroad", "utility"} and game.properties_state[idx].owner_index is None:
                winner, price = _auction_window(game, idx)
                if winner is not None and price is not None:
                    game.auction_buy(idx, winner, price)
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
        if event == "Build":
            idx = _select_owned_property(game, game.current_player_index)
            if idx is not None:
                if not game.build_house(idx):
                    sg.popup_error("Cannot build here.")
                refresh_all()
        if event == "Sell":
            idx = _select_owned_property(game, game.current_player_index)
            if idx is not None:
                if not game.sell_house(idx):
                    sg.popup_error("Cannot sell here.")
                refresh_all()
        if event == "Mortgage":
            idx = _select_owned_property(game, game.current_player_index)
            if idx is not None:
                if not game.mortgage(idx):
                    sg.popup_error("Cannot mortgage.")
                refresh_all()
        if event == "Unmortgage":
            idx = _select_owned_property(game, game.current_player_index, mortgaged_only=True)
            if idx is not None:
                if not game.unmortgage(idx):
                    sg.popup_error("Cannot unmortgage.")
                refresh_all()
        if event == "Trade":
            offer = _trade_window(game)
            if offer:
                game.apply_trade(offer)
                refresh_all()
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
        if event == "Save Board Settings":
            try:
                game.go_salary = int(values['-ED-GO-'])
                game.config['board']['go_salary'] = game.go_salary
                game.config['board']['jail_fine'] = int(values['-ED-JF-'])
                game.bank_houses = int(values['-ED-BH-'])
                game.bank_hotels = int(values['-ED-BT-'])
                game.house_costs = json.loads(values['-ED-HC-'])
                game.config['board']['bank_houses'] = game.bank_houses
                game.config['board']['bank_hotels'] = game.bank_hotels
                game.config['board']['house_costs'] = game.house_costs
                sg.popup("Board settings saved (runtime). Use Save Config to persist.")
            except Exception as e:
                sg.popup_error(f"Save failed: {e}")
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


def _auction_window(game: Game, prop_index: int):
    sq = game.squares[prop_index]
    layout = [
        [sg.Text(f"Auction: {sq.get('name')} (list price {game.currency}{sq.get('price',0)})")],
        [sg.Text(f"{game.players[0].name} bid"), sg.Input(key='-BID0-', size=(10,1))],
        [sg.Text(f"{game.players[1].name} bid"), sg.Input(key='-BID1-', size=(10,1))],
        [sg.Button("OK"), sg.Button("Cancel")]
    ]
    win = sg.Window("Auction", layout)
    winner = None
    price = None
    while True:
        e, v = win.read()
        if e in (sg.WIN_CLOSED, "Cancel"):
            break
        if e == "OK":
            try:
                b0 = int(v['-BID0-'] or 0)
                b1 = int(v['-BID1-'] or 0)
                if b0 < 0 or b1 < 0:
                    raise ValueError
                if b0 == b1:
                    sg.popup("Tie or no bids. No sale.")
                    break
                if b0 > b1:
                    winner = 0
                    price = b0
                else:
                    winner = 1
                    price = b1
                # ensure cash
                if game.players[winner].cash < price:
                    sg.popup_error("Winner lacks cash.")
                    winner = None
                    price = None
                else:
                    break
            except Exception:
                sg.popup_error("Invalid bids")
    win.close()
    return winner, price


def _select_owned_property(game: Game, player_index: int, mortgaged_only: bool=False):
    props = [i for i in game.players[player_index].properties if (not mortgaged_only or game.properties_state[i].mortgaged)]
    names = [f"{i:02d} {game.squares[i].get('name')}" for i in props]
    layout = [[sg.Listbox(values=names, size=(40, 10), key='-LB-')], [sg.Button("OK"), sg.Button("Cancel")]]
    win = sg.Window("Select Property", layout)
    idx = None
    while True:
        e, v = win.read()
        if e in (sg.WIN_CLOSED, "Cancel"):
            break
        if e == "OK":
            sel = v['-LB-']
            if sel:
                sel_text = sel[0]
                idx = int(sel_text.split()[0])
                break
    win.close()
    return idx


def _trade_window(game: Game):
    p0_props = [f"{i:02d} {game.squares[i].get('name')}" for i in game.players[0].properties]
    p1_props = [f"{i:02d} {game.squares[i].get('name')}" for i in game.players[1].properties]
    layout = [
        [sg.Text("Trade")],
        [sg.Text(game.players[0].name)],
        [sg.Listbox(values=p0_props, select_mode=sg.SELECT_MODE_MULTIPLE, size=(30,10), key='-P0PROPS-'),
         sg.VSeparator(),
         sg.Listbox(values=p1_props, select_mode=sg.SELECT_MODE_MULTIPLE, size=(30,10), key='-P1PROPS-')],
        [sg.Text(f"{game.players[0].name} gives cash"), sg.Input("0", key='-P0CASH-', size=(8,1)),
         sg.Text(f"{game.players[1].name} gives cash"), sg.Input("0", key='-P1CASH-', size=(8,1))],
        [sg.Text("GOJ from P0->P1"), sg.Input("0", key='-GOJ01-', size=(4,1)),
         sg.Text("GOJ from P1->P0"), sg.Input("0", key='-GOJ10-', size=(4,1))],
        [sg.Button("Make Trade"), sg.Button("Cancel")]
    ]
    win = sg.Window("Trade", layout)
    offer = None
    while True:
        e, v = win.read()
        if e in (sg.WIN_CLOSED, "Cancel"):
            break
        if e == "Make Trade":
            try:
                props_from = [int(x.split()[0]) for x in v['-P0PROPS-']]
                props_to = [int(x.split()[0]) for x in v['-P1PROPS-']]
                offer = {
                    'from': 0,
                    'to': 1,
                    'cash_from': int(v['-P0CASH-'] or 0),
                    'cash_to': int(v['-P1CASH-'] or 0),
                    'props_from': props_from,
                    'props_to': props_to,
                    'goj_from': int(v['-GOJ01-'] or 0),
                    'goj_to': int(v['-GOJ10-'] or 0)
                }
                break
            except Exception:
                sg.popup_error("Invalid trade inputs")
    win.close()
    return offer