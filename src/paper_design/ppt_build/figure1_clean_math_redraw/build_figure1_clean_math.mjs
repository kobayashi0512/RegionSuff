import fs from "node:fs/promises";
import path from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const BUILD = "/Users/tongyue/Documents/77f /7hao/paper_design/ppt_build/figure1_clean_math_redraw";
const FINAL_PPTX = "/Users/tongyue/Documents/ppf/第四论文/图1_规范重绘版_LaTeX公式版_统一字号_证据放大图.pptx";
const PREVIEW = path.join(BUILD, "figure1-clean-math-preview.png");
const LAYOUT = path.join(BUILD, "figure1-clean-math.layout.json");
const FORMULA_DIR = path.join(BUILD, "latex-formulas");
const OLD = "/Users/tongyue/Documents/77f /7hao/paper_design/ppt_build/figure1_algorithm_revision";
const ASSETS = path.join(OLD, "assets");
const FULL_IMAGE = path.join(OLD, "template-inspect/assets/ppt/media/image1.png");

const W = 1600;
const H = 900;
const FONT = "Times New Roman";
const MATH = "STIX Two Math";
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
// All equations use exactly the same source-scale. The surrounding frames are
// deliberately enlarged rather than allowing long equations to shrink.
const MATH_SCALE = 1.75;

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
    fontSize: options.size ?? 18,
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

function imageFrame(slide, name, bytes, alt, x, y, w, h, stroke = C.brown) {
  box(slide, `${name}-border`, x - 2, y - 2, w + 4, h + 4, C.cream, { style: "solid", fill: stroke, width: 1 }, 6);
  return slide.images.add({
    blob: bytes,
    contentType: "image/png",
    alt,
    fit: "contain",
    position: { left: x, top: y, width: w, height: h },
    geometry: "rect",
  });
}

// For the pixel-aperture examples, show the retained retinal content at a
// readable scale rather than enlarging the black masked canvas. The crop is
// derived from the same UWF source and the geometry still encodes the aperture.
function croppedEvidenceFrame(slide, name, bytes, alt, x, y, w, h, stroke, crop, geometry = "rect") {
  if (geometry === "ellipse") {
    slide.shapes.add({
      geometry: "ellipse",
      name: `${name}-border`,
      position: { left: x - 2, top: y - 2, width: w + 4, height: h + 4 },
      fill: "transparent",
      line: { style: "solid", fill: stroke, width: 1.2 },
    });
  } else {
    box(slide, `${name}-border`, x - 2, y - 2, w + 4, h + 4, C.cream, { style: "solid", fill: stroke, width: 1 }, 6);
  }
  return slide.images.add({
    blob: bytes,
    contentType: "image/png",
    alt,
    fit: "cover",
    crop,
    position: { left: x, top: y, width: w, height: h },
    geometry,
  });
}

function grid(slide, x, y, w, h) {
  const xs = [x + w / 3, x + (2 * w) / 3];
  const ys = [y + h / 3, y + (2 * h) / 3];
  xs.forEach((gx, i) => box(slide, `grid-v-${x}-${i}`, gx, y, 1.2, h, "#FFFFFF", { style: "solid", fill: "#FFFFFF", width: 0 }));
  ys.forEach((gy, i) => box(slide, `grid-h-${x}-${i}`, x, gy, w, 1.2, "#FFFFFF", { style: "solid", fill: "#FFFFFF", width: 0 }));
}

function regionalMask(slide, name, x, y, w, h, mode) {
  const cellW = w / 3;
  const cellH = h / 3;
  const visible = new Set(
    mode === "center" ? [4] : mode === "cross" ? [1, 3, 4, 5, 7] : [0, 1, 2, 3, 4, 5, 6, 7, 8],
  );
  for (let index = 0; index < 9; index += 1) {
    if (visible.has(index)) continue;
    const col = index % 3;
    const row = Math.floor(index / 3);
    box(slide, `${name}-${index}`, x + col * cellW, y + row * cellH, cellW, cellH, "#000000", { style: "solid", fill: "#000000", width: 0 });
  }
}

