import fs from "node:fs/promises";
import path from "node:path";
import sharp from "sharp";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const BUILD = "/Users/tongyue/Documents/77f /7hao/paper_design/figure2_real_retina_revision";
const ASSET_DIR = path.join(BUILD, "assets");
const FINAL_PPTX = "/Users/tongyue/Documents/ppf/第四论文/图2_真实眼底原图版.pptx";
const PREVIEW = path.join(BUILD, "figure2-real-retina-preview.png");
const LAYOUT = path.join(BUILD, "figure2-real-retina.layout.json");
const FORMULA_DIR = path.join(BUILD, "latex");
const SOURCE_IMAGE = "/Users/tongyue/Documents/77f /7hao/paper_design/figure2_rebuild/figure1_style_inventory/template-inspect/assets/ppt/media/image.png";

const W = 1600;
const H = 900;
const FONT = "Times New Roman";
const FORMULA_SCALE = 1.62;
const C = {
  page: "#FFFDF8", ink: "#332720", brown: "#704C2B", rust: "#965E4A",
  orange: "#C68A32", orangePale: "#F6E5CD", olive: "#78866B", olivePale: "#EDF1E8",
  magenta: "#B84067", magentaPale: "#F9EDF1", line: "#D8CABB", muted: "#6F6259",
  grayPale: "#F4F0EA", white: "#FFFFFF",
};
const latexSources = [];

async function writeBlob(filePath, blob) {
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

async function bytes(filePath) {
  const buffer = await fs.readFile(filePath);
  return buffer.buffer.slice(buffer.byteOffset, buffer.byteOffset + buffer.byteLength);
}

function rect(slide, name, x, y, w, h, fill = "none", stroke = "none", radius = 0, width = 0) {
  return slide.shapes.add({
    geometry: radius ? "roundRect" : "rect", name,
    position: { left: x, top: y, width: w, height: h }, fill,
    line: { style: "solid", fill: stroke, width }, borderRadius: radius || undefined,
  });
}

function txt(slide, name, value, x, y, w, h, opts = {}) {
  const shape = rect(slide, name, x, y, w, h, "none", "none", 0, 0);
  shape.text = value;
  shape.text.style = {
    typeface: opts.typeface ?? FONT, fontSize: opts.size ?? 17, color: opts.color ?? C.ink,
    bold: opts.bold ?? false, italic: opts.italic ?? false, alignment: opts.align ?? "left",
    verticalAlignment: opts.valign ?? "middle", lineSpacing: opts.lineSpacing ?? 0.92,
    insets: opts.insets ?? { top: 0, right: 0, bottom: 0, left: 0 }, autoFit: "none", wrap: "square",
  };
  return shape;
}

function arrow(slide, name, x, y, w, h, color) {
  return slide.shapes.add({ geometry: "rightArrow", name, position: { left: x, top: y, width: w, height: h }, fill: color, line: { style: "solid", fill: color, width: 0 } });
}

function down(slide, name, x, y, w, h, color) {
  return slide.shapes.add({ geometry: "downArrow", name, position: { left: x, top: y, width: w, height: h }, fill: color, line: { style: "solid", fill: color, width: 0 } });
}

function header(slide, letter, label, x, y, w, accent) {
  rect(slide, `header-${letter}-badge`, x, y, 42, 28, accent, accent, 11, 0);
  txt(slide, `header-${letter}-letter`, letter, x, y + 1, 42, 25, { size: 16, bold: true, color: C.white, align: "center" });
  txt(slide, `header-${letter}-title`, label, x + 54, y - 1, w - 54, 31, { size: 22, bold: true, color: C.ink });
  rect(slide, `header-${letter}-rule`, x, y + 39, w, 1.3, accent, accent, 0, 0);
}

function imageFrame(slide, name, blob, alt, x, y, w, h, stroke) {
  rect(slide, `${name}-edge`, x - 2, y - 2, w + 4, h + 4, C.white, stroke, 5, 1.1);
  return slide.images.add({ blob, contentType: "image/png", alt, fit: "contain", position: { left: x, top: y, width: w, height: h }, geometry: "rect" });
}

function gridSvg(width, height) {
  const s = width / 3;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}"><g stroke="#FFFFFF" stroke-width="3"><path d="M ${s} 0 V ${height} M ${2 * s} 0 V ${height} M 0 ${s} H ${width} M 0 ${2 * s} H ${width}"/></g></svg>`;
}

