const canvas = document.getElementById('mapCanvas');
const ctx = canvas.getContext('2d');
const viewport = document.getElementById('viewport');

const layers = [
  { id: 'terrain', name: 'Terrain', visible: true, opacity: 1, locked: false },
  { id: 'mountains', name: 'Mountains', visible: true, opacity: 1, locked: false },
  { id: 'rivers', name: 'Rivers', visible: true, opacity: 1, locked: false },
  { id: 'forests', name: 'Forests', visible: true, opacity: 0.92, locked: false },
  { id: 'settlements', name: 'Settlements', visible: true, opacity: 1, locked: false },
  { id: 'roads', name: 'Roads', visible: true, opacity: 0.85, locked: false },
  { id: 'borders', name: 'Political Borders', visible: true, opacity: 0.85, locked: false },
  { id: 'labels', name: 'Labels', visible: true, opacity: 1, locked: false }
];

let state = {
  seed: 1337,
  waterPct: 48,
  zoom: 1,
  offsetX: 0,
  offsetY: 0,
  tool: 'pan',
  brushRadius: 22,
  brushStrength: 0.28,
  style: 'parchment',
  width: 1600,
  height: 900,
  worldUnits: 2200,
  unit: 'miles',
  grid: 'none',
  map: null,
  history: [],
  redo: [],
  versions: []
};

const stylePalettes = {
  parchment: { sea: ['#c4d3d0', '#8ea6a4'], land: ['#e9d8b4', '#c4ab7a'], mountain: '#7f6747', forest: '#5f6b44', river: '#557b97', border: '#684b2f', text: '#2f2618' },
  vibrant: { sea: ['#1f6ecf', '#52b2ff'], land: ['#7fcc65', '#e4db87'], mountain: '#8a7364', forest: '#2f8148', river: '#9be6ff', border: '#f2f4ff', text: '#f8fcff' },
  grimdark: { sea: ['#1a2531', '#364958'], land: ['#6b705c', '#a5a58d'], mountain: '#3f3b37', forest: '#2f4634', river: '#89a9b4', border: '#d6d6d6', text: '#ececec' },
  watercolor: { sea: ['#90caf9', '#bbdefb'], land: ['#ffd6a5', '#caffbf'], mountain: '#b08968', forest: '#6a994e', river: '#457b9d', border: '#4a4e69', text: '#22223b' },
  inked: { sea: ['#e6eef7', '#c8d5e5'], land: ['#f8f4e3', '#e8dab2'], mountain: '#2f2f2f', forest: '#425466', river: '#1f3b57', border: '#111', text: '#111' }
};

function mulberry32(a) { return function() { let t = (a += 0x6d2b79f5); t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
function fractalNoise(x, y, rand) {
  let amp = 1, freq = 1, total = 0, max = 0;
  for (let i = 0; i < 5; i++) {
    const nx = x * freq * 0.007 + rand() * 3;
    const ny = y * freq * 0.007 + rand() * 3;
    total += amp * (Math.sin(nx * 4.7 + ny * 3.1) + Math.cos(nx * 3.3 - ny * 5.2)) * 0.5;
    max += amp;
    amp *= 0.5;
    freq *= 2.1;
  }
  return total / max;
}

function generateMap() {
  const rand = mulberry32(Number(state.seed));
  const w = Math.round(state.width / 2), h = Math.round(state.height / 2);
  const height = new Float32Array(w * h);
  const moisture = new Float32Array(w * h);
  const temp = new Float32Array(w * h);
  const mountainMask = new Float32Array(w * h);

  const ridgeCount = 3 + Math.floor(rand() * 3);
  const ridges = Array.from({ length: ridgeCount }, () => ({ x1: rand() * w, y1: rand() * h, x2: rand() * w, y2: rand() * h, power: 0.12 + rand() * 0.2 }));

  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      const i = y * w + x;
      const nx = (x / w) * 2 - 1, ny = (y / h) * 2 - 1;
      let e = fractalNoise(x, y, rand) * 0.35 + (1 - Math.hypot(nx * 1.2, ny * 1.1)) * 0.6;
      let ridgeVal = 0;
      for (const r of ridges) {
        const d = pointToLineDistance(x, y, r.x1, r.y1, r.x2, r.y2);
        ridgeVal += Math.max(0, 1 - d / (Math.min(w, h) * 0.11)) * r.power;
      }
      e += ridgeVal;
      moisture[i] = fractalNoise(x + 99, y - 66, rand) * 0.5 + 0.5;
      temp[i] = 1 - Math.abs((y / h) * 2 - 1) * 0.8 - e * 0.25;
      mountainMask[i] = Math.max(0, ridgeVal * 1.5 + e - 0.62);
      height[i] = e;
    }
  }

  normalizeArray(height);
  normalizeArray(moisture);
  normalizeArray(temp);

  const seaLevel = percentile(height, state.waterPct / 100);
  const rivers = buildRivers(height, w, h, seaLevel);
  const settlements = placeSettlements(height, moisture, w, h, seaLevel, rivers);

  state.map = { w, h, height, moisture, temp, mountainMask, seaLevel, rivers, settlements, borders: [], labels: [] };
  pushHistory();
  render();
}