async function latexSvg(name, latex) {
  await fs.mkdir(FORMULA_DIR, { recursive: true });
  const query = `\\dpi{220}\\displaystyle ${latex}`;
  const response = await fetch(`https://latex.codecogs.com/svg.image?${encodeURIComponent(query)}`);
  if (!response.ok) throw new Error(`LaTeX renderer failed for ${name}: ${response.status}`);
  const svg = await response.text();
  if (!svg.includes("<svg")) throw new Error(`LaTeX renderer returned no SVG for ${name}`);
  const dimensions = svg.match(/width='([0-9.]+)pt' height='([0-9.]+)pt'/);
  if (!dimensions) throw new Error(`LaTeX renderer returned no dimensions for ${name}`);
  const out = path.join(FORMULA_DIR, `${name}.svg`);
  await fs.writeFile(out, svg, "utf8");
  latexSources.push({ name, latex });
  const bytes = Buffer.from(svg, "utf8");
  return {
    bytes: bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength),
    width: Number(dimensions[1]),
    height: Number(dimensions[2]),
  };
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
const rect055 = await readBytes(path.join(ASSETS, "uwf_rect_055.png"));
const circle055 = await readBytes(path.join(ASSETS, "uwf_circle_055.png"));
const rect035 = await readBytes(path.join(ASSETS, "uwf_rect_035.png"));

// Global reading order.
text(slide, "title", "RegionSuff: auditing retinal evidence under limited fields of view", 48, 30, 1160, 36, { size: 32, color: C.brown, bold: true });
text(slide, "figure-id", "FIGURE 1", 1320, 32, 228, 28, { size: 18, color: C.green, bold: true, align: "right" });
text(slide, "subtitle", "A clear image may still omit task-relevant retinal evidence; RegionSuff makes that availability explicit and testable.", 50, 75, 1320, 24, { size: 16, color: C.rust });
box(slide, "top-rule", 48, 111, 1504, 1, C.divider, { style: "solid", fill: C.divider, width: 0 });

// Connectors are deliberately created before foreground content.
arrow(slide, "a-to-b", 300, 399, 20, 18, C.brown);
arrow(slide, "b-to-c", 665, 399, 20, 18, C.brown);
arrow(slide, "c-to-d", 1110, 399, 20, 18, C.brown);

// A. Hidden evidence gap.
panelHeader(slide, "A", "Quality ≠ evidence", 48, 138, 244, C.rust);
text(slide, "a-full-label", "Full field", 54, 188, 105, 18, { size: 16, color: C.gray, bold: true, align: "center" });
text(slide, "a-center-label", "Center-only", 177, 188, 105, 18, { size: 16, color: C.gray, bold: true, align: "center" });
imageFrame(slide, "a-full", fullBytes, "Full UWF field with a 3 by 3 regional overlay.", 54, 212, 105, 105, C.rust);
grid(slide, 54, 212, 105, 105);
imageFrame(slide, "a-center", fullBytes, "Center-only regional view of the same UWF image.", 177, 212, 105, 105, C.magenta);
regionalMask(slide, "a-center-mask", 177, 212, 105, 105, "center");
grid(slide, 177, 212, 105, 105);
box(slide, "a-callout", 52, 338, 236, 90, C.orangePale, { style: "solid", fill: C.orange, width: 1 }, 12);
text(slide, "a-callout-title", "Clear does not mean sufficient", 62, 348, 216, 20, { size: 16, color: C.brown, bold: true, align: "center" });
text(slide, "a-callout-copy", "Both views can be sharp.\nThey do not contain the same retinal evidence.", 62, 374, 216, 42, { size: 16, color: C.ink, align: "center" });
box(slide, "a-question", 52, 460, 236, 172, C.cream, { style: "solid", fill: C.rust, width: 1 }, 12);
text(slide, "a-question-head", "Audit question", 70, 478, 200, 22, { size: 17, color: C.rust, bold: true, align: "center" });
text(slide, "a-question-copy", "How does a fixed DR classifier change when visible evidence is systematically restricted?", 70, 514, 200, 98, { size: 19, color: C.ink, align: "center", lineSpacing: 0.94 });