function crossMaskSvg(width, height) {
  const s = width / 3;
  const hidden = [[0, 0], [2, 0], [0, 2], [2, 2]];
  const overlays = hidden.map(([cx, cy]) => `<rect x="${cx * s}" y="${cy * s}" width="${s}" height="${s}" fill="#000000" fill-opacity="0.98"/>`).join("");
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}">${overlays}<g stroke="#FFFFFF" stroke-width="3"><path d="M ${s} 0 V ${height} M ${2 * s} 0 V ${height} M 0 ${s} H ${width} M 0 ${2 * s} H ${width}"/></g></svg>`;
}

async function prepareRetinaAssets() {
  await fs.mkdir(ASSET_DIR, { recursive: true });
  const meta = await sharp(SOURCE_IMAGE).metadata();
  const imageW = meta.width ?? 512;
  const imageH = meta.height ?? 512;
  if (imageW !== imageH) throw new Error(`Expected square UWF source image, received ${imageW}×${imageH}.`);

  const target = 512;
  const source = sharp(SOURCE_IMAGE).resize(target, target, { fit: "fill" });
  const fullGrid = path.join(ASSET_DIR, "raw_uwf_full_grid.png");
  const cross = path.join(ASSET_DIR, "raw_uwf_center_cross.png");
  const rawFull = path.join(ASSET_DIR, "raw_uwf_full.png");
  const cropTop = path.join(ASSET_DIR, "raw_crop_top_middle.png");
  const cropCenter = path.join(ASSET_DIR, "raw_crop_center.png");
  const cropRight = path.join(ASSET_DIR, "raw_crop_middle_right.png");

  await sharp(SOURCE_IMAGE).resize(target, target, { fit: "fill" }).png().toFile(rawFull);
  await source.clone().composite([{ input: Buffer.from(gridSvg(target, target)), top: 0, left: 0 }]).png().toFile(fullGrid);
  await source.clone().composite([{ input: Buffer.from(crossMaskSvg(target, target)), top: 0, left: 0 }]).png().toFile(cross);

  const cell = Math.floor(target / 3);
  await sharp(SOURCE_IMAGE).resize(target, target, { fit: "fill" }).extract({ left: cell, top: 0, width: cell, height: cell }).png().toFile(cropTop);
  await sharp(SOURCE_IMAGE).resize(target, target, { fit: "fill" }).extract({ left: cell, top: cell, width: cell, height: cell }).png().toFile(cropCenter);
  await sharp(SOURCE_IMAGE).resize(target, target, { fit: "fill" }).extract({ left: cell * 2, top: cell, width: target - cell * 2, height: cell }).png().toFile(cropRight);

  return { rawFull, fullGrid, cross, cropTop, cropCenter, cropRight };
}

async function latexSvg(name, latex) {
  await fs.mkdir(FORMULA_DIR, { recursive: true });
  const query = `\\dpi{220}\\displaystyle ${latex}`;
  const response = await fetch(`https://latex.codecogs.com/svg.image?${encodeURIComponent(query)}`);
  if (!response.ok) throw new Error(`LaTeX renderer failed for ${name}: ${response.status}`);
  const svg = await response.text();
  const dims = svg.match(/width='([0-9.]+)pt' height='([0-9.]+)pt'/);
  if (!dims) throw new Error(`LaTeX renderer did not return dimensions for ${name}.`);
  await fs.writeFile(path.join(FORMULA_DIR, `${name}.svg`), svg, "utf8");
  latexSources.push({ name, latex });
  const imageBytes = Buffer.from(svg, "utf8");
  return { bytes: imageBytes.buffer.slice(imageBytes.byteOffset, imageBytes.byteOffset + imageBytes.byteLength), width: Number(dims[1]), height: Number(dims[2]) };
}

