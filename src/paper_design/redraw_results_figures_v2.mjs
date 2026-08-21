/**
 * Exact SVG redraw of RegionSuff Figures 3–8.
 *
 * Values come only from the locked experiment registry. The design revision
 * removes black default error/reference lines, provides semantic reference
 * labels, and reserves space for annotations instead of printing them over
 * chart marks.
 */
import fs from 'node:fs/promises';
import path from 'node:path';
import sharp from '/Users/tongyue/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp/dist/index.mjs';

const ROOT = '/Users/tongyue/Documents/77f /7hao';
const EXP = path.join(ROOT, 'experiments');
const OUT = path.join(ROOT, 'paper_design', 'figures_v6_callout_fixed');
const FONT_SCALE = 1.25;

const C = {
  ink: '#3F3027', brown: '#704C2B', umber: '#965E4A', orange: '#E49F5D',
  olive: '#8B9A7C', rose: '#C74282', paper: '#FFFDFC', pale: '#F7ECE6',
  paleOlive: '#E5E8D9', grid: '#E5D8CD', reference: '#9B928A', muted: '#766961',
  lightLine: '#D8CEC5', error: '#8E8176', white: '#FFFFFF',
};
const VIEW = [C.brown, C.orange, C.olive];

async function json(name) {
  return JSON.parse(await fs.readFile(path.join(EXP, name, 'results.json'), 'utf8'));
}

function esc(value) {
  return String(value).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
}
function n(value, digits = 3) { return Number(value).toFixed(digits); }
function clamp(x, a, b) { return Math.min(b, Math.max(a, x)); }
function map(value, domainMin, domainMax, rangeMin, rangeMax) {
  return rangeMin + ((value - domainMin) / (domainMax - domainMin)) * (rangeMax - rangeMin);
}
function font(size = 18, opts = {}) {
  const weight = opts.bold ? 700 : (opts.weight ?? 400);
  const style = opts.italic ? 'italic' : 'normal';
  const renderedSize = Math.round(size * FONT_SCALE * 10) / 10;
  return `font-family="Arial, Helvetica, sans-serif" font-size="${renderedSize}" font-weight="${weight}" font-style="${style}"`;
}
function t(x, y, label, opts = {}) {
  const anchor = opts.anchor ?? 'start';
  const fill = opts.fill ?? C.ink;
  const rotate = opts.rotate ? ` transform="rotate(${opts.rotate} ${x} ${y})"` : '';
  return `<text x="${x}" y="${y}" text-anchor="${anchor}" fill="${fill}" ${font(opts.size ?? 18, opts)}${rotate}>${esc(label)}</text>`;
}
function multiText(x, y, lines, opts = {}) {
  const anchor = opts.anchor ?? 'middle';
  const fill = opts.fill ?? C.ink;
  const lineHeight = (opts.lineHeight ?? (opts.size ?? 18) * 1.12) * FONT_SCALE;
  const tspans = lines.map((line, index) => `<tspan x="${x}" dy="${index === 0 ? 0 : lineHeight}">${esc(line)}</tspan>`).join('');
  return `<text x="${x}" y="${y}" text-anchor="${anchor}" fill="${fill}" ${font(opts.size ?? 18, opts)}>${tspans}</text>`;
}
function line(x1, y1, x2, y2, opts = {}) {
  return `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${opts.stroke ?? C.ink}" stroke-width="${opts.width ?? 1.5}"${opts.dash ? ` stroke-dasharray="${opts.dash}"` : ''}${opts.opacity ? ` opacity="${opts.opacity}"` : ''}/>`;
}
function rect(x, y, w, h, opts = {}) {
  return `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${opts.fill ?? 'none'}" stroke="${opts.stroke ?? 'none'}" stroke-width="${opts.width ?? 1}"${opts.rx ? ` rx="${opts.rx}"` : ''}/>`;
}
function circle(x, y, r, opts = {}) {
  return `<circle cx="${x}" cy="${y}" r="${r}" fill="${opts.fill ?? C.ink}" stroke="${opts.stroke ?? 'none'}" stroke-width="${opts.width ?? 1}"/>`;
}
function pathEl(d, opts = {}) {
  return `<path d="${d}" fill="${opts.fill ?? 'none'}" stroke="${opts.stroke ?? C.ink}" stroke-width="${opts.width ?? 1.5}" stroke-linejoin="round" stroke-linecap="round"${opts.dash ? ` stroke-dasharray="${opts.dash}"` : ''}/>`;
}
function diamond(x, y, r, opts = {}) {
  return `<path d="M ${x} ${y - r} L ${x + r} ${y} L ${x} ${y + r} L ${x - r} ${y} Z" fill="${opts.fill ?? C.orange}" stroke="${opts.stroke ?? C.brown}" stroke-width="${opts.width ?? 1.2}"/>`;
}
function square(x, y, s, opts = {}) {
  return rect(x - s / 2, y - s / 2, s, s, opts);
}
function triangle(x, y, r, opts = {}) {
  return `<path d="M ${x} ${y - r} L ${x + r * 0.9} ${y + r * 0.8} L ${x - r * 0.9} ${y + r * 0.8} Z" fill="${opts.fill ?? C.olive}" stroke="${opts.stroke ?? C.brown}" stroke-width="${opts.width ?? 1.1}"/>`;
}
function errorV(x, center, low, high, color) {
  const cap = 5.5;
  return line(x, low, x, high, { stroke: color, width: 1.65 }) +
    line(x - cap, low, x + cap, low, { stroke: color, width: 1.65 }) +
    line(x - cap, high, x + cap, high, { stroke: color, width: 1.65 });
}
function errorH(y, center, low, high, color) {
  const cap = 5.5;
  return line(low, y, high, y, { stroke: color, width: 1.65 }) +
    line(low, y - cap, low, y + cap, { stroke: color, width: 1.65 }) +
    line(high, y - cap, high, y + cap, { stroke: color, width: 1.65 });
}
function polyline(points, opts = {}) {
  return `<polyline points="${points.map(([x, y]) => `${x},${y}`).join(' ')}" fill="none" stroke="${opts.stroke ?? C.ink}" stroke-width="${opts.width ?? 2}" stroke-linejoin="round" stroke-linecap="round"${opts.dash ? ` stroke-dasharray="${opts.dash}"` : ''}/>`;
}
function legendItem(x, y, color, label, kind = 'line', opts = {}) {
  let mark = '';
  if (kind === 'bar') mark = rect(x, y - 11, 22, 14, { fill: color, stroke: C.ink, width: 0.8 });
  else if (kind === 'dot') mark = circle(x + 10, y - 4, 5, { fill: color, stroke: C.paper, width: 1 });
  else mark = line(x, y - 4, x + 24, y - 4, { stroke: color, width: 2.4 });
  return mark + t(x + 31, y, label, { size: opts.size ?? 17, fill: opts.fill ?? C.ink });
}