// B. Controlled evidence loss.
panelHeader(slide, "B", "Controlled evidence loss", 338, 138, 296, C.orange);
text(slide, "b-region-title", "Region-level views", 350, 188, 272, 20, { size: 16, color: C.brown, bold: true, align: "left" });
const regionXs = [350, 438, 526];
const regionSpecs = [
  ["full", "Full", C.brown],
  ["center", "Center", C.magenta],
  ["cross", "Center +\ncross", C.orange],
];
for (let i = 0; i < regionSpecs.length; i += 1) {
  const [mode, label, stroke] = regionSpecs[i];
  imageFrame(slide, `b-region-${i}`, fullBytes, `${label} regional mask.`, regionXs[i], 208, 78, 78, stroke);
  regionalMask(slide, `b-region-${i}-mask`, regionXs[i], 208, 78, 78, mode);
  grid(slide, regionXs[i], 208, 78, 78);
  text(slide, `b-region-label-${i}`, label, regionXs[i] - 5, 294, 88, 30, { size: 16, color: C.ink, bold: true, align: "center", valign: "top" });
}
box(slide, "b-divider", 350, 326, 270, 1, C.divider, { style: "solid", fill: C.divider, width: 0 });
text(slide, "b-aperture-title", "Pixel-space apertures: retained evidence", 350, 344, 272, 20, { size: 16, color: C.brown, bold: true });
const apertureXs = [350, 445, 540];
const apertureSpecs = [
  ["Centered\nrectangle", "f=0.55", C.orange, { left: 0.225, top: 0.225, right: 0.225, bottom: 0.225 }, "rect"],
  ["Area-matched\ncircle", "f=0.55", C.green, { left: 0.225, top: 0.225, right: 0.225, bottom: 0.225 }, "ellipse"],
  ["Severe\nrectangle", "f=0.35", C.magenta, { left: 0.325, top: 0.325, right: 0.325, bottom: 0.325 }, "rect"],
];
for (let i = 0; i < apertureSpecs.length; i += 1) {
  const [label, latex, stroke, crop, geometry] = apertureSpecs[i];
  croppedEvidenceFrame(slide, `b-aperture-${i}`, fullBytes, `Magnified retained retinal evidence from the same UWF source with ${label} aperture.`, apertureXs[i], 374, 80, 80, stroke, crop, geometry);
  text(slide, `b-aperture-label-${i}`, label, apertureXs[i] - 5, 462, 90, 39, { size: 14, color: C.ink, bold: true, align: "center", valign: "top" });
  await formula(slide, `b-aperture-f-${i}`, latex, apertureXs[i] - 4, 506, 88, 22);
}
await outlinedFormula(slide, "b-area-formula", "\\begin{array}{c} A_{\\mathrm{rect}}=f^{2},\\quad r_{\\mathrm{circle}}=\\frac{f}{\\sqrt{\\pi}} \\\\ A_{\\mathrm{circle}}=\\pi r_{\\mathrm{circle}}^{2}=f^{2} \\end{array}", 350, 538, 270, 72, C.orange);
box(slide, "b-note", 350, 630, 270, 54, C.orangePale, { style: "solid", fill: C.orange, width: 1 }, 12);
text(slide, "b-note-copy", "Retained content is magnified for display; aperture geometry and DR label are unchanged.", 362, 638, 246, 34, { size: 15, color: C.rust, italic: true, align: "center" });