function buildRivers(height, w, h, seaLevel) {
  const rivers = [];
  const candidates = [];
  for (let i = 0; i < height.length; i++) if (height[i] > seaLevel + 0.14) candidates.push(i);
  candidates.sort((a, b) => height[b] - height[a]);

  for (let s = 0; s < Math.min(30, candidates.length); s += 3) {
    let i = candidates[s], path = [];
    const visited = new Set();
    while (!visited.has(i)) {
      visited.add(i);
      const x = i % w, y = Math.floor(i / w);
      path.push([x, y]);
      if (height[i] <= seaLevel) break;
      let next = i;
      let best = height[i];
      for (let oy = -1; oy <= 1; oy++) {
        for (let ox = -1; ox <= 1; ox++) {
          if (!ox && !oy) continue;
          const nx = x + ox, ny = y + oy;
          if (nx < 0 || ny < 0 || nx >= w || ny >= h) continue;
          const ni = ny * w + nx;
          if (height[ni] < best) { best = height[ni]; next = ni; }
        }
      }
      if (next === i) break;
      i = next;
    }
    if (path.length > 22) rivers.push(path);
  }
  return rivers;
}

function placeSettlements(height, moisture, w, h, seaLevel, rivers) {
  const hits = new Set(rivers.flatMap(r => r.filter((_, idx) => idx % 10 === 0).map(([x, y]) => y * w + x)));
  const list = [];
  for (let i = 0; i < height.length; i += 60) {
    if (height[i] <= seaLevel + 0.02 || height[i] > 0.78) continue;
    let score = moisture[i] * 0.5 + (hits.has(i) ? 0.4 : 0) + (0.7 - Math.abs(height[i] - 0.45));
    if (score > 0.95) list.push({ i, score });
  }
  return list.sort((a, b) => b.score - a.score).slice(0, 35).map((s, idx) => {
    const x = s.i % w, y = Math.floor(s.i / w);
    return { x, y, tier: idx < 4 ? 'capital' : idx < 15 ? 'town' : 'village' };
  });
}

function generateBordersAndLabels() {
  if (!state.map) return;
  const { settlements } = state.map;
  const capitals = settlements.filter(s => s.tier === 'capital');
  state.map.borders = capitals.map((c, idx) => ({ owner: idx, points: radialPolygon(c.x, c.y, 140 + idx * 20, 11 + idx) }));
  const names = generateNameBank(1200);
  state.map.labels = [
    ...capitals.map((c, i) => ({ x: c.x, y: c.y - 16, text: names[i], size: 18 })),
    ...state.map.rivers.slice(0, 8).map((r, i) => ({ x: r[Math.floor(r.length / 2)][0], y: r[Math.floor(r.length / 2)][1], text: `${names[100 + i]} River`, size: 13 }))
  ];
  document.getElementById('nameBank').innerHTML = names.slice(0, 120).map(n => `<span class="name-chip">${n}</span>`).join('');
  render();
}

