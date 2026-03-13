export class GameUI {
  constructor(engine, hooks) {
    this.engine = engine;
    this.hooks = hooks;
    this.boardEl = null;
    this.playersEl = null;
    this.statusEl = null;
    this.cardEl = null;
  }

  mount(root) {
    root.innerHTML = `
      <div class="layout">
        <section>
          <div id="board" class="board"></div>
          <div class="controls">
            <button id="rollBtn">Roll Dice</button>
            <button id="buyBtn">Buy Property</button>
            <button id="endTurnBtn">End Turn</button>
            <button id="saveBtn">Save</button>
            <button id="loadBtn">Load</button>
            <button id="downloadBtn">Download Save</button>
            <label class="upload-label">Upload Save <input id="uploadSave" type="file" accept="application/json" /></label>
          </div>
          <div class="status" id="status"></div>
          <div class="card" id="lastCard"></div>
        </section>
        <aside>
          <h3>Players</h3>
          <div id="players"></div>
          <h3>Owned Properties</h3>
          <div id="properties"></div>
        </aside>
      </div>
    `;

    this.boardEl = root.querySelector('#board');
    this.playersEl = root.querySelector('#players');
    this.statusEl = root.querySelector('#status');
    this.cardEl = root.querySelector('#lastCard');

    root.querySelector('#rollBtn').onclick = () => {
      this.animateDice();
      this.engine.rollDice();
      this.render();
    };
    root.querySelector('#buyBtn').onclick = () => {
      this.engine.buyProperty();
      this.render();
    };
    root.querySelector('#endTurnBtn').onclick = () => {
      this.engine.endTurn();
      this.render();
    };

    root.querySelector('#saveBtn').onclick = () => this.hooks.onSave(this.engine.serialize());
    root.querySelector('#loadBtn').onclick = () => this.hooks.onLoad();
    root.querySelector('#downloadBtn').onclick = () => this.hooks.onDownload(this.engine.serialize());
    root.querySelector('#uploadSave').onchange = (e) => {
      const file = e.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = () => this.hooks.onUpload(reader.result);
      reader.readAsText(file);
    };

    this.render();
  }

  render() {
    this.renderBoard();
    this.renderPlayers();
    this.renderProperties();

    const { dice, message, phase, winner, lastCard } = this.engine.state;
    this.statusEl.textContent = winner !== null
      ? `${this.engine.players[winner].name} wins!`
      : `${message} | Dice: ${dice[0]} + ${dice[1]} | Phase: ${phase} | Current: ${this.engine.currentPlayer.name}`;

    this.cardEl.textContent = lastCard ? `Card: ${lastCard.description}` : '';
  }

  renderBoard() {
    const squares = this.engine.config.board.squares;
    this.boardEl.innerHTML = '';
    for (const square of squares) {
      const squareEl = document.createElement('div');
      squareEl.className = `square type-${square.type}`;
      squareEl.innerHTML = `
        <strong>${square.name}</strong>
        <span>${square.type}</span>
      `;

      const owner = this.engine.state.ownership[square.id];
      if (owner !== undefined) {
        squareEl.style.borderColor = this.engine.players[owner].color;
      }

      const building = this.engine.state.buildings[square.id];
      if (building) {
        const label = building.hotel ? '🏨' : `🏠x${building.houses}`;
        const b = document.createElement('div');
        b.className = 'building';
        b.textContent = label;
        squareEl.appendChild(b);
      }

      const tokens = document.createElement('div');
      tokens.className = 'tokens';
      for (const player of this.engine.players) {
        if (player.position === square.id && !player.bankrupt) {
          const token = document.createElement('span');
          token.className = 'token move-in';
          token.style.background = player.color;
          token.textContent = player.token;
          tokens.appendChild(token);
        }
      }
      squareEl.appendChild(tokens);
      this.boardEl.appendChild(squareEl);
    }
  }

  renderPlayers() {
    this.playersEl.innerHTML = this.engine.players.map((p, idx) => `
      <div class="player-card ${idx === this.engine.state.currentPlayerIndex ? 'active' : ''}">
        <span class="token" style="background:${p.color}">${p.token}</span>
        <div>
          <strong>${p.name}</strong>
          <div>$${p.money} ${p.bankrupt ? '(Bankrupt)' : ''}</div>
          <div>Position: ${p.position}${p.inJail ? ' | In Jail' : ''}</div>
        </div>
      </div>
    `).join('');
  }

  renderProperties() {
    const container = document.querySelector('#properties');
    const current = this.engine.currentPlayer;
    const items = current.properties
      .map((id) => {
        const sq = this.engine.getSquare(id);
        const canBuild = this.engine.canBuild(current.id, id);
        return `<div class="property-item">${sq.name} <button data-build="${id}" ${canBuild ? '' : 'disabled'}>Build</button></div>`;
      })
      .join('') || '<p>No properties</p>';

    container.innerHTML = items;
    container.querySelectorAll('button[data-build]').forEach((btn) => {
      btn.onclick = () => {
        this.engine.buildOnProperty(Number(btn.dataset.build));
        this.render();
      };
    });
  }

  animateDice() {
    this.statusEl.classList.remove('pulse');
    void this.statusEl.offsetWidth;
    this.statusEl.classList.add('pulse');
  }
}
