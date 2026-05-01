'use strict';

// ── Constants ────────────────────────────────────────────────────────────────

const CELL = 4; // pixels per simulation cell

const E = Object.freeze({
  EMPTY: 0, SAND: 1, WATER: 2, FIRE: 3,
  WOOD: 4, STONE: 5, SMOKE: 6, STEAM: 7,
  SAPLING: 8, TNT: 9,
});

const ELEM_LIST = [E.SAND, E.WATER, E.FIRE, E.WOOD, E.STONE, E.SMOKE, E.STEAM, E.SAPLING, E.TNT];

const META = [
  { name: 'Empty',   key: null, r: 10,  g: 10,  b: 10,  hex: '#0a0a0a' },
  { name: 'Sand',    key: '1',  r: 194, g: 178, b: 128, hex: '#c2b280' },
  { name: 'Water',   key: '2',  r: 28,  g: 107, b: 214, hex: '#1c6bd6' },
  { name: 'Fire',    key: '3',  r: 255, g: 80,  b: 0,   hex: '#ff5000' },
  { name: 'Wood',    key: '4',  r: 120, g: 72,  b: 30,  hex: '#78481e' },
  { name: 'Stone',   key: '5',  r: 110, g: 110, b: 110, hex: '#6e6e6e' },
  { name: 'Smoke',   key: '6',  r: 70,  g: 70,  b: 70,  hex: '#464646' },
  { name: 'Steam',   key: '7',  r: 180, g: 210, b: 230, hex: '#b4d2e6' },
  { name: 'Sapling', key: '8',  r: 60,  g: 180, b: 60,  hex: '#3cb43c' },
  { name: 'TNT',     key: '9',  r: 210, g: 40,  b: 40,  hex: '#d22828' },
];

// ── Grid ─────────────────────────────────────────────────────────────────────

class Grid {
  constructor(width, height) {
    this.width = width;
    this.height = height;
    const n = width * height;
    this.cells   = new Uint8Array(n);
    this.updated = new Uint8Array(n);
    this.fireAge = new Int32Array(n);
    this.gasAge  = new Int32Array(n);
    this.dirty   = new Uint8Array(n);
    this.fullRedraw = true;
  }

  idx(x, y)          { return y * this.width + x; }
  inBounds(x, y)     { return x >= 0 && x < this.width && y >= 0 && y < this.height; }
  get(x, y)          { return this.inBounds(x, y) ? this.cells[this.idx(x, y)] : E.STONE; }

  set(x, y, elem) {
    if (!this.inBounds(x, y)) return;
    const i = this.idx(x, y);
    this.cells[i] = elem;
    if (elem === E.FIRE)    this.fireAge[i] = 20 + (Math.random() * 41 | 0);
    if (elem === E.SAPLING) {
      this.gasAge[i]  = 40 + (Math.random() * 60 | 0); // ticks until next growth
      this.fireAge[i] = 4  + (Math.random() * 4  | 0); // remaining trunk extensions
    }
    this.dirty[i] = 1;
  }

  swap(x1, y1, x2, y2) {
    const i1 = this.idx(x1, y1), i2 = this.idx(x2, y2);
    const tmp = this.cells[i1];
    this.cells[i1] = this.cells[i2];
    this.cells[i2] = tmp;
    this.updated[i1] = this.updated[i2] = 1;
    this.dirty[i1]   = this.dirty[i2]   = 1;
  }

  clear() {
    this.cells.fill(0);
    this.fireAge.fill(0);
    this.gasAge.fill(0);
    this.fullRedraw = true;
  }

  tick() {
    this.updated.fill(0);
    const { width, height, cells, updated } = this;
    for (let y = height - 1; y >= 0; y--) {
      const base = y * width;
      for (let x = 0; x < width; x++) {
        const i = base + x;
        if (!updated[i] && cells[i] !== E.EMPTY) _updateCell(this, x, y, cells[i]);
      }
    }
  }
}

// ── Physics ──────────────────────────────────────────────────────────────────

function _updateCell(g, x, y, elem) {
  switch (elem) {
    case E.SAND:    _sand(g, x, y);    break;
    case E.WATER:   _water(g, x, y);   break;
    case E.FIRE:    _fire(g, x, y);    break;
    case E.SMOKE:   _smoke(g, x, y);   break;
    case E.STEAM:   _steam(g, x, y);   break;
    case E.SAPLING: _sapling(g, x, y); break;
    case E.TNT:     _tnt(g, x, y);     break;
  }
}