async function formula(slide, name, latex, x, y, w, h) {
  const asset = await latexSvg(name, latex);
  const scale = Math.min(FORMULA_SCALE, w / asset.width, h / asset.height);
  const pw = asset.width * scale;
  const ph = asset.height * scale;
  slide.images.add({ blob: asset.bytes, contentType: "image/svg+xml", alt: `LaTeX: ${latex}`, fit: "contain", position: { left: x + (w - pw) / 2, top: y + (h - ph) / 2, width: pw, height: ph }, geometry: "rect" });
}

const paths = await prepareRetinaAssets();
const [fullGridBytes, crossBytes, cropTopBytes, cropCenterBytes, cropRightBytes] = await Promise.all([
  bytes(paths.fullGrid), bytes(paths.cross), bytes(paths.cropTop), bytes(paths.cropCenter), bytes(paths.cropRight),
]);

const presentation = Presentation.create({ slideSize: { width: W, height: H } });
const slide = presentation.slides.add();
slide.background.fill = C.page;

// Connector layer behind every module.
arrow(slide, "connector-a-b", 484, 408, 26, 20, C.brown);
arrow(slide, "connector-b-c", 1150, 408, 26, 20, C.brown);

// Title.
txt(slide, "title", "RegionSuff model: visibility-conditioned DR severity inference", 48, 30, 1235, 38, { size: 30, bold: true, color: C.brown });
txt(slide, "figure-number", "FIGURE 2", 1325, 32, 225, 26, { size: 17, bold: true, color: C.olive, align: "right" });
txt(slide, "subtitle", "The same raw UWF image is used to show which retinal evidence remains available to the fixed DR classifier.", 50, 76, 1490, 24, { size: 16, color: C.rust });
rect(slide, "title-rule", 48, 112, 1504, 1.3, C.line, C.line, 0, 0);

// A. Real source image, then two true masked views of the same image.
header(slide, "A", "Visible retinal evidence", 48, 138, 410, C.rust);
txt(slide, "a-label", "Raw UWF image, divided into a 3 × 3 evidence bank", 62, 184, 382, 22, { size: 16, color: C.brown, bold: true, align: "center" });
imageFrame(slide, "a-source", fullGridBytes, "Original UWF fundus image from the dataset, overlaid with a three by three grid.", 66, 218, 226, 226, C.rust);
txt(slide, "a-source-note", "The raw image supplies the same nine regional inputs in every view.", 68, 456, 220, 40, { size: 15, color: C.muted, align: "center" });
rect(slide, "a-view-box", 310, 218, 132, 278, C.grayPale, C.line, 12, 1);
txt(slide, "a-view-head", "Visibility map m", 320, 228, 112, 20, { size: 17, bold: true, color: C.olive, align: "center" });
imageFrame(slide, "a-view-full", fullGridBytes, "Full view from the same UWF source image.", 332, 260, 88, 88, C.orange);
txt(slide, "a-view-full-label", "Full view", 318, 354, 116, 18, { size: 15, bold: true, color: C.brown, align: "center" });
imageFrame(slide, "a-view-cross", crossBytes, "Center plus cross view created by masking four corner regions of the same UWF source image.", 332, 390, 88, 88, C.magenta);
txt(slide, "a-view-cross-label", "Center + cross", 316, 483, 120, 18, { size: 14, bold: true, color: C.magenta, align: "center" });
rect(slide, "a-principle", 62, 540, 376, 100, C.orangePale, C.orange, 12, 1);
txt(slide, "a-principle-head", "Controlled evidence loss", 76, 551, 348, 20, { size: 17, bold: true, color: C.brown, align: "center" });
txt(slide, "a-principle-copy", "The DR label is fixed; black tiles mark retinal evidence excluded by the visibility mask.", 82, 580, 336, 42, { size: 16, color: C.ink, align: "center" });

