const TOKEN_EMOJIS = ["🚗", "🐕", "🎩", "🛳️", "🧲", "🐎"];

const DEFAULT_MONOPOLY_CONFIG = {
  name: "Classic Monopoly",
  startingMoney: 1500,
  salaryOnPassGo: 200,
  jailPosition: 10,
  goToJailPosition: 30,
  maxHouses: 4,
  board: [
    { name: "GO", type: "go" },
    { name: "Mediterranean Avenue", type: "property", price: 60, rent: [2, 10, 30, 90, 160, 250], houseCost: 50, group: "Brown" },
    { name: "Community Chest", type: "community", deck: "community" },
    { name: "Baltic Avenue", type: "property", price: 60, rent: [4, 20, 60, 180, 320, 450], houseCost: 50, group: "Brown" },
    { name: "Income Tax", type: "tax", amount: 200 },
    { name: "Reading Railroad", type: "railroad", price: 200, rent: [25, 50, 100, 200], group: "Railroad" },
    { name: "Oriental Avenue", type: "property", price: 100, rent: [6, 30, 90, 270, 400, 550], houseCost: 50, group: "Light Blue" },
    { name: "Chance", type: "chance", deck: "chance" },
    { name: "Vermont Avenue", type: "property", price: 100, rent: [6, 30, 90, 270, 400, 550], houseCost: 50, group: "Light Blue" },
    { name: "Connecticut Avenue", type: "property", price: 120, rent: [8, 40, 100, 300, 450, 600], houseCost: 50, group: "Light Blue" },
    { name: "Jail / Just Visiting", type: "jail" },
    { name: "St. Charles Place", type: "property", price: 140, rent: [10, 50, 150, 450, 625, 750], houseCost: 100, group: "Pink" },
    { name: "Electric Company", type: "utility", price: 150, rentMultiplier: [4, 10], group: "Utility" },
    { name: "States Avenue", type: "property", price: 140, rent: [10, 50, 150, 450, 625, 750], houseCost: 100, group: "Pink" },
    { name: "Virginia Avenue", type: "property", price: 160, rent: [12, 60, 180, 500, 700, 900], houseCost: 100, group: "Pink" },
    { name: "Pennsylvania Railroad", type: "railroad", price: 200, rent: [25, 50, 100, 200], group: "Railroad" },
    { name: "St. James Place", type: "property", price: 180, rent: [14, 70, 200, 550, 750, 950], houseCost: 100, group: "Orange" },
    { name: "Community Chest", type: "community", deck: "community" },
    { name: "Tennessee Avenue", type: "property", price: 180, rent: [14, 70, 200, 550, 750, 950], houseCost: 100, group: "Orange" },
    { name: "New York Avenue", type: "property", price: 200, rent: [16, 80, 220, 600, 800, 1000], houseCost: 100, group: "Orange" },
    { name: "Free Parking", type: "freeParking" },
    { name: "Kentucky Avenue", type: "property", price: 220, rent: [18, 90, 250, 700, 875, 1050], houseCost: 150, group: "Red" },
    { name: "Chance", type: "chance", deck: "chance" },
    { name: "Indiana Avenue", type: "property", price: 220, rent: [18, 90, 250, 700, 875, 1050], houseCost: 150, group: "Red" },
    { name: "Illinois Avenue", type: "property", price: 240, rent: [20, 100, 300, 750, 925, 1100], houseCost: 150, group: "Red" },
    { name: "B. & O. Railroad", type: "railroad", price: 200, rent: [25, 50, 100, 200], group: "Railroad" },
    { name: "Atlantic Avenue", type: "property", price: 260, rent: [22, 110, 330, 800, 975, 1150], houseCost: 150, group: "Yellow" },
    { name: "Ventnor Avenue", type: "property", price: 260, rent: [22, 110, 330, 800, 975, 1150], houseCost: 150, group: "Yellow" },
    { name: "Water Works", type: "utility", price: 150, rentMultiplier: [4, 10], group: "Utility" },
    { name: "Marvin Gardens", type: "property", price: 280, rent: [24, 120, 360, 850, 1025, 1200], houseCost: 150, group: "Yellow" },
    { name: "Go To Jail", type: "goToJail" },
    { name: "Pacific Avenue", type: "property", price: 300, rent: [26, 130, 390, 900, 1100, 1275], houseCost: 200, group: "Green" },
    { name: "North Carolina Avenue", type: "property", price: 300, rent: [26, 130, 390, 900, 1100, 1275], houseCost: 200, group: "Green" },
    { name: "Community Chest", type: "community", deck: "community" },
    { name: "Pennsylvania Avenue", type: "property", price: 320, rent: [28, 150, 450, 1000, 1200, 1400], houseCost: 200, group: "Green" },
    { name: "Short Line", type: "railroad", price: 200, rent: [25, 50, 100, 200], group: "Railroad" },
    { name: "Chance", type: "chance", deck: "chance" },
    { name: "Park Place", type: "property", price: 350, rent: [35, 175, 500, 1100, 1300, 1500], houseCost: 200, group: "Dark Blue" },
    { name: "Luxury Tax", type: "tax", amount: 100 },
    { name: "Boardwalk", type: "property", price: 400, rent: [50, 200, 600, 1400, 1700, 2000], houseCost: 200, group: "Dark Blue" }
  ],
  decks: {
    chance: [
      { text: "Advance to GO", effects: [{ type: "goTo", position: 0, passGo: true }] },
      { text: "Advance to Illinois Avenue", effects: [{ type: "goTo", position: 24, passGo: true }] },
      { text: "Advance to St. Charles Place", effects: [{ type: "goTo", position: 11, passGo: true }] },
      { text: "Bank pays you dividend of $50", effects: [{ type: "receive", amount: 50 }] },
      { text: "Go back 3 spaces", effects: [{ type: "move", steps: -3 }] },
      { text: "Go to Jail", effects: [{ type: "goToJail" }] },
      { text: "Pay poor tax of $15", effects: [{ type: "pay", amount: 15 }] },
      { text: "Take a trip to Reading Railroad", effects: [{ type: "goTo", position: 5, passGo: true }] },
      { text: "You have been elected chairman. Pay each player $50", effects: [{ type: "payAll", amount: 50 }] },
      { text: "Your building loan matures. Collect $150", effects: [{ type: "receive", amount: 150 }] }
    ],
    community: [
      { text: "Advance to GO", effects: [{ type: "goTo", position: 0, passGo: true }] },
      { text: "Bank error in your favor. Collect $200", effects: [{ type: "receive", amount: 200 }] },
      { text: "Doctor's fees. Pay $50", effects: [{ type: "pay", amount: 50 }] },
      { text: "From sale of stock you get $50", effects: [{ type: "receive", amount: 50 }] },
      { text: "Go to Jail", effects: [{ type: "goToJail" }] },
      { text: "Holiday fund matures. Receive $100", effects: [{ type: "receive", amount: 100 }] },
      { text: "Income tax refund. Collect $20", effects: [{ type: "receive", amount: 20 }] },
      { text: "Pay hospital fees of $100", effects: [{ type: "pay", amount: 100 }] },
      { text: "Pay school fees of $50", effects: [{ type: "pay", amount: 50 }] },
      { text: "You inherit $100", effects: [{ type: "receive", amount: 100 }] }
    ]
  }
};