function makePanel(svg, cfg) {
  const { x, y, w, h, letter, title, xDomain, yDomain, xTicks = [], yTicks = [], xLabels = [], yLabel, xLabel, grid = 'y' } = cfg;
  svg.push(t(x - 34, y - 37, letter, { size: 22, bold: true, fill: C.brown }));
  svg.push(t(x, y - 37, title, { size: 22, bold: true, fill: C.ink }));
  svg.push(rect(x, y, w, h, { fill: C.paper, stroke: 'none' }));
  const sx = (v) => map(v, xDomain[0], xDomain[1], x, x + w);
  const sy = (v) => map(v, yDomain[0], yDomain[1], y + h, y);
  if (grid.includes('y')) {
    for (const tick of yTicks) {
      const yy = sy(tick.value ?? tick);
      svg.push(line(x, yy, x + w, yy, { stroke: C.grid, width: 1 }));
      const label = tick.label ?? (typeof tick === 'number' ? tick.toFixed(tick % 1 ? 2 : 1) : tick.value);
      svg.push(t(x - 12, yy + 6, label, { size: 17, anchor: 'end', fill: C.muted }));
    }
  }
  if (grid.includes('x')) {
    for (const tick of xTicks) {
      const xx = sx(tick.value ?? tick);
      svg.push(line(xx, y, xx, y + h, { stroke: C.grid, width: 1 }));
    }
  }
  svg.push(line(x, y, x, y + h, { stroke: C.ink, width: 1.35 }));
  svg.push(line(x, y + h, x + w, y + h, { stroke: C.ink, width: 1.35 }));
  for (let i = 0; i < xTicks.length; i += 1) {
    const tick = xTicks[i];
    const value = tick.value ?? tick;
    const xx = sx(value);
    svg.push(line(xx, y + h, xx, y + h + 5, { stroke: C.ink, width: 1.1 }));
    const label = tick.label ?? xLabels[i] ?? String(value);
    const lines = Array.isArray(label) ? label : [label];
    svg.push(multiText(xx, y + h + 27, lines, { size: 17, fill: C.ink, lineHeight: 18 }));
  }
  if (yLabel) svg.push(t(x - 74, y + h / 2, yLabel, { size: 18, anchor: 'middle', rotate: -90, fill: C.ink }));
  if (xLabel) svg.push(t(x + w / 2, y + h + 67, xLabel, { size: 18, anchor: 'middle', fill: C.ink }));
  return { x, y, w, h, sx, sy };
}
function simplePanel(svg, cfg) {
  const { x, y, w, h, letter, title } = cfg;
  svg.push(t(x - 34, y - 37, letter, { size: 22, bold: true, fill: C.brown }));
  svg.push(t(x, y - 37, title, { size: 22, bold: true, fill: C.ink }));
  return { x, y, w, h };
}
function noDiff(svg, panel, value = 0, label = 'No difference') {
  const xx = panel.sx(value);
  svg.push(line(xx, panel.y, xx, panel.y + panel.h, { stroke: C.reference, width: 1.4, dash: '5 5' }));
  const width = label.length * 8.5 + 14;
  svg.push(rect(xx + 6, panel.y + 7, width, 24, { fill: C.paper, stroke: 'none', rx: 3 }));
  svg.push(t(xx + 12, panel.y + 24, label, { size: 14, fill: C.reference }));
}
function svgRoot(width, height, parts) {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}"><rect width="100%" height="100%" fill="${C.paper}"/>${parts.join('')}</svg>`;
}
async function saveSvg(stem, width, height, parts) {
  const svg = svgRoot(width, height, parts);
  await fs.writeFile(path.join(OUT, `${stem}.svg`), svg);
  await sharp(Buffer.from(svg)).png().toFile(path.join(OUT, `${stem}.png`));
}

function valueStyle(metric, delta) {
  const improved = (metric === 'under' || metric === 'mae') ? delta < 0 : delta > 0;
  return improved ? C.olive : C.rose;
}