function render() {
  if (!state.map) return;
  const pal = stylePalettes[state.style];
  const { w, h, height, moisture, temp, mountainMask, seaLevel } = state.map;
  canvas.width = w;
  canvas.height = h;
  const img = ctx.createImageData(w, h);

  for (let i = 0; i < height.length; i++) {
    const x = i % w, y = Math.floor(i / w);
    const e = height[i];
    let [r, g, b] = [0, 0, 0];
    if (layerVisible('terrain')) {
      if (e <= seaLevel) {
        const t = e / seaLevel;
        [r, g, b] = mix(hexToRgb(pal.sea[0]), hexToRgb(pal.sea[1]), t);
      } else {
        const t = Math.min(1, (e - seaLevel) / (1 - seaLevel));
        let land = mix(hexToRgb(pal.land[0]), hexToRgb(pal.land[1]), t * (1 - moisture[i] * 0.4));
        if (temp[i] < 0.35) land = mix(land, [224, 230, 236], 0.35);
        if (moisture[i] > 0.68) land = mix(land, hexToRgb(pal.forest), 0.25);
        [r, g, b] = land;
      }
      const shade = (height[y * w + Math.min(w - 1, x + 1)] - height[i]) * 70;
      r = clamp(r + shade, 0, 255); g = clamp(g + shade, 0, 255); b = clamp(b + shade, 0, 255);
    }
    if (layerVisible('mountains') && mountainMask[i] > 0.02 && e > seaLevel) {
      [r, g, b] = mix([r, g, b], hexToRgb(pal.mountain), Math.min(0.8, mountainMask[i]));
    }
    if (layerVisible('forests') && moisture[i] > 0.66 && e > seaLevel + 0.03) {
      [r, g, b] = mix([r, g, b], hexToRgb(pal.forest), 0.3);
    }
    const p = i * 4;
    img.data[p] = r; img.data[p + 1] = g; img.data[p + 2] = b; img.data[p + 3] = 255;
  }
  ctx.putImageData(img, 0, 0);

  if (layerVisible('rivers')) drawRivers(pal);
  if (layerVisible('roads')) drawRoads();
  if (layerVisible('settlements')) drawSettlements(pal);
  if (layerVisible('borders')) drawBorders(pal);
  if (layerVisible('labels')) drawLabels(pal);
  drawGrid();

  canvas.style.transform = `translate(${state.offsetX}px, ${state.offsetY}px) scale(${state.zoom})`;
}

function drawRivers(pal) {
  ctx.strokeStyle = pal.river;
  state.map.rivers.forEach((path, idx) => {
    ctx.beginPath();
    path.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y));
    ctx.lineWidth = Math.max(0.8, 2.8 - idx * 0.05);
    ctx.globalAlpha = layerAlpha('rivers');
    ctx.stroke();
  });
  ctx.globalAlpha = 1;
}
function drawSettlements(pal) {
  state.map.settlements.forEach(s => {
    ctx.fillStyle = s.tier === 'capital' ? '#ffe089' : s.tier === 'town' ? '#e8e8e8' : '#c5c5c5';
    ctx.strokeStyle = '#1d1d1d';
    const size = s.tier === 'capital' ? 4.2 : s.tier === 'town' ? 3 : 2.1;
    ctx.beginPath(); ctx.arc(s.x, s.y, size, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
  });
}
function drawRoads() {
  const towns = state.map.settlements.slice(0, 18);
  ctx.strokeStyle = '#aa8f67'; ctx.globalAlpha = layerAlpha('roads'); ctx.lineWidth = 1.1;
  for (let i = 0; i < towns.length - 1; i++) {
    ctx.beginPath(); ctx.moveTo(towns[i].x, towns[i].y); ctx.lineTo(towns[i + 1].x, towns[i + 1].y); ctx.stroke();
  }
  ctx.globalAlpha = 1;
}
function drawBorders(pal) {
  ctx.strokeStyle = pal.border; ctx.lineWidth = 1.8; ctx.setLineDash([6, 4]); ctx.globalAlpha = layerAlpha('borders');
  state.map.borders.forEach(b => {
    ctx.beginPath(); b.points.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)); ctx.closePath(); ctx.stroke();
  });
  ctx.setLineDash([]); ctx.globalAlpha = 1;
}
function drawLabels(pal) {
  ctx.fillStyle = pal.text; ctx.textAlign = 'center'; ctx.globalAlpha = layerAlpha('labels');
  state.map.labels.forEach(l => {
    ctx.font = `${l.size}px serif`;
    ctx.shadowColor = 'rgba(0,0,0,0.55)'; ctx.shadowBlur = 4;
    ctx.fillText(l.text, l.x, l.y);
  });
  ctx.shadowBlur = 0; ctx.globalAlpha = 1;
}
function drawGrid() {
  if (state.grid === 'none') return;
  const step = 58;
  ctx.strokeStyle = 'rgba(255,255,255,.23)'; ctx.lineWidth = 0.6;
  if (state.grid === 'square') {
    for (let x = 0; x < canvas.width; x += step) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke(); }
    for (let y = 0; y < canvas.height; y += step) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke(); }
  } else {
    const h = Math.sqrt(3) * step / 2;
    for (let y = -h; y < canvas.height + h; y += h) {
      for (let x = -step; x < canvas.width + step; x += step * 1.5) {
        const ox = Math.floor(y / h) % 2 ? x + step * .75 : x;
        hex(ox, y, step / 2);
      }
    }
  }
}

