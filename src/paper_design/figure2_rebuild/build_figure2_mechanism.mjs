import fs from "node:fs/promises";
import path from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const BUILD = "/Users/tongyue/Documents/77f /7hao/paper_design/figure2_rebuild";
const FINAL_PPTX = "/Users/tongyue/Documents/ppf/第四论文/图2_算法机制重绘版_LaTeX公式版.pptx";
const PREVIEW = path.join(BUILD, "figure2-mechanism-preview.png");
const LAYOUT = path.join(BUILD, "figure2-mechanism.layout.json");
const FORMULA_DIR = path.join(BUILD, "latex-formulas-mechanism");
const FULL_IMAGE = "/Users/tongyue/Documents/77f /7hao/paper_design/ppt_build/figure1_algorithm_revision/template-inspect/assets/ppt/media/image1.png";

const W = 1600;
const H = 900;
const FONT = "Times New Roman";
// Every equation is produced from the same LaTeX scale.  Individual frames are
// deliberately sized so this ceiling is reached instead of shrinking formulas
// to squeeze them into cramped cards.
const MATH_SCALE = 1.55;
const C = {
  ink: "#332720", brown: "#704C2B", rust: "#965E4A", orange: "#D0913C", orangePale: "#F7E7D4",
  green: "#8B9A7C", greenPale: "#EFF3EA", magenta: "#C14F75", magentaPale: "#FAEEF3",
  cream: "#FFFDFC", divider: "#D9CBBE", gray: "#6E625A", black: "#1C1714",
};
const latexSources = [];

