import { defaultMonopoly } from './data/defaultMonopoly.js';
import { GameEngine } from './src/engine.js';
import { GameUI } from './src/ui.js';
import { BoardEditor } from './src/editor.js';

const root = document.getElementById('root');

const state = {
  config: defaultMonopoly,
  engine: null,
  ui: null,
  editor: null
};

function createPlayers() {
  const defaults = [
    { name: 'Player 1', token: '🚗', color: '#f94144' },
    { name: 'Player 2', token: '🎩', color: '#577590' },
    { name: 'Player 3', token: '🐕', color: '#43aa8b' },
    { name: 'Player 4', token: '🛳️', color: '#f9c74f' }
  ];
  return defaults;
}

function mountGame(engine) {
  state.engine = engine;
  root.innerHTML = '<h1>Monopoly-Style Board Game Platform</h1><div id="game"></div><div id="editor"></div>';

  state.ui = new GameUI(state.engine, {
    onSave: (serialized) => localStorage.setItem('boardgame-save', serialized),
    onLoad: () => {
      const save = localStorage.getItem('boardgame-save');
      if (save) {
        state.engine = GameEngine.fromSerialized(save);
        mountGame(state.engine);
      }
    },
    onDownload: (serialized) => {
      const blob = new Blob([serialized], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'boardgame-save.json';
      a.click();
      URL.revokeObjectURL(url);
    },
    onUpload: (serialized) => {
      state.engine = GameEngine.fromSerialized(serialized);
      mountGame(state.engine);
    }
  });
  state.ui.mount(document.getElementById('game'));

  state.editor = new BoardEditor((newConfig) => {
    state.config = newConfig;
    mountGame(new GameEngine(newConfig, createPlayers()));
  });
  state.editor.mount(document.getElementById('editor'), state.config);
}

mountGame(new GameEngine(state.config, createPlayers()));