async function figure3() {
  const fov = (await json('exp48b_pixel_fov_geometry')).aggregate;
  const multi = await json('exp36_multiseed_deep_region');
  const W = 2000, H = 1160, svg = [];
  svg.push(t(1000, 67, 'Controlled evidence-loss tests: area, location, shape, and topology are not interchangeable', { size: 31, bold: true, fill: C.brown, anchor: 'middle' }));
  const A = makePanel(svg, { x: 150, y: 180, w: 720, h: 320, letter: 'A', title: 'Visible fraction changes performance', xDomain: [0.32, 0.93], yDomain: [0.42, 0.87], xTicks: [0.35, 0.45, 0.55, 0.65, 0.75, 0.90], yTicks: [0.45, 0.55, 0.65, 0.75, 0.85], yLabel: 'Macro-F1', xLabel: 'Visible linear fraction' });
  const fractions = [0.35, 0.45, 0.55, 0.65, 0.75, 0.90];
  for (const [shape, color, mark] of [['rect', C.brown, 'circle'], ['circle', C.rose, 'square']]) {
    const points = fractions.map((f) => [A.sx(f), A.sy(fov[`${shape}_center_${f.toFixed(2)}`].macro_f1.mean)]);
    svg.push(polyline(points, { stroke: color, width: 2.7 }));
    for (let idx = 0; idx < fractions.length; idx += 1) {
      const rec = fov[`${shape}_center_${fractions[idx].toFixed(2)}`].macro_f1;
      const xx = A.sx(fractions[idx]), yy = A.sy(rec.mean);
      svg.push(errorV(xx, yy, A.sy(rec.mean + rec.std), A.sy(rec.mean - rec.std), color));
      svg.push(mark === 'circle' ? circle(xx, yy, 5.4, { fill: color, stroke: C.paper, width: 1.2 }) : square(xx, yy, 10.5, { fill: color, stroke: C.paper, width: 1.2 }));
    }
  }
  svg.push(legendItem(552, 212, C.brown, 'Rectangle', 'line'));
  svg.push(legendItem(705, 212, C.rose, 'Area-matched circle', 'line'));

  const B = makePanel(svg, { x: 1130, y: 180, w: 720, h: 320, letter: 'B', title: 'Same fraction, different retinal location', xDomain: [-0.4, 4.4], yDomain: [0, 0.30], xTicks: [{ value: 0, label: 'Center' }, { value: 1, label: 'Left' }, { value: 2, label: 'Right' }, { value: 3, label: 'Superior' }, { value: 4, label: 'Inferior' }], yTicks: [0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30], yLabel: 'Underestimation rate' });
  const locs = ['center', 'left', 'right', 'up', 'down'];
  const locColors = [C.orange, C.olive, C.olive, C.umber, C.umber];
  const locPoints = [];
  for (let i = 0; i < locs.length; i += 1) {
    const rec = fov[`rect_${locs[i]}_0.55`].underestimation_rate;
    const xx = B.sx(i), yy = B.sy(rec.mean);
    locPoints.push([xx, yy]);
    svg.push(errorV(xx, yy, B.sy(rec.mean + rec.std), B.sy(rec.mean - rec.std), locColors[i]));
    svg.push(circle(xx, yy, 7, { fill: locColors[i], stroke: C.paper, width: 1.4 }));
  }
  svg.push(polyline(locPoints, { stroke: C.lightLine, width: 2.1 }));
  svg.push(t(B.x + 12, B.y + 25, 'Centered rectangular aperture: f = 0.55', { size: 16, fill: C.umber }));

  const D = makePanel(svg, { x: 1130, y: 700, w: 720, h: 320, letter: 'D', title: 'Regional evidence topology (internal test)', xDomain: [-0.3, 2.3], yDomain: [0.74, 0.87], xTicks: [{ value: 0, label: 'Full' }, { value: 1, label: 'Center' }, { value: 2, label: ['Center +', 'cross'] }], yTicks: [0.74, 0.78, 0.82, 0.86], yLabel: 'Macro-F1' });
  const views = ['full', 'center', 'cross'];
  for (let seed = 0; seed < 5; seed += 1) {
    const points = views.map((view, idx) => [D.sx(idx), D.sy(multi.rows.find((r) => r.seed === seed && r.view === view).macro_f1)]);
    svg.push(polyline(points, { stroke: C.lightLine, width: 1.8 }));
    for (const [xx, yy] of points) svg.push(circle(xx, yy, 4.3, { fill: C.paper, stroke: '#A8927F', width: 1.1 }));
  }
  for (let idx = 0; idx < views.length; idx += 1) {
    const rec = multi.aggregate[views[idx]].macro_f1;
    const xx = D.sx(idx), yy = D.sy(rec.mean);
    svg.push(errorV(xx, yy, D.sy(rec.mean + rec.std), D.sy(rec.mean - rec.std), C.brown));
    svg.push(diamond(xx, yy, 7.3, { fill: C.orange, stroke: C.brown, width: 1.2 }));
  }
  svg.push(legendItem(D.x + 12, D.y + 30, C.orange, 'Mean ± SD', 'dot', { size: 16 }));

  const Cpanel = makePanel(svg, { x: 150, y: 700, w: 720, h: 320, letter: 'C', title: 'Matched nominal area, different shape', xDomain: [-0.6, 1.6], yDomain: [0.54, 0.86], xTicks: [{ value: 0, label: 'Rectangle' }, { value: 1, label: ['Area-matched', 'circle'] }], yTicks: [0.55, 0.65, 0.75, 0.85], yLabel: 'Macro-F1' });
  const shapeRec = ['rect', 'circle'].map((shape) => fov[`${shape}_center_0.55`].macro_f1);
  const barW = 158;
  for (let i = 0; i < 2; i += 1) {
    const xx = Cpanel.sx(i) - barW / 2;
    const yy = Cpanel.sy(shapeRec[i].mean);
    const baseY = Cpanel.sy(0.54);
    const color = i === 0 ? C.brown : C.orange;
    svg.push(rect(xx, yy, barW, baseY - yy, { fill: color, stroke: C.ink, width: 1.0, rx: 2 }));
    svg.push(errorV(Cpanel.sx(i), yy, Cpanel.sy(shapeRec[i].mean + shapeRec[i].std), Cpanel.sy(shapeRec[i].mean - shapeRec[i].std), color));
    svg.push(t(Cpanel.sx(i), Cpanel.sy(shapeRec[i].mean + shapeRec[i].std) - 11, n(shapeRec[i].mean), { size: 18, anchor: 'middle', bold: true }));
  }
  await saveSvg('Figure3_Controlled_Visibility_RMB20_v3_large_font', W, H, svg);
}

