export class GameEngine {
  constructor(config, players) {
    this.config = structuredClone(config);
    this.players = players.map((p, idx) => ({
      id: idx,
      name: p.name,
      token: p.token,
      color: p.color,
      money: config.rules.startingMoney,
      position: 0,
      properties: [],
      inJail: false,
      jailTurns: 0,
      bankrupt: false,
      skippedTurns: 0
    }));

    this.state = {
      currentPlayerIndex: 0,
      dice: [1, 1],
      phase: 'roll',
      winner: null,
      message: 'Game started.',
      ownership: {},
      buildings: {},
      decks: this.#initializeDecks(config.decks),
      lastCard: null
    };

    this.actionHandlers = this.#createActionHandlers();
  }

  #initializeDecks(decks) {
    const map = {};
    for (const deck of decks) {
      map[deck.id] = {
        id: deck.id,
        cards: [...deck.cards],
        discard: []
      };
      this.#shuffle(map[deck.id].cards);
    }
    return map;
  }

  #createActionHandlers() {
    return {
      moveForward: (ctx, action) => this.movePlayer(ctx.player.id, action.spaces),
      moveBackward: (ctx, action) => this.movePlayer(ctx.player.id, -action.spaces),
      moveTo: (ctx, action) => this.movePlayerTo(ctx.player.id, action.square),
      moveToNearest: (ctx, action) => this.movePlayerToNearest(ctx.player.id, action.category),
      drawCard: (ctx, action) => this.drawCard(ctx.player.id, action.deckId),
      payMoney: (ctx, action) => this.adjustMoney(ctx.player.id, -action.amount),
      receiveMoney: (ctx, action) => this.adjustMoney(ctx.player.id, action.amount),
      payAllPlayers: (ctx, action) => this.transferToAll(ctx.player.id, -action.amount),
      receiveFromAllPlayers: (ctx, action) => this.transferToAll(ctx.player.id, action.amount),
      skipTurns: (ctx, action) => {
        ctx.player.skippedTurns += action.turns;
      },
      goToJail: (ctx) => this.sendToJail(ctx.player.id),
      exitJail: (ctx) => {
        ctx.player.inJail = false;
        ctx.player.jailTurns = 0;
      },
      customEffect: (ctx, action) => {
        this.state.message = action.message ?? `${ctx.player.name} triggered a custom effect.`;
      }
    };
  }

  get currentPlayer() {
    return this.players[this.state.currentPlayerIndex];
  }

  getSquare(index) {
    return this.config.board.squares[index];
  }

  rollDice() {
    const p = this.currentPlayer;
    if (p.bankrupt || this.state.phase !== 'roll') return;

    if (p.skippedTurns > 0) {
      p.skippedTurns -= 1;
      this.state.message = `${p.name} skips this turn.`;
      return this.endTurn();
    }

    if (p.inJail) {
      p.jailTurns -= 1;
      if (p.jailTurns <= 0) {
        p.inJail = false;
        this.state.message = `${p.name} exits jail.`;
      } else {
        this.state.message = `${p.name} is in jail (${p.jailTurns} turns left).`;
        return this.endTurn();
      }
    }

    const d1 = 1 + Math.floor(Math.random() * 6);
    const d2 = 1 + Math.floor(Math.random() * 6);
    this.state.dice = [d1, d2];
    const steps = d1 + d2;

    this.state.phase = 'resolving';
    const passedGo = this.movePlayer(p.id, steps);
    if (passedGo) this.adjustMoney(p.id, this.config.rules.passGoAmount);
    this.resolveLanding(p.id);
  }

  movePlayer(playerId, steps) {
    const player = this.players[playerId];
    const total = this.config.board.squares.length;
    const start = player.position;
    let target = (start + steps) % total;
    if (target < 0) target += total;
    const passedGo = steps > 0 && target < start;
    player.position = target;
    return passedGo;
  }

  movePlayerTo(playerId, squareIndex) {
    const player = this.players[playerId];
    const passedGo = squareIndex < player.position;
    player.position = squareIndex;
    if (passedGo) this.adjustMoney(playerId, this.config.rules.passGoAmount);
    this.resolveLanding(playerId);
  }

  movePlayerToNearest(playerId, category) {
    const player = this.players[playerId];
    const squares = this.config.board.squares;
    for (let i = 1; i <= squares.length; i += 1) {
      const idx = (player.position + i) % squares.length;
      if (squares[idx].category === category) {
        this.movePlayerTo(playerId, idx);
        return;
      }
    }
  }

  resolveLanding(playerId) {
    const player = this.players[playerId];
    const square = this.getSquare(player.position);
    this.state.message = `${player.name} landed on ${square.name}.`;

    if (square.type === 'property') {
      const ownerId = this.state.ownership[square.id];
      if (ownerId === undefined) {
        this.state.phase = 'buy';
        this.state.message += ` ${square.name} is available for $${square.price}.`;
        return;
      }
      if (ownerId !== playerId) {
        const rent = this.calculateRent(square.id);
        this.adjustMoney(playerId, -rent);
        this.adjustMoney(ownerId, rent);
        this.state.message += ` Paid $${rent} rent to ${this.players[ownerId].name}.`;
      }
    }

    if (square.type === 'tax') {
      this.adjustMoney(playerId, -square.amount);
      this.state.message += ` Paid tax $${square.amount}.`;
    }

    if (square.type === 'draw') {
      const card = this.drawCard(playerId, square.deckId);
      this.state.lastCard = card;
      this.state.message += ` Drew card: ${card.description}`;
    }

    if (square.actions?.length) {
      for (const action of square.actions) {
        this.executeAction(player, action);
      }
    }

    this.checkBankruptcy(playerId);
    this.state.phase = 'end';
  }

  executeAction(player, action) {
    const handler = this.actionHandlers[action.type];
    if (handler) handler({ player }, action);
  }

  drawCard(playerId, deckId) {
    const deck = this.state.decks[deckId];
    if (!deck.cards.length) {
      deck.cards = [...deck.discard];
      deck.discard = [];
      this.#shuffle(deck.cards);
    }
    const card = deck.cards.shift();
    deck.discard.push(card);
    for (const action of card.actions ?? []) {
      this.executeAction(this.players[playerId], action);
    }
    return card;
  }

  buyProperty() {
    const p = this.currentPlayer;
    const square = this.getSquare(p.position);
    if (this.state.phase !== 'buy' || square.type !== 'property') return false;
    if (p.money < square.price) return false;
    this.adjustMoney(p.id, -square.price);
    p.properties.push(square.id);
    this.state.ownership[square.id] = p.id;
    this.state.message = `${p.name} bought ${square.name} for $${square.price}.`;
    this.state.phase = 'end';
    return true;
  }

  canBuild(playerId, propertyId) {
    const property = this.getSquare(propertyId);
    if (!property || property.type !== 'property' || !property.houseCost) return false;
    const owner = this.state.ownership[propertyId];
    if (owner !== playerId) return false;
    const player = this.players[playerId];
    if (player.money < property.houseCost) return false;
    const buildings = this.state.buildings[propertyId] ?? { houses: 0, hotel: false };
    if (buildings.hotel) return false;
    if (buildings.houses < this.config.rules.maxHouses) return true;
    return buildings.houses === this.config.rules.maxHouses;
  }

  buildOnProperty(propertyId) {
    const p = this.currentPlayer;
    if (!this.canBuild(p.id, propertyId)) return false;
    const prop = this.getSquare(propertyId);
    const buildings = this.state.buildings[propertyId] ?? { houses: 0, hotel: false };
    if (buildings.houses >= this.config.rules.maxHouses) {
      buildings.hotel = true;
    } else {
      buildings.houses += 1;
    }
    this.state.buildings[propertyId] = buildings;
    this.adjustMoney(p.id, -prop.houseCost);
    this.state.message = `${p.name} built on ${prop.name}.`;
    return true;
  }

  calculateRent(propertyId) {
    const square = this.getSquare(propertyId);
    const ownerId = this.state.ownership[propertyId];
    if (ownerId === undefined) return 0;
    let rent = square.baseRent;

    if (square.group === 'railroad') {
      const ownedRailroads = this.players[ownerId].properties.filter((pid) => this.getSquare(pid).group === 'railroad').length;
      rent = 25 * ownedRailroads;
    }

    const buildings = this.state.buildings[propertyId] ?? { houses: 0, hotel: false };
    if (buildings.houses > 0) rent += Math.floor(rent * buildings.houses * this.config.rules.houseRentMultiplier);
    if (buildings.hotel) rent += Math.floor(rent * this.config.rules.hotelRentMultiplier);
    return rent;
  }

  adjustMoney(playerId, amount) {
    this.players[playerId].money += amount;
  }

  transferToAll(playerId, amountEach) {
    const actor = this.players[playerId];
    for (const p of this.players) {
      if (p.id === playerId || p.bankrupt) continue;
      if (amountEach > 0) {
        this.adjustMoney(p.id, -amountEach);
        this.adjustMoney(playerId, amountEach);
      } else {
        this.adjustMoney(playerId, amountEach);
        this.adjustMoney(p.id, -amountEach);
      }
    }
    if (actor.money < 0) this.checkBankruptcy(playerId);
  }

  sendToJail(playerId) {
    const p = this.players[playerId];
    p.position = this.config.rules.jailIndex;
    p.inJail = true;
    p.jailTurns = 2;
    this.state.message = `${p.name} goes to jail.`;
  }

  checkBankruptcy(playerId) {
    const p = this.players[playerId];
    if (p.money >= 0 || p.bankrupt) return;
    p.bankrupt = true;
    for (const prop of p.properties) {
      delete this.state.ownership[prop];
      delete this.state.buildings[prop];
    }
    p.properties = [];
    this.state.message = `${p.name} is bankrupt and out of the game.`;
    const active = this.players.filter((pl) => !pl.bankrupt);
    if (active.length === 1) this.state.winner = active[0].id;
  }

  endTurn() {
    if (this.state.winner !== null) return;
    this.state.phase = 'roll';
    let next = this.state.currentPlayerIndex;
    for (let i = 0; i < this.players.length; i += 1) {
      next = (next + 1) % this.players.length;
      if (!this.players[next].bankrupt) break;
    }
    this.state.currentPlayerIndex = next;
    this.state.lastCard = null;
  }

  serialize() {
    return JSON.stringify({ config: this.config, players: this.players, state: this.state });
  }

  static fromSerialized(serialized) {
    const parsed = JSON.parse(serialized);
    const engine = new GameEngine(parsed.config, parsed.players);
    engine.players = parsed.players;
    engine.state = parsed.state;
    return engine;
  }

  #shuffle(arr) {
    for (let i = arr.length - 1; i > 0; i -= 1) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
  }
}
