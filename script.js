const canvas = document.getElementById('mapCanvas');
const ctx = canvas.getContext('2d', { alpha: false });
const viewport = document.getElementById('viewport');

const layers = [
  { id: 'terrain', name: 'Terrain', visible: true, opacity: 1, locked: false },
  { id: 'mountains', name: 'Mountains', visible: true, opacity: 1, locked: false },
  { id: 'rivers', name: 'Rivers', visible: true, opacity: 1, locked: false },
  { id: 'forests', name: 'Forests', visible: true, opacity: 1, locked: false },
  { id: 'settlements', name: 'Settlements', visible: true, opacity: 1, locked: false },
  { id: 'roads', name: 'Roads', visible: true, opacity: 0.8, locked: false },
  { id: 'borders', name: 'Political Borders', visible: true, opacity: 0.7, locked: false },
  { id: 'labels', name: 'Labels', visible: true, opacity: 1, locked: false }
];

const state = {
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
  versions: [],
  selectedAssetId: null,
  dragAsset: false,
  assetType: 'mountain',
  assetSize: 24,
  customLabelText: 'New Realm'
};

const stylePalettes = {
  parchment: { seaDeep: '#5f8788', seaShallow: '#91bbb7', coast: '#d7eeea', low: '#b59f69', mid: '#8a8450', high: '#747d54', snow: '#e2e9e4', mountain: '#6e5a43', forest: '#3f5631', river: '#8ad3d6', road: '#8e7445', text: '#2d2416', border: '#433220' },
  vibrant: { seaDeep: '#276bc1', seaShallow: '#67b5ff', coast: '#dff6ff', low: '#b9d86a', mid: '#88b64e', high: '#66984f', snow: '#f7fdff', mountain: '#7f756a', forest: '#2f7a47', river: '#bdefff', road: '#d2ad79', text: '#f4f9ff', border: '#f8fdff' },
  grimdark: { seaDeep: '#2c3e4f', seaShallow: '#546a79', coast: '#a7b8bd', low: '#7c7f61', mid: '#65684f', high: '#555b46', snow: '#d2d8db', mountain: '#4e4b47', forest: '#334636', river: '#9eb8c2', road: '#8a7a65', text: '#e8ecef', border: '#dadde0' },
  watercolor: { seaDeep: '#79a9c2', seaShallow: '#b8ddea', coast: '#eef9ff', low: '#d8c191', mid: '#b8c782', high: '#8fa96c', snow: '#f8f9f4', mountain: '#a18670', forest: '#5a8f51', river: '#75bcd6', road: '#a58b6b', text: '#2f334f', border: '#505778' },
  inked: { seaDeep: '#7f98b0', seaShallow: '#c8d6e5', coast: '#f3f6f8', low: '#d5c08f', mid: '#b5ab78', high: '#96956d', snow: '#ffffff', mountain: '#313131', forest: '#425366', river: '#314f70', road: '#705b3f', text: '#101010', border: '#101010' }
};

function hash2(x, y, seed) { let h = x * 374761393 + y * 668265263 + seed * 2147483647; h = (h ^ (h >>> 13)) * 1274126177; return ((h ^ (h >>> 16)) >>> 0) / 4294967295; }
function smooth(t) { return t * t * (3 - 2 * t); }
function layerVisible(id) { return layers.find((l) => l.id === id)?.visible; }
function layerAlpha(id) { return layers.find((l) => l.id === id)?.opacity ?? 1; }
function hexToRgb(hex) { const c = hex.replace('#', ''); return [parseInt(c.slice(0, 2), 16), parseInt(c.slice(2, 4), 16), parseInt(c.slice(4, 6), 16)]; }
function rgbToHex([r, g, b]) { return `#${[r, g, b].map((x) => Math.round(x).toString(16).padStart(2, '0')).join('')}`; }
function mix(a, b, t) { return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t]; }
function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }
function shadeHex(hex, delta) { const [r, g, b] = hexToRgb(hex); return `rgb(${clamp(r + delta, 0, 255)},${clamp(g + delta, 0, 255)},${clamp(b + delta, 0, 255)})`; }

function rgbToHsl(r, g, b) {
  r /= 255; g /= 255; b /= 255;
  const max = Math.max(r, g, b), min = Math.min(r, g, b);
  let h = 0, s = 0, l = (max + min) / 2;
  if (max !== min) {
    const d = max - min;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
    switch (max) {
      case r: h = ((g - b) / d + (g < b ? 6 : 0)); break;
      case g: h = ((b - r) / d + 2); break;
      default: h = ((r - g) / d + 4);
    }
    h /= 6;
  }
  return [h, s, l];
}
function hslToRgb(h, s, l) {
  if (s === 0) return [l * 255, l * 255, l * 255];
  const hue2rgb = (p, q, t) => {
    if (t < 0) t += 1; if (t > 1) t -= 1;
    if (t < 1 / 6) return p + (q - p) * 6 * t;
    if (t < 1 / 2) return q;
    if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6;
    return p;
  };
  const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
  const p = 2 * l - q;
  return [hue2rgb(p, q, h + 1 / 3) * 255, hue2rgb(p, q, h) * 255, hue2rgb(p, q, h - 1 / 3) * 255];
}
function shiftPaletteColor(hex, hueShift, satShift, lightShift) {
  const [h, s, l] = rgbToHsl(...hexToRgb(hex));
  const rgb = hslToRgb((h + hueShift + 1) % 1, clamp(s + satShift, 0, 1), clamp(l + lightShift, 0, 1));
  return rgbToHex(rgb);
}