class MonopolyEngine {
  constructor(config, players) {
    this.config = structuredClone(config);
    this.players = players;
    this.currentPlayerIndex = 0;
    this.turn = 1;
    this.pendingBuy = null;
    this.lastRoll = [0, 0];
    this.messageLog = [];
    this.freeParkingPot = 0;
    this.deckPointers = Object.fromEntries(Object.keys(this.config.decks).map((k) => [k, 0]));
  }

  get currentPlayer() {
    return this.players[this.currentPlayerIndex];
  }

  pushLog(msg) {
    this.messageLog.unshift(`[T${this.turn}] ${msg}`);
    this.messageLog = this.messageLog.slice(0, 60);
  }

  rollDice() {
    const p = this.currentPlayer;
    if (p.bankrupt) return;
    if (p.skipTurns > 0) {
      p.skipTurns -= 1;
      this.pushLog(`${p.name} skips turn.`);
      this.endTurn();
      return;
    }
    if (p.inJail) {
      p.jailTurns += 1;
      const [d1, d2] = this.randomDice();
      this.lastRoll = [d1, d2];
      if (d1 === d2) {
        p.inJail = false;
        p.jailTurns = 0;
        this.pushLog(`${p.name} rolled doubles and leaves jail.`);
        this.movePlayer(p, d1 + d2);
      } else if (p.jailTurns >= 3) {
        this.payPlayer(p, 50, "Jail fine", true);
        p.inJail = false;
        p.jailTurns = 0;
        this.movePlayer(p, d1 + d2);
      } else {
        this.pushLog(`${p.name} remains in jail.`);
        this.endTurn();
      }
      return;
    }

    const [d1, d2] = this.randomDice();
    this.lastRoll = [d1, d2];
    this.movePlayer(p, d1 + d2);
    if (d1 !== d2) this.endTurn();
    else this.pushLog(`${p.name} rolled doubles and gets another roll.`);
  }

