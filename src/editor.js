export class BoardEditor {
  constructor(onApply) {
    this.onApply = onApply;
  }

  mount(root, initialConfig) {
    root.innerHTML = `
      <h3>Board Game Editor</h3>
      <p>Create/edit Monopoly-style game JSON data. Action types supported: moveForward, moveBackward, moveTo, drawCard, payMoney, receiveMoney, payAllPlayers, receiveFromAllPlayers, skipTurns, goToJail, exitJail, customEffect.</p>
      <div class="editor-controls">
        <button id="newSquareBtn">Add Square</button>
        <button id="newDeckBtn">Add Deck</button>
        <button id="applyConfigBtn">Apply JSON to Game</button>
      </div>
      <textarea id="configEditor" spellcheck="false"></textarea>
    `;

    const textarea = root.querySelector('#configEditor');
    textarea.value = JSON.stringify(initialConfig, null, 2);

    root.querySelector('#newSquareBtn').onclick = () => {
      const cfg = JSON.parse(textarea.value);
      const id = cfg.board.squares.length;
      cfg.board.squares.push({ id, name: `Custom ${id}`, type: 'custom', actions: [{ type: 'customEffect', message: 'Custom action!' }] });
      textarea.value = JSON.stringify(cfg, null, 2);
    };

    root.querySelector('#newDeckBtn').onclick = () => {
      const cfg = JSON.parse(textarea.value);
      cfg.decks.push({ id: `deck${cfg.decks.length + 1}`, name: 'New Deck', cards: [] });
      textarea.value = JSON.stringify(cfg, null, 2);
    };

    root.querySelector('#applyConfigBtn').onclick = () => {
      try {
        const parsed = JSON.parse(textarea.value);
        this.onApply(parsed);
      } catch (err) {
        alert(`Invalid JSON: ${err.message}`);
      }
    };
  }
}