function valueNoise(x, y, seed) {
  const x0 = Math.floor(x), y0 = Math.floor(y), x1 = x0 + 1, y1 = y0 + 1;
  const sx = smooth(x - x0), sy = smooth(y - y0);
  const n00 = hash2(x0, y0, seed), n10 = hash2(x1, y0, seed), n01 = hash2(x0, y1, seed), n11 = hash2(x1, y1, seed);
  return (n00 + (n10 - n00) * sx) + ((n01 + (n11 - n01) * sx) - (n00 + (n10 - n00) * sx)) * sy;
}
function fbm(x, y, seed, oct = 5) {
  let total = 0, amp = 0.5, freq = 1, norm = 0;
  for (let i = 0; i < oct; i++) { total += valueNoise(x * freq, y * freq, seed + i * 101) * amp; norm += amp; amp *= 0.5; freq *= 2.1; }
  return total / norm;
}

function buildAdaptivePalette() {
  const base = stylePalettes[state.style];
  const m = state.map;
  if (!m) return base;
  const meanMoisture = average(m.moisture);
  const meanTemp = average(m.temp);
  const hueShift = ((state.seed % 37) - 18) / 720;
  const satShift = (meanMoisture - 0.5) * 0.2;
  const lightShift = (meanTemp - 0.5) * 0.15;
  const p = {};
  for (const [k, v] of Object.entries(base)) p[k] = shiftPaletteColor(v, hueShift, satShift, lightShift);
  p.low = shiftPaletteColor(p.low, 0, 0.06, 0.04);
  p.forest = shiftPaletteColor(p.forest, 0.01, 0.08, -0.04);
  p.coast = shiftPaletteColor(p.coast, 0, -0.05, 0.05);
  return p;
}

function generateMap() {
  const w = Math.round(state.width / 2), h = Math.round(state.height / 2);
  const height = new Float32Array(w * h), moisture = new Float32Array(w * h), temp = new Float32Array(w * h), mountainMask = new Float32Array(w * h);
  const tectonic = Array.from({ length: 5 }, (_, i) => ({
    x1: hash2(i, 11, state.seed) * w,
    y1: hash2(i, 21, state.seed) * h,
    x2: hash2(i, 31, state.seed) * w,
    y2: hash2(i, 41, state.seed) * h,
    width: 0.05 + hash2(i, 51, state.seed) * 0.08,
    power: 0.18 + hash2(i, 61, state.seed) * 0.32
  }));

  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      const i = y * w + x;
      const radial = 1 - Math.pow(Math.hypot((x / w - 0.5) * 1.35, (y / h - 0.5) * 1.15), 1.35);
      const warpX = x / 180 + (fbm(x / 240, y / 240, state.seed + 700, 3) - 0.5) * 1.4;
      const warpY = y / 180 + (fbm(x / 210, y / 210, state.seed + 900, 3) - 0.5) * 1.2;
      let e = fbm(warpX, warpY, state.seed + 100, 6) * 0.65 + radial * 0.55;
      let ridge = 0;
      for (const r of tectonic) {
        const d = pointToLineDistance(x, y, r.x1, r.y1, r.x2, r.y2) / Math.min(w, h);
        ridge += Math.max(0, 1 - d / r.width) * r.power;
      }
      e += ridge * 0.42;
      height[i] = e;
      moisture[i] = fbm(x / 220, y / 220, state.seed + 300, 5);
      temp[i] = 1 - Math.abs((y / h) * 2 - 1) * 0.88 - e * 0.25;
      mountainMask[i] = ridge;
    }
  }

  normalizeArray(height); normalizeArray(moisture); normalizeArray(temp);
  const seaLevel = percentile(height, state.waterPct / 100);
  const rivers = buildRivers(height, w, h, seaLevel);
  const settlements = placeSettlements(height, moisture, w, h, seaLevel, rivers);
  state.map = {
    w, h, height, moisture, temp, mountainMask, seaLevel,
    rivers, settlements, roads: buildRoads(settlements), coastDistance: computeSeaDistance(height, w, h, seaLevel),
    borders: [], labels: [], manualAssets: [], customLabels: []
  };
  state.map.palette = buildAdaptivePalette();
  pushHistory();
  render();
}

function buildRivers(height, w, h, seaLevel) {
  const starts = [];
  for (let i = 0; i < height.length; i++) if (height[i] > seaLevel + 0.18) starts.push(i);
  starts.sort((a, b) => height[b] - height[a]);
  const rivers = [];
  for (let s = 0; s < Math.min(120, starts.length); s += 6) {
    let i = starts[s], path = []; const seen = new Set();
    while (!seen.has(i) && path.length < 900) {
      seen.add(i);
      const x = i % w, y = Math.floor(i / w); path.push([x, y]);
      if (height[i] <= seaLevel) break;
      let next = i, best = height[i];
      for (let oy = -1; oy <= 1; oy++) for (let ox = -1; ox <= 1; ox++) {
        if (!ox && !oy) continue;
        const nx = x + ox, ny = y + oy;
        if (nx < 0 || ny < 0 || nx >= w || ny >= h) continue;
        const ni = ny * w + nx, val = height[ni] + (ox && oy ? 0.001 : 0);
        if (val < best) { best = val; next = ni; }
      }
      if (next === i) break; i = next;
    }
    if (path.length > 40) rivers.push(path);
    if (rivers.length > 18) break;
  }
  return rivers;
}