  randomDice() {
    return [1 + Math.floor(Math.random() * 6), 1 + Math.floor(Math.random() * 6)];
  }

  movePlayer(player, steps) {
    const oldPos = player.position;
    const size = this.config.board.length;
    let newPos = (oldPos + steps) % size;
    if (newPos < 0) newPos += size;
    if (steps > 0 && oldPos + steps >= size) {
      player.money += this.config.salaryOnPassGo;
      this.pushLog(`${player.name} passed GO and collected $${this.config.salaryOnPassGo}.`);
    }
    player.position = newPos;
    this.handleLanding(player, this.config.board[newPos]);
  }

  handleLanding(player, square) {
    this.pendingBuy = null;
    this.pushLog(`${player.name} landed on ${square.name}.`);
    if (square.type === "go") return;
    if (square.type === "tax") {
      this.payPlayer(player, square.amount || 0, `${square.name}`);
      this.freeParkingPot += square.amount || 0;
      return;
    }
    if (square.type === "freeParking") {
      player.money += this.freeParkingPot;
      this.pushLog(`${player.name} collected free parking pot $${this.freeParkingPot}.`);
      this.freeParkingPot = 0;
      return;
    }
    if (square.type === "goToJail") {
      this.sendToJail(player);
      return;
    }
    if (square.type === "chance" || square.type === "community") {
      this.drawCard(player, square.deck || square.type);
      return;
    }
    if (["property", "railroad", "utility"].includes(square.type)) {
      if (square.ownerId === undefined) {
        this.pendingBuy = { playerId: player.id, position: player.position };
        this.pushLog(`${square.name} is unowned. ${player.name} can buy for $${square.price}.`);
        return;
      }
      if (square.ownerId !== player.id) {
        const owner = this.players.find((pl) => pl.id === square.ownerId);
        if (owner && !owner.bankrupt) {
          const rent = this.calculateRent(square, owner);
          this.transferMoney(player, owner, rent, `rent for ${square.name}`);
        }
      }
      return;
    }

    if (square.actions) this.applyEffects(player, square.actions);
  }

  calculateRent(square, owner) {
    if (square.type === "property") {
      const lvl = square.houses || 0;
      return square.rent[Math.min(lvl, square.rent.length - 1)] || 0;
    }
    if (square.type === "railroad") {
      const count = this.config.board.filter((s) => s.type === "railroad" && s.ownerId === owner.id).length;
      return square.rent[Math.max(0, count - 1)] || 25;
    }
    if (square.type === "utility") {
      const count = this.config.board.filter((s) => s.type === "utility" && s.ownerId === owner.id).length;
      const diceTotal = this.lastRoll[0] + this.lastRoll[1] || 7;
      return diceTotal * (square.rentMultiplier[Math.max(0, count - 1)] || 4);
    }
    return 0;
  }