async function writeBlob(filePath, blob) {
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

async function readBytes(filePath) {
  const bytes = await fs.readFile(filePath);
  return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
}

function box(slide, name, x, y, w, h, fill = "none", line = { style: "solid", fill: "none", width: 0 }, radius = 0) {
  return slide.shapes.add({ geometry: radius ? "roundRect" : "rect", name, position: { left: x, top: y, width: w, height: h }, fill, line, borderRadius: radius || undefined });
}

function text(slide, name, value, x, y, w, h, options = {}) {
  const shape = box(slide, name, x, y, w, h, "none");
  shape.text = value;
  shape.text.style = {
    typeface: options.typeface ?? FONT, fontSize: options.size ?? 17, color: options.color ?? C.ink,
    bold: options.bold ?? false, italic: options.italic ?? false, alignment: options.align ?? "left",
    verticalAlignment: options.valign ?? "middle", lineSpacing: options.lineSpacing ?? 0.92,
    insets: options.insets ?? { top: 0, right: 0, bottom: 0, left: 0 }, autoFit: "none", wrap: "square",
  };
  return shape;
}

function panelHeader(slide, letter, title, x, y, w, accent) {
  box(slide, `panel-${letter}-strip`, x, y, 44, 30, accent, { style: "solid", fill: accent, width: 0 }, 10);
  text(slide, `panel-${letter}-label`, letter, x, y + 1, 44, 28, { size: 16, color: C.cream, align: "center", bold: true });
  text(slide, `panel-${letter}-title`, title, x + 54, y - 1, w - 54, 32, { size: 22, color: C.ink, bold: true });
  box(slide, `panel-${letter}-rule`, x, y + 39, w, 1, accent, { style: "solid", fill: accent, width: 0 });
}

function arrow(slide, name, x, y, w = 18, h = 18, color = C.brown) {
  return slide.shapes.add({ geometry: "rightArrow", name, position: { left: x, top: y, width: w, height: h }, fill: color, line: { style: "solid", fill: color, width: 0 } });
}

function downArrow(slide, name, x, y, h = 20, color = C.green) {
  return slide.shapes.add({ geometry: "downArrow", name, position: { left: x, top: y, width: 18, height: h }, fill: color, line: { style: "solid", fill: color, width: 0 } });
}

function imageFrame(slide, name, bytes, alt, x, y, w, h, stroke = C.brown, crop) {
  box(slide, `${name}-border`, x - 2, y - 2, w + 4, h + 4, C.cream, { style: "solid", fill: stroke, width: 1 }, 6);
  return slide.images.add({
    blob: bytes, contentType: "image/png", alt, fit: crop ? "cover" : "contain", ...(crop ? { crop } : {}),
    position: { left: x, top: y, width: w, height: h }, geometry: "rect",
  });
}

function grid(slide, name, x, y, w, h) {
  [x + w / 3, x + (2 * w) / 3].forEach((gx, i) => box(slide, `${name}-v-${i}`, gx, y, 1.3, h, "#FFFFFF", { style: "solid", fill: "#FFFFFF", width: 0 }));
  [y + h / 3, y + (2 * h) / 3].forEach((gy, i) => box(slide, `${name}-h-${i}`, x, gy, w, 1.3, "#FFFFFF", { style: "solid", fill: "#FFFFFF", width: 0 }));
}

function maskGrid(slide, name, x, y, size, mode, accent) {
  const cell = size / 3;
  const visible = new Set(mode === "center" ? [4] : mode === "cross" ? [1, 3, 4, 5, 7] : [0, 1, 2, 3, 4, 5, 6, 7, 8]);
  for (let i = 0; i < 9; i += 1) {
    const row = Math.floor(i / 3);
    const col = i % 3;
    const fill = visible.has(i) ? `${accent}/85` : "#1C1714/35";
    box(slide, `${name}-${i}`, x + col * cell, y + row * cell, cell - 1.2, cell - 1.2, fill, { style: "solid", fill: C.cream, width: 0.4 }, 1);
  }
}

async function latexSvg(name, latex) {
  await fs.mkdir(FORMULA_DIR, { recursive: true });
  const query = `\\dpi{220}\\displaystyle ${latex}`;
  const response = await fetch(`https://latex.codecogs.com/svg.image?${encodeURIComponent(query)}`);
  if (!response.ok) throw new Error(`LaTeX renderer failed for ${name}: ${response.status}`);
  const svg = await response.text();
  const dims = svg.match(/width='([0-9.]+)pt' height='([0-9.]+)pt'/);
  if (!dims) throw new Error(`LaTeX renderer returned no dimensions for ${name}`);
  await fs.writeFile(path.join(FORMULA_DIR, `${name}.svg`), svg, "utf8");
  latexSources.push({ name, latex });
  const bytes = Buffer.from(svg, "utf8");
  return { bytes: bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength), width: Number(dims[1]), height: Number(dims[2]) };
}

async function formula(slide, name, latex, x, y, w, h) {
  const asset = await latexSvg(name, latex);
  const scale = Math.min(MATH_SCALE, w / asset.width, h / asset.height);
  const width = asset.width * scale;
  const height = asset.height * scale;
  slide.images.add({
    blob: asset.bytes, contentType: "image/svg+xml", alt: `LaTeX: ${latex}`, fit: "contain",
    position: { left: x + (w - width) / 2, top: y + (h - height) / 2, width, height }, geometry: "rect",
  });
}

async function outlinedFormula(slide, name, latex, x, y, w, h, stroke) {
  box(slide, `${name}-frame`, x, y, w, h, C.cream, { style: "solid", fill: stroke, width: 1.1 }, 12);
  await formula(slide, name, latex, x + 10, y + 6, w - 20, h - 12);
}

const presentation = Presentation.create({ slideSize: { width: W, height: H } });
const slide = presentation.slides.add();
slide.background.fill = C.cream;
const fullBytes = await readBytes(FULL_IMAGE);