function placeSettlements(height, moisture, w, h, seaLevel, rivers) {
  const nearRiver = new Set(rivers.flatMap((r) => r.filter((_, idx) => idx % 8 === 0).map(([x, y]) => y * w + x)));
  const list = [];
  for (let i = 0; i < height.length; i += 23) {
    if (height[i] <= seaLevel + 0.02 || height[i] >= 0.79) continue;
    const score = (0.75 - Math.abs(height[i] - 0.42)) + moisture[i] * 0.2 + (nearRiver.has(i) ? 0.4 : 0);
    if (score > 0.72) list.push({ i, score });
  }
  return list.sort((a, b) => b.score - a.score).slice(0, 52).map((s, idx) => ({ x: s.i % w, y: Math.floor(s.i / w), tier: idx < 5 ? 'capital' : idx < 18 ? 'town' : 'village' }));
}

function buildRoads(settlements) {
  const cities = settlements.filter((s) => s.tier !== 'village');
  if (!cities.length) return [];
  const used = new Set([0]), edges = [];
  while (used.size < cities.length) {
    let best = null;
    for (const a of used) for (let b = 0; b < cities.length; b++) {
      if (used.has(b)) continue;
      const d = Math.hypot(cities[a].x - cities[b].x, cities[a].y - cities[b].y);
      if (!best || d < best.d) best = { a, b, d };
    }
    if (!best) break;
    used.add(best.b); edges.push([cities[best.a], cities[best.b]]);
  }
  return edges;
}

function computeSeaDistance(height, w, h, seaLevel) {
  const dist = new Float32Array(w * h).fill(9999), queue = [];
  for (let i = 0; i < height.length; i++) if (height[i] <= seaLevel) { dist[i] = 0; queue.push(i); }
  let head = 0;
  while (head < queue.length) {
    const i = queue[head++], x = i % w, y = Math.floor(i / w);
    for (let oy = -1; oy <= 1; oy++) for (let ox = -1; ox <= 1; ox++) {
      if (!ox && !oy) continue;
      const nx = x + ox, ny = y + oy;
      if (nx < 0 || ny < 0 || nx >= w || ny >= h) continue;
      const ni = ny * w + nx, nd = dist[i] + (ox && oy ? 1.41 : 1);
      if (nd < dist[ni]) { dist[ni] = nd; queue.push(ni); }
    }
  }
  return dist;
}

function generateBordersAndLabels() {
  if (!state.map) return;
  const capitals = state.map.settlements.filter((s) => s.tier === 'capital');
  const names = generateNameBank(1200);
  state.map.borders = capitals.map((c, idx) => ({ owner: idx, points: radialPolygon(c.x, c.y, 90 + idx * 14, 18 + idx * 2) }));
  state.map.labels = [
    ...capitals.map((c, i) => ({ x: c.x, y: c.y - 13, text: names[i], size: 17, type: 'city' })),
    ...state.map.rivers.slice(0, 8).map((r, i) => ({ x: r[Math.floor(r.length * 0.56)][0], y: r[Math.floor(r.length * 0.56)][1], text: `${names[120 + i]} River`, size: 12, type: 'river' }))
  ];
  document.getElementById('nameBank').innerHTML = names.slice(0, 140).map((n) => `<span class="name-chip">${n}</span>`).join('');
  render();
}

function render() {
  if (!state.map) return;
  const pal = state.map.palette || stylePalettes[state.style];
  const { w, h, height, moisture, temp, mountainMask, seaLevel, coastDistance } = state.map;
  canvas.width = w; canvas.height = h;
  const img = ctx.createImageData(w, h);
  const deep = hexToRgb(pal.seaDeep), shallow = hexToRgb(pal.seaShallow), low = hexToRgb(pal.low), mid = hexToRgb(pal.mid), high = hexToRgb(pal.high), snow = hexToRgb(pal.snow), forest = hexToRgb(pal.forest);

  for (let i = 0; i < height.length; i++) {
    const x = i % w, y = Math.floor(i / w), e = height[i], m = moisture[i], t = temp[i], n = fbm(x / 85, y / 85, state.seed + 1400, 3) - 0.5;
    let c;
    if (e <= seaLevel) c = mix(shallow, deep, clamp((seaLevel - e) / Math.max(0.01, seaLevel), 0, 1) * 0.9);
    else {
      const alt = clamp((e - seaLevel) / Math.max(0.0001, 1 - seaLevel), 0, 1);
      c = mix(low, mid, clamp(alt * 1.25, 0, 1));
      if (alt > 0.45) c = mix(c, high, (alt - 0.45) / 0.55);
      if (m > 0.62) c = mix(c, forest, clamp((m - 0.62) * 1.2, 0, 0.45));
      if (alt > 0.7 || t < 0.28) c = mix(c, snow, clamp((alt - 0.7) * 2.1 + (0.3 - t), 0, 0.85));
      const coast = clamp(1 - coastDistance[i] / 16, 0, 1);
      if (coast > 0) c = mix(c, [235, 228, 190], coast * 0.35);
    }
    const sx = height[y * w + Math.min(w - 1, x + 1)] - height[y * w + Math.max(0, x - 1)];
    const sy = height[Math.min(h - 1, y + 1) * w + x] - height[Math.max(0, y - 1) * w + x];
    const shade = clamp((sx * -45 + sy * -55) + n * 18, -38, 38);
    const p = i * 4;
    img.data[p] = clamp(c[0] + shade, 0, 255);
    img.data[p + 1] = clamp(c[1] + shade, 0, 255);
    img.data[p + 2] = clamp(c[2] + shade, 0, 255);
    img.data[p + 3] = 255;
  }
  ctx.putImageData(img, 0, 0);

  if (layerVisible('terrain')) drawCoastGlow(pal);
  if (layerVisible('mountains')) drawMountains(pal, mountainMask, seaLevel);
  if (layerVisible('forests')) drawForestClusters(pal, seaLevel);
  if (layerVisible('rivers')) drawRivers(pal);
  if (layerVisible('roads')) drawRoads(pal);
  if (layerVisible('settlements')) drawSettlements();
  drawManualAssets(pal);
  if (layerVisible('borders')) drawBorders(pal);
  if (layerVisible('labels')) drawLabels(pal);
  drawGrid();

  canvas.style.transform = `translate(${state.offsetX}px, ${state.offsetY}px) scale(${state.zoom})`;
}