  buyCurrentProperty() {
    if (!this.pendingBuy) return;
    const p = this.currentPlayer;
    if (p.id !== this.pendingBuy.playerId) return;
    const square = this.config.board[this.pendingBuy.position];
    if (!square?.price) return;
    if (p.money < square.price) {
      this.pushLog(`${p.name} cannot afford ${square.name}; starts auction.`);
      this.runAuction(square, p.id);
      this.pendingBuy = null;
      return;
    }
    p.money -= square.price;
    square.ownerId = p.id;
    square.houses = 0;
    p.properties.push(this.pendingBuy.position);
    this.pushLog(`${p.name} bought ${square.name} for $${square.price}.`);
    this.pendingBuy = null;
  }

  runAuction(square, excludedId) {
    const bidders = this.players.filter((p) => !p.bankrupt && p.id !== excludedId && p.money > 0);
    if (!bidders.length) return;
    let highest = null;
    bidders.forEach((bidder) => {
      const maxBid = Math.min(bidder.money, Math.max(1, Math.floor((square.price || 100) * (0.4 + Math.random() * 0.6))));
      if (!highest || maxBid > highest.bid) highest = { bidder, bid: maxBid };
    });
    if (highest) {
      highest.bidder.money -= highest.bid;
      square.ownerId = highest.bidder.id;
      square.houses = 0;
      highest.bidder.properties.push(this.config.board.indexOf(square));
      this.pushLog(`${highest.bidder.name} wins auction for ${square.name} at $${highest.bid}.`);
    }
  }

  drawCard(player, deckName) {
    const deck = this.config.decks[deckName];
    if (!deck?.length) return;
    const idx = this.deckPointers[deckName] % deck.length;
    const card = deck[idx];
    this.deckPointers[deckName] = (idx + 1) % deck.length;
    this.pushLog(`${player.name} drew ${deckName}: ${card.text}`);
    this.applyEffects(player, card.effects || []);
  }

  applyEffects(player, effects) {
    for (const effect of effects) {
      switch (effect.type) {
        case "move":
          this.movePlayer(player, effect.steps || 0);
          break;
        case "goTo": {
          const old = player.position;
          player.position = effect.position ?? 0;
          if (effect.passGo && player.position < old) player.money += this.config.salaryOnPassGo;
          this.handleLanding(player, this.config.board[player.position]);
          break;
        }
        case "draw":
          this.drawCard(player, effect.deck);
          break;
        case "pay":
          this.payPlayer(player, effect.amount || 0, "card effect");
          break;
        case "receive":
          player.money += effect.amount || 0;
          this.pushLog(`${player.name} received $${effect.amount || 0}.`);
          break;
        case "payAll":
          this.players.forEach((other) => {
            if (other.id !== player.id && !other.bankrupt) this.transferMoney(player, other, effect.amount || 0, "pay all players");
          });
          break;
        case "receiveFromAll":
          this.players.forEach((other) => {
            if (other.id !== player.id && !other.bankrupt) this.transferMoney(other, player, effect.amount || 0, "receive from all");
          });
          break;
        case "skipTurns":
          player.skipTurns += effect.count || 1;
          this.pushLog(`${player.name} will skip ${effect.count || 1} turn(s).`);
          break;
        case "goToJail":
          this.sendToJail(player);
          break;
        case "leaveJail":
          player.inJail = false;
          player.jailTurns = 0;
          break;
        case "customLog":
          this.pushLog(effect.message || `${player.name} triggered a custom effect.`);
          break;
      }
    }
  }

  sendToJail(player) {
    player.position = this.config.jailPosition;
    player.inJail = true;
    player.jailTurns = 0;
    this.pushLog(`${player.name} was sent to jail.`);
  }

  payPlayer(player, amount, reason, toBank = false) {
    if (amount <= 0) return;
    player.money -= amount;
    this.pushLog(`${player.name} paid $${amount} (${reason}).`);
    if (player.money < 0) this.bankruptPlayer(player, toBank ? null : undefined);
  }

  transferMoney(from, to, amount, reason) {
    if (amount <= 0) return;
    from.money -= amount;
    to.money += amount;
    this.pushLog(`${from.name} paid ${to.name} $${amount} for ${reason}.`);
    if (from.money < 0) this.bankruptPlayer(from, to);
  }