function hex(x, y, r) { ctx.beginPath(); for (let i = 0; i < 6; i++) { const a = Math.PI / 3 * i; const px = x + Math.cos(a) * r, py = y + Math.sin(a) * r; i ? ctx.lineTo(px, py) : ctx.moveTo(px, py); } ctx.closePath(); ctx.stroke(); }
function radialPolygon(cx, cy, r, n) { return Array.from({ length: n }, (_, i) => { const a = (i / n) * Math.PI * 2; const rr = r * (0.7 + Math.sin(i * 12.9898) * 0.2 + 0.2); return [cx + Math.cos(a) * rr, cy + Math.sin(a) * rr]; }); }
function pointToLineDistance(px, py, x1, y1, x2, y2) { const A = px - x1, B = py - y1, C = x2 - x1, D = y2 - y1; const dot = A * C + B * D; const len = C * C + D * D; const t = Math.max(0, Math.min(1, dot / len)); const x = x1 + C * t, y = y1 + D * t; return Math.hypot(px - x, py - y); }
function normalizeArray(arr) { let min = Infinity, max = -Infinity; for (const v of arr) { if (v < min) min = v; if (v > max) max = v; } const range = max - min || 1; for (let i = 0; i < arr.length; i++) arr[i] = (arr[i] - min) / range; }
function percentile(arr, p) { const copy = Array.from(arr).sort((a, b) => a - b); return copy[Math.floor((copy.length - 1) * p)] }
function mix(a, b, t) { return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t]; }
function hexToRgb(hex) { const c = hex.replace('#', ''); return [parseInt(c.slice(0, 2), 16), parseInt(c.slice(2, 4), 16), parseInt(c.slice(4, 6), 16)]; }
function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }
function layerVisible(id) { const l = layers.find(l => l.id === id); return l?.visible; }
function layerAlpha(id) { return layers.find(l => l.id === id)?.opacity ?? 1; }

function setupUI() {
  const layerList = document.getElementById('layerList');
  layerList.innerHTML = layers.map(l => `
    <div class="layer-row" data-layer="${l.id}">
      <div class="top"><label><input type="checkbox" ${l.visible ? 'checked' : ''} class="layer-visible"> ${l.name}</label><button class="lock-btn">${l.locked ? 'Unlock' : 'Lock'}</button></div>
      <input class="layer-opacity" type="range" min="0" max="1" step="0.05" value="${l.opacity}">
    </div>
  `).join('');
  layerList.oninput = (e) => {
    const row = e.target.closest('.layer-row'); if (!row) return;
    const l = layers.find(x => x.id === row.dataset.layer); if (!l) return;
    if (e.target.classList.contains('layer-visible')) l.visible = e.target.checked;
    if (e.target.classList.contains('layer-opacity')) l.opacity = Number(e.target.value);
    render();
  };
  layerList.onclick = (e) => {
    if (!e.target.classList.contains('lock-btn')) return;
    const row = e.target.closest('.layer-row'); const l = layers.find(x => x.id === row.dataset.layer);
    l.locked = !l.locked; e.target.textContent = l.locked ? 'Unlock' : 'Lock';
  };

  bind('generateBtn', 'click', () => {
    const preset = document.getElementById('canvasPreset').value;
    if (preset === 'custom') {
      state.width = Number(document.getElementById('customWidth').value);
      state.height = Number(document.getElementById('customHeight').value);
    } else {
      const [w, h] = preset.split('x').map(Number); state.width = w; state.height = h;
    }
    state.style = document.getElementById('stylePreset').value;
    state.seed = Number(document.getElementById('seedInput').value);
    state.waterPct = Number(document.getElementById('waterInput').value);
    state.worldUnits = Number(document.getElementById('mapDistance').value);
    state.unit = document.getElementById('scaleUnit').value;
    generateMap();
    autoSave();
  });

  bind('waterInput', 'input', e => document.getElementById('waterValue').textContent = e.target.value);
  bind('canvasPreset', 'change', e => document.getElementById('customSizeFields').hidden = e.target.value !== 'custom');
  bind('zoomRange', 'input', e => { state.zoom = Number(e.target.value) / 100; document.getElementById('zoomValue').textContent = `${e.target.value}%`; render(); });
  bind('gridMode', 'change', e => { state.grid = e.target.value; render(); });
  bind('toolMode', 'change', e => { state.tool = e.target.value; canvas.classList.toggle('drawing', state.tool !== 'pan'); });
  bind('brushRadius', 'input', e => { state.brushRadius = Number(e.target.value); document.getElementById('brushValue').textContent = e.target.value; });
  bind('brushStrength', 'input', e => { state.brushStrength = Number(e.target.value) / 100; document.getElementById('strengthValue').textContent = e.target.value; });
  bind('themeToggle', 'click', () => document.body.classList.toggle('theme-light'));
  bind('genBordersBtn', 'click', generateBordersAndLabels);
  bind('genLabelsBtn', 'click', generateBordersAndLabels);
  bind('runErosionBtn', 'click', runErosion);
  bind('undoBtn', 'click', undo);
  bind('redoBtn', 'click', redo);
  bind('saveVersionBtn', 'click', saveVersion);

  document.querySelectorAll('[data-export]').forEach(btn => btn.addEventListener('click', () => exportMap(btn.dataset.export)));

  setupCanvasInput();
  hydrateFromAutosave();
  generateMap();
  generateBordersAndLabels();
}