function drawCoastGlow(pal) { const { height, seaLevel, w, h } = state.map; ctx.strokeStyle = pal.coast; ctx.globalAlpha = 0.25 * layerAlpha('terrain'); for (let ring = 1; ring <= 4; ring++) { ctx.lineWidth = 1.2; ctx.beginPath(); const th = seaLevel - ring * 0.014; for (let y = 1; y < h - 1; y += 2) for (let x = 1; x < w - 1; x += 2) { const i = y * w + x; if (height[i] <= th && height[i] > th - 0.01) { ctx.moveTo(x, y); ctx.arc(x, y, ring * 2.7, 0, Math.PI * 2); } } ctx.stroke(); } ctx.globalAlpha = 1; }
function drawMountains(pal, mountainMask, seaLevel) {
  const { height, w, h } = state.map; ctx.globalAlpha = layerAlpha('mountains');
  for (let y = 4; y < h - 4; y += 6) for (let x = 4; x < w - 4; x += 6) {
    const i = y * w + x; if (height[i] <= seaLevel + 0.08) continue;
    const strength = clamp(mountainMask[i] + (height[i] - seaLevel) - 0.25, 0, 1); if (strength < 0.28) continue;
    const size = 5 + strength * 18;
    ctx.beginPath(); ctx.fillStyle = shadeHex(pal.mountain, 8 + Math.floor(strength * 38)); ctx.moveTo(x, y - size); ctx.lineTo(x - size * 0.62, y + size * 0.5); ctx.lineTo(x + size * 0.62, y + size * 0.5); ctx.closePath(); ctx.fill();
    ctx.beginPath(); ctx.fillStyle = 'rgba(255,255,255,.34)'; ctx.moveTo(x, y - size); ctx.lineTo(x - size * 0.24, y + size * 0.12); ctx.lineTo(x, y + size * 0.22); ctx.closePath(); ctx.fill();
  }
  ctx.globalAlpha = 1;
}
function drawForestClusters(pal, seaLevel) {
  const { height, moisture, w, h } = state.map; ctx.globalAlpha = layerAlpha('forests');
  for (let y = 3; y < h; y += 3) for (let x = 3; x < w; x += 3) {
    const i = y * w + x;
    if (height[i] <= seaLevel + 0.03 || height[i] > 0.78 || moisture[i] < 0.63) continue;
    const density = clamp((moisture[i] - 0.63) * 2.1, 0, 1); if (hash2(x, y, state.seed + 4900) > density) continue;
    const tree = 2 + density * 2.3;
    ctx.fillStyle = shadeHex(pal.forest, -15 + Math.floor(hash2(y, x, state.seed + 23) * 28));
    ctx.beginPath(); ctx.moveTo(x, y - tree); ctx.lineTo(x - tree * 0.75, y + tree * 0.6); ctx.lineTo(x + tree * 0.75, y + tree * 0.6); ctx.closePath(); ctx.fill();
  }
  ctx.globalAlpha = 1;
}
function drawRivers(pal) { ctx.strokeStyle = pal.river; state.map.rivers.forEach((path, idx) => { ctx.beginPath(); path.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y))); ctx.lineWidth = Math.max(0.8, 2.6 - idx * 0.1); ctx.globalAlpha = layerAlpha('rivers'); ctx.lineJoin = 'round'; ctx.lineCap = 'round'; ctx.stroke(); }); ctx.globalAlpha = 1; }
function drawRoads(pal) { ctx.globalAlpha = layerAlpha('roads'); ctx.strokeStyle = pal.road; ctx.lineWidth = 1.05; ctx.setLineDash([4, 2]); state.map.roads.forEach(([a, b]) => { const mx = (a.x + b.x) / 2 + (hash2(a.x, b.y, state.seed + 91) - 0.5) * 10; const my = (a.y + b.y) / 2 + (hash2(b.x, a.y, state.seed + 73) - 0.5) * 10; ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.quadraticCurveTo(mx, my, b.x, b.y); ctx.stroke(); }); ctx.setLineDash([]); ctx.globalAlpha = 1; }
function drawSettlements() { state.map.settlements.forEach((s) => { ctx.fillStyle = s.tier === 'capital' ? '#fbf2c7' : s.tier === 'town' ? '#ece8d0' : '#cfc5ad'; ctx.strokeStyle = '#463a2c'; const size = s.tier === 'capital' ? 3.8 : s.tier === 'town' ? 2.7 : 1.9; ctx.beginPath(); ctx.arc(s.x, s.y, size, 0, Math.PI * 2); ctx.fill(); ctx.stroke(); }); }
function drawBorders(pal) { ctx.strokeStyle = pal.border; ctx.globalAlpha = layerAlpha('borders'); ctx.lineWidth = 1.2; ctx.setLineDash([6, 5]); state.map.borders.forEach((b) => { ctx.beginPath(); b.points.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y))); ctx.closePath(); ctx.stroke(); }); ctx.setLineDash([]); ctx.globalAlpha = 1; }
function drawLabels(pal) {
  ctx.fillStyle = pal.text; ctx.globalAlpha = layerAlpha('labels'); ctx.textAlign = 'center';
  state.map.labels.forEach((l) => { ctx.font = `${l.type === 'river' ? 'italic ' : ''}${l.size}px Georgia, serif`; ctx.shadowColor = 'rgba(0,0,0,.35)'; ctx.shadowBlur = 3; ctx.fillText(l.text, l.x, l.y); });
  state.map.customLabels.forEach((l) => { ctx.font = `${l.style === 'river' ? 'italic ' : ''}${l.size}px Cinzel, Georgia, serif`; ctx.shadowColor = 'rgba(0,0,0,.5)'; ctx.shadowBlur = 4; ctx.fillStyle = l.color || pal.text; ctx.fillText(l.text, l.x, l.y); });
  ctx.shadowBlur = 0; ctx.globalAlpha = 1;
}