function _sand(g, x, y) {
  const b = g.get(x, y + 1);
  if (b === E.EMPTY || b === E.WATER) { g.swap(x, y, x, y + 1); return; }
  const d = Math.random() < 0.5 ? 1 : -1;
  const b1 = g.get(x + d, y + 1);
  if (b1 === E.EMPTY || b1 === E.WATER) { g.swap(x, y, x + d, y + 1); return; }
  const b2 = g.get(x - d, y + 1);
  if (b2 === E.EMPTY || b2 === E.WATER) { g.swap(x, y, x - d, y + 1); }
}

function _water(g, x, y) {
  if (g.get(x, y + 1) === E.EMPTY) { g.swap(x, y, x, y + 1); return; }
  const d = Math.random() < 0.5 ? 1 : -1;
  if (g.get(x + d, y) === E.EMPTY) { g.swap(x, y, x + d, y); return; }
  if (g.get(x - d, y) === E.EMPTY) { g.swap(x, y, x - d, y); }
}

function _fire(g, x, y) {
  const i = g.idx(x, y);
  g.dirty[i] = 1; // force redraw every tick for flicker
  g.fireAge[i]--;

  if (g.fireAge[i] <= 0) {
    const next = Math.random() < 0.5 ? E.SMOKE : E.EMPTY;
    g.cells[i] = next;
    if (next === E.SMOKE) g.gasAge[i] = 15 + (Math.random() * 26 | 0);
    g.updated[i] = 1;
    return;
  }

  const dirs = [[1,0],[-1,0],[0,1],[0,-1]];
  for (const [dx, dy] of dirs) {
    const nx = x + dx, ny = y + dy;
    if (!g.inBounds(nx, ny)) continue;
    const ni = g.idx(nx, ny);
    const nb = g.cells[ni];
    if ((nb === E.WOOD || nb === E.SAPLING) && Math.random() < 0.05) {
      g.cells[ni] = E.FIRE;
      g.fireAge[ni] = 20 + (Math.random() * 41 | 0);
      g.updated[ni] = g.dirty[ni] = 1;
    } else if (nb === E.WATER && Math.random() < 0.30) {
      g.cells[ni] = E.STEAM;
      g.gasAge[ni] = 30 + (Math.random() * 51 | 0);
      g.updated[ni] = g.dirty[ni] = 1;
      g.cells[i] = E.EMPTY;
      g.updated[i] = 1;
      return;
    }
  }
}

function _rise(g, x, y, extraUp) {
  const candidates = [];
  if (extraUp && g.get(x, y - 2) === E.EMPTY) candidates.push([x, y - 2]);
  if (g.get(x, y - 1) === E.EMPTY) candidates.push([x, y - 1]);
  if (!candidates.length) {
    const lr = Math.random() < 0.5 ? [[x-1,y-1],[x+1,y-1]] : [[x+1,y-1],[x-1,y-1]];
    for (const p of lr) { if (g.get(p[0], p[1]) === E.EMPTY) { candidates.push(p); break; } }
  }
  if (!candidates.length) {
    const lr = Math.random() < 0.5 ? [[x-1,y],[x+1,y]] : [[x+1,y],[x-1,y]];
    for (const p of lr) { if (g.get(p[0], p[1]) === E.EMPTY) { candidates.push(p); break; } }
  }
  if (candidates.length) {
    const [nx, ny] = candidates[0];
    g.gasAge[g.idx(nx, ny)] = g.gasAge[g.idx(x, y)];
    g.swap(x, y, nx, ny);
  }
}

function _smoke(g, x, y) {
  const i = g.idx(x, y);
  g.gasAge[i]--;
  if (g.gasAge[i] <= 0 || Math.random() < 0.03) {
    g.cells[i] = E.EMPTY; g.updated[i] = g.dirty[i] = 1; return;
  }
  _rise(g, x, y, false);
}

function _steam(g, x, y) {
  const i = g.idx(x, y);
  g.gasAge[i]--;
  if (g.gasAge[i] <= 0) {
    g.cells[i] = E.EMPTY; g.updated[i] = g.dirty[i] = 1; return;
  }
  if (Math.random() < 0.01) {
    g.cells[i] = E.WATER; g.updated[i] = g.dirty[i] = 1; return;
  }
  _rise(g, x, y, true);
}

