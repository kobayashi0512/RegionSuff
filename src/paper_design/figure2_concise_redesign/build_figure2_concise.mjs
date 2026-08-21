import fs from "node:fs/promises";
import path from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const BUILD = "/Users/tongyue/Documents/77f /7hao/paper_design/figure2_concise_redesign";
const FINAL_PPTX = "/Users/tongyue/Documents/ppf/第四论文/图2_架构精简重绘版_核心公式.pptx";
const PREVIEW = path.join(BUILD, "figure2-concise-preview.png");
const LAYOUT = path.join(BUILD, "figure2-concise.layout.json");
const FORMULA_DIR = path.join(BUILD, "latex");
const FULL_IMAGE = "/Users/tongyue/Documents/77f /7hao/paper_design/figure2_rebuild/figure1_style_inventory/template-inspect/assets/ppt/media/image.png";

const W = 1600;
const H = 900;
const FONT = "Times New Roman";
const FORMULA_SCALE = 1.62;
const C = {
  page: "#FFFDF8",
  ink: "#332720",
  brown: "#704C2B",
  rust: "#965E4A",
  orange: "#C68A32",
  orangePale: "#F6E5CD",
  olive: "#78866B",
  olivePale: "#EDF1E8",
  magenta: "#B84067",
  magentaPale: "#F9EDF1",
  line: "#D8CABB",
  muted: "#6F6259",
  grayPale: "#F4F0EA",
  hidden: "#DCD7CF",
  white: "#FFFFFF",
};

const latexSources = [];

