import fs from "node:fs/promises";
import path from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const BUILD = "/Users/tongyue/Documents/77f /7hao/paper_design/figure2_rebuild";
const FINAL_PPTX = "/Users/tongyue/Documents/ppf/第四论文/图2_规范重绘版_LaTeX公式版.pptx";
const PREVIEW = path.join(BUILD, "figure2-preview.png");
const LAYOUT = path.join(BUILD, "figure2.layout.json");
const FORMULA_DIR = path.join(BUILD, "latex-formulas");
const FULL_IMAGE = "/Users/tongyue/Documents/77f /7hao/paper_design/ppt_build/figure1_algorithm_revision/template-inspect/assets/ppt/media/image1.png";

const W = 1600;
const H = 900;
const FONT = "Times New Roman";
const MATH_SCALE = 1.55;
const C = {
  ink: "#332720",
  brown: "#704C2B",
  rust: "#965E4A",
  orange: "#D0913C",
  orangePale: "#F7E7D4",
  green: "#8B9A7C",
  greenPale: "#EFF3EA",
  magenta: "#C14F75",
  magentaPale: "#FAEEF3",
  cream: "#FFFDFC",
  divider: "#D9CBBE",
  gray: "#6E625A",
  black: "#1C1714",
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
  return slide.shapes.add({
    geometry: radius ? "roundRect" : "rect",
    name,
    position: { left: x, top: y, width: w, height: h },
    fill,
    line,
    borderRadius: radius || undefined,
  });
}

function text(slide, name, value, x, y, w, h, options = {}) {
  const shape = box(slide, name, x, y, w, h, "none");
  shape.text = value;
  shape.text.style = {
    typeface: options.typeface ?? FONT,
    fontSize: options.size ?? 17,
    color: options.color ?? C.ink,
    bold: options.bold ?? false,
    italic: options.italic ?? false,
    alignment: options.align ?? "left",
    verticalAlignment: options.valign ?? "middle",
    lineSpacing: options.lineSpacing ?? 0.92,
    insets: options.insets ?? { top: 0, right: 0, bottom: 0, left: 0 },
    autoFit: "none",
    wrap: "square",
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
  return slide.shapes.add({
    geometry: "rightArrow",
    name,
    position: { left: x, top: y, width: w, height: h },
    fill: color,
    line: { style: "solid", fill: color, width: 0 },
  });
}

function downArrow(slide, name, x, y, h = 20, color = C.green) {
  return slide.shapes.add({
    geometry: "downArrow",
    name,
    position: { left: x, top: y, width: 18, height: h },
    fill: color,
    line: { style: "solid", fill: color, width: 0 },
  });
}

function imageFrame(slide, name, bytes, alt, x, y, w, h, stroke = C.brown, crop) {
  box(slide, `${name}-border`, x - 2, y - 2, w + 4, h + 4, C.cream, { style: "solid", fill: stroke, width: 1 }, 6);
  return slide.images.add({
    blob: bytes,
    contentType: "image/png",
    alt,
    fit: crop ? "cover" : "contain",
    ...(crop ? { crop } : {}),
    position: { left: x, top: y, width: w, height: h },
    geometry: "rect",
  });
}

function grid(slide, name, x, y, w, h) {
  const xs = [x + w / 3, x + (2 * w) / 3];
  const ys = [y + h / 3, y + (2 * h) / 3];
  xs.forEach((gx, i) => box(slide, `${name}-v-${i}`, gx, y, 1.2, h, "#FFFFFF", { style: "solid", fill: "#FFFFFF", width: 0 }));
  ys.forEach((gy, i) => box(slide, `${name}-h-${i}`, x, gy, w, 1.2, "#FFFFFF", { style: "solid", fill: "#FFFFFF", width: 0 }));
}

function regionalMask(slide, name, x, y, w, h, mode) {
  const visible = new Set(mode === "center" ? [4] : mode === "cross" ? [1, 3, 4, 5, 7] : [0, 1, 2, 3, 4, 5, 6, 7, 8]);
  const cellW = w / 3;
  const cellH = h / 3;
  for (let index = 0; index < 9; index += 1) {
    if (visible.has(index)) continue;
    const col = index % 3;
    const row = Math.floor(index / 3);
    box(slide, `${name}-${index}`, x + col * cellW, y + row * cellH, cellW, cellH, "#1C1714/70", { style: "solid", fill: "#1C1714/70", width: 0 });
  }
}

async function latexSvg(name, latex) {
  await fs.mkdir(FORMULA_DIR, { recursive: true });
  const query = `\\dpi{220}\\displaystyle ${latex}`;
  const response = await fetch(`https://latex.codecogs.com/svg.image?${encodeURIComponent(query)}`);
  if (!response.ok) throw new Error(`LaTeX renderer failed for ${name}: ${response.status}`);
  const svg = await response.text();
  const dimensions = svg.match(/width='([0-9.]+)pt' height='([0-9.]+)pt'/);
  if (!dimensions) throw new Error(`LaTeX renderer returned no dimensions for ${name}`);
  const out = path.join(FORMULA_DIR, `${name}.svg`);
  await fs.writeFile(out, svg, "utf8");
  latexSources.push({ name, latex });
  const bytes = Buffer.from(svg, "utf8");
  return { bytes: bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength), width: Number(dimensions[1]), height: Number(dimensions[2]) };
}