function setupCanvasInput() {
  let isDown = false, startX = 0, startY = 0;
  let measureStart = null;
  canvas.addEventListener('mousedown', (e) => {
    isDown = true; startX = e.clientX; startY = e.clientY;
    if (state.tool === 'measure') {
      const p = screenToMap(e.clientX, e.clientY);
      if (!measureStart) measureStart = p;
      else {
        const d = Math.hypot(p.x - measureStart.x, p.y - measureStart.y);
        const world = (d / state.map.w) * state.worldUnits;
        document.getElementById('measureReadout').textContent = `Distance: ${world.toFixed(1)} ${state.unit}`;
        measureStart = null;
      }
      return;
    }
    if (state.tool !== 'pan') applyBrush(e);
  });
  window.addEventListener('mouseup', () => isDown = false);
  window.addEventListener('mousemove', (e) => {
    if (!isDown) return;
    if (state.tool === 'pan') {
      state.offsetX += e.clientX - startX;
      state.offsetY += e.clientY - startY;
      startX = e.clientX; startY = e.clientY; render();
    } else applyBrush(e);
  });
}

function applyBrush(e) {
  if (!state.map) return;
  const p = screenToMap(e.clientX, e.clientY);
  const { w, h, height } = state.map;
  const sign = state.tool === 'heightRaise' ? 1 : -1;
  for (let y = -state.brushRadius; y <= state.brushRadius; y++) {
    for (let x = -state.brushRadius; x <= state.brushRadius; x++) {
      const d = Math.hypot(x, y);
      if (d > state.brushRadius) continue;
      const xx = Math.floor(p.x + x), yy = Math.floor(p.y + y);
      if (xx < 0 || yy < 0 || xx >= w || yy >= h) continue;
      const i = yy * w + xx;
      height[i] = clamp(height[i] + sign * state.brushStrength * (1 - d / state.brushRadius) * 0.02, 0, 1);
    }
  }
  render();
}
function screenToMap(clientX, clientY) { const r = viewport.getBoundingClientRect(); return { x: (clientX - r.left - state.offsetX) / state.zoom, y: (clientY - r.top - state.offsetY) / state.zoom }; }
function runErosion() {
  if (!state.map) return;
  const { w, h, height } = state.map;
  const copy = Float32Array.from(height);
  for (let y = 1; y < h - 1; y++) for (let x = 1; x < w - 1; x++) {
    const i = y * w + x;
    const avg = (copy[i] + copy[i - 1] + copy[i + 1] + copy[i - w] + copy[i + w]) / 5;
    height[i] = copy[i] * 0.75 + avg * 0.25;
  }
  normalizeArray(height); render(); pushHistory();
}