async function writeBlob(filePath, blob) {
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

async function readBytes(filePath) {
  const bytes = await fs.readFile(filePath);
  return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
}

function rect(slide, name, x, y, w, h, fill = "none", stroke = "none", radius = 0, width = 0) {
  return slide.shapes.add({
    geometry: radius ? "roundRect" : "rect",
    name,
    position: { left: x, top: y, width: w, height: h },
    fill,
    line: { style: "solid", fill: stroke, width },
    borderRadius: radius || undefined,
  });
}

function txt(slide, name, value, x, y, w, h, opts = {}) {
  const shape = rect(slide, name, x, y, w, h, "none", "none", 0, 0);
  shape.text = value;
  shape.text.style = {
    typeface: opts.typeface ?? FONT,
    fontSize: opts.size ?? 17,
    color: opts.color ?? C.ink,
    bold: opts.bold ?? false,
    italic: opts.italic ?? false,
    alignment: opts.align ?? "left",
    verticalAlignment: opts.valign ?? "middle",
    lineSpacing: opts.lineSpacing ?? 0.92,
    insets: opts.insets ?? { top: 0, right: 0, bottom: 0, left: 0 },
    autoFit: "none",
    wrap: "square",
  };
  return shape;
}

function arrow(slide, name, x, y, w, h, fill) {
  return slide.shapes.add({
    geometry: "rightArrow",
    name,
    position: { left: x, top: y, width: w, height: h },
    fill,
    line: { style: "solid", fill, width: 0 },
  });
}

function down(slide, name, x, y, w, h, fill) {
  return slide.shapes.add({
    geometry: "downArrow",
    name,
    position: { left: x, top: y, width: w, height: h },
    fill,
    line: { style: "solid", fill, width: 0 },
  });
}

function header(slide, letter, label, x, y, w, accent) {
  rect(slide, `header-${letter}-badge`, x, y, 42, 28, accent, accent, 11, 0);
  txt(slide, `header-${letter}-letter`, letter, x, y + 1, 42, 25, { size: 16, bold: true, color: C.white, align: "center" });
  txt(slide, `header-${letter}-title`, label, x + 54, y - 1, w - 54, 31, { size: 22, bold: true, color: C.ink });
  rect(slide, `header-${letter}-rule`, x, y + 39, w, 1.3, accent, accent, 0, 0);
}

function imageFrame(slide, name, bytes, alt, x, y, w, h, stroke) {
  rect(slide, `${name}-edge`, x - 2, y - 2, w + 4, h + 4, C.white, stroke, 6, 1.1);
  return slide.images.add({
    blob: bytes,
    contentType: "image/png",
    alt,
    fit: "contain",
    position: { left: x, top: y, width: w, height: h },
    geometry: "rect",
  });
}

function gridLines(slide, name, x, y, size, lineColor = C.white) {
  for (let i = 1; i < 3; i += 1) {
    rect(slide, `${name}-v-${i}`, x + (size * i) / 3, y, 1.5, size, lineColor, lineColor, 0, 0);
    rect(slide, `${name}-h-${i}`, x, y + (size * i) / 3, size, 1.5, lineColor, lineColor, 0, 0);
  }
}

function viewMap(slide, name, x, y, size, mode, accent) {
  const visible = new Set(mode === "full" ? [0, 1, 2, 3, 4, 5, 6, 7, 8] : [1, 3, 4, 5, 7]);
  const cell = size / 3;
  for (let i = 0; i < 9; i += 1) {
    const r = Math.floor(i / 3);
    const c = i % 3;
    const fill = visible.has(i) ? accent : C.hidden;
    rect(slide, `${name}-cell-${i}`, x + c * cell, y + r * cell, cell - 2, cell - 2, fill, C.white, 2, 0.8);
  }
}

function tokenStrip(slide, name, x, y, count, accent) {
  for (let i = 0; i < count; i += 1) {
    rect(slide, `${name}-token-${i}`, x + i * 25, y, 19, 18, accent, accent, 3, 0);
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
  return {
    bytes: bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength),
    width: Number(dims[1]),
    height: Number(dims[2]),
  };
}

async function formula(slide, name, latex, x, y, w, h) {
  const asset = await latexSvg(name, latex);
  const scale = Math.min(FORMULA_SCALE, w / asset.width, h / asset.height);
  const pw = asset.width * scale;
  const ph = asset.height * scale;
  slide.images.add({
    blob: asset.bytes,
    contentType: "image/svg+xml",
    alt: `LaTeX: ${latex}`,
    fit: "contain",
    position: { left: x + (w - pw) / 2, top: y + (h - ph) / 2, width: pw, height: ph },
    geometry: "rect",
  });
}

const presentation = Presentation.create({ slideSize: { width: W, height: H } });
const slide = presentation.slides.add();
slide.background.fill = C.page;
const fullBytes = await readBytes(FULL_IMAGE);

// Connector layer first: straight reading path behind the content.
arrow(slide, "connector-a-b", 484, 408, 26, 20, C.brown);
arrow(slide, "connector-b-c", 1150, 408, 26, 20, C.brown);

// Top matter.
txt(slide, "title", "RegionSuff model: visibility-conditioned DR severity inference", 48, 30, 1235, 38, { size: 30, bold: true, color: C.brown });
txt(slide, "figure-number", "FIGURE 2", 1325, 32, 225, 26, { size: 17, bold: true, color: C.olive, align: "right" });
txt(slide, "subtitle", "A fixed DR classifier is conditioned on which retinal regions remain visible; the paired analysis begins only after two severity outputs are available.", 50, 76, 1490, 24, { size: 16, color: C.rust });
rect(slide, "title-rule", 48, 112, 1504, 1.3, C.line, C.line, 0, 0);

// A. Evidence entry: a large real UWF image plus visibility maps.
header(slide, "A", "Visible retinal evidence", 48, 138, 410, C.rust);
txt(slide, "a-image-label", "One UWF image is partitioned into a 3 × 3 evidence bank", 62, 184, 382, 22, { size: 16, color: C.brown, bold: true, align: "center" });
imageFrame(slide, "a-source", fullBytes, "UWF source image partitioned into a three by three regional evidence bank.", 76, 218, 230, 230, C.rust);
gridLines(slide, "a-source-grid", 76, 218, 230);
txt(slide, "a-source-note", "A single source image\nprovides nine regional inputs.", 80, 459, 222, 42, { size: 16, color: C.muted, align: "center" });
rect(slide, "a-map-box", 322, 218, 116, 230, C.grayPale, C.line, 12, 1);
txt(slide, "a-map-head", "Visibility\nmap m", 334, 228, 92, 43, { size: 17, bold: true, color: C.olive, align: "center" });
viewMap(slide, "a-full", 344, 286, 72, "full", C.orange);
txt(slide, "a-full-text", "Full", 336, 364, 88, 18, { size: 15, bold: true, align: "center" });
viewMap(slide, "a-cross", 344, 393, 72, "cross", C.magenta);
txt(slide, "a-cross-text", "Center + cross", 328, 470, 104, 20, { size: 14, bold: true, color: C.magenta, align: "center" });
rect(slide, "a-principle", 62, 536, 376, 104, C.orangePale, C.orange, 12, 1);
txt(slide, "a-principle-head", "What changes?", 76, 548, 348, 18, { size: 17, bold: true, color: C.brown, align: "center" });
txt(slide, "a-principle-text", "The image label is fixed. Only the retinal evidence permitted to reach the classifier changes.", 84, 576, 332, 48, { size: 16, color: C.ink, align: "center" });

// B. Central mechanism: architecture, one formula, and classification output.
header(slide, "B", "Shared RegionSuff severity model", 516, 138, 612, C.olive);
txt(slide, "b-topline", "Each visible region becomes a token along one shared feature path", 530, 184, 584, 22, { size: 16, color: C.brown, bold: true, align: "center" });
rect(slide, "b-regional-input", 538, 224, 144, 102, C.grayPale, C.rust, 12, 1);
txt(slide, "b-regional-input-head", "Visible regional\ncrops", 552, 237, 116, 38, { size: 17, bold: true, color: C.rust, align: "center" });
tokenStrip(slide, "b-regional-tokens", 557, 289, 4, C.rust);
arrow(slide, "b-input-encoder", 694, 261, 26, 19, C.orange);
rect(slide, "b-encoder", 732, 224, 158, 102, C.grayPale, C.brown, 12, 1);
txt(slide, "b-encoder-head", "Frozen encoder", 746, 239, 130, 20, { size: 17, bold: true, color: C.brown, align: "center" });
txt(slide, "b-encoder-body", "RetinaRadar\nEfficientNet-B0", 746, 268, 130, 38, { size: 16, color: C.ink, align: "center" });
arrow(slide, "b-encoder-projection", 902, 261, 26, 19, C.orange);
rect(slide, "b-projection", 940, 224, 158, 102, C.orangePale, C.orange, 12, 1);
txt(slide, "b-projection-head", "Trainable projection", 954, 239, 130, 20, { size: 17, bold: true, color: C.brown, align: "center" });
txt(slide, "b-projection-body", "Regional feature tokens\n(128 dimensions)", 954, 268, 130, 38, { size: 16, color: C.ink, align: "center" });
down(slide, "b-down-attention", 802, 340, 22, 27, C.olive);
rect(slide, "b-attention", 538, 382, 560, 156, C.olivePale, C.olive, 14, 1.15);
txt(slide, "b-attention-head", "Masked attention pool", 554, 395, 528, 24, { size: 19, bold: true, color: C.olive, align: "center" });
await formula(slide, "masked_attention", "a_i(\\mathbf{m})=\\frac{m_i\\exp(e_i)}{\\sum_{j=1}^{K}m_j\\exp(e_j)}", 574, 425, 488, 46);
txt(slide, "b-attention-annotation-left", "mᵢ  visibility gate", 562, 485, 160, 22, { size: 15, bold: true, color: C.brown, align: "center" });
txt(slide, "b-attention-annotation-center", "eᵢ  regional evidence score", 722, 485, 192, 22, { size: 15, bold: true, color: C.brown, align: "center" });
txt(slide, "b-attention-annotation-right", "Normalize over visible regions only", 912, 485, 172, 22, { size: 14, italic: true, color: C.olive, align: "center" });
down(slide, "b-down-severity", 802, 548, 22, 25, C.olive);
rect(slide, "b-severity", 538, 590, 560, 118, C.grayPale, C.olive, 14, 1.1);
txt(slide, "b-severity-head", "Aggregate available evidence → DR severity probability", 558, 604, 520, 22, { size: 18, bold: true, color: C.brown, align: "center" });
rect(slide, "b-class-normal", 618, 646, 110, 34, C.white, C.orange, 11, 1);
rect(slide, "b-class-npdr", 763, 646, 110, 34, C.white, C.olive, 11, 1);
rect(slide, "b-class-pdr", 908, 646, 110, 34, C.white, C.magenta, 11, 1);
txt(slide, "b-class-normal-text", "Normal", 618, 650, 110, 22, { size: 16, bold: true, color: C.brown, align: "center" });
txt(slide, "b-class-npdr-text", "NPDR", 763, 650, 110, 22, { size: 16, bold: true, color: C.olive, align: "center" });
txt(slide, "b-class-pdr-text", "PDR", 908, 650, 110, 22, { size: 16, bold: true, color: C.magenta, align: "center" });

// C. Downstream paired audit: after the severity model, without additional equations.
header(slide, "C", "Downstream paired-view audit", 1176, 138, 376, C.magenta);
txt(slide, "c-topline", "The same fitted severity model is run twice.", 1188, 184, 352, 22, { size: 16, color: C.muted, align: "center" });
rect(slide, "c-full-card", 1188, 226, 150, 110, C.orangePale, C.orange, 12, 1);
viewMap(slide, "c-full-map", 1201, 243, 52, "full", C.orange);
txt(slide, "c-full-label", "Full view", 1263, 245, 62, 18, { size: 16, bold: true, color: C.brown, align: "center" });
txt(slide, "c-full-result", "severity output", 1263, 274, 62, 18, { size: 14, color: C.ink, align: "center" });
rect(slide, "c-limited-card", 1390, 226, 150, 110, C.magentaPale, C.magenta, 12, 1);
viewMap(slide, "c-limited-map", 1403, 243, 52, "cross", C.magenta);
txt(slide, "c-limited-label", "Center + cross", 1465, 242, 62, 24, { size: 14, bold: true, color: C.magenta, align: "center" });
txt(slide, "c-limited-result", "severity output", 1465, 274, 62, 18, { size: 14, color: C.ink, align: "center" });
down(slide, "c-down-features", 1354, 347, 24, 27, C.magenta);
rect(slide, "c-feature-box", 1188, 390, 352, 100, C.magentaPale, C.magenta, 12, 1.1);
txt(slide, "c-feature-head", "Compare the two severity outputs", 1204, 403, 320, 20, { size: 18, bold: true, color: C.magenta, align: "center" });
txt(slide, "c-feature-copy", "Probability shift  ·  severity shift\nuncertainty difference", 1204, 434, 320, 38, { size: 16, color: C.ink, align: "center" });
down(slide, "c-down-risk", 1354, 502, 24, 27, C.magenta);
rect(slide, "c-risk", 1188, 544, 352, 80, C.white, C.magenta, 12, 1.1);
txt(slide, "c-risk-head", "Rank limited-view underestimation risk", 1204, 559, 320, 22, { size: 17, bold: true, color: C.magenta, align: "center" });
txt(slide, "c-risk-note", "Exploratory paired analysis", 1204, 589, 320, 18, { size: 15, color: C.muted, italic: true, align: "center" });
rect(slide, "c-boundary", 1188, 650, 352, 58, C.grayPale, C.rust, 12, 1);
txt(slide, "c-boundary-copy", "Requires both full and limited predictions; not a single-image triage rule.", 1202, 662, 324, 32, { size: 15, color: C.rust, bold: true, align: "center" });

// Bottom takeaway.
rect(slide, "bottom-rule", 48, 750, 1504, 1.3, C.line, C.line, 0, 0);
rect(slide, "takeaway-frame", 48, 776, 1504, 58, C.grayPale, C.orange, 14, 1.1);
txt(slide, "takeaway", "Core mechanism: visibility is explicit inside severity inference; limited-view risk is assessed afterward by comparing two model outputs.", 72, 789, 1456, 28, { size: 19, bold: true, color: C.brown, align: "center" });

slide.speakerNotes.textFrame.setText(
  `[Sources]\n- UWF source image: local RegionSuff project asset.\n- Method terms and the masked-attention equation: RegionSuff_1.7.docx, Sections 2.3-2.8.\n- Narrative reference: DiSTect, Figure 1 (input data → one central model expression → downstream applications).\n- Formula rendering: CodeCogs LaTeX-to-SVG; the vector equation is embedded in this PPTX.\n\n[LaTeX source]\n${latexSources.map(({ name, latex }) => `${name}: ${latex}`).join("\n")}\n\nDesign decision: Figure 2 intentionally contains one core equation only. All remaining mathematical definitions remain in the Methods and are represented here as module operations.`
);
slide.speakerNotes.setVisible(true);

await writeBlob(PREVIEW, await presentation.export({ slide, format: "png", scale: 2 }));
await fs.writeFile(LAYOUT, await (await slide.export({ format: "layout" })).text());
const pptx = await PresentationFile.exportPptx(presentation);
await pptx.save(FINAL_PPTX);
console.log(JSON.stringify({ finalPptx: FINAL_PPTX, preview: PREVIEW, layout: LAYOUT }, null, 2));