  bankruptPlayer(player, creditor = null) {
    if (player.bankrupt) return;
    player.bankrupt = true;
    this.pushLog(`${player.name} is bankrupt.`);
    for (const idx of player.properties) {
      const square = this.config.board[idx];
      if (square) square.ownerId = creditor ? creditor.id : undefined;
      if (creditor) creditor.properties.push(idx);
    }
    player.properties = [];
  }

  endTurn() {
    this.pendingBuy = null;
    let loops = 0;
    do {
      this.currentPlayerIndex = (this.currentPlayerIndex + 1) % this.players.length;
      loops += 1;
      if (this.currentPlayerIndex === 0) this.turn += 1;
    } while (this.players[this.currentPlayerIndex].bankrupt && loops <= this.players.length);
  }

  buildHouse() {
    const p = this.currentPlayer;
    const ownProps = p.properties.filter((idx) => this.config.board[idx]?.type === "property");
    const target = ownProps.find((idx) => (this.config.board[idx].houses || 0) < this.config.maxHouses);
    if (!target) return;
    const sq = this.config.board[target];
    const cost = sq.houseCost || 100;
    if (p.money >= cost) {
      p.money -= cost;
      sq.houses = (sq.houses || 0) + 1;
      this.pushLog(`${p.name} built on ${sq.name} (level ${sq.houses}).`);
    }
  }

  toJSON() {
    return {
      config: this.config,
      players: this.players,
      currentPlayerIndex: this.currentPlayerIndex,
      turn: this.turn,
      pendingBuy: this.pendingBuy,
      lastRoll: this.lastRoll,
      freeParkingPot: this.freeParkingPot,
      deckPointers: this.deckPointers,
      messageLog: this.messageLog
    };
  }

  static fromJSON(data) {
    const engine = new MonopolyEngine(data.config, data.players);
    Object.assign(engine, data);
    return engine;
  }
}

const ui = {
  board: document.getElementById("board"),
  players: document.getElementById("players"),
  log: document.getElementById("log"),
  turnInfo: document.getElementById("turnInfo")
};

let engine = null;

function createPlayers(count = 4) {
  return Array.from({ length: count }).map((_, i) => ({
    id: i + 1,
    name: `Player ${i + 1}`,
    token: TOKEN_EMOJIS[i % TOKEN_EMOJIS.length],
    position: 0,
    money: 1500,
    properties: [],
    inJail: false,
    jailTurns: 0,
    skipTurns: 0,
    bankrupt: false
  }));
}

function startGame(config = DEFAULT_MONOPOLY_CONFIG) {
  const players = createPlayers(4);
  players.forEach((p) => (p.money = config.startingMoney ?? 1500));
  engine = new MonopolyEngine(config, players);
  render();
  engine.pushLog("Game started.");
  render();
}

function render() {
  if (!engine) return;
  renderBoard();
  renderPlayers();
  renderTurn();
  ui.log.innerHTML = engine.messageLog.map((m) => `<div>${m}</div>`).join("");
}

function renderBoard() {
  ui.board.innerHTML = "";
  engine.config.board.forEach((square, idx) => {
    const el = document.createElement("div");
    el.className = `square type-${square.type}`;
    el.innerHTML = `<strong>${idx}</strong><span>${square.name}</span><small>${square.price ? "$" + square.price : square.type}</small>`;
    const holders = document.createElement("div");
    holders.className = "tokens";
    engine.players.filter((p) => p.position === idx && !p.bankrupt).forEach((p) => {
      const token = document.createElement("span");
      token.textContent = p.token;
      token.className = "token pulse";
      holders.appendChild(token);
    });
    el.appendChild(holders);
    ui.board.appendChild(el);
  });
}

function renderPlayers() {
  ui.players.innerHTML = engine.players.map((p, i) => {
    const active = i === engine.currentPlayerIndex ? "active-player" : "";
    return `<div class="player-row ${active}">
      <strong>${p.token} ${p.name}</strong>
      <span>$${p.money}</span>
      <span>Pos: ${p.position}</span>
      <span>Props: ${p.properties.length}</span>
      <span>${p.inJail ? "In Jail" : ""}</span>
      <span>${p.bankrupt ? "Bankrupt" : ""}</span>
    </div>`;
  }).join("");
}