// Title hierarchy.
text(slide, "title", "RegionSuff mechanism: from visible retinal evidence to paired-view audit", 48, 30, 1200, 36, { size: 30, color: C.brown, bold: true });
text(slide, "figure-id", "FIGURE 2", 1320, 32, 228, 28, { size: 18, color: C.green, bold: true, align: "right" });
text(slide, "subtitle", "Figure 1 establishes the study question; this figure specifies the model, the visibility-conditioned inference path, and the downstream paired analysis.", 50, 75, 1420, 24, { size: 16, color: C.rust });
box(slide, "top-rule", 48, 111, 1504, 1, C.divider, { style: "solid", fill: C.divider, width: 0 });

// Connector layer: one clean left-to-right reading path between the three panels.
arrow(slide, "a-to-b", 480, 397, 18, 18, C.brown);
arrow(slide, "b-to-c", 1110, 397, 18, 18, C.brown);

// A. Input evidence is explicit and large enough to see.
panelHeader(slide, "A", "Input evidence and visibility", 48, 138, 430, C.rust);
text(slide, "a-image-head", "Retinal foreground → 3 × 3 evidence bank", 58, 188, 210, 20, { size: 16, color: C.brown, bold: true, align: "center" });
imageFrame(slide, "a-source", fullBytes, "Large UWF retinal source image partitioned into a three-by-three evidence bank.", 58, 216, 202, 202, C.rust);
grid(slide, "a-source", 58, 216, 202, 202);
text(slide, "a-mask-head", "Deterministic evaluation maps m", 276, 190, 174, 18, { size: 16, color: C.brown, bold: true, align: "center" });
const masks = [["full", "Full", C.rust], ["center", "Center", C.magenta], ["cross", "Center +\ncross", C.orange]];
const mx = [276, 335, 394];
for (let i = 0; i < masks.length; i += 1) {
  const [mode, label, color] = masks[i];
  maskGrid(slide, `a-mask-${mode}`, mx[i], 224, 54, mode, color);
  text(slide, `a-mask-label-${mode}`, label, mx[i] - 3, 284, 60, 34, { size: 14, color: C.ink, bold: true, align: "center", valign: "top" });
}
await outlinedFormula(slide, "a-mask-vector", "\\mathbf{m}=(m_1,\\ldots,m_9)\\in\\{0,1\\}^{9}", 276, 330, 168, 50, C.rust);
box(slide, "a-training", 58, 446, 392, 158, C.orangePale, { style: "solid", fill: C.orange, width: 1 }, 12);
text(slide, "a-training-head", "Source training: stochastic evidence removal", 74, 460, 360, 20, { size: 17, color: C.rust, bold: true, align: "center" });
await formula(slide, "a-stochastic", "m_i\\sim\\operatorname{Bernoulli}(1-\\rho),\\quad\\rho=0.30", 82, 494, 344, 30);
text(slide, "a-empty", "All-empty draw → restore row-major token 0", 82, 532, 344, 20, { size: 15, color: C.ink, align: "center" });
text(slide, "a-eval", "Evaluation uses deterministic full, center, and center + cross views.", 82, 558, 344, 28, { size: 15, color: C.ink, align: "center" });