async function formula(slide, name, latex, x, y, w, h) {
  const asset = await latexSvg(name, latex);
  const scale = Math.min(MATH_SCALE, w / asset.width, h / asset.height);
  const displayW = asset.width * scale;
  const displayH = asset.height * scale;
  slide.images.add({
    blob: asset.bytes,
    contentType: "image/svg+xml",
    alt: `LaTeX: ${latex}`,
    fit: "contain",
    position: { left: x + (w - displayW) / 2, top: y + (h - displayH) / 2, width: displayW, height: displayH },
    geometry: "rect",
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

// Global title and reading order.
text(slide, "title", "RegionSuff model: visibility-conditioned DR inference and paired-view auditing", 48, 30, 1200, 36, { size: 30, color: C.brown, bold: true });
text(slide, "figure-id", "FIGURE 2", 1320, 32, 228, 28, { size: 18, color: C.green, bold: true, align: "right" });
text(slide, "subtitle", "A fixed retinal classifier is evaluated under explicit visibility masks; the paired risk audit occurs only after two severity predictions are available.", 50, 75, 1420, 24, { size: 16, color: C.rust });
box(slide, "top-rule", 48, 111, 1504, 1, C.divider, { style: "solid", fill: C.divider, width: 0 });

// Arrows must exist before their foreground nodes.
arrow(slide, "a-to-b", 358, 395, 18, 18, C.brown);
arrow(slide, "b-to-c", 682, 395, 18, 18, C.brown);
arrow(slide, "c-to-d", 1104, 395, 18, 18, C.brown);

// A. Explicit retinal evidence and mask protocol.
panelHeader(slide, "A", "Evidence bank and masks", 48, 138, 310, C.rust);
text(slide, "a-source-head", "Retinal foreground", 58, 188, 120, 18, { size: 16, color: C.brown, bold: true, align: "center" });
imageFrame(slide, "a-source-image", fullBytes, "UWF retinal source image partitioned into a 3 by 3 evidence bank.", 58, 212, 120, 120, C.rust);
grid(slide, "a-source-grid", 58, 212, 120, 120);
text(slide, "a-mask-head", "Evaluation visibility masks", 190, 188, 156, 18, { size: 16, color: C.brown, bold: true, align: "center" });
const maskXs = [192, 246, 300];
const maskInfo = [["full", "Full", C.brown], ["center", "Center", C.magenta], ["cross", "Cross", C.orange]];
for (let i = 0; i < maskInfo.length; i += 1) {
  const [mode, label, color] = maskInfo[i];
  imageFrame(slide, `a-mask-${mode}`, fullBytes, `${label} visibility mask.`, maskXs[i], 218, 48, 48, color);
  regionalMask(slide, `a-mask-${mode}`, maskXs[i], 218, 48, 48, mode);
  grid(slide, `a-mask-grid-${mode}`, maskXs[i], 218, 48, 48);
  text(slide, `a-mask-label-${mode}`, label, maskXs[i] - 4, 274, 56, 18, { size: 14, color: C.ink, bold: true, align: "center" });
}
box(slide, "a-training-frame", 58, 356, 290, 168, C.orangePale, { style: "solid", fill: C.orange, width: 1 }, 12);
text(slide, "a-training-head", "Stochastic masking during source training", 72, 370, 262, 20, { size: 16, color: C.rust, bold: true, align: "center" });
await formula(slide, "a-training-math", "m_i\\sim\\operatorname{Bernoulli}(1-\\rho),\\quad\\rho=0.30", 76, 400, 254, 30);
await formula(slide, "a-nonempty-math", "\\sum_{i=1}^{9}m_i=0\\Rightarrow m_1\\leftarrow 1", 76, 438, 254, 30);
text(slide, "a-training-note", "Full, center, and cross masks are used only at evaluation.", 76, 478, 254, 30, { size: 15, color: C.ink, align: "center" });

// B. Frozen regional representation and trainable projection.
panelHeader(slide, "B", "Frozen regional encoder", 382, 138, 300, C.orange);
text(slide, "b-step", "Each of K = 9 regional crops follows the same path", 394, 188, 276, 20, { size: 15, color: C.brown, bold: true, align: "center" });
imageFrame(slide, "b-region-crop", fullBytes, "Example regional crop r_i from the UWF image.", 398, 220, 76, 76, C.orange, { left: 0.32, top: 0.32, right: 0.32, bottom: 0.32 });
text(slide, "b-region-caption", "Regional crop\n rᵢ", 388, 304, 96, 38, { size: 16, color: C.ink, bold: true, align: "center" });
arrow(slide, "b-to-encoder", 484, 247, 18, 18, C.orange);
box(slide, "b-encoder", 514, 214, 148, 92, C.cream, { style: "solid", fill: C.rust, width: 1.1 }, 12);
text(slide, "b-encoder-title", "Frozen encoder E", 528, 226, 120, 20, { size: 16, color: C.rust, bold: true, align: "center" });
text(slide, "b-encoder-copy", "RetinaRadar\nEfficientNet-B0", 528, 252, 120, 40, { size: 16, color: C.ink, align: "center" });
downArrow(slide, "b-down-1", 579, 316, 18, C.orange);
box(slide, "b-projection", 498, 348, 180, 84, C.orangePale, { style: "solid", fill: C.orange, width: 1.1 }, 12);
text(slide, "b-projection-title", "Trainable projection P", 512, 360, 152, 20, { size: 16, color: C.brown, bold: true, align: "center" });
text(slide, "b-projection-copy", "Linear · LayerNorm · ReLU", 512, 390, 152, 22, { size: 15, color: C.ink, align: "center" });
await outlinedFormula(slide, "b-token", "z_i=P(E(r_i))\\in\\mathbb{R}^{128}", 394, 464, 276, 56, C.orange);
text(slide, "b-token-note", "One 128-dimensional token per region", 404, 528, 256, 20, { size: 15, color: C.gray, align: "center" });

// C. Masked attention and primary severity prediction.
panelHeader(slide, "C", "Visibility-conditioned pooling", 706, 138, 398, C.green);
text(slide, "c-visible-head", "1. Score and normalize only visible regional evidence", 718, 188, 374, 20, { size: 16, color: C.brown, bold: true, align: "center" });
box(slide, "c-mask-card", 720, 218, 112, 86, C.greenPale, { style: "solid", fill: C.green, width: 1 }, 12);
text(slide, "c-mask-card-head", "Visibility mask", 730, 230, 92, 18, { size: 15, color: C.green, bold: true, align: "center" });
await formula(slide, "c-mask-math", "\\mathbf{m}\\in\\{0,1\\}^{9}", 728, 254, 96, 26);
arrow(slide, "c-mask-to-attn", 846, 252, 18, 18, C.green);
box(slide, "c-attention-frame", 876, 214, 216, 176, C.cream, { style: "solid", fill: C.green, width: 1.1 }, 12);
text(slide, "c-attention-head", "Masked attention", 888, 228, 192, 18, { size: 16, color: C.green, bold: true, align: "center" });
await formula(slide, "c-score", "e_i=\\mathbf{w}_a^{\\top}\\tanh(\\mathbf{W}_a z_i+\\mathbf{b}_a)+b_s", 888, 260, 192, 42);
box(slide, "c-attention-divider", 892, 316, 184, 1, C.divider, { style: "solid", fill: C.divider, width: 0 });
await formula(slide, "c-attention", "a_i(m)=\\dfrac{m_i\\exp(e_i)}{\\sum_{j=1}^{K}m_j\\exp(e_j)}", 888, 330, 192, 52);
text(slide, "c-attention-note", "Unavailable regions receive zero weight.", 728, 318, 132, 48, { size: 15, color: C.gray, italic: true, align: "center" });
downArrow(slide, "c-down-1", 895, 404, 20, C.green);
box(slide, "c-severity-frame", 720, 440, 372, 132, C.greenPale, { style: "solid", fill: C.green, width: 1.1 }, 12);
text(slide, "c-severity-head", "2. Aggregate evidence and predict DR severity", 734, 452, 344, 20, { size: 16, color: C.brown, bold: true, align: "center" });
await formula(slide, "c-aggregate", "h(m)=\\sum_{i=1}^{K}a_i(m)z_i", 734, 482, 344, 32);
await formula(slide, "c-predict", "\\begin{array}{c}p(m)=\\operatorname{softmax}(W_ch(m)+b_c)\\\\\\hat{y}(m)=\\arg\\max_c p_c(m)\\end{array}", 730, 518, 352, 48);
await outlinedFormula(slide, "c-loss", "L_{\\mathrm{CE}}=-\\dfrac{1}{B}\\sum_{n=1}^{B}\\log p_{n,y_n}(m_n)", 720, 600, 372, 60, C.green);
text(slide, "c-loss-note", "Unweighted cross-entropy for three-class DR severity", 730, 668, 352, 20, { size: 15, color: C.gray, align: "center" });

// D. Paired full/limited audit occurs strictly downstream of severity prediction.
panelHeader(slide, "D", "Downstream paired-view risk audit", 1128, 138, 424, C.magenta);
text(slide, "d-intro", "The same fitted severity model is evaluated under two masks.", 1140, 188, 400, 20, { size: 15, color: C.gray, align: "center" });
box(slide, "d-full", 1142, 222, 176, 74, C.orangePale, { style: "solid", fill: C.orange, width: 1 }, 12);
text(slide, "d-full-head", "Full-view mask", 1154, 234, 152, 18, { size: 16, color: C.brown, bold: true, align: "center" });
await formula(slide, "d-full-math", "p_F=p(m_{\\mathrm{full}})", 1154, 258, 152, 28);
box(slide, "d-limited", 1362, 222, 176, 74, C.magentaPale, { style: "solid", fill: C.magenta, width: 1 }, 12);
text(slide, "d-limited-head", "Limited-view mask", 1374, 234, 152, 18, { size: 16, color: C.magenta, bold: true, align: "center" });
await formula(slide, "d-limited-math", "p_L=p(m_{\\mathrm{limited}})", 1374, 258, 152, 28);
downArrow(slide, "d-down-1", 1331, 306, 20, C.magenta);
await outlinedFormula(slide, "d-features", "\\begin{array}{c}\\mathbf{g}=[p_F,p_L,p_F-p_L,|p_F-p_L|,s_F,s_L,\\\\ s_F-s_L,H_F,H_L,D_{\\mathrm{SKL}}]\\in\\mathbb{R}^{18}\\end{array}", 1142, 338, 396, 82, C.magenta);
text(slide, "d-features-note", "Four probability blocks · severity shifts · entropy · symmetric KL", 1152, 428, 376, 20, { size: 14, color: C.gray, align: "center" });
await outlinedFormula(slide, "d-risk", "\\tilde{\\mathbf{g}}=(\\mathbf{g}-\\boldsymbol{\\mu}_g)\\oslash\\boldsymbol{\\sigma}_g,\\quad q(\\mathbf{g})=\\sigma(\\boldsymbol{\\beta}^{\\top}\\tilde{\\mathbf{g}}+b)", 1142, 466, 396, 60, C.magenta);
box(slide, "d-boundary", 1142, 548, 396, 70, C.cream, { style: "solid", fill: C.rust, width: 1 }, 12);
text(slide, "d-boundary-copy", "Exploratory analytical audit—not a deployable single-image triage head. Both full and limited predictions are required.", 1156, 558, 368, 48, { size: 15, color: C.rust, bold: true, align: "center" });

// Protocol separation keeps each use of the data explicit.
box(slide, "protocol-rule", 48, 704, 1504, 1, C.divider, { style: "solid", fill: C.divider, width: 0 });
text(slide, "protocol-title", "Protocol separation", 48, 718, 1504, 20, { size: 16, color: C.brown, bold: true, align: "center" });
const protocol = [
  ["Source fitting", "UWF-DR train / validation\nρ = 0.30 · epoch selection", C.orange],
  ["Internal test", "390 held-out images\nfive independent seeds", C.rust],
  ["Paired risk audit", "Fixed split + grouped nested analysis\npaired predictions only", C.magenta],
  ["External UWF", "MMRDR-UWF, n = 2,597\nno target training or selection", C.green],
];
const protocolXs = [58, 432, 806, 1180];
for (let i = 0; i < protocol.length; i += 1) {
  const [head, copy, color] = protocol[i];
  box(slide, `protocol-${i}`, protocolXs[i], 750, 362, 72, C.cream, { style: "solid", fill: color, width: 1 }, 12);
  text(slide, `protocol-head-${i}`, head, protocolXs[i] + 12, 760, 338, 20, { size: 16, color, bold: true, align: "center" });
  text(slide, `protocol-copy-${i}`, copy, protocolXs[i] + 14, 785, 334, 28, { size: 14, color: C.ink, align: "center" });
}
box(slide, "conclusion-frame", 48, 844, 1504, 42, C.cream, { style: "solid", fill: C.orange, width: 1.2 }, 14);
text(slide, "conclusion", "Core mechanism: visibility is represented explicitly, attention is normalized over available evidence only, and paired risk is assessed after—not alongside—severity prediction.", 72, 851, 1456, 26, { size: 18, color: C.brown, bold: true, align: "center" });

slide.speakerNotes.textFrame.setText(
  `[Sources]\n- Local UWF image: RegionSuff project assets.\n- Algorithm, notation, and protocol roles: RegionSuff_1.5.docx, Sections 2.3--2.8.\n- Formula rendering: CodeCogs LaTeX-to-SVG renderer; vector paths embedded in this PPTX.\n\n[LaTeX source]\n${latexSources.map(({ name, latex }) => `${name}: ${latex}`).join("\n")}\n\nDesign note: all equations use one fixed source scale (${MATH_SCALE}) and are centered inside deliberately enlarged formula frames.`
);
slide.speakerNotes.setVisible(true);

await writeBlob(PREVIEW, await presentation.export({ slide, format: "png", scale: 2 }));
await fs.writeFile(LAYOUT, await (await slide.export({ format: "layout" })).text());
const pptx = await PresentationFile.exportPptx(presentation);
await pptx.save(FINAL_PPTX);
console.log(JSON.stringify({ finalPptx: FINAL_PPTX, preview: PREVIEW, layout: LAYOUT }, null, 2));