function _sapling(g, x, y) {
  const i = g.idx(x, y);
  g.gasAge[i]--;
  if (g.gasAge[i] > 0) return;

  // Reset growth timer for next cycle
  g.gasAge[i] = 30 + (Math.random() * 50 | 0);

  const heightLeft = g.fireAge[i];

  // Convert this cell to wood and grow upward
  g.cells[i] = E.WOOD;
  g.updated[i] = g.dirty[i] = 1;

  if (g.get(x, y - 1) === E.EMPTY) {
    if (heightLeft > 0) {
      // Place a new sapling above to continue the trunk
      const ni = g.idx(x, y - 1);
      g.cells[ni]   = E.SAPLING;
      g.gasAge[ni]  = 20 + (Math.random() * 30 | 0);
      g.fireAge[ni] = heightLeft - 1;
      g.dirty[ni]   = 1;
    } else {
      // Top of tree — cap with wood
      g.set(x, y - 1, E.WOOD);
    }
  }

  // Branches: more frequent near the top of the tree
  const branchChance = heightLeft <= 2 ? 0.45 : 0.18;
  for (const dx of [-1, 1]) {
    if (Math.random() < branchChance && g.get(x + dx, y - 1) === E.EMPTY)
      g.set(x + dx, y - 1, E.WOOD);
    // Extra horizontal branch near crown
    if (heightLeft <= 1 && Math.random() < 0.3 && g.get(x + dx, y) === E.EMPTY)
      g.set(x + dx, y, E.WOOD);
  }
}

function _explode(g, x, y) {
  const R = 10;
  // Clear the TNT first so recursive calls skip it
  const i = g.idx(x, y);
  g.cells[i] = E.EMPTY;
  g.updated[i] = g.dirty[i] = 1;

  for (let dy = -R; dy <= R; dy++) {
    for (let dx = -R; dx <= R; dx++) {
      if (dx * dx + dy * dy > R * R) continue;
      const nx = x + dx, ny = y + dy;
      if (!g.inBounds(nx, ny)) continue;
      const ni = g.idx(nx, ny);
      const nc = g.cells[ni];
      if (nc === E.STONE) continue;
      if (nc === E.TNT) { _explode(g, nx, ny); continue; } // chain reaction
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < R * 0.6) {
        g.cells[ni] = E.EMPTY;
      } else if (Math.random() < 0.5) {
        g.cells[ni] = E.FIRE;
        g.fireAge[ni] = 10 + (Math.random() * 20 | 0);
      } else {
        g.cells[ni] = E.EMPTY;
      }
      g.updated[ni] = g.dirty[ni] = 1;
    }
  }
}

function _tnt(g, x, y) {
  const dirs = [[1,0],[-1,0],[0,1],[0,-1]];
  for (const [dx, dy] of dirs) {
    if (g.get(x + dx, y + dy) === E.FIRE) { _explode(g, x, y); return; }
  }
}

// ── Renderer ─────────────────────────────────────────────────────────────────

class Renderer {
  constructor(canvas, grid) {
    this.canvas = canvas;
    this.ctx    = canvas.getContext('2d');
    this.grid   = grid;
    this._img   = this.ctx.createImageData(canvas.width, canvas.height);
    this._px    = this._img.data;
  }

  attachCanvas(canvas) {
    this.canvas = canvas;
    this.ctx    = canvas.getContext('2d');
    this._img   = this.ctx.createImageData(canvas.width, canvas.height);
    this._px    = this._img.data;
  }

  _cellColor(elem) {
    const m = META[elem];
    if (elem === E.FIRE)  return [m.r, Math.random() * 130 | 0, m.b];
    if (elem === E.STEAM) { const v = Math.random() * 20 | 0; return [m.r - v, m.g - v, m.b]; }
    if (elem === E.SAND)  { const v = (Math.random() * 14 | 0) - 7; return [m.r + v, m.g + v, m.b + v]; }
    return [m.r, m.g, m.b];
  }

  _writeBlock(x, y, r, g, b) {
    const cw = this.canvas.width;
    const px = x * CELL, py = y * CELL;
    const buf = this._px;
    for (let dy = 0; dy < CELL; dy++) {
      let o = ((py + dy) * cw + px) * 4;
      for (let dx = 0; dx < CELL; dx++, o += 4) {
        buf[o] = r; buf[o+1] = g; buf[o+2] = b; buf[o+3] = 255;
      }
    }
  }