async function figure4() {
  const abl = await json('exp35_region_mask_pool_ablation');
  const enc = (await json('exp37_encoder_ablation')).representations;
  const pair = (await json('exp45_grid_paired_bootstrap')).rows;
  const W = 2000, H = 1160, svg = [];
  svg.push(t(1000, 67, 'Component ablations: retinal representations help; selected controls are not unique optima', { size: 31, bold: true, fill: C.brown, anchor: 'middle' }));
  const A = makePanel(svg, { x: 150, y: 180, w: 720, h: 320, letter: 'A', title: 'Regional encoder control', xDomain: [-0.6, 3.6], yDomain: [0, 0.92], xTicks: [{ value: 0, label: ['RetinaRadar', '(frozen)'] }, { value: 1, label: ['ImageNet', 'ResNet-50'] }, { value: 2, label: 'Handcrafted' }, { value: 3, label: ['Random', 'ResNet-50'] }], yTicks: [0, 0.2, 0.4, 0.6, 0.8], yLabel: 'Center + cross macro-F1' });
  const order = ['retinaradar_region', 'imagenet_resnet50_region', 'handcrafted_region', 'random_resnet50_region'];
  const colors = [C.rose, C.orange, C.olive, C.pale];
  const values = order.map((key) => enc[key].cross.macro_f1);
  for (let i = 0; i < values.length; i += 1) {
    const bx = A.sx(i) - 57, by = A.sy(values[i]), bottom = A.sy(0);
    svg.push(rect(bx, by, 114, bottom - by, { fill: colors[i], stroke: C.ink, width: 1.0, rx: 2 }));
    svg.push(t(A.sx(i), by - 12, n(values[i]), { size: 17, anchor: 'middle', bold: true }));
  }

  const B = makePanel(svg, { x: 1130, y: 180, w: 720, h: 320, letter: 'B', title: 'Aggregation operator', xDomain: [-0.55, 2.55], yDomain: [0.70, 0.88], xTicks: [{ value: 0, label: 'Mean' }, { value: 1, label: 'Max' }, { value: 2, label: 'Attention' }], yTicks: [0.70, 0.75, 0.80, 0.85], yLabel: 'Macro-F1' });
  const pools = ['mean', 'max', 'attention'];
  for (let j = 0; j < 3; j += 1) {
    const view = ['full', 'center', 'cross'][j];
    const color = VIEW[j];
    for (let i = 0; i < pools.length; i += 1) {
      const value = abl.pooling[pools[i]][view].macro_f1;
      const cx = B.sx(i) + (j - 1) * 48, by = B.sy(value), bottom = B.sy(0.70);
      svg.push(rect(cx - 21, by, 42, bottom - by, { fill: color, stroke: C.ink, width: 0.8, rx: 1.5 }));
    }
  }
  svg.push(legendItem(B.x + 12, B.y + 31, C.brown, 'Full', 'bar', { size: 16 }));
  svg.push(legendItem(B.x + 155, B.y + 31, C.orange, 'Center', 'bar', { size: 16 }));
  svg.push(legendItem(B.x + 317, B.y + 31, C.olive, 'Center + cross', 'bar', { size: 16 }));

  const Cpanel = makePanel(svg, { x: 150, y: 700, w: 720, h: 320, letter: 'C', title: 'Training mask-ratio sensitivity', xDomain: [-0.03, 0.63], yDomain: [0.77, 0.88], xTicks: [0, 0.15, 0.30, 0.45, 0.60], yTicks: [0.78, 0.80, 0.82, 0.84, 0.86, 0.88], yLabel: 'Macro-F1', xLabel: 'Random region mask ratio' });
  const ratios = [0, 0.15, 0.30, 0.45, 0.60];
  const markers = ['circle', 'square', 'triangle'];
  for (let j = 0; j < 3; j += 1) {
    const view = ['full', 'center', 'cross'][j];
    const points = ratios.map((ratio) => [Cpanel.sx(ratio), Cpanel.sy(abl.mask_ratio[String(ratio) === '0' ? '0' : String(ratio)][view].macro_f1)]);
    svg.push(polyline(points, { stroke: VIEW[j], width: 2.35 }));
    for (const [xx, yy] of points) {
      if (markers[j] === 'circle') svg.push(circle(xx, yy, 4.7, { fill: VIEW[j], stroke: C.paper, width: 1.1 }));
      if (markers[j] === 'square') svg.push(square(xx, yy, 9, { fill: VIEW[j], stroke: C.paper, width: 1.1 }));
      if (markers[j] === 'triangle') svg.push(triangle(xx, yy, 5.4, { fill: VIEW[j], stroke: C.paper, width: 1.1 }));
    }
  }
  const refX = Cpanel.sx(0.30);
  svg.push(line(refX, Cpanel.y, refX, Cpanel.y + Cpanel.h, { stroke: C.rose, width: 1.35, dash: '5 5' }));
  svg.push(rect(refX + 8, Cpanel.y + Cpanel.h - 32, 166, 25, { fill: C.paper, stroke: 'none', rx: 3 }));
  svg.push(t(refX + 15, Cpanel.y + Cpanel.h - 14, 'Reference ratio 0.30', { size: 15, fill: C.rose }));
  svg.push(legendItem(Cpanel.x + 310, Cpanel.y + 31, C.brown, 'Full', 'line', { size: 16 }));
  svg.push(legendItem(Cpanel.x + 420, Cpanel.y + 31, C.orange, 'Center', 'line', { size: 16 }));
  svg.push(legendItem(Cpanel.x + 555, Cpanel.y + 31, C.olive, 'Center + cross', 'line', { size: 16 }));

  const D = makePanel(svg, { x: 1130, y: 700, w: 720, h: 320, letter: 'D', title: 'Five-seed paired bootstrap: 4×4 minus 3×3', xDomain: [-0.075, 0.09], yDomain: [-0.5, 4.5], xTicks: [-0.06, -0.03, 0, 0.03, 0.06, 0.09], yTicks: [], yLabel: '', xLabel: 'Paired Δ macro-F1 (4×4 − 3×3)', grid: 'x' });
  noDiff(svg, D, 0);
  const rows = pair.filter((row) => row.view === 'cross');
  for (let i = 0; i < rows.length; i += 1) {
    const rec = rows[i].delta_4x4_minus_3x3.macro_f1;
    const yy = D.sy(i), xx = D.sx(rec.mean);
    svg.push(errorH(yy, xx, D.sx(rec.ci95[0]), D.sx(rec.ci95[1]), C.orange));
    svg.push(circle(xx, yy, 5.0, { fill: C.brown, stroke: C.paper, width: 1.2 }));
    svg.push(t(D.x - 15, yy + 6, `Seed ${rows[i].seed}`, { size: 17, anchor: 'end', fill: C.muted }));
  }
  svg.push(rect(D.x + D.w - 216, D.y + D.h - 41, 203, 27, { fill: C.pale, stroke: 'none', rx: 4 }));
  svg.push(t(D.x + D.w - 114, D.y + D.h - 21, 'All 95% CIs cross zero', { size: 15, anchor: 'middle', fill: C.umber }));
  await saveSvg('Figure4_Ablations_RMB20_v3_large_font', W, H, svg);
}

function heatColor(value, min, max, stops) {
  const tval = clamp((value - min) / (max - min), 0, 1);
  const index = Math.min(stops.length - 2, Math.floor(tval * (stops.length - 1)));
  const frac = tval * (stops.length - 1) - index;
  const hexToRgb = (hex) => [parseInt(hex.slice(1, 3), 16), parseInt(hex.slice(3, 5), 16), parseInt(hex.slice(5, 7), 16)];
  const rgb = (a, b) => `#${a.map((v, i) => Math.round(v + (b[i] - v) * frac).toString(16).padStart(2, '0')).join('')}`;
  return rgb(hexToRgb(stops[index]), hexToRgb(stops[index + 1]));
}
function heatmap(svg, x, y, size, matrix, cfg) {
  const cell = size / 3;
  for (let r = 0; r < 3; r += 1) for (let c = 0; c < 3; c += 1) {
    const value = matrix[r][c];
    const fill = heatColor(value, cfg.min, cfg.max, cfg.stops);
    svg.push(rect(x + c * cell, y + r * cell, cell, cell, { fill, stroke: C.paper, width: 2 }));
    const intensity = clamp((value - cfg.min) / (cfg.max - cfg.min), 0, 1);
    svg.push(t(x + c * cell + cell / 2, y + r * cell + cell / 2 + 6, cfg.format(value), { size: cfg.fontSize ?? 18, anchor: 'middle', fill: intensity > 0.58 ? C.white : C.ink, bold: true }));
  }
  svg.push(rect(x, y, size, size, { fill: 'none', stroke: C.brown, width: 1.0 }));
}