function drawManualAssets(pal) {
  if (!state.map?.manualAssets?.length) return;
  state.map.manualAssets.forEach((a) => {
    ctx.save();
    ctx.translate(a.x, a.y); ctx.rotate(a.rot || 0);
    const s = a.size;
    if (a.id === state.selectedAssetId) { ctx.strokeStyle = 'rgba(255,215,120,.9)'; ctx.lineWidth = 1; ctx.strokeRect(-s * 0.7, -s * 0.7, s * 1.4, s * 1.4); }
    if (a.type === 'mountain') { ctx.fillStyle = shadeHex(pal.mountain, 25); tri(0, -s * 0.6, s * 0.7); ctx.fillStyle = 'rgba(255,255,255,.4)'; tri(-s * 0.1, -s * 0.6, s * 0.3); }
    else if (a.type === 'hill') { ctx.fillStyle = shadeHex(pal.low, -18); ctx.beginPath(); ctx.ellipse(0, 0, s * 0.55, s * 0.35, 0, 0, Math.PI * 2); ctx.fill(); }
    else if (a.type === 'forest') { for (let i = 0; i < 5; i++) { ctx.fillStyle = shadeHex(pal.forest, i * 8 - 12); tri((i - 2) * s * 0.2, -s * 0.55 + Math.abs(i - 2) * 2, s * (0.38 - Math.abs(i - 2) * 0.03)); } }
    else if (a.type === 'city' || a.type === 'village') { ctx.fillStyle = '#efe4cf'; ctx.strokeStyle = '#4a3a2a'; ctx.lineWidth = 1; ctx.beginPath(); ctx.arc(0, 0, a.type === 'city' ? s * 0.22 : s * 0.16, 0, Math.PI * 2); ctx.fill(); ctx.stroke(); ctx.strokeRect(-s * 0.2, s * 0.04, s * 0.4, s * 0.3); }
    else if (a.type === 'ruin') { ctx.strokeStyle = '#8a7e68'; ctx.lineWidth = 1.3; ctx.strokeRect(-s * 0.3, -s * 0.2, s * 0.6, s * 0.4); ctx.beginPath(); ctx.moveTo(-s * 0.3, -s * 0.2); ctx.lineTo(0, -s * 0.45); ctx.lineTo(s * 0.3, -s * 0.2); ctx.stroke(); }
    else if (a.type === 'ship') { ctx.fillStyle = '#6a4d31'; ctx.beginPath(); ctx.moveTo(-s * 0.45, s * 0.15); ctx.lineTo(s * 0.45, s * 0.15); ctx.lineTo(s * 0.25, s * 0.35); ctx.lineTo(-s * 0.25, s * 0.35); ctx.closePath(); ctx.fill(); ctx.strokeStyle = '#dddfeb'; ctx.beginPath(); ctx.moveTo(0, s * 0.15); ctx.lineTo(0, -s * 0.5); ctx.lineTo(s * 0.28, -s * 0.1); ctx.closePath(); ctx.stroke(); }
    else if (a.type === 'monster') { ctx.strokeStyle = '#2f453f'; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(0, 0, s * 0.2, 0, Math.PI * 2); ctx.stroke(); for (let i = -2; i <= 2; i++) { ctx.beginPath(); ctx.moveTo(i * s * 0.16, s * 0.1); ctx.bezierCurveTo(i * s * 0.16 + 3, s * 0.35, i * s * 0.12 - 3, s * 0.55, i * s * 0.22, s * 0.7); ctx.stroke(); } }
    else if (a.type === 'compass') { ctx.strokeStyle = '#5d4528'; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(0, 0, s * 0.45, 0, Math.PI * 2); ctx.stroke(); tri(0, -s * 0.55, s * 0.25); tri(0, s * 0.55, s * 0.25, true); tri(-s * 0.55, 0, s * 0.25, true, Math.PI / 2); tri(s * 0.55, 0, s * 0.25, true, Math.PI / 2); }
    else if (a.type === 'banner') { ctx.fillStyle = '#d6b87f'; ctx.strokeStyle = '#71553a'; ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(-s * 0.6, -s * 0.3); ctx.lineTo(s * 0.6, -s * 0.3); ctx.lineTo(s * 0.45, s * 0.3); ctx.lineTo(-s * 0.45, s * 0.3); ctx.closePath(); ctx.fill(); ctx.stroke(); }
    ctx.restore();
  });
}

function tri(x, y, size, down = false, rot = 0) {
  ctx.save();
  ctx.translate(x, y); ctx.rotate(rot);
  ctx.beginPath();
  if (!down) { ctx.moveTo(0, -size); ctx.lineTo(-size * 0.8, size * 0.7); ctx.lineTo(size * 0.8, size * 0.7); }
  else { ctx.moveTo(0, size); ctx.lineTo(-size * 0.8, -size * 0.7); ctx.lineTo(size * 0.8, -size * 0.7); }
  ctx.closePath(); ctx.fill();
  ctx.restore();
}

