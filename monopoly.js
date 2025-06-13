class MonopolyGame {
  constructor(config) {
    this.board = config.board;
    this.chanceDeck = config.chanceDeck;
    this.communityDeck = config.communityDeck;
    this.startMoney = config.startMoney || 1500;
    this.players = [];
    this.current = 0;
    this.logs = [];
  }

  addPlayer(name) {
    const player = {
      name,
      position: 0,
      money: this.startMoney,
      properties: [],
      inJail: false,
      jailTurns: 0
    };
    this.players.push(player);
  }

  log(msg) {
    this.logs.push(msg);
    const logDiv = document.getElementById("log");
    if (logDiv) {
      logDiv.textContent = this.logs.join("\n");
    }
  }

  rollDice() {
    return [1 + Math.floor(Math.random()*6), 1 + Math.floor(Math.random()*6)];
  }

  move(player, steps) {
    const old = player.position;
    let pos = (old + steps) % this.board.length;
    if (old + steps >= this.board.length) {
      player.money += 200;
      this.log(`${player.name} passed GO and collects $200.`);
    }
    player.position = pos;
    this.handleSquare(player, this.board[pos]);
  }

  handleSquare(player, square) {
    if (square.action) {
      if (square.action.money) {
        player.money += square.action.money;
        this.log(`${player.name} ${square.action.money > 0 ? 'receives' : 'pays'} $${Math.abs(square.action.money)}.`);
      }
      if (square.action.moveBy) {
        this.move(player, square.action.moveBy);
        return;
      }
      if (square.action.moveTo !== undefined) {
        player.position = square.action.moveTo % this.board.length;
        square = this.board[player.position];
        this.log(`${player.name} moves to ${square.name}.`);
      }
      if (square.action.gotoJail) {
        player.position = 10;
        player.inJail = true;
        player.jailTurns = 3;
        this.log(`${player.name} was sent to Jail.`);
        return;
      }
    }
    switch(square.type) {
      case 'property':
        if (!square.owner) {
          if (player.money >= square.price) {
            player.money -= square.price;
            square.owner = player;
            player.properties.push(square);
            this.log(`${player.name} bought ${square.name} for $${square.price}.`);
          }
        } else if (square.owner !== player) {
          const rent = square.rent;
          player.money -= rent;
          square.owner.money += rent;
          this.log(`${player.name} paid $${rent} rent to ${square.owner.name}.`);
        }
        break;
      case 'chance':
        this.drawCard(player, this.chanceDeck);
        break;
      case 'community':
        this.drawCard(player, this.communityDeck);
        break;
      case 'tax':
        player.money -= square.price;
        this.log(`${player.name} paid tax of $${square.price}.`);
        break;
      case 'gotojail':
        player.position = 10; // jail index
        player.inJail = true;
        player.jailTurns = 3;
        this.log(`${player.name} was sent to Jail.`);
        break;
      default:
        // go, parking, jail etc.
        break;
    }
  }

  drawCard(player, deck) {
    const card = deck.shift();
    this.log(`${player.name} drew card: ${card.text}`);
    if (typeof card.action === 'function') {
      card.action(this, player);
    }
    deck.push(card);
  }

  nextTurn() {
    const player = this.players[this.current];
    if (player.money <= 0) {
      this.log(`${player.name} is bankrupt!`);
      this.players.splice(this.current,1);
      if (this.players.length === 1) {
        this.log(`${this.players[0].name} wins!`);
        return;
      }
      if (this.current >= this.players.length) this.current = 0;
    }
    if (player.inJail) {
      player.jailTurns -= 1;
      if (player.jailTurns <= 0) {
        player.inJail = false;
        this.log(`${player.name} is out of Jail.`);
      } else {
        this.log(`${player.name} is in Jail (${player.jailTurns} turns left).`);
        this.current = (this.current + 1) % this.players.length;
        return;
      }
    }
    const [d1,d2] = this.rollDice();
    this.log(`${player.name} rolled ${d1} and ${d2}.`);
    this.move(player, d1+d2);
    this.current = (this.current + 1) % this.players.length;
  }
}

function startGame() {
  const boardData = JSON.parse(document.getElementById('boardData').value);
  const chanceData = JSON.parse(document.getElementById('chanceData').value);
  const communityData = JSON.parse(document.getElementById('communityData').value);
  const playerNames = document.getElementById('players').value.split(',').map(s => s.trim()).filter(Boolean);
  const game = new MonopolyGame({
    board: boardData,
    chanceDeck: chanceData,
    communityDeck: communityData
  });
  playerNames.forEach(name => game.addPlayer(name));
  window.game = game;
  document.getElementById('controls').style.display = 'block';
  game.log('Game started!');
}

function takeTurn() {
  if (window.game) window.game.nextTurn();
}