  render() {
    const { width, height, cells, dirty, fullRedraw } = this.grid;

    if (fullRedraw) {
      for (let y = 0; y < height; y++) {
        const base = y * width;
        for (let x = 0; x < width; x++) {
          const [r, g, b] = this._cellColor(cells[base + x]);
          this._writeBlock(x, y, r, g, b);
        }
      }
      this.grid.fullRedraw = false;
      dirty.fill(0);
    } else {
      for (let i = 0; i < dirty.length; i++) {
        if (dirty[i]) {
          const x = i % width, y = (i / width) | 0;
          const [r, g, b] = this._cellColor(cells[i]);
          this._writeBlock(x, y, r, g, b);
          dirty[i] = 0;
        }
      }
    }
    this.ctx.putImageData(this._img, 0, 0);
  }
}

// ── Input ─────────────────────────────────────────────────────────────────────

class InputHandler {
  constructor(canvas, grid) {
    this.canvas  = canvas;
    this.grid    = grid;
    this.elem    = E.SAND;
    this.brush   = 1;
    this.paused  = false;
    this._drawing = false;
    this._erasing = false;
    this._lx = -1;
    this._ly = -1;
    this._bind();
  }

  _toCell(cx, cy) {
    const r = this.canvas.getBoundingClientRect();
    return [((cx - r.left) / CELL) | 0, ((cy - r.top) / CELL) | 0];
  }

  _paint(x, y, elem) {
    const r = this.brush - 1;
    for (let dy = -r; dy <= r; dy++)
      for (let dx = -r; dx <= r; dx++)
        this.grid.set(x + dx, y + dy, elem);
  }

  _line(x0, y0, x1, y1, elem) {
    const dx = Math.abs(x1 - x0), dy = Math.abs(y1 - y0);
    const sx = x0 < x1 ? 1 : -1, sy = y0 < y1 ? 1 : -1;
    let err = dx - dy;
    for (;;) {
      this._paint(x0, y0, elem);
      if (x0 === x1 && y0 === y1) break;
      const e2 = 2 * err;
      if (e2 > -dy) { err -= dy; x0 += sx; }
      if (e2 <  dx) { err += dx; y0 += sy; }
    }
  }

  _down(cx, cy, erase) {
    const [x, y] = this._toCell(cx, cy);
    if (erase) { this._erasing = true; this._drawing = false; }
    else       { this._drawing = true; this._erasing = false; }
    this._paint(x, y, erase ? E.EMPTY : this.elem);
    this._lx = x; this._ly = y;
  }

  _move(cx, cy) {
    if (!this._drawing && !this._erasing) return;
    const [x, y] = this._toCell(cx, cy);
    const elem = this._erasing ? E.EMPTY : this.elem;
    if (this._lx >= 0) this._line(this._lx, this._ly, x, y, elem);
    else               this._paint(x, y, elem);
    this._lx = x; this._ly = y;
  }

  _up() {
    this._drawing = this._erasing = false;
    this._lx = this._ly = -1;
  }

  _bind() {
    const c = this.canvas;

    c.addEventListener('mousedown',  e => { e.preventDefault(); this._down(e.clientX, e.clientY, e.button === 2); });
    c.addEventListener('mousemove',  e => { e.preventDefault(); this._move(e.clientX, e.clientY); });
    c.addEventListener('mouseup',    e => this._up());
    c.addEventListener('mouseleave', e => this._up());
    c.addEventListener('contextmenu', e => e.preventDefault());

    c.addEventListener('touchstart', e => { e.preventDefault(); const t = e.touches[0]; this._down(t.clientX, t.clientY, false); }, { passive: false });
    c.addEventListener('touchmove',  e => { e.preventDefault(); const t = e.touches[0]; this._move(t.clientX, t.clientY); }, { passive: false });
    c.addEventListener('touchend',   e => this._up());

    document.addEventListener('keydown', e => {
      if (e.target.tagName === 'INPUT') return;
      switch (e.key) {
        case '1': case '2': case '3': case '4': case '5': case '6': case '7': case '8': case '9':
          if (+e.key - 1 < ELEM_LIST.length) { this.elem = ELEM_LIST[+e.key - 1]; updateHUD(); } break;
        case 'p': case 'P': this.paused = !this.paused; updateHUD(); break;
        case 'r': case 'R': this.grid.clear(); break;
        case '[': this.brush = Math.max(1, this.brush - 1); updateHUD(); break;
        case ']': this.brush = Math.min(5, this.brush + 1); updateHUD(); break;
        case 'e': {
          const i = (ELEM_LIST.indexOf(this.elem) + 1) % ELEM_LIST.length;
          this.elem = ELEM_LIST[i]; updateHUD(); break;
        }
        case 'E': {
          const i = (ELEM_LIST.indexOf(this.elem) + ELEM_LIST.length - 1) % ELEM_LIST.length;
          this.elem = ELEM_LIST[i]; updateHUD(); break;
        }
      }
    });
  }
}