function drawGrid() {
  if (state.grid === 'none') return;
  const step = 58; ctx.strokeStyle = 'rgba(255,255,255,.22)'; ctx.lineWidth = 0.6;
  if (state.grid === 'square') { for (let x = 0; x < canvas.width; x += step) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke(); } for (let y = 0; y < canvas.height; y += step) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke(); } return; }
  const h = Math.sqrt(3) * step / 2;
  for (let y = -h; y < canvas.height + h; y += h) for (let x = -step; x < canvas.width + step; x += step * 1.5) { const ox = Math.floor(y / h) % 2 ? x + step * 0.75 : x; hex(ox, y, step / 2); }
}

function exportMap(type) {
  if (!state.map) return;
  if (type === 'project') { downloadBlob(new Blob([JSON.stringify({ state: { ...state, map: null }, layers, map: serializeMap() }, null, 2)], { type: 'application/json' }), `map-${Date.now()}.aethermap`); return; }
  if (type === 'heightmap') {
    const c = document.createElement('canvas'); c.width = state.map.w; c.height = state.map.h; const cctx = c.getContext('2d'); const img = cctx.createImageData(c.width, c.height);
    for (let i = 0; i < state.map.height.length; i++) { const v = Math.floor(state.map.height[i] * 255); img.data[i * 4] = v; img.data[i * 4 + 1] = v; img.data[i * 4 + 2] = v; img.data[i * 4 + 3] = 255; }
    cctx.putImageData(img, 0, 0); c.toBlob((b) => downloadBlob(b, 'heightmap.png'), 'image/png'); return;
  }
  if (type === 'pdf') { const { jsPDF } = window.jspdf; const pdf = new jsPDF({ orientation: canvas.width > canvas.height ? 'landscape' : 'portrait', unit: 'pt', format: [canvas.width * 0.28, canvas.height * 0.28] }); pdf.addImage(canvas.toDataURL('image/png'), 'PNG', 0, 0, canvas.width * 0.28, canvas.height * 0.28); pdf.save('fantasy-map.pdf'); return; }
  if (type === 'vtt') { const prev = state.grid; state.grid = 'square'; render(); canvas.toBlob((blob) => { downloadBlob(blob, 'fantasy-map-vtt.png'); state.grid = prev; render(); }, 'image/png'); return; }
  if (type === 'tiff') { canvas.toBlob((blob) => downloadBlob(blob, 'fantasy-map.tiff'), 'image/png'); return; }
  const mime = type === 'jpg' ? 'image/jpeg' : 'image/png'; canvas.toBlob((blob) => downloadBlob(blob, `fantasy-map.${type}`), mime, type === 'jpg' ? 0.94 : undefined);
}

function serializeMap() {
  const m = state.map;
  return {
    ...m,
    height: Array.from(m.height), moisture: Array.from(m.moisture), temp: Array.from(m.temp), mountainMask: Array.from(m.mountainMask), coastDistance: Array.from(m.coastDistance)
  };
}

function setupUI() {
  const layerList = document.getElementById('layerList');
  layerList.innerHTML = layers.map((l) => `<div class="layer-row" data-layer="${l.id}"><div class="top"><label><input type="checkbox" ${l.visible ? 'checked' : ''} class="layer-visible"> ${l.name}</label><button class="lock-btn">${l.locked ? 'Unlock' : 'Lock'}</button></div><input class="layer-opacity" type="range" min="0" max="1" step="0.05" value="${l.opacity}"></div>`).join('');
  layerList.oninput = (e) => { const row = e.target.closest('.layer-row'); if (!row) return; const l = layers.find((x) => x.id === row.dataset.layer); if (!l) return; if (e.target.classList.contains('layer-visible')) l.visible = e.target.checked; if (e.target.classList.contains('layer-opacity')) l.opacity = Number(e.target.value); render(); };
  layerList.onclick = (e) => { if (!e.target.classList.contains('lock-btn')) return; const row = e.target.closest('.layer-row'); const l = layers.find((x) => x.id === row.dataset.layer); l.locked = !l.locked; e.target.textContent = l.locked ? 'Unlock' : 'Lock'; };

  bind('generateBtn', 'click', () => {
    const preset = document.getElementById('canvasPreset').value;
    if (preset === 'custom') { state.width = Number(document.getElementById('customWidth').value); state.height = Number(document.getElementById('customHeight').value); }
    else [state.width, state.height] = preset.split('x').map(Number);
    state.style = document.getElementById('stylePreset').value; state.seed = Number(document.getElementById('seedInput').value); state.waterPct = Number(document.getElementById('waterInput').value); state.worldUnits = Number(document.getElementById('mapDistance').value); state.unit = document.getElementById('scaleUnit').value;
    generateMap(); generateBordersAndLabels(); autoSave();
  });

  bind('regenPaletteBtn', 'click', () => { if (!state.map) return; state.seed += 17; state.map.palette = buildAdaptivePalette(); render(); });
  bind('assetType', 'change', (e) => state.assetType = e.target.value);
  bind('assetSize', 'input', (e) => { state.assetSize = Number(e.target.value); document.getElementById('assetSizeValue').textContent = e.target.value; });
  bind('customLabelInput', 'input', (e) => state.customLabelText = e.target.value || 'New Realm');
  bind('waterInput', 'input', (e) => document.getElementById('waterValue').textContent = e.target.value);
  bind('canvasPreset', 'change', (e) => document.getElementById('customSizeFields').hidden = e.target.value !== 'custom');
  bind('zoomRange', 'input', (e) => { state.zoom = Number(e.target.value) / 100; document.getElementById('zoomValue').textContent = `${e.target.value}%`; render(); });
  bind('gridMode', 'change', (e) => { state.grid = e.target.value; render(); });
  bind('toolMode', 'change', (e) => { state.tool = e.target.value; canvas.classList.toggle('drawing', state.tool !== 'pan'); });
  bind('brushRadius', 'input', (e) => { state.brushRadius = Number(e.target.value); document.getElementById('brushValue').textContent = e.target.value; });
  bind('brushStrength', 'input', (e) => { state.brushStrength = Number(e.target.value) / 100; document.getElementById('strengthValue').textContent = e.target.value; });
  bind('themeToggle', 'click', () => document.body.classList.toggle('theme-light'));
  bind('genBordersBtn', 'click', generateBordersAndLabels); bind('genLabelsBtn', 'click', generateBordersAndLabels); bind('runErosionBtn', 'click', runErosion); bind('undoBtn', 'click', undo); bind('redoBtn', 'click', redo); bind('saveVersionBtn', 'click', saveVersion);
  document.querySelectorAll('[data-export]').forEach((btn) => btn.addEventListener('click', () => exportMap(btn.dataset.export)));

  setupCanvasInput(); hydrateFromAutosave(); generateMap(); generateBordersAndLabels();
}