async function figure5() {
  const occ = await json('exp39_attention_occlusion_validation');
  const rows = occ.rows;
  const W = 2000, H = 1160, svg = [];
  svg.push(t(1000, 67, 'Attention is assessed against a controlled intervention, not treated as explanation by itself', { size: 31, bold: true, fill: C.brown, anchor: 'middle' }));
  const A = simplePanel(svg, { x: 150, y: 180, w: 720, h: 320, letter: 'A', title: 'Mean learned regional attention' });
  const att = Array.from({ length: 3 }, (_, r) => Array.from({ length: 3 }, (_, c) => rows[r * 3 + c].mean_attention));
  heatmap(svg, A.x + 115, A.y + 22, 250, att, { min: 0, max: 0.42, stops: [C.pale, C.orange, C.rose, C.brown], format: (v) => n(v), fontSize: 18 });
  ['Left', 'Center', 'Right'].forEach((label, idx) => svg.push(t(A.x + 115 + 42 + idx * 83, A.y + 311, label, { size: 16, anchor: 'middle', fill: C.muted })));
  svg.push(t(A.x + 98, A.y + 99, 'Superior', { size: 16, anchor: 'end', fill: C.muted }));
  svg.push(t(A.x + 98, A.y + 181, 'Middle', { size: 16, anchor: 'end', fill: C.muted }));
  svg.push(t(A.x + 98, A.y + 264, 'Inferior', { size: 16, anchor: 'end', fill: C.muted }));
  svg.push(line(A.x + 430, A.y + 34, A.x + 430, A.y + 262, { stroke: C.grid, width: 16 }));
  for (let s = 0; s < 8; s += 1) svg.push(line(A.x + 430, A.y + 34 + (228 / 7) * s, A.x + 430, A.y + 34 + (228 / 7) * (s + 1), { stroke: heatColor((7 - s) / 7, 0, 1, [C.pale, C.orange, C.rose, C.brown]), width: 16 }));
  svg.push(t(A.x + 455, A.y + 51, '0.42', { size: 15, fill: C.muted }));
  svg.push(t(A.x + 455, A.y + 262, '0.00', { size: 15, fill: C.muted }));
  svg.push(t(A.x + 535, A.y + 150, 'Attention weight', { size: 15, anchor: 'middle', rotate: -90, fill: C.muted }));

  const B = simplePanel(svg, { x: 1130, y: 180, w: 720, h: 320, letter: 'B', title: 'One-region occlusion loss' });
  const drop = Array.from({ length: 3 }, (_, r) => Array.from({ length: 3 }, (_, c) => rows[r * 3 + c].performance_drop_macro_f1));
  heatmap(svg, B.x + 115, B.y + 22, 250, drop, { min: -0.065, max: 0.065, stops: [C.olive, C.paper, C.rose], format: (v) => `${v >= 0 ? '+' : ''}${n(v)}`, fontSize: 18 });
  svg.push(t(B.x + 98, B.y + 99, 'Superior', { size: 16, anchor: 'end', fill: C.muted }));
  svg.push(t(B.x + 98, B.y + 181, 'Middle', { size: 16, anchor: 'end', fill: C.muted }));
  svg.push(t(B.x + 98, B.y + 264, 'Inferior', { size: 16, anchor: 'end', fill: C.muted }));
  ['Left', 'Center', 'Right'].forEach((label, idx) => svg.push(t(B.x + 115 + 42 + idx * 83, B.y + 311, label, { size: 16, anchor: 'middle', fill: C.muted })));
  svg.push(line(B.x + 430, B.y + 34, B.x + 430, B.y + 262, { stroke: C.grid, width: 16 }));
  for (let s = 0; s < 8; s += 1) svg.push(line(B.x + 430, B.y + 34 + (228 / 7) * s, B.x + 430, B.y + 34 + (228 / 7) * (s + 1), { stroke: heatColor((7 - s) / 7, 0, 1, [C.olive, C.paper, C.rose]), width: 16 }));
  svg.push(t(B.x + 455, B.y + 51, '+0.065', { size: 15, fill: C.muted }));
  svg.push(t(B.x + 455, B.y + 154, '0', { size: 15, fill: C.muted }));
  svg.push(t(B.x + 455, B.y + 262, '−0.065', { size: 15, fill: C.muted }));
  svg.push(t(B.x + 535, B.y + 150, 'Macro-F1 loss', { size: 15, anchor: 'middle', rotate: -90, fill: C.muted }));

  const Cpanel = makePanel(svg, { x: 150, y: 700, w: 720, h: 320, letter: 'C', title: 'Attention versus occlusion loss', xDomain: [0, 0.44], yDomain: [-0.012, 0.07], xTicks: [0, 0.1, 0.2, 0.3, 0.4], yTicks: [0, 0.02, 0.04, 0.06], yLabel: 'Macro-F1 loss after occlusion', xLabel: 'Mean attention weight' });
  const xs = rows.map((r) => r.mean_attention), ys = rows.map((r) => r.performance_drop_macro_f1);
  const meanX = xs.reduce((a, b) => a + b, 0) / xs.length, meanY = ys.reduce((a, b) => a + b, 0) / ys.length;
  const beta = xs.reduce((s, v, i) => s + (v - meanX) * (ys[i] - meanY), 0) / xs.reduce((s, v) => s + (v - meanX) ** 2, 0);
  const alpha = meanY - beta * meanX;
  svg.push(line(Cpanel.sx(0), Cpanel.sy(alpha), Cpanel.sx(0.44), Cpanel.sy(alpha + beta * 0.44), { stroke: C.rose, width: 2.6 }));
  rows.forEach((row) => {
    svg.push(circle(Cpanel.sx(row.mean_attention), Cpanel.sy(row.performance_drop_macro_f1), 6.3, { fill: C.orange, stroke: C.brown, width: 1.2 }));
  });
  const center = rows.find((row) => row.region === 4);
  const cx = Cpanel.sx(center.mean_attention), cy = Cpanel.sy(center.performance_drop_macro_f1);
  svg.push(circle(cx, cy, 8.2, { fill: C.orange, stroke: C.rose, width: 2.6 }));
  svg.push(circle(Cpanel.x + Cpanel.w - 210, Cpanel.y - 15, 6.0, { fill: C.orange, stroke: C.rose, width: 2.2 }));
  svg.push(t(Cpanel.x + Cpanel.w - 194, Cpanel.y - 9, 'Middle-center region', { size: 15.5, fill: C.umber }));
  svg.push(rect(Cpanel.x + 12, Cpanel.y + 12, 292, 76, { fill: C.pale, stroke: C.grid, width: 1, rx: 6 }));
  svg.push(multiText(Cpanel.x + 28, Cpanel.y + 36, [`Spearman ρ = ${n(occ.attention_occlusion_spearman.rho, 2)}`, `p = ${n(occ.attention_occlusion_spearman.p_value, 3)}; n = 9 regions`], { size: 16, anchor: 'start', fill: C.ink, lineHeight: 19 }));

  const D = simplePanel(svg, { x: 1130, y: 700, w: 720, h: 320, letter: 'D', title: 'Attention stratified by true DR class' });
  const csv = await fs.readFile(path.join(EXP, 'exp30_deep_region_attention', 'attention_test.csv'), 'utf8');
  const lines = csv.trim().split(/\r?\n/), headers = lines[0].split(',');
  const byClass = { 0: [], 1: [], 2: [] };
  for (const raw of lines.slice(1)) {
    const fields = raw.split(',');
    const rec = Object.fromEntries(headers.map((key, idx) => [key, fields[idx]]));
    if (rec.model === 'deep_attention_mask_augmented') byClass[Number(rec.true_label)].push(Array.from({ length: 9 }, (_, i) => Number(rec[`attention_region_${i}`])));
  }
  ['Normal', 'NPDR', 'PDR'].forEach((name, idx) => {
    const vals = byClass[idx];
    const matrix = Array.from({ length: 3 }, (_, r) => Array.from({ length: 3 }, (_, c) => vals.reduce((s, arr) => s + arr[r * 3 + c], 0) / vals.length));
    const hx = D.x + 44 + idx * 225, hy = D.y + 50;
    svg.push(t(hx + 84, hy - 15, name, { size: 18, anchor: 'middle', bold: true, fill: C.umber }));
    heatmap(svg, hx, hy, 168, matrix, { min: 0, max: 0.42, stops: [C.pale, C.orange, C.rose, C.brown], format: (v) => n(v, 2), fontSize: 14 });
  });
  svg.push(t(D.x + D.w / 2, D.y + D.h - 20, 'Held-out images; class labels are used only for stratified visualization.', { size: 15.5, anchor: 'middle', fill: C.umber }));
  await saveSvg('Figure5_Attention_Occlusion_RMB20_v6_callout_fixed', W, H, svg);
}

