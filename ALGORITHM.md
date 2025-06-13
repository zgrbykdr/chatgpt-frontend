# Monopoly Game Algorithm (Python/Pygame)

This document outlines a high-level algorithm for implementing a graphical Monopoly game in Python using the `pygame` library. All rules from the original board game are included while allowing the user to edit square names and card text before starting play.

## Data Structures
1. **Square** – represents one of the 40 spaces on the board.
   - `id`: index from 0–39
   - `name`: editable display name
   - `type`: `property`, `railroad`, `utility`, `chance`, `community`, `tax`, `go`, `jail`, `gotojail`, or `parking`
   - `price`, `rent`, `houseCost`, `hotelCost`
   - `owner`: reference to a `Player` or `None`
   - `mortgaged`: boolean
   - `houses`: number of houses on the property (0–4)
   - `hasHotel`: whether a hotel is present

2. **Card** – element in the Chance or Community Chest decks.
   - `text`: message shown to the player
   - `action(game, player)`: function executed when drawn

3. **Player**
   - `name`
   - `tokenColor`
   - `position` (0–39)
   - `money`
   - list of owned properties
   - `inJail` flag and remaining `jailTurns`
   - cards held such as "Get Out of Jail Free"

4. **Game** – controller tracking board state, decks, current player index and dice.

## Initialization
1. Read board definition and card data from JSON so users can change names or rules.
2. Create players with starting balance of $1500 and assign each a colour token.
3. Shuffle the Chance and Community Chest decks.
4. Start with the first player.

## Turn Sequence
1. If the current player is in Jail:
   - Allow paying bail, using "Get Out of Jail Free" or attempting to roll doubles.
   - If released, move according to dice; otherwise end the turn.
2. Roll two six-sided dice and move the player's token. Collect $200 when passing GO.
3. Handle the landed square:
   - **Property/Railroad/Utility** – allow purchase if unowned, or pay rent (with houses/hotel and monopoly bonuses). Players can mortgage/unmortgage.
   - **Chance/Community** – draw a card and run its action.
   - **Tax** – pay income or luxury tax.
   - **Go To Jail** – move to Jail square and set `inJail` with 3 turns.
   - **Jail/Free Parking/GO** – mostly passive squares.
4. After movement, players may trade, buy houses/hotels, or manage mortgages.
5. End the turn and move to the next active player. Remove bankrupt players.

## Victory Condition
The last remaining player with a positive balance wins the game.

## Graphical Interface
- The game uses `pygame` in full screen mode and scales the board based on the detected screen resolution.
- The board is drawn around the edges of the screen with each space scaled to fit.
- Player tokens are coloured circles that animate around the board when moving.
- Simple dialogs or text areas provide prompts for buying properties, paying rent and drawing cards.

## Dependencies
- The Python script checks for the `pygame` module at startup and attempts to install it with `pip` if it is missing.
- When `DIAGNOSTIC` mode is enabled, every caught exception is logged to `errorlog.txt` with a timestamp and numeric error code. Missing files, JSON parse failures and unexpected crashes each have distinct codes.

This algorithm targets a complete implementation of classic Monopoly rules in a Python environment. The JSON configuration allows users to rename squares and cards before playing.

## Customisation
- **Square Actions** – Each board entry may include an `action` object with keys like `moveTo`, `moveBy`, `money` or `gotoJail`. These allow the game rules for any square to be modified without editing code.
- **Fonts** – The web editor exposes controls for font family and size. These values update CSS variables so the configuration screen automatically centres and resizes text.