function setupCanvasInput() {
  let isDown = false, startX = 0, startY = 0, measureStart = null;
  canvas.addEventListener('mousedown', (e) => {
    isDown = true; startX = e.clientX; startY = e.clientY;
    const p = screenToMap(e.clientX, e.clientY);

    if (state.tool === 'measure') {
      if (!measureStart) measureStart = p;
      else { const d = Math.hypot(p.x - measureStart.x, p.y - measureStart.y); document.getElementById('measureReadout').textContent = `Distance: ${((d / state.map.w) * state.worldUnits).toFixed(1)} ${state.unit}`; measureStart = null; }
      return;
    }
    if (state.tool === 'placeAsset') { addAssetAt(p.x, p.y); pushHistory(); render(); return; }
    if (state.tool === 'placeLabel') { addLabelAt(p.x, p.y); pushHistory(); render(); return; }
    if (state.tool === 'eraseAsset') { eraseAssetAt(p.x, p.y); pushHistory(); render(); return; }
    if (state.tool === 'moveAsset') {
      state.selectedAssetId = findAssetIdAt(p.x, p.y);
      state.dragAsset = Boolean(state.selectedAssetId);
      render();
      return;
    }
    if (state.tool !== 'pan') applyBrush(e);
  });

  window.addEventListener('mouseup', () => { if (isDown && (state.tool === 'heightRaise' || state.tool === 'heightLower' || state.dragAsset)) pushHistory(); isDown = false; state.dragAsset = false; });
  window.addEventListener('mousemove', (e) => {
    if (!isDown) return;
    const p = screenToMap(e.clientX, e.clientY);
    if (state.tool === 'pan') { state.offsetX += e.clientX - startX; state.offsetY += e.clientY - startY; startX = e.clientX; startY = e.clientY; render(); return; }
    if (state.tool === 'moveAsset' && state.dragAsset) {
      const asset = state.map.manualAssets.find((a) => a.id === state.selectedAssetId);
      if (asset) { asset.x = p.x; asset.y = p.y; render(); }
      return;
    }
    if (state.tool === 'heightRaise' || state.tool === 'heightLower') applyBrush(e);
  });
}

function addAssetAt(x, y) {
  if (!state.map) return;
  state.map.manualAssets.push({ id: `a-${Date.now()}-${Math.random()}`, type: state.assetType, x, y, size: state.assetSize, rot: (hash2(x, y, state.seed) - 0.5) * 0.6 });
}
function addLabelAt(x, y) {
  state.map.customLabels.push({ id: `l-${Date.now()}-${Math.random()}`, x, y, text: state.customLabelText || 'New Realm', size: Math.max(10, Math.round(state.assetSize * 0.65)), style: state.assetType === 'ship' ? 'river' : 'city', color: null });
}
function findAssetIdAt(x, y) {
  for (let i = state.map.manualAssets.length - 1; i >= 0; i--) {
    const a = state.map.manualAssets[i];
    if (Math.hypot(a.x - x, a.y - y) < a.size * 0.8) return a.id;
  }
  return null;
}
function eraseAssetAt(x, y) {
  state.map.manualAssets = state.map.manualAssets.filter((a) => Math.hypot(a.x - x, a.y - y) >= a.size * 0.8);
  state.map.customLabels = state.map.customLabels.filter((l) => Math.hypot(l.x - x, l.y - y) >= 20);
}

function applyBrush(e) {
  if (!state.map) return;
  const p = screenToMap(e.clientX, e.clientY), { w, h, height } = state.map, sign = state.tool === 'heightRaise' ? 1 : -1;
  for (let y = -state.brushRadius; y <= state.brushRadius; y++) for (let x = -state.brushRadius; x <= state.brushRadius; x++) {
    const d = Math.hypot(x, y); if (d > state.brushRadius) continue;
    const xx = Math.floor(p.x + x), yy = Math.floor(p.y + y); if (xx < 0 || yy < 0 || xx >= w || yy >= h) continue;
    const i = yy * w + xx; height[i] = clamp(height[i] + sign * state.brushStrength * (1 - d / state.brushRadius) * 0.02, 0, 1);
  }
  state.map.rivers = buildRivers(state.map.height, w, h, state.map.seaLevel); render();
}

function runErosion() { if (!state.map) return; const { w, h, height } = state.map; const copy = Float32Array.from(height); for (let y = 1; y < h - 1; y++) for (let x = 1; x < w - 1; x++) { const i = y * w + x; const avg = (copy[i] + copy[i - 1] + copy[i + 1] + copy[i - w] + copy[i + w]) / 5; height[i] = copy[i] * 0.68 + avg * 0.32; } normalizeArray(height); state.map.rivers = buildRivers(height, w, h, state.map.seaLevel); render(); pushHistory(); }