function exportMap(type) {
  if (!state.map) return;
  if (type === 'project') {
    downloadBlob(new Blob([JSON.stringify({ state, layers }, null, 2)], { type: 'application/json' }), `map-${Date.now()}.aethermap`);
    return;
  }
  if (type === 'heightmap') {
    const c = document.createElement('canvas'); c.width = state.map.w; c.height = state.map.h; const cctx = c.getContext('2d');
    const img = cctx.createImageData(c.width, c.height);
    for (let i = 0; i < state.map.height.length; i++) { const v = Math.floor(state.map.height[i] * 255); img.data[i * 4] = v; img.data[i * 4 + 1] = v; img.data[i * 4 + 2] = v; img.data[i * 4 + 3] = 255; }
    cctx.putImageData(img, 0, 0);
    c.toBlob(b => downloadBlob(b, 'heightmap.png'), 'image/png');
    return;
  }
  if (type === 'pdf') {
    const { jsPDF } = window.jspdf;
    const pdf = new jsPDF({ orientation: canvas.width > canvas.height ? 'landscape' : 'portrait', unit: 'pt', format: [canvas.width * 0.3, canvas.height * 0.3] });
    pdf.addImage(canvas.toDataURL('image/png'), 'PNG', 0, 0, canvas.width * 0.3, canvas.height * 0.3);
    pdf.save('fantasy-map.pdf');
    return;
  }
  if (type === 'vtt') state.grid = 'square', render();
  const mime = type === 'jpg' ? 'image/jpeg' : 'image/png';
  canvas.toBlob((blob) => downloadBlob(blob, `fantasy-map.${type === 'tiff' ? 'tiff' : type === 'vtt' ? 'png' : type}`), mime, type === 'jpg' ? 0.94 : undefined);
}
function downloadBlob(blob, name) { const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = name; a.click(); URL.revokeObjectURL(a.href); }

function bind(id, ev, fn) { document.getElementById(id).addEventListener(ev, fn); }
function pushHistory() {
  if (!state.map) return;
  state.history.push(Float32Array.from(state.map.height));
  if (state.history.length > 30) state.history.shift();
  state.redo = [];
}
function undo() {
  if (state.history.length < 2 || !state.map) return;
  state.redo.push(state.history.pop());
  state.map.height = Float32Array.from(state.history[state.history.length - 1]);
  render();
}
function redo() {
  if (!state.redo.length || !state.map) return;
  const next = state.redo.pop();
  state.history.push(Float32Array.from(next));
  state.map.height = Float32Array.from(next);
  render();
}
function saveVersion() {
  if (!state.map) return;
  state.versions.push({ t: new Date().toLocaleString(), seed: state.seed, style: state.style, water: state.waterPct });
  if (state.versions.length > 20) state.versions.shift();
  document.getElementById('versionList').innerHTML = state.versions.map((v, i) => `<div class="version-item"><span>#${i + 1} ${v.t}</span><span>${v.style}</span></div>`).join('');
  autoSave();
}
function autoSave() { localStorage.setItem('aethermap-autosave', JSON.stringify({ seed: state.seed, waterPct: state.waterPct, style: state.style, versions: state.versions })); }
function hydrateFromAutosave() {
  const raw = localStorage.getItem('aethermap-autosave');
  if (!raw) return;
  try {
    const saved = JSON.parse(raw);
    state.seed = saved.seed ?? state.seed;
    state.waterPct = saved.waterPct ?? state.waterPct;
    state.style = saved.style ?? state.style;
    state.versions = saved.versions ?? [];
    document.getElementById('seedInput').value = state.seed;
    document.getElementById('waterInput').value = state.waterPct;
    document.getElementById('waterValue').textContent = state.waterPct;
    document.getElementById('stylePreset').value = state.style;
    document.getElementById('versionList').innerHTML = state.versions.map((v, i) => `<div class="version-item"><span>#${i + 1} ${v.t}</span><span>${v.style}</span></div>`).join('');
  } catch (_) {}
}

function generateNameBank(count = 1200) {
  const pre = ['Ael', 'Dra', 'Kor', 'Val', 'Ith', 'Mor', 'Fen', 'Tha', 'Nor', 'Syl', 'Gal', 'Bryn', 'Zar', 'Riv', 'Eld'];
  const mid = ['an', 'or', 'il', 'en', 'ath', 'dor', 'mir', 'vel', 'ion', 'ara', 'uin', 'eth'];
  const suf = ['ia', 'heim', 'ford', 'spire', 'mere', 'hold', 'gard', 'reach', 'crest', 'fall', 'keep', 'mar'];
  const names = [];
  for (let i = 0; i < count; i++) names.push(`${pre[i % pre.length]}${mid[(i * 7) % mid.length]}${suf[(i * 11) % suf.length]}`);
  return names;
}

setupUI();