async function figure6() {
  const internal = (await json('exp36_multiseed_deep_region')).aggregate;
  const externalAll = await json('exp53_mmrdr_uwf_external_fov');
  const external = externalAll.summary;
  const boot = (await json('exp54_mmrdr_paired_bootstrap')).per_seed;
  const W = 2000, H = 1160, svg = [];
  svg.push(t(1000, 67, 'Independent same-modality UWF evaluation: topology ordering persists under domain shift', { size: 31, bold: true, fill: C.brown, anchor: 'middle' }));
  const labels = ['Full', 'Center', ['Center +', 'cross']];
  const internalViews = ['full', 'center', 'cross'], externalViews = ['full', 'center', 'center_plus_cross'];
  const A = makePanel(svg, { x: 150, y: 180, w: 720, h: 320, letter: 'A', title: 'Internal and external UWF performance', xDomain: [-0.55, 2.55], yDomain: [0.52, 0.88], xTicks: labels.map((label, idx) => ({ value: idx, label })), yTicks: [0.55, 0.65, 0.75, 0.85], yLabel: 'Macro-F1' });
  for (let i = 0; i < 3; i += 1) {
    const bars = [
      { x: A.sx(i) - 94, rec: internal[internalViews[i]].macro_f1, fill: C.orange },
      { x: A.sx(i) + 8, rec: external[externalViews[i]].macro_f1, fill: C.olive },
    ];
    for (const bar of bars) {
      const yy = A.sy(bar.rec.mean), bottom = A.sy(0.52);
      svg.push(rect(bar.x, yy, 86, bottom - yy, { fill: bar.fill, stroke: C.ink, width: 0.9, rx: 2 }));
      svg.push(errorV(bar.x + 43, yy, A.sy(bar.rec.mean + bar.rec.std), A.sy(bar.rec.mean - bar.rec.std), bar.fill));
    }
  }
  svg.push(legendItem(A.x + 12, A.y - 7, C.orange, 'UWF-DR internal', 'bar', { size: 16 }));
  svg.push(legendItem(A.x + 262, A.y - 7, C.olive, 'MMRDR-UWF external', 'bar', { size: 16 }));

  const B = makePanel(svg, { x: 1130, y: 180, w: 720, h: 320, letter: 'B', title: 'External error burden by view', xDomain: [-0.5, 1.5], yDomain: [0, 0.48], xTicks: [{ value: 0, label: ['Severity', 'MAE'] }, { value: 1, label: 'Underestimation' }], yTicks: [0, 0.1, 0.2, 0.3, 0.4], yLabel: 'Error metric' });
  for (let viewIdx = 0; viewIdx < 3; viewIdx += 1) {
    const rec = external[externalViews[viewIdx]];
    const values = [rec.severity_mae, rec.underestimation_rate];
    for (let metricIdx = 0; metricIdx < 2; metricIdx += 1) {
      const cx = B.sx(metricIdx) + (viewIdx - 1) * 58, yy = B.sy(values[metricIdx].mean), bottom = B.sy(0);
      svg.push(rect(cx - 25, yy, 50, bottom - yy, { fill: VIEW[viewIdx], stroke: C.ink, width: 0.8, rx: 1.5 }));
      svg.push(errorV(cx, yy, B.sy(values[metricIdx].mean + values[metricIdx].std), B.sy(values[metricIdx].mean - values[metricIdx].std), VIEW[viewIdx]));
    }
  }
  svg.push(legendItem(B.x + 10, B.y - 7, C.brown, 'Full', 'bar', { size: 16 }));
  svg.push(legendItem(B.x + 154, B.y - 7, C.orange, 'Center', 'bar', { size: 16 }));
  svg.push(legendItem(B.x + 320, B.y - 7, C.olive, 'Center + cross', 'bar', { size: 16 }));

  const Cpanel = makePanel(svg, { x: 220, y: 700, w: 650, h: 320, letter: 'C', title: 'Paired external Δ macro-F1 versus full view', xDomain: [-0.055, 0.055], yDomain: [-0.5, 9.5], xTicks: [-0.05, -0.025, 0, 0.025, 0.05], yTicks: [], xLabel: 'Paired Δ macro-F1', grid: 'x' });
  svg.push(line(Cpanel.sx(0), Cpanel.y, Cpanel.sx(0), Cpanel.y + Cpanel.h, { stroke: C.reference, width: 1.4, dash: '5 5' }));
  let p = 0;
  for (const record of boot) {
    for (const [view, label, color] of [['center', 'Center', C.umber], ['center_plus_cross', 'Center + cross', C.olive]]) {
      const rec = record.bootstrap.paired_delta_vs_full[view].macro_f1;
      const yy = Cpanel.sy(p), xx = Cpanel.sx(rec.estimate);
      const lowX = clamp(Cpanel.sx(rec.ci95[0]), Cpanel.x + 7, Cpanel.x + Cpanel.w - 7);
      const highX = clamp(Cpanel.sx(rec.ci95[1]), Cpanel.x + 7, Cpanel.x + Cpanel.w - 7);
      svg.push(errorH(yy, xx, lowX, highX, color));
      svg.push(circle(xx, yy, 4.8, { fill: color, stroke: C.paper, width: 1 }));
      svg.push(t(Cpanel.x - 14, yy + 6, `S${record.seed} · ${label === 'Center + cross' ? 'Cross' : 'Center'}`, { size: 15.5, anchor: 'end', fill: C.muted }));
      p += 1;
    }
  }

  const D = makePanel(svg, { x: 1130, y: 700, w: 720, h: 320, letter: 'D', title: 'Exploratory external quality-proxy strata', xDomain: [-0.2, 1.2], yDomain: [0.53, 0.65], xTicks: [{ value: 0, label: ['Lowest proxy', 'quartile'] }, { value: 1, label: ['Highest proxy', 'quartile'] }], yTicks: [0.54, 0.57, 0.60, 0.63], yLabel: 'Full-view macro-F1' });
  externalAll.records.forEach((record) => {
    const q = record.views.full.quality_proxy_quartiles;
    const left = q.lowest.macro_f1, right = q.highest.macro_f1;
    svg.push(line(D.sx(0), D.sy(left), D.sx(1), D.sy(right), { stroke: C.lightLine, width: 1.8 }));
    svg.push(circle(D.sx(0), D.sy(left), 5.4, { fill: C.umber, stroke: C.brown, width: 1 }));
    svg.push(circle(D.sx(1), D.sy(right), 5.4, { fill: C.olive, stroke: C.brown, width: 1 }));
  });
  svg.push(legendItem(D.x + 14, D.y + D.h - 14, C.umber, 'Lowest', 'dot', { size: 15 }));
  svg.push(legendItem(D.x + 140, D.y + D.h - 14, C.olive, 'Highest', 'dot', { size: 15 }));
  svg.push(t(D.x + D.w / 2, D.y + 24, 'Unlabeled coverage / contrast / sharpness proxy', { size: 15.5, anchor: 'middle', fill: C.umber }));
  await saveSvg('Figure6_External_Replication_RMB20_v4_overlap_fixed', W, H, svg);
}