// C. RegionSuff model.
panelHeader(slide, "C", "Visibility-conditioned inference", 704, 138, 388, C.green);
text(slide, "c-step-1", "1. Build a 3×3 regional evidence bank", 714, 186, 368, 20, { size: 16, color: C.brown, bold: true });
imageFrame(slide, "c-full", fullBytes, "UWF image divided into a 3 by 3 evidence bank.", 714, 211, 110, 110, C.green);
grid(slide, 714, 211, 110, 110);
box(slide, "c-mask", 850, 226, 222, 78, C.greenPale, { style: "solid", fill: C.green, width: 1 }, 12);
text(slide, "c-mask-head", "Visibility mask", 866, 236, 190, 18, { size: 16, color: C.green, bold: true, align: "center" });
await formula(slide, "c-mask-math", "m\\in\\{0,1\\}^{9}", 866, 260, 190, 28);
downArrow(slide, "c-arrow-1", 889, 328, 18, C.green);
await outlinedFormula(slide, "c-encode", "z_i=P(E(r_i))\\in\\mathbb{R}^{128}", 714, 350, 366, 52, C.rust);
text(slide, "c-encode-note", "Frozen encoder + trainable projection: one token per region.", 724, 404, 346, 28, { size: 16, color: C.gray, align: "center" });
downArrow(slide, "c-arrow-2", 889, 438, 22, C.green);
box(slide, "c-attention-frame", 714, 470, 366, 150, C.cream, { style: "solid", fill: C.green, width: 1.2 }, 12);
text(slide, "c-attention-head", "2. Normalize attention only over visible regions", 730, 482, 334, 22, { size: 16, color: C.green, bold: true, align: "center" });
await formula(slide, "c-attention-equations", "\\begin{array}{c} e_i=\\mathbf{w}_a^{\\top}\\tanh(\\mathbf{W}_a z_i+\\mathbf{b}_a)+b_s \\\\ a_i(m)=\\dfrac{m_i\\exp(e_i)}{\\sum_{j=1}^{K}m_j\\exp(e_j)} \\end{array}", 730, 516, 334, 96);
downArrow(slide, "c-arrow-3", 889, 632, 22, C.green);
box(slide, "c-output-frame", 714, 668, 366, 154, C.greenPale, { style: "solid", fill: C.green, width: 1.2 }, 12);
text(slide, "c-output-head", "3. Aggregate evidence and predict DR severity", 730, 680, 334, 22, { size: 16, color: C.brown, bold: true, align: "center" });
await formula(slide, "c-output-h", "\\textstyle h(m)=\\sum_{i=1}^{K}a_i(m)z_i", 726, 710, 342, 38);
await formula(slide, "c-output-p", "p(m)=\\mathrm{softmax}(W_c h(m)+b_c)", 726, 752, 342, 34);
await formula(slide, "c-output-y", "\\hat{y}(m)\\in\\{\\mathrm{Normal},\\mathrm{NPDR},\\mathrm{PDR}\\}", 726, 792, 342, 24);