// B. The central mechanism: true regional image crops replace abstract token squares.
header(slide, "B", "Shared RegionSuff severity model", 516, 138, 612, C.olive);
txt(slide, "b-topline", "Each visible crop becomes a regional feature token along one shared path", 530, 184, 584, 22, { size: 16, color: C.brown, bold: true, align: "center" });
rect(slide, "b-crops", 534, 220, 188, 112, C.grayPale, C.rust, 12, 1);
txt(slide, "b-crops-head", "Visible regional crops", 544, 230, 168, 19, { size: 17, bold: true, color: C.rust, align: "center" });
imageFrame(slide, "b-crop-top", cropTopBytes, "Actual top-middle retinal crop from the UWF source image.", 552, 263, 45, 45, C.rust);
imageFrame(slide, "b-crop-center", cropCenterBytes, "Actual center retinal crop from the UWF source image.", 607, 263, 45, 45, C.rust);
imageFrame(slide, "b-crop-right", cropRightBytes, "Actual middle-right retinal crop from the UWF source image.", 662, 263, 45, 45, C.rust);
arrow(slide, "b-crops-encoder", 730, 260, 26, 19, C.orange);
rect(slide, "b-encoder", 768, 220, 150, 112, C.grayPale, C.brown, 12, 1);
txt(slide, "b-encoder-head", "Frozen encoder", 782, 238, 122, 20, { size: 17, bold: true, color: C.brown, align: "center" });
txt(slide, "b-encoder-copy", "RetinaRadar\nEfficientNet-B0", 782, 269, 122, 36, { size: 16, color: C.ink, align: "center" });
arrow(slide, "b-encoder-projection", 930, 260, 26, 19, C.orange);
rect(slide, "b-projection", 968, 220, 130, 112, C.orangePale, C.orange, 12, 1);
txt(slide, "b-projection-head", "Trainable\nprojection", 982, 233, 102, 38, { size: 17, bold: true, color: C.brown, align: "center" });
txt(slide, "b-projection-copy", "128-D regional\nfeature tokens", 982, 278, 102, 32, { size: 15, color: C.ink, align: "center" });
down(slide, "b-down-attention", 802, 346, 22, 26, C.olive);
rect(slide, "b-attention", 538, 384, 560, 154, C.olivePale, C.olive, 14, 1.15);
txt(slide, "b-attention-head", "Masked attention pool", 554, 397, 528, 24, { size: 19, bold: true, color: C.olive, align: "center" });
await formula(slide, "masked_attention", "a_i(\\mathbf{m})=\\frac{m_i\\exp(e_i)}{\\sum_{j=1}^{K}m_j\\exp(e_j)}", 574, 427, 488, 46);
txt(slide, "b-attention-left", "mᵢ: visibility gate", 560, 486, 150, 22, { size: 15, bold: true, color: C.brown, align: "center" });
txt(slide, "b-attention-mid", "eᵢ: regional evidence score", 715, 486, 192, 22, { size: 15, bold: true, color: C.brown, align: "center" });
txt(slide, "b-attention-right", "Normalize only across visible regions", 905, 486, 178, 28, { size: 14, italic: true, color: C.olive, align: "center" });
down(slide, "b-down-output", 802, 548, 22, 25, C.olive);
rect(slide, "b-output", 538, 590, 560, 118, C.grayPale, C.olive, 14, 1.1);
txt(slide, "b-output-title", "Aggregate available evidence → DR severity probability", 558, 604, 520, 22, { size: 18, bold: true, color: C.brown, align: "center" });
rect(slide, "b-normal", 618, 646, 110, 34, C.white, C.orange, 11, 1);
rect(slide, "b-npdr", 763, 646, 110, 34, C.white, C.olive, 11, 1);
rect(slide, "b-pdr", 908, 646, 110, 34, C.white, C.magenta, 11, 1);
txt(slide, "b-normal-text", "Normal", 618, 650, 110, 22, { size: 16, bold: true, color: C.brown, align: "center" });
txt(slide, "b-npdr-text", "NPDR", 763, 650, 110, 22, { size: 16, bold: true, color: C.olive, align: "center" });
txt(slide, "b-pdr-text", "PDR", 908, 650, 110, 22, { size: 16, bold: true, color: C.magenta, align: "center" });