async function figure7() {
  const fixed = await json('exp40_final_region_selective_risk');
  const nested = await json('exp47_nested_risk_calibration');
  const W = 2000, H = 1160, svg = [];
  svg.push(t(1000, 67, 'Paired-view underestimation audit: useful ranking, but unstable threshold transport', { size: 31, bold: true, fill: C.brown, anchor: 'middle' }));
  const A = makePanel(svg, { x: 150, y: 180, w: 720, h: 320, letter: 'A', title: 'Risk ranking under distinct protocols', xDomain: [-0.55, 3.55], yDomain: [0.45, 0.80], xTicks: [{ value: 0, label: ['Paired risk', 'head'] }, { value: 1, label: ['Severity', 'gap'] }, { value: 2, label: ['Symmetric', 'KL'] }, { value: 3, label: ['Nested grouped', 'risk head'] }], yTicks: [0.45, 0.50, 0.60, 0.70, 0.80], yLabel: 'AUROC' });
  const rankVals = [fixed.risk_head.test.auroc, fixed.direct_scores.severity_gap.test.auroc, fixed.direct_scores.student_teacher_kl.test.auroc, nested.aggregate.risk_auroc.mean];
  const rankErrs = [0, 0, 0, nested.aggregate.risk_auroc.std];
  const rankColors = [C.rose, C.orange, C.paleOlive, C.olive];
  const chanceY = A.sy(0.5);
  svg.push(line(A.x, chanceY, A.x + A.w, chanceY, { stroke: C.reference, width: 1.3, dash: '5 5' }));
  for (let i = 0; i < rankVals.length; i += 1) {
    const bx = A.sx(i) - 56, yy = A.sy(rankVals[i]), bottom = A.sy(0.45);
    svg.push(rect(bx, yy, 112, bottom - yy, { fill: rankColors[i], stroke: C.ink, width: 0.9, rx: 2 }));
    if (rankErrs[i]) svg.push(errorV(A.sx(i), yy, A.sy(rankVals[i] + rankErrs[i]), A.sy(rankVals[i] - rankErrs[i]), rankColors[i]));
    svg.push(t(A.sx(i), A.sy(rankVals[i] + rankErrs[i]) - 11, n(rankVals[i]), { size: 17, anchor: 'middle', bold: true }));
  }

  const B = makePanel(svg, { x: 1130, y: 180, w: 720, h: 320, letter: 'B', title: 'Exploratory fixed-split coverage', xDomain: [0.04, 0.21], yDomain: [0.20, 1.08], xTicks: [{ value: 0.05, label: '5%' }, { value: 0.10, label: '10%' }, { value: 0.20, label: '20%' }], yTicks: [0.20, 0.40, 0.60, 0.80, 1.00], yLabel: 'Accepted coverage', xLabel: 'Nominal underestimation-risk target' });
  const targets = [0.05, 0.10, 0.20], fixedKeys = ['0.05', '0.1', '0.2'];
  const cover = fixedKeys.map((key) => fixed.selective[key].test.coverage);
  const coverPoints = targets.map((target, i) => [B.sx(target), B.sy(cover[i])]);
  svg.push(polyline(coverPoints, { stroke: C.rose, width: 2.8 }));
  coverPoints.forEach(([xx, yy], i) => {
    svg.push(circle(xx, yy, 6, { fill: C.rose, stroke: C.paper, width: 1.2 }));
    svg.push(t(xx, yy - 13, n(cover[i]), { size: 17, anchor: 'middle', bold: true, fill: C.rose }));
  });
  svg.push(rect(B.x + 12, B.y + B.h - 68, 410, 53, { fill: C.pale, stroke: 'none', rx: 5 }));
  svg.push(multiText(B.x + 23, B.y + B.h - 45, ['Shared validation predictions were used for risk fitting', 'and threshold selection; this panel is exploratory.'], { size: 15, anchor: 'start', fill: C.umber, lineHeight: 17 }));

  const Cpanel = makePanel(svg, { x: 150, y: 700, w: 720, h: 320, letter: 'C', title: 'Nested grouped threshold transport', xDomain: [0.04, 0.21], yDomain: [0, 0.22], xTicks: [{ value: 0.05, label: '5%' }, { value: 0.10, label: '10%' }, { value: 0.20, label: '20%' }], yTicks: [0, 0.05, 0.10, 0.15, 0.20], yLabel: 'Observed accepted risk', xLabel: 'Nominal underestimation-risk target' });
  svg.push(line(Cpanel.sx(0.04), Cpanel.sy(0.04), Cpanel.sx(0.21), Cpanel.sy(0.21), { stroke: C.reference, width: 1.3, dash: '5 5' }));
  svg.push(t(Cpanel.sx(0.205), Cpanel.sy(0.205) - 8, 'Observed = target', { size: 14, anchor: 'end', fill: C.reference }));
  const nestedKeys = ['target_0.05', 'target_0.10', 'target_0.20'];
  const nRisk = nestedKeys.map((key) => nested.aggregate[key].test_accepted_risk.mean);
  const nErr = nestedKeys.map((key) => nested.aggregate[key].test_accepted_risk.std);
  const nPoints = targets.map((target, i) => [Cpanel.sx(target), Cpanel.sy(nRisk[i])]);
  svg.push(polyline(nPoints, { stroke: C.olive, width: 2.8 }));
  nPoints.forEach(([xx, yy], i) => {
    svg.push(errorV(xx, yy, Cpanel.sy(nRisk[i] + nErr[i]), Cpanel.sy(nRisk[i] - nErr[i]), C.olive));
    svg.push(square(xx, yy, 10.5, { fill: C.olive, stroke: C.paper, width: 1.2 }));
  });
  svg.push(legendItem(Cpanel.x + 18, Cpanel.y + 28, C.olive, 'Nested grouped', 'line', { size: 16 }));

  const D = makePanel(svg, { x: 1130, y: 700, w: 720, h: 320, letter: 'D', title: 'Nested outer-fold coverage–risk points', xDomain: [0.30, 1.03], yDomain: [0, 0.18], xTicks: [0.4, 0.6, 0.8, 1.0], yTicks: [0, 0.05, 0.10, 0.15], yLabel: 'Observed accepted risk', xLabel: 'Accepted coverage' });
  const markers = { '0.05': 'circle', '0.10': 'square', '0.20': 'triangle' }, colors = { '0.05': C.rose, '0.10': C.orange, '0.20': C.olive };
  nested.folds.forEach((fold) => ['0.05', '0.10', '0.20'].forEach((target) => {
    const rec = fold.selective[target], xx = D.sx(rec.test_coverage), yy = D.sy(rec.test_accepted_risk), color = colors[target];
    if (markers[target] === 'circle') svg.push(circle(xx, yy, 5.8, { fill: color, stroke: C.brown, width: 0.8 }));
    if (markers[target] === 'square') svg.push(square(xx, yy, 11, { fill: color, stroke: C.brown, width: 0.8 }));
    if (markers[target] === 'triangle') svg.push(triangle(xx, yy, 6.4, { fill: color, stroke: C.brown, width: 0.8 }));
  }));
  svg.push(legendItem(D.x + 12, D.y + 30, C.rose, 'Target 5%', 'dot', { size: 16 }));
  svg.push(legendItem(D.x + 180, D.y + 30, C.orange, 'Target 10%', 'bar', { size: 16 }));
  svg.push(legendItem(D.x + 365, D.y + 30, C.olive, 'Target 20%', 'dot', { size: 16 }));
  await saveSvg('Figure7_Selective_Risk_RMB20_v3_large_font', W, H, svg);
}