// D. Audit chain. This is intentionally downstream from RegionSuff severity prediction.
panelHeader(slide, "D", "Downstream paired-view audit", 1146, 138, 404, C.magenta);
text(slide, "d-intro", "The same fitted severity model is evaluated twice.", 1158, 187, 380, 20, { size: 16, color: C.gray, align: "center" });
box(slide, "d-full-mask", 1160, 228, 154, 70, C.orangePale, { style: "solid", fill: C.orange, width: 1 }, 12);
text(slide, "d-full-mask-title", "Full-view mask", 1170, 238, 134, 18, { size: 16, color: C.brown, bold: true, align: "center" });
await formula(slide, "d-full-mask-sub", "p(m_{\\mathrm{full}})", 1170, 262, 134, 26);
box(slide, "d-limited-mask", 1380, 228, 154, 70, C.magentaPale, { style: "solid", fill: C.magenta, width: 1 }, 12);
text(slide, "d-limited-mask-title", "Limited-view mask", 1390, 238, 134, 18, { size: 16, color: C.magenta, bold: true, align: "center" });
await formula(slide, "d-limited-mask-sub", "p(m_{\\mathrm{limited}})", 1390, 262, 134, 26);
downArrow(slide, "d-arrow-1", 1341, 306, 18, C.magenta);
await outlinedFormula(slide, "d-gap", "\\mathbf{g}=[\\Delta p,|\\Delta p|,\\Delta s,H,D_{\\mathrm{SKL}}]", 1174, 330, 346, 60, C.magenta);
downArrow(slide, "d-arrow-2", 1341, 402, 24, C.magenta);
await outlinedFormula(slide, "d-risk", "q(\\mathbf{g})=\\sigma(\\boldsymbol{\\beta}^{\\top}\\tilde{\\mathbf{g}}+b)", 1174, 438, 346, 60, C.magenta);
text(slide, "d-risk-label", "Rank the risk of limited-view underestimation", 1174, 510, 346, 22, { size: 16, color: C.magenta, bold: true, align: "center" });
box(slide, "d-not-second-head", 1174, 548, 346, 60, C.cream, { style: "solid", fill: C.rust, width: 1 }, 12);
text(slide, "d-not-second-copy", "Not a second classifier: it requires both full and limited predictions.", 1190, 558, 314, 38, { size: 15, color: C.rust, bold: true, align: "center" });
box(slide, "d-evidence-line", 1160, 642, 374, 1, C.divider, { style: "solid", fill: C.divider, width: 0 });
text(slide, "d-evidence-head", "Evidence chain", 1160, 658, 374, 20, { size: 16, color: C.brown, bold: true, align: "center" });
const evidence = [
  ["Internal", "390 images · five seeds", C.orange],
  ["Intervention", "one-region occlusion", C.green],
  ["External UWF", "2,597 images · no adaptation", C.magenta],
];
const evidenceXs = [1162, 1288, 1414];
for (let i = 0; i < evidence.length; i += 1) {
  const [head, sub, color] = evidence[i];
  box(slide, `d-evidence-${i}`, evidenceXs[i], 692, 114, 76, C.cream, { style: "solid", fill: color, width: 1 }, 10);
  text(slide, `d-evidence-head-${i}`, head, evidenceXs[i] + 7, 700, 100, 20, { size: 16, color, bold: true, align: "center" });
  text(slide, `d-evidence-sub-${i}`, sub, evidenceXs[i] + 7, 726, 100, 34, { size: 16, color: C.ink, align: "center", valign: "top" });
}

// Bottom conclusion strip.
box(slide, "conclusion-frame", 48, 842, 1504, 48, C.cream, { style: "solid", fill: C.orange, width: 1.2 }, 14);
text(slide, "conclusion", "Core finding: diagnostic evidence depends on the composition and topology of visible retina—not photographic quality or field area alone.", 70, 850, 1460, 28, { size: 20, color: C.brown, bold: true, align: "center" });

slide.speakerNotes.textFrame.setText(
  `[Sources]\n- Local UWF source image and deterministic aperture masks from the RegionSuff project assets.\n- Method terminology and formulas: RegionSuff_1.4.docx, Sections 2.3--2.8.\n- Formula rendering: CodeCogs LaTeX-to-SVG renderer; the SVG paths are embedded in this PPTX.\n\n[LaTeX source]\n${latexSources.map(({ name, latex }) => `${name}: ${latex}`).join("\n")}\n\nFigure design note: the full 18-dimensional paired-view feature expansion is intentionally omitted from Figure 1 to preserve readability; it remains in Figure 2 and the Methods.`
);
slide.speakerNotes.setVisible(true);

await writeBlob(PREVIEW, await presentation.export({ slide, format: "png", scale: 2 }));
await fs.writeFile(LAYOUT, await (await slide.export({ format: "layout" })).text());
const pptx = await PresentationFile.exportPptx(presentation);
await pptx.save(FINAL_PPTX);

console.log(JSON.stringify({ finalPptx: FINAL_PPTX, preview: PREVIEW, layout: LAYOUT }, null, 2));