// C. The paired input thumbnails are likewise real complete and masked UWF images.
header(slide, "C", "Downstream paired-view audit", 1176, 138, 376, C.magenta);
txt(slide, "c-topline", "The same fitted severity model evaluates two real views.", 1188, 184, 352, 22, { size: 16, color: C.muted, align: "center" });
rect(slide, "c-full-card", 1188, 220, 150, 124, C.orangePale, C.orange, 12, 1);
imageFrame(slide, "c-full-image", fullGridBytes, "Full UWF input for one pass through the fitted severity model.", 1228, 232, 70, 70, C.orange);
txt(slide, "c-full-label", "Full-view severity output", 1198, 308, 130, 20, { size: 15, bold: true, color: C.brown, align: "center" });
rect(slide, "c-limited-card", 1390, 220, 150, 124, C.magentaPale, C.magenta, 12, 1);
imageFrame(slide, "c-limited-image", crossBytes, "Center plus cross UWF input for the second pass through the same fitted severity model.", 1430, 232, 70, 70, C.magenta);
txt(slide, "c-limited-label", "Center + cross severity output", 1400, 308, 130, 20, { size: 14, bold: true, color: C.magenta, align: "center" });
down(slide, "c-down-compare", 1354, 356, 24, 26, C.magenta);
rect(slide, "c-compare", 1188, 398, 352, 100, C.magentaPale, C.magenta, 12, 1.1);
txt(slide, "c-compare-title", "Compare the two severity outputs", 1204, 411, 320, 20, { size: 18, bold: true, color: C.magenta, align: "center" });
txt(slide, "c-compare-copy", "Probability shift  ·  severity shift\nuncertainty difference", 1204, 442, 320, 38, { size: 16, color: C.ink, align: "center" });
down(slide, "c-down-risk", 1354, 510, 24, 26, C.magenta);
rect(slide, "c-risk", 1188, 552, 352, 78, C.white, C.magenta, 12, 1.1);
txt(slide, "c-risk-title", "Rank limited-view underestimation risk", 1204, 566, 320, 22, { size: 17, bold: true, color: C.magenta, align: "center" });
txt(slide, "c-risk-note", "Exploratory paired analysis", 1204, 596, 320, 18, { size: 15, color: C.muted, italic: true, align: "center" });
rect(slide, "c-boundary", 1188, 650, 352, 58, C.grayPale, C.rust, 12, 1);
txt(slide, "c-boundary-copy", "Requires both full and limited predictions; not a single-image triage rule.", 1202, 662, 324, 32, { size: 15, color: C.rust, bold: true, align: "center" });

// Takeaway.
rect(slide, "bottom-rule", 48, 750, 1504, 1.3, C.line, C.line, 0, 0);
rect(slide, "takeaway-frame", 48, 776, 1504, 58, C.grayPale, C.orange, 14, 1.1);
txt(slide, "takeaway", "Core mechanism: the same UWF image yields different inferences when different retinal evidence is visible; paired risk is computed only after two severity outputs exist.", 72, 789, 1456, 28, { size: 19, bold: true, color: C.brown, align: "center" });

slide.speakerNotes.textFrame.setText(
  `[Sources]\n- All UWF thumbnails in panels A-C are derived from the same local UWF source image in the RegionSuff project assets.\n- Method terminology and masked-attention equation: RegionSuff_1.8.docx, Sections 2.3-2.8.\n- Formula rendering: CodeCogs LaTeX-to-SVG; all equation paths are embedded.\n\n[LaTeX source]\n${latexSources.map(({ name, latex }) => `${name}: ${latex}`).join("\n")}\n\nDesign note: all former colored token and view placeholders were replaced by raw UWF full-view, masked-view, or regional-crop images. Black regions identify evidence excluded by the corresponding visibility mask.`
);
slide.speakerNotes.setVisible(true);

await writeBlob(PREVIEW, await presentation.export({ slide, format: "png", scale: 2 }));
await fs.writeFile(LAYOUT, await (await slide.export({ format: "layout" })).text());
const pptx = await PresentationFile.exportPptx(presentation);
await pptx.save(FINAL_PPTX);
console.log(JSON.stringify({ finalPptx: FINAL_PPTX, preview: PREVIEW, assets: paths }, null, 2));