// ── HUD helpers ───────────────────────────────────────────────────────────────

function updateHUD() {
  document.querySelectorAll('.elem-btn').forEach(btn => {
    btn.classList.toggle('active', +btn.dataset.elem === handler.elem);
  });
  document.getElementById('brushDisplay').textContent =
    '■'.repeat(handler.brush) + '□'.repeat(5 - handler.brush);
  document.getElementById('pauseBtn').textContent = handler.paused ? 'Resume' : 'Pause';
  document.getElementById('pauseBadge').style.display = handler.paused ? 'inline' : 'none';
}

// ── Game loop ─────────────────────────────────────────────────────────────────

let _lastTs = 0;
const _fpsBuf = [];

function loop(ts) {
  requestAnimationFrame(loop);

  const dt = ts - _lastTs;
  _lastTs = ts;

  _fpsBuf.push(dt > 0 ? 1000 / dt : 60);
  if (_fpsBuf.length > 60) _fpsBuf.shift();
  const fps = Math.round(_fpsBuf.reduce((a, b) => a + b) / _fpsBuf.length);
  document.getElementById('fpsDisplay').textContent = fps + ' fps';

  if (!handler.paused) grid.tick();
  renderer.render();
}

// ── Resize ────────────────────────────────────────────────────────────────────

function resize() {
  const hud  = document.getElementById('hud');
  const hudH = hud.offsetHeight;
  const W = window.innerWidth;
  const H = window.innerHeight - hudH;
  const gw = Math.max(1, (W / CELL) | 0);
  const gh = Math.max(1, (H / CELL) | 0);

  canvas.width  = gw * CELL;
  canvas.height = gh * CELL;

  if (gw !== grid.width || gh !== grid.height) {
    const old = grid;
    grid = new Grid(gw, gh);
    const mw = Math.min(old.width, gw), mh = Math.min(old.height, gh);
    for (let y = 0; y < mh; y++) {
      for (let x = 0; x < mw; x++) {
        const oi = old.idx(x, y), ni = grid.idx(x, y);
        grid.cells[ni]   = old.cells[oi];
        grid.fireAge[ni] = old.fireAge[oi];
        grid.gasAge[ni]  = old.gasAge[oi];
      }
    }
    handler.grid = grid;
    renderer.grid = grid;
  }
  renderer.attachCanvas(canvas);
}

// ── Init ──────────────────────────────────────────────────────────────────────

const canvas = document.getElementById('gameCanvas');
let grid, renderer, handler;

function init() {
  // Build element buttons
  const bar = document.getElementById('elements');
  ELEM_LIST.forEach((elem, i) => {
    const m = META[elem];
    const btn = document.createElement('button');
    btn.className = 'elem-btn';
    btn.dataset.elem = elem;
    btn.style.setProperty('--color', m.hex);
    btn.innerHTML = `<span class="key">${m.key}</span>${m.name}`;
    btn.addEventListener('click', () => { handler.elem = elem; updateHUD(); });
    bar.appendChild(btn);
  });

  document.getElementById('pauseBtn').addEventListener('click', () => { handler.paused = !handler.paused; updateHUD(); });
  document.getElementById('resetBtn').addEventListener('click', () => grid.clear());
  document.getElementById('brushDown').addEventListener('click', () => { handler.brush = Math.max(1, handler.brush - 1); updateHUD(); });
  document.getElementById('brushUp').addEventListener('click',   () => { handler.brush = Math.min(5, handler.brush + 1); updateHUD(); });

  // Initial layout
  const hudH = document.getElementById('hud').offsetHeight;
  const gw = Math.max(1, (window.innerWidth  / CELL) | 0);
  const gh = Math.max(1, ((window.innerHeight - hudH) / CELL) | 0);
  canvas.width  = gw * CELL;
  canvas.height = gh * CELL;

  grid     = new Grid(gw, gh);
  renderer = new Renderer(canvas, grid);
  handler  = new InputHandler(canvas, grid);

  window.addEventListener('resize', resize);

  updateHUD();
  requestAnimationFrame(loop);
}

document.addEventListener('DOMContentLoaded', init);