function pushHistory() {
  if (!state.map) return;
  state.history.push({
    height: Float32Array.from(state.map.height),
    manualAssets: JSON.parse(JSON.stringify(state.map.manualAssets)),
    customLabels: JSON.parse(JSON.stringify(state.map.customLabels))
  });
  if (state.history.length > 60) state.history.shift();
  state.redo = [];
}
function undo() { if (!state.map || state.history.length < 2) return; state.redo.push(state.history.pop()); applySnapshot(state.history[state.history.length - 1]); }
function redo() { if (!state.map || !state.redo.length) return; const next = state.redo.pop(); state.history.push({ height: Float32Array.from(next.height), manualAssets: JSON.parse(JSON.stringify(next.manualAssets)), customLabels: JSON.parse(JSON.stringify(next.customLabels)) }); applySnapshot(next); }
function applySnapshot(s) { state.map.height = Float32Array.from(s.height); state.map.manualAssets = JSON.parse(JSON.stringify(s.manualAssets)); state.map.customLabels = JSON.parse(JSON.stringify(s.customLabels)); state.map.rivers = buildRivers(state.map.height, state.map.w, state.map.h, state.map.seaLevel); render(); }

function saveVersion() { if (!state.map) return; state.versions.push({ t: new Date().toLocaleString(), seed: state.seed, style: state.style, water: state.waterPct }); if (state.versions.length > 20) state.versions.shift(); document.getElementById('versionList').innerHTML = state.versions.map((v, i) => `<div class="version-item"><span>#${i + 1} ${v.t}</span><span>${v.style}</span></div>`).join(''); autoSave(); }
function autoSave() { localStorage.setItem('aethermap-autosave', JSON.stringify({ seed: state.seed, waterPct: state.waterPct, style: state.style, versions: state.versions })); }
function hydrateFromAutosave() { const raw = localStorage.getItem('aethermap-autosave'); if (!raw) return; try { const s = JSON.parse(raw); state.seed = s.seed ?? state.seed; state.waterPct = s.waterPct ?? state.waterPct; state.style = s.style ?? state.style; state.versions = s.versions ?? []; document.getElementById('seedInput').value = state.seed; document.getElementById('waterInput').value = state.waterPct; document.getElementById('waterValue').textContent = state.waterPct; document.getElementById('stylePreset').value = state.style; document.getElementById('versionList').innerHTML = state.versions.map((v, i) => `<div class="version-item"><span>#${i + 1} ${v.t}</span><span>${v.style}</span></div>`).join(''); } catch (_) {} }

function generateNameBank(count = 1200) { const pre = ['Ael', 'Dra', 'Kor', 'Val', 'Ith', 'Mor', 'Fen', 'Tha', 'Nor', 'Syl', 'Gal', 'Bryn', 'Zar', 'Riv', 'Eld', 'Kael', 'Vorn', 'Lun']; const mid = ['an', 'or', 'il', 'en', 'ath', 'dor', 'mir', 'vel', 'ion', 'ara', 'uin', 'eth', 'yr', 'ess']; const suf = ['ia', 'heim', 'ford', 'spire', 'mere', 'hold', 'gard', 'reach', 'crest', 'fall', 'keep', 'mar', 'watch', 'hollow']; const names = []; for (let i = 0; i < count; i++) names.push(`${pre[i % pre.length]}${mid[(i * 7 + 3) % mid.length]}${suf[(i * 11 + 5) % suf.length]}`); return names; }
function pointToLineDistance(px, py, x1, y1, x2, y2) { const A = px - x1, B = py - y1, C = x2 - x1, D = y2 - y1, dot = A * C + B * D, len = C * C + D * D, t = clamp(dot / len, 0, 1), x = x1 + C * t, y = y1 + D * t; return Math.hypot(px - x, py - y); }
function normalizeArray(arr) { let min = Infinity, max = -Infinity; for (const v of arr) { if (v < min) min = v; if (v > max) max = v; } const range = max - min || 1; for (let i = 0; i < arr.length; i++) arr[i] = (arr[i] - min) / range; }
function percentile(arr, p) { const copy = Array.from(arr).sort((a, b) => a - b); return copy[Math.floor((copy.length - 1) * p)]; }
function average(arr) { let sum = 0; for (const v of arr) sum += v; return sum / arr.length; }
function radialPolygon(cx, cy, r, n) { return Array.from({ length: n }, (_, i) => { const a = (i / n) * Math.PI * 2; const rr = r * (0.85 + (hash2(i, n, state.seed + 8000) - 0.5) * 0.35); return [cx + Math.cos(a) * rr, cy + Math.sin(a) * rr]; }); }
function hex(x, y, r) { ctx.beginPath(); for (let i = 0; i < 6; i++) { const a = Math.PI / 3 * i; const px = x + Math.cos(a) * r, py = y + Math.sin(a) * r; i ? ctx.lineTo(px, py) : ctx.moveTo(px, py); } ctx.closePath(); ctx.stroke(); }
function bind(id, ev, fn) { document.getElementById(id).addEventListener(ev, fn); }
function screenToMap(clientX, clientY) { const r = viewport.getBoundingClientRect(); return { x: (clientX - r.left - state.offsetX) / state.zoom, y: (clientY - r.top - state.offsetY) / state.zoom }; }
function downloadBlob(blob, name) { const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = name; a.click(); URL.revokeObjectURL(a.href); }

setupUI();