// B. The central model mechanism receives most horizontal space.
panelHeader(slide, "B", "Visibility-conditioned DR inference", 510, 138, 600, C.green);
text(slide, "b-path-head", "Each regional crop follows the same shared feature path", 524, 188, 572, 18, { size: 16, color: C.brown, bold: true, align: "center" });
imageFrame(slide, "b-crop", fullBytes, "Enlarged region r_i taken from the same UWF source image.", 528, 208, 120, 120, C.orange, { left: 0.18, top: 0.18, right: 0.18, bottom: 0.18 });
text(slide, "b-crop-label", "Enlarged regional crop rᵢ", 518, 334, 140, 20, { size: 16, color: C.ink, bold: true, align: "center" });
arrow(slide, "b-crop-to-encoder", 662, 259, 18, 18, C.orange);
box(slide, "b-encoder", 694, 208, 152, 120, C.cream, { style: "solid", fill: C.rust, width: 1.1 }, 12);
text(slide, "b-encoder-head", "Frozen encoder E", 708, 222, 124, 20, { size: 16, color: C.rust, bold: true, align: "center" });
text(slide, "b-encoder-copy", "RetinaRadar\nEfficientNet-B0", 708, 254, 124, 42, { size: 16, color: C.ink, align: "center" });
arrow(slide, "b-encoder-to-proj", 856, 259, 18, 18, C.orange);
box(slide, "b-proj", 888, 208, 190, 120, C.orangePale, { style: "solid", fill: C.orange, width: 1.1 }, 12);
text(slide, "b-proj-head", "Trainable projection P", 900, 222, 166, 20, { size: 16, color: C.brown, bold: true, align: "center" });
text(slide, "b-proj-copy", "Linear → LayerNorm → ReLU", 900, 256, 166, 24, { size: 16, color: C.ink, align: "center" });
downArrow(slide, "b-proj-to-token", 972, 336, 18, C.orange);
await outlinedFormula(slide, "b-token", "z_i=P(E(r_i))\\in\\mathbb{R}^{128}", 528, 370, 550, 56, C.orange);
text(slide, "b-token-note", "E remains frozen; P, attention, and the severity classifier are trained.", 538, 434, 530, 20, { size: 15, color: C.gray, align: "center" });
downArrow(slide, "b-token-to-attention", 794, 452, 14, C.green);
box(slide, "b-attention", 528, 474, 550, 124, C.cream, { style: "solid", fill: C.green, width: 1.1 }, 12);
text(slide, "b-attention-head", "Visibility-conditioned attention", 542, 486, 522, 20, { size: 17, color: C.green, bold: true, align: "center" });
await formula(slide, "b-score", "e_i=\\mathbf{w}_a^{\\top}\\tanh(\\mathbf{W}_a z_i+\\mathbf{b}_a)+b_s", 542, 514, 522, 26);
box(slide, "b-attention-divider", 548, 546, 510, 1, C.divider, { style: "solid", fill: C.divider, width: 0 });
await formula(slide, "b-normalization", "a_i(m)=\\dfrac{m_i\\exp(e_i)}{\\sum_{j=1}^{K}m_j\\exp(e_j)}", 542, 556, 522, 32);
downArrow(slide, "b-attention-to-prediction", 794, 602, 14, C.green);
box(slide, "b-prediction", 528, 622, 550, 114, C.greenPale, { style: "solid", fill: C.green, width: 1.1 }, 12);
text(slide, "b-prediction-head", "Aggregate available evidence → predict DR severity", 542, 634, 522, 20, { size: 17, color: C.brown, bold: true, align: "center" });
await formula(slide, "b-aggregate", "h(m)=\\sum_{i=1}^{K}a_i(m)z_i", 542, 662, 522, 24);
await formula(slide, "b-classify", "\\begin{array}{c}p(m)=\\operatorname{softmax}(W_ch(m)+b_c)\\\\\\hat{y}(m)=\\arg\\max_c p_c(m)\\end{array}", 542, 690, 522, 40);
await outlinedFormula(slide, "b-loss", "L_{\\mathrm{CE}}=-\\dfrac{1}{B}\\sum_{n=1}^{B}\\log p_{n,y_n}(m_n)", 528, 752, 550, 52, C.green);