function renderTurn() {
  const p = engine.currentPlayer;
  ui.turnInfo.innerHTML = `<div><strong>Turn ${engine.turn}</strong></div>
  <div>Current: ${p.name} ${p.token}</div>
  <div>Dice: ${engine.lastRoll[0]} + ${engine.lastRoll[1]}</div>
  <div>${engine.pendingBuy ? "Property available to buy." : "No pending purchase."}</div>`;
}

function parseJsonField(id, fallback) {
  const text = document.getElementById(id).value.trim();
  if (!text) return fallback;
  try { return JSON.parse(text); } catch { return fallback; }
}

document.getElementById("startDefaultBtn").addEventListener("click", () => startGame());
document.getElementById("rollBtn").addEventListener("click", () => { engine.rollDice(); engine.buildHouse(); render(); });
document.getElementById("buyBtn").addEventListener("click", () => { engine.buyCurrentProperty(); render(); });
document.getElementById("endTurnBtn").addEventListener("click", () => { engine.endTurn(); render(); });
document.getElementById("saveBtn").addEventListener("click", () => {
  if (!engine) return;
  localStorage.setItem("monopoly-studio-save", JSON.stringify(engine.toJSON()));
  engine.pushLog("Saved game to browser storage.");
  render();
});
document.getElementById("loadBtn").addEventListener("click", () => {
  const raw = localStorage.getItem("monopoly-studio-save");
  if (!raw) return;
  engine = MonopolyEngine.fromJSON(JSON.parse(raw));
  engine.pushLog("Loaded saved game.");
  render();
});

document.getElementById("addSquareBtn").addEventListener("click", () => {
  const customBoard = engine ? structuredClone(engine.config.board) : structuredClone(DEFAULT_MONOPOLY_CONFIG.board);
  const square = {
    name: document.getElementById("squareName").value || "Custom Square",
    type: document.getElementById("squareType").value,
    price: Number(document.getElementById("squareAmount").value || 0),
    amount: Number(document.getElementById("squareAmount").value || 0),
    deck: document.getElementById("squareDeck").value || undefined,
    actions: parseJsonField("squareAction", undefined)
  };
  customBoard.push(square);
  const cfg = engine ? structuredClone(engine.config) : structuredClone(DEFAULT_MONOPOLY_CONFIG);
  cfg.board = customBoard;
  engine = new MonopolyEngine(cfg, createPlayers(4));
  engine.pushLog(`Added custom square ${square.name}.`);
  render();
});

document.getElementById("rebuildBoardBtn").addEventListener("click", () => {
  if (!engine) startGame();
  const cfg = structuredClone(engine.config);
  cfg.startingMoney = DEFAULT_MONOPOLY_CONFIG.startingMoney;
  engine = new MonopolyEngine(cfg, createPlayers(4));
  engine.pushLog("Started game with custom board/decks.");
  render();
});

document.getElementById("addCardBtn").addEventListener("click", () => {
  if (!engine) startGame();
  const deckName = document.getElementById("deckName").value || "chance";
  const text = document.getElementById("cardText").value || "Custom Card";
  const effects = parseJsonField("cardEffects", [{ type: "customLog", message: "Custom card triggered." }]);
  if (!engine.config.decks[deckName]) engine.config.decks[deckName] = [];
  engine.config.decks[deckName].push({ text, effects });
  if (engine.deckPointers[deckName] === undefined) engine.deckPointers[deckName] = 0;
  engine.pushLog(`Added card to ${deckName}.`);
  render();
});

document.getElementById("removeDeckBtn").addEventListener("click", () => {
  if (!engine) return;
  const deckName = document.getElementById("deckName").value;
  if (!deckName) return;
  delete engine.config.decks[deckName];
  delete engine.deckPointers[deckName];
  engine.pushLog(`Removed deck ${deckName}.`);
  render();
});

document.getElementById("listDecksBtn").addEventListener("click", () => {
  if (!engine) return;
  engine.pushLog(`Decks: ${Object.keys(engine.config.decks).join(", ")}`);
  render();
});

startGame();