async function figure8() {
  const result = await json('exp60_pixel_aperture_training');
  const base = result.variants.baseline.aggregate.pixel;
  const augmented = result.variants.pixel_augmented.aggregate.pixel;
  const W = 2000, H = 900, svg = [];
  svg.push(t(1000, 58, 'Pixel-aperture training improves F1 and MAE; underestimation changes are aperture-specific', { size: 29, bold: true, fill: C.brown, anchor: 'middle' }));
  svg.push(legendItem(672, 102, C.olive, 'Protocol-matched baseline', 'bar', { size: 17 }));
  svg.push(legendItem(1010, 102, C.rose, 'Pixel-aperture training', 'bar', { size: 17 }));
  const scenarios = ['rect_center_0.35', 'rect_center_0.55', 'rect_center_0.75', 'circle_center_0.55'];
  const xLabels = [['Rect.', '0.35'], ['Rect.', '0.55'], ['Rect.', '0.75'], ['Circle', '0.55']];
  const configs = [
    { letter: 'A', title: 'Held-out macro-F1', metric: 'macro_f1', ylabel: 'Macro-F1', domain: [0.35, 0.88], ticks: [0.40, 0.50, 0.60, 0.70, 0.80], x: 115 },
    { letter: 'B', title: 'Held-out ordinal error', metric: 'severity_mae', ylabel: 'Severity MAE', domain: [0.12, 0.58], ticks: [0.15, 0.25, 0.35, 0.45, 0.55], x: 740 },
    { letter: 'C', title: 'Held-out underestimation', metric: 'underestimation_rate', ylabel: 'Underestimation rate', domain: [0, 0.40], ticks: [0, 0.10, 0.20, 0.30, 0.40], x: 1365 },
  ];
  for (const cfg of configs) {
    const P = makePanel(svg, { x: cfg.x, y: 175, w: 510, h: 400, letter: cfg.letter, title: cfg.title, xDomain: [-0.6, 3.6], yDomain: cfg.domain, xTicks: xLabels.map((label, idx) => ({ value: idx, label })), yTicks: cfg.ticks, yLabel: cfg.ylabel });
    for (let i = 0; i < scenarios.length; i += 1) {
      const b = base[scenarios[i]][cfg.metric], a = augmented[scenarios[i]][cfg.metric];
      const leftX = P.sx(i) - 57, rightX = P.sx(i) + 5, bw = 52, bottom = P.sy(cfg.domain[0]);
      const by = P.sy(b.mean), ay = P.sy(a.mean);
      svg.push(rect(leftX, by, bw, bottom - by, { fill: C.olive, stroke: C.ink, width: 0.8, rx: 1.5 }));
      svg.push(rect(rightX, ay, bw, bottom - ay, { fill: C.rose, stroke: C.ink, width: 0.8, rx: 1.5 }));
      svg.push(errorV(leftX + bw / 2, by, P.sy(b.mean + b.std), P.sy(b.mean - b.std), C.olive));
      svg.push(errorV(rightX + bw / 2, ay, P.sy(a.mean + a.std), P.sy(a.mean - a.std), C.rose));
      const cue = cfg.metric === 'underestimation_rate' ? 'under' : (cfg.metric === 'severity_mae' ? 'mae' : 'f1');
      const delta = a.mean - b.mean, fill = valueStyle(cue, delta);
      svg.push(t(P.sx(i), P.y + P.h + 75, `Δ ${delta >= 0 ? '+' : ''}${n(delta)}`, { size: 17, anchor: 'middle', bold: true, fill }));
    }
    svg.push(t(P.x + P.w / 2, P.y + P.h + 106, 'Augmented − baseline', { size: 15.5, anchor: 'middle', fill: C.umber }));
  }
  await saveSvg('Figure8_Continuous_Aperture_Optimization_RMB20_v3_large_font', W, H, svg);
}

async function main() {
  await fs.mkdir(OUT, { recursive: true });
  await figure3();
  await figure4();
  await figure5();
  await figure6();
  await figure7();
  await figure8();
  console.log(`Created corrected figures in ${OUT}`);
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