// C. Pairing is downstream; it is not a second parallel classifier.
panelHeader(slide, "C", "Downstream paired-view audit", 1130, 138, 422, C.magenta);
text(slide, "c-intro", "Run the same fitted severity model twice under two visibility maps.", 1142, 188, 398, 20, { size: 15, color: C.gray, align: "center" });
maskGrid(slide, "c-full-grid", 1148, 226, 56, "full", C.rust);
box(slide, "c-full", 1216, 218, 128, 78, C.orangePale, { style: "solid", fill: C.orange, width: 1 }, 12);
text(slide, "c-full-head", "Full view", 1226, 230, 108, 18, { size: 16, color: C.brown, bold: true, align: "center" });
await formula(slide, "c-full-formula", "p_F=p(m_{\\mathrm{full}})", 1224, 254, 112, 28);
maskGrid(slide, "c-limited-grid", 1354, 226, 56, "cross", C.magenta);
box(slide, "c-limited", 1422, 218, 118, 78, C.magentaPale, { style: "solid", fill: C.magenta, width: 1 }, 12);
text(slide, "c-limited-head", "Center + cross", 1430, 230, 102, 18, { size: 15, color: C.magenta, bold: true, align: "center" });
await formula(slide, "c-limited-formula", "p_L=p(m_{\\mathrm{limited}})", 1430, 254, 102, 28);
downArrow(slide, "c-down", 1330, 312, 22, C.magenta);
await outlinedFormula(slide, "c-features", "\\begin{array}{c}\\mathbf{g}=[p_F,p_L,p_F-p_L,|p_F-p_L|,s_F,s_L,\\\\s_F-s_L,H_F,H_L,D_{\\mathrm{SKL}}]\\in\\mathbb{R}^{18}\\end{array}", 1142, 350, 396, 88, C.magenta);
text(slide, "c-features-note", "Paired probabilities · severity shifts · entropy · symmetric KL", 1152, 446, 376, 20, { size: 14, color: C.gray, align: "center" });
await outlinedFormula(slide, "c-risk", "\\tilde{\\mathbf{g}}=(\\mathbf{g}-\\boldsymbol{\\mu}_g)\\oslash\\boldsymbol{\\sigma}_g,\\quad q(\\mathbf{g})=\\sigma(\\boldsymbol{\\beta}^{\\top}\\tilde{\\mathbf{g}}+b)", 1142, 484, 396, 60, C.magenta);
box(slide, "c-boundary", 1142, 570, 396, 94, C.cream, { style: "solid", fill: C.rust, width: 1 }, 12);
text(slide, "c-boundary-head", "Interpretation boundary", 1154, 584, 372, 20, { size: 16, color: C.rust, bold: true, align: "center" });
text(slide, "c-boundary-copy", "This exploratory audit requires both full and limited predictions. It is not a deployable single-image triage rule.", 1160, 612, 360, 38, { size: 15, color: C.rust, bold: true, align: "center" });

box(slide, "bottom-rule", 48, 824, 1504, 1, C.divider, { style: "solid", fill: C.divider, width: 0 });
box(slide, "conclusion-frame", 48, 842, 1504, 44, C.cream, { style: "solid", fill: C.orange, width: 1.2 }, 14);
text(slide, "conclusion", "Mechanism boundary: evidence visibility enters the severity model through m; the paired feature g and risk estimate q(g) are constructed only after the two severity predictions exist.", 72, 850, 1456, 26, { size: 18, color: C.brown, bold: true, align: "center" });

slide.speakerNotes.textFrame.setText(
  `[Sources]\n- Local UWF source image: RegionSuff project assets.\n- Model equations, masks, and paired-risk notation: RegionSuff_1.6.docx, Sections 2.3--2.8.\n- Formula rendering: CodeCogs LaTeX-to-SVG renderer; all equation paths are embedded.\n\n[LaTeX source]\n${latexSources.map(({ name, latex }) => `${name}: ${latex}`).join("\n")}\n\nDesign note: Figure 1 owns the study-level evidence chain. Figure 2 deliberately shows only the algorithmic mechanism; all formula objects share the same fixed source scale (${MATH_SCALE}).`
);
slide.speakerNotes.setVisible(true);

await writeBlob(PREVIEW, await presentation.export({ slide, format: "png", scale: 2 }));
await fs.writeFile(LAYOUT, await (await slide.export({ format: "layout" })).text());
const pptx = await PresentationFile.exportPptx(presentation);
await pptx.save(FINAL_PPTX);
console.log(JSON.stringify({ finalPptx: FINAL_PPTX, preview: PREVIEW, layout: LAYOUT }, null, 2));
