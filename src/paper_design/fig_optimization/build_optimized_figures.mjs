import fs from "node:fs/promises";
import path from "node:path";
import sharp from "sharp";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const BUILD = "/Users/tongyue/Documents/77f /7hao/paper_design/fig_optimization";
const OUT_DIR = "/Users/tongyue/Documents/ppf/第四论文";
const FIG1_OUT = path.join(OUT_DIR, "图1_术语统一版.pptx");
const FIG2_OUT = path.join(OUT_DIR, "图2_术语统一版.pptx");
const ASSETS = path.join(BUILD, "assets");
const SOURCE = "/Users/tongyue/Documents/77f /7hao/paper_design/figure2_rebuild/figure1_style_inventory/template-inspect/assets/ppt/media/image.png";
const FORMULA_SVG = "/Users/tongyue/Documents/77f /7hao/paper_design/figure2_real_retina_revision/latex/masked_attention.svg";

const W = 1600;
const H = 900;
const FONT = "Times New Roman";
const C = {
  page: "#FFFDF8", ink: "#332720", brown: "#704C2B", rust: "#965E4A",
  orange: "#C68A32", orangePale: "#F8E7CD", olive: "#78866B", olivePale: "#EDF1E8",
  magenta: "#B84067", magentaPale: "#F9EDF1", line: "#D8CABB", muted: "#6F6259",
  grayPale: "#F4F0EA", black: "#000000", white: "#FFFFFF",
};

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
    typeface: opts.typeface ?? FONT,
    fontSize: opts.size ?? 17,
    color: opts.color ?? C.ink,
    bold: opts.bold ?? false,
    italic: opts.italic ?? false,
    alignment: opts.align ?? "left",
    verticalAlignment: opts.valign ?? "middle",
    lineSpacing: opts.lineSpacing ?? 0.94,
    insets: opts.insets ?? { top: 0, right: 0, bottom: 0, left: 0 },
    autoFit: "none",
    wrap: "square",
  };
  return shape;
}

function arrow(slide, name, x, y, w, h, color) {
  return slide.shapes.add({
    geometry: "rightArrow", name, position: { left: x, top: y, width: w, height: h }, fill: color,
    line: { style: "solid", fill: color, width: 0 },
  });
}

function down(slide, name, x, y, w, h, color) {
  return slide.shapes.add({
    geometry: "downArrow", name, position: { left: x, top: y, width: w, height: h }, fill: color,
    line: { style: "solid", fill: color, width: 0 },
  });
}

function imageFrame(slide, name, blob, alt, x, y, w, h, stroke) {
  rect(slide, `${name}-edge`, x - 2, y - 2, w + 4, h + 4, C.white, stroke, 5, 1.15);
  return slide.images.add({
    blob, contentType: "image/png", alt, fit: "contain",
    position: { left: x, top: y, width: w, height: h }, geometry: "rect",
  });
}

function smallImageLabel(slide, name, label, x, y, w, color = C.ink) {
  txt(slide, name, label, x, y, w, 34, { size: 14.5, bold: true, color, align: "center", lineSpacing: 0.9 });
}

function header(slide, letter, title, x, y, w, accent) {
  rect(slide, `header-${letter}-badge`, x, y, 40, 28, accent, accent, 11, 0);
  txt(slide, `header-${letter}-letter`, letter, x, y + 1, 40, 24, { size: 15.5, bold: true, color: C.white, align: "center" });
  txt(slide, `header-${letter}-title`, title, x + 54, y - 1, w - 54, 31, { size: 22, bold: true, color: C.ink });
  rect(slide, `header-${letter}-rule`, x, y + 39, w, 1.2, accent, accent, 0, 0);
}

function titleBlock(slide, title, figureNumber, subtitle) {
  txt(slide, "title", title, 48, 30, 1260, 38, { size: 30, bold: true, color: C.brown });
  txt(slide, "figure-number", figureNumber, 1325, 32, 225, 26, { size: 17, bold: true, color: C.olive, align: "right" });
  txt(slide, "subtitle", subtitle, 50, 76, 1492, 24, { size: 16, color: C.rust });
  rect(slide, "title-rule", 48, 112, 1504, 1.2, C.line, C.line, 0, 0);
}

function maskSvg(kind, size) {
  const cell = size / 3;
  const grid = `<g stroke="#FFFFFF" stroke-width="3"><path d="M ${cell} 0 V ${size} M ${2 * cell} 0 V ${size} M 0 ${cell} H ${size} M 0 ${2 * cell} H ${size}"/></g>`;
  if (kind === "full") return `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}">${grid}</svg>`;
  if (kind === "center") {
    const cells = [];
    for (let y = 0; y < 3; y += 1) for (let x = 0; x < 3; x += 1) if (!(x === 1 && y === 1)) cells.push(`<rect x="${x * cell}" y="${y * cell}" width="${cell}" height="${cell}" fill="#000000" fill-opacity="0.98"/>`);
    return `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}">${cells.join("")}${grid}</svg>`;
  }
  const hidden = [[0, 0], [2, 0], [0, 2], [2, 2]].map(([x, y]) => `<rect x="${x * cell}" y="${y * cell}" width="${cell}" height="${cell}" fill="#000000" fill-opacity="0.98"/>`).join("");
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}">${hidden}${grid}</svg>`;
}

function apertureSvg(kind, size, f) {
  const dim = size * f;
  const x = (size - dim) / 2;
  const y = x;
  let mask = "";
  if (kind === "circle") {
    const r = (f / Math.sqrt(Math.PI)) * size;
    mask = `<circle cx="${size / 2}" cy="${size / 2}" r="${r}" fill="#000000" fill-opacity="0"/><rect width="${size}" height="${size}" fill="#000000" fill-opacity="0.82"/><circle cx="${size / 2}" cy="${size / 2}" r="${r}" fill="#FFFFFF" fill-opacity="1" style="mix-blend-mode:destination-out"/>`;
  } else {
    mask = `<rect width="${size}" height="${size}" fill="#000000" fill-opacity="0.82"/><rect x="${x}" y="${y}" width="${dim}" height="${dim}" fill="#FFFFFF" fill-opacity="1" style="mix-blend-mode:destination-out"/>`;
  }
  // SVG masking with destination-out is not consistently supported by all rasterizers, so a second mask is supplied in sharp composites.
  return mask;
}

async function makeAperture(base, type, f, outPath) {
  const size = 512;
  const overlay = Buffer.alloc(size * size * 4, 0);
  const side = Math.round(size * f);
  const offset = Math.floor((size - side) / 2);
  if (type === "circle") {
    const r = (f / Math.sqrt(Math.PI)) * size;
    const c = (size - 1) / 2;
    for (let yy = 0; yy < size; yy += 1) for (let xx = 0; xx < size; xx += 1) {
      const index = 4 * (yy * size + xx);
      overlay[index + 3] = (xx - c) ** 2 + (yy - c) ** 2 <= r ** 2 ? 0 : 214;
    }
  } else {
    for (let yy = 0; yy < size; yy += 1) for (let xx = 0; xx < size; xx += 1) {
      const index = 4 * (yy * size + xx);
      overlay[index + 3] = xx >= offset && xx < offset + side && yy >= offset && yy < offset + side ? 0 : 214;
    }
  }
  await sharp(base).resize(size, size).composite([
    { input: overlay, raw: { width: size, height: size, channels: 4 }, top: 0, left: 0 },
  ]).png().toFile(outPath);
}

async function createAssets() {
  await fs.mkdir(ASSETS, { recursive: true });
  const base = path.join(ASSETS, "raw.png");
  const full = path.join(ASSETS, "full.png");
  const center = path.join(ASSETS, "center.png");
  const cross = path.join(ASSETS, "cross.png");
  const rect055 = path.join(ASSETS, "rect055.png");
  const circle055 = path.join(ASSETS, "circle055.png");
  const rect035 = path.join(ASSETS, "rect035.png");
  const cropTop = path.join(ASSETS, "crop_top.png");
  const cropCenter = path.join(ASSETS, "crop_center.png");
  const cropRight = path.join(ASSETS, "crop_right.png");
  const size = 512;
  const cell = Math.floor(size / 3);
  await sharp(SOURCE).resize(size, size).png().toFile(base);
  await sharp(base).composite([{ input: Buffer.from(maskSvg("full", size)), top: 0, left: 0 }]).png().toFile(full);
  await sharp(base).composite([{ input: Buffer.from(maskSvg("center", size)), top: 0, left: 0 }]).png().toFile(center);
  await sharp(base).composite([{ input: Buffer.from(maskSvg("cross", size)), top: 0, left: 0 }]).png().toFile(cross);
  await makeAperture(base, "rect", 0.55, rect055);
  await makeAperture(base, "circle", 0.55, circle055);
  await makeAperture(base, "rect", 0.35, rect035);
  await sharp(base).extract({ left: cell, top: 0, width: cell, height: cell }).png().toFile(cropTop);
  await sharp(base).extract({ left: cell, top: cell, width: cell, height: cell }).png().toFile(cropCenter);
  await sharp(base).extract({ left: cell * 2, top: cell, width: size - cell * 2, height: cell }).png().toFile(cropRight);
  return { base, full, center, cross, rect055, circle055, rect035, cropTop, cropCenter, cropRight };
}

async function addFormula(slide, svgBytes, x, y, w, h) {
  slide.images.add({ blob: svgBytes, contentType: "image/svg+xml", alt: "LaTeX: a_i(m) = m_i exp(e_i) / sum_j m_j exp(e_j)", fit: "contain", position: { left: x, top: y, width: w, height: h }, geometry: "rect" });
}

function addNotes(slide, title, body) {
  slide.speakerNotes.textFrame.setText(`[Sources]\n- ${title}\n- ${body}\n- Source image: one local de-identified UWF fundus image in the RegionSuff project assets.\n- Method labels and cohort counts: RegionSuff_1.9.docx, Methods Sections 2.3–2.8.`);
  slide.speakerNotes.setVisible(true);
}

async function buildFigure1(img) {
  const [full, center, cross, rect055, circle055, rect035] = await Promise.all([bytes(img.full), bytes(img.center), bytes(img.cross), bytes(img.rect055), bytes(img.circle055), bytes(img.rect035)]);
  const presentation = Presentation.create({ slideSize: { width: W, height: H } });
  const slide = presentation.slides.add();
  slide.background.fill = C.page;
  // Connector layer first: establishes a single left-to-right study logic behind the panels.
  arrow(slide, "a-to-b", 386, 432, 24, 18, C.brown);
  arrow(slide, "b-to-c", 780, 432, 24, 18, C.brown);
  arrow(slide, "c-to-d", 1172, 432, 24, 18, C.brown);

  titleBlock(slide, "RegionSuff: auditing model-specific evidence availability under limited fields of view", "FIGURE 1", "A clear acquisition may still omit retinal evidence; RegionSuff makes model-specific evidence availability explicit and testable.");

  header(slide, "A", "Quality is not evidence", 48, 138, 320, C.rust);
  txt(slide, "a-caption", "Same source image; different visible retinal evidence", 60, 184, 296, 22, { size: 16, color: C.brown, bold: true, align: "center" });
  imageFrame(slide, "a-full", full, "Full UWF image from the data asset with a 3 by 3 regional grid.", 70, 218, 120, 120, C.rust);
  imageFrame(slide, "a-center", center, "Center-only UWF view from exactly the same source image.", 220, 218, 120, 120, C.magenta);
  smallImageLabel(slide, "a-full-label", "Full field", 70, 343, 120, C.brown);
  smallImageLabel(slide, "a-center-label", "Center-only view", 220, 343, 120, C.magenta);
  rect(slide, "a-statement", 62, 405, 286, 78, C.orangePale, C.orange, 12, 1);
  txt(slide, "a-statement-head", "Clear retina ≠ evidence availability", 75, 416, 260, 19, { size: 16.5, bold: true, color: C.brown, align: "center" });
  txt(slide, "a-statement-copy", "A clear acquisition can still omit retinal evidence needed by the fixed DR model.", 77, 443, 256, 30, { size: 15.5, color: C.ink, align: "center" });
  rect(slide, "a-question", 62, 544, 286, 118, C.grayPale, C.rust, 12, 1);
  txt(slide, "a-question-head", "Audit question", 76, 558, 258, 19, { size: 16.5, bold: true, color: C.rust, align: "center" });
  txt(slide, "a-question-copy", "How does a fixed DR model behave as model-specific retinal evidence availability is restricted?", 78, 588, 254, 58, { size: 17, color: C.ink, align: "center", lineSpacing: 0.98 });

  header(slide, "B", "Controlled masks", 412, 138, 344, C.orange);
  txt(slide, "b-regions-label", "Regional topology", 424, 184, 320, 20, { size: 16, bold: true, color: C.brown, align: "left" });
  imageFrame(slide, "b-full", full, "Full regional view from the same source UWF image.", 430, 218, 82, 82, C.orange);
  imageFrame(slide, "b-center", center, "Center-only regional view from the same source UWF image.", 540, 218, 82, 82, C.magenta);
  imageFrame(slide, "b-cross", cross, "Center plus cross regional view from the same source UWF image.", 650, 218, 82, 82, C.olive);
  smallImageLabel(slide, "b-full-label", "Full", 425, 306, 92, C.brown);
  smallImageLabel(slide, "b-center-label", "Center", 535, 306, 92, C.magenta);
  smallImageLabel(slide, "b-cross-label", "Center +\ncross", 645, 302, 92, C.olive);
  rect(slide, "b-divider", 424, 354, 320, 1.2, C.line, C.line, 0, 0);
  txt(slide, "b-aperture-label", "Pixel-space apertures", 424, 372, 320, 20, { size: 16, bold: true, color: C.brown, align: "left" });
  imageFrame(slide, "b-rect", rect055, "Same UWF source image with a centered rectangle aperture, f equals 0.55.", 430, 404, 82, 82, C.orange);
  imageFrame(slide, "b-circle", circle055, "Same UWF source image with an area-matched circle aperture, f equals 0.55.", 540, 404, 82, 82, C.orange);
  imageFrame(slide, "b-severe", rect035, "Same UWF source image with a severe rectangle aperture, f equals 0.35.", 650, 404, 82, 82, C.magenta);
  smallImageLabel(slide, "b-rect-label", "Centered rect.\nf = 0.55", 424, 491, 94, C.brown);
  smallImageLabel(slide, "b-circle-label", "Matched circle\nf = 0.55", 534, 491, 94, C.brown);
  smallImageLabel(slide, "b-severe-label", "Severe rect.\nf = 0.35", 644, 491, 94, C.magenta);
  rect(slide, "b-control", 424, 588, 320, 70, C.orangePale, C.orange, 12, 1);
  txt(slide, "b-control-copy", "Source DR label fixed; available evidence changes by area, location, shape, or topology.", 440, 601, 288, 44, { size: 15.5, color: C.brown, bold: true, align: "center" });

  header(slide, "C", "Masked regional inference", 804, 138, 344, C.olive);
  txt(slide, "c-intro", "Only regions marked visible enter the model", 816, 184, 320, 22, { size: 16, color: C.brown, bold: true, align: "center" });
  imageFrame(slide, "c-image", full, "Source UWF image partitioned as the 3 by 3 regional evidence bank.", 850, 220, 128, 128, C.olive);
  rect(slide, "c-mask", 1000, 222, 116, 126, C.olivePale, C.olive, 12, 1);
  txt(slide, "c-mask-title", "Visibility mask", 1012, 236, 92, 20, { size: 16.5, bold: true, color: C.olive, align: "center" });
  txt(slide, "c-mask-copy", "Selects visible\nevidence", 1012, 274, 92, 40, { size: 15.5, color: C.ink, align: "center" });
  down(slide, "c-down-one", 973, 364, 22, 26, C.olive);
  rect(slide, "c-aggregation", 824, 404, 304, 94, C.olivePale, C.olive, 12, 1);
  txt(slide, "c-aggregation-title", "Visibility-conditioned aggregation", 842, 416, 268, 22, { size: 17, bold: true, color: C.olive, align: "center" });
  txt(slide, "c-aggregation-copy", "Unavailable regions contribute zero evidence; visible regions are combined for DR severity inference.", 846, 446, 260, 38, { size: 15.5, color: C.ink, align: "center" });
  down(slide, "c-down-two", 973, 512, 22, 26, C.olive);
  // Layered output block: title, a quiet descriptor, then three equal class capsules.
  // Symmetric 28 px side margins and 20 px inter-capsule gaps prevent the classes
  // from visually competing with one another or the preceding aggregation module.
  rect(slide, "c-output", 820, 548, 312, 122, C.grayPale, C.olive, 14, 1.1);
  txt(slide, "c-output-title", "Three-class DR severity prediction", 836, 561, 280, 24, { size: 18, bold: true, color: C.brown, align: "center" });
  rect(slide, "c-output-rule", 846, 592, 260, 1, C.line, C.line, 0, 0);
  txt(slide, "c-output-subtitle", "Predicted class", 848, 598, 256, 16, { size: 14.5, italic: true, color: C.olive, align: "center" });
  rect(slide, "c-normal-pill", 848, 625, 72, 30, C.white, C.orange, 10, 1);
  rect(slide, "c-npdr-pill", 940, 625, 72, 30, C.white, C.olive, 10, 1);
  rect(slide, "c-pdr-pill", 1032, 625, 72, 30, C.white, C.magenta, 10, 1);
  txt(slide, "c-normal-text", "Normal", 848, 629, 72, 18, { size: 15.5, bold: true, color: C.brown, align: "center" });
  txt(slide, "c-npdr-text", "NPDR", 940, 629, 72, 18, { size: 15.5, bold: true, color: C.olive, align: "center" });
  txt(slide, "c-pdr-text", "PDR", 1032, 629, 72, 18, { size: 15.5, bold: true, color: C.magenta, align: "center" });

  header(slide, "D", "Evidence chain", 1196, 138, 356, C.magenta);
  txt(slide, "d-intro", "The story is tested, not assumed", 1208, 184, 332, 22, { size: 16, color: C.brown, bold: true, align: "center" });
  const evidence = [
    ["Internal test", "390 held-out images\nfive source-training seeds", C.orange, C.orangePale],
    ["Functional occlusion test", "One-region occlusion\nversus learned attention", C.olive, C.olivePale],
    ["Independent UWF evaluation", "MMRDR-UWF: 2,597 images\nno target adaptation", C.magenta, C.magentaPale],
    ["Paired-view audit", "Ranks limited-view underestimation\nrequires two predictions", C.rust, C.grayPale],
  ];
  for (let i = 0; i < evidence.length; i += 1) {
    const y = 218 + i * 103;
    const [head, copy, stroke, fill] = evidence[i];
    rect(slide, `d-box-${i}`, 1212, y, 324, 78, fill, stroke, 12, 1);
    txt(slide, `d-head-${i}`, head, 1228, y + 10, 292, 19, { size: 16.5, bold: true, color: stroke, align: "center" });
    txt(slide, `d-copy-${i}`, copy, 1228, y + 33, 292, 32, { size: 15.2, color: C.ink, align: "center" });
    if (i < evidence.length - 1) down(slide, `d-arrow-${i}`, 1364, y + 80, 20, 17, C.muted);
  }

  rect(slide, "bottom-rule", 48, 728, 1504, 1.2, C.line, C.line, 0, 0);
  rect(slide, "takeaway-frame", 48, 758, 1504, 62, C.grayPale, C.orange, 14, 1);
  txt(slide, "takeaway", "Core finding: DR model behavior depends on which retinal evidence is available and how it is spatially organized—not on photographic quality or field area alone.", 72, 773, 1456, 28, { size: 19, bold: true, color: C.brown, align: "center" });
  addNotes(slide, "Figure 1 study overview.", "Diagnostic sufficiency is the clinical motivation. Model-specific retinal evidence availability is the operational construct examined here. Figure 1 intentionally contains no mathematical equations: it states the study question, controlled restrictions, model role, and validation chain. Figure 2 contains the single core masked-attention equation.");

  const preview = await presentation.export({ slide, format: "png", scale: 2 });
  await writeBlob(path.join(BUILD, "preview_fig1.png"), preview);
  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(FIG1_OUT);
}

async function buildFigure2(img, formulaSvg) {
  const [full, cross, cropTop, cropCenter, cropRight] = await Promise.all([bytes(img.full), bytes(img.cross), bytes(img.cropTop), bytes(img.cropCenter), bytes(img.cropRight)]);
  const presentation = Presentation.create({ slideSize: { width: W, height: H } });
  const slide = presentation.slides.add();
  slide.background.fill = C.page;
  // Connector layer first: inputs -> shared severity model -> downstream audit.
  arrow(slide, "a-to-b", 478, 420, 24, 18, C.brown);
  arrow(slide, "b-to-c", 1144, 420, 24, 18, C.brown);
  titleBlock(slide, "RegionSuff model: visibility-conditioned DR severity inference", "FIGURE 2", "The same source UWF image is processed under explicit visibility masks; these control model-specific retinal evidence availability—not photographic quality.");

  header(slide, "A", "Same source image, different visible evidence", 48, 138, 410, C.rust);
  txt(slide, "a-explain", "Each 3 × 3 token is a real retinal crop, not an abstract placeholder", 60, 184, 390, 40, { size: 16, color: C.brown, bold: true, align: "center" });
  imageFrame(slide, "a-full", full, "Raw UWF source image with a 3 by 3 regional grid.", 64, 236, 238, 238, C.rust);
  txt(slide, "a-full-note", "Raw UWF evidence bank", 66, 486, 234, 20, { size: 16, color: C.muted, italic: true, align: "center" });
  rect(slide, "a-views", 324, 236, 118, 270, C.grayPale, C.line, 12, 1);
  txt(slide, "a-views-title", "Visibility\nmasks", 334, 244, 98, 38, { size: 16.5, bold: true, color: C.olive, align: "center" });
  imageFrame(slide, "a-view-full", full, "Full view rendered from the raw UWF source image.", 344, 288, 78, 78, C.orange);
  smallImageLabel(slide, "a-view-full-label", "Full view", 334, 372, 98, C.brown);
  imageFrame(slide, "a-view-cross", cross, "Center plus cross view rendered from the raw UWF source image.", 344, 408, 78, 78, C.magenta);
  smallImageLabel(slide, "a-view-cross-label", "Center +\ncross", 334, 492, 98, C.magenta);
  rect(slide, "a-message", 60, 548, 382, 92, C.orangePale, C.orange, 12, 1);
  txt(slide, "a-message-title", "Visibility is an explicit model input", 76, 560, 350, 20, { size: 17, bold: true, color: C.brown, align: "center" });
  txt(slide, "a-message-copy", "The source DR label is retained; black tiles withhold the corresponding regional evidence from the model.", 84, 589, 334, 36, { size: 15.8, color: C.ink, align: "center" });

  header(slide, "B", "Shared RegionSuff severity model", 502, 138, 626, C.olive);
  txt(slide, "b-intro", "Visible retinal crops pass through one shared encoder → projection → masked-attention pathway", 516, 184, 598, 22, { size: 16, color: C.brown, bold: true, align: "center" });
  rect(slide, "b-crops", 524, 226, 188, 126, C.grayPale, C.rust, 12, 1);
  txt(slide, "b-crop-head", "Actual visible regional crops", 536, 236, 164, 18, { size: 16.5, bold: true, color: C.rust, align: "center" });
  imageFrame(slide, "b-crop-top", cropTop, "Actual top-middle crop from the source UWF image.", 542, 268, 48, 48, C.rust);
  imageFrame(slide, "b-crop-center", cropCenter, "Actual center crop from the source UWF image.", 596, 268, 48, 48, C.rust);
  imageFrame(slide, "b-crop-right", cropRight, "Actual middle-right crop from the source UWF image.", 650, 268, 48, 48, C.rust);
  arrow(slide, "b-to-encoder", 725, 277, 26, 18, C.orange);
  rect(slide, "b-encoder", 764, 226, 150, 126, C.grayPale, C.brown, 12, 1);
  txt(slide, "b-encoder-head", "Frozen retinal quality\nencoder", 778, 240, 122, 40, { size: 16, bold: true, color: C.brown, align: "center" });
  txt(slide, "b-encoder-copy", "RetinaRadar\nEfficientNet-B0", 778, 292, 122, 36, { size: 16, color: C.ink, align: "center" });
  arrow(slide, "b-to-projection", 930, 277, 26, 18, C.orange);
  rect(slide, "b-projection", 968, 226, 130, 126, C.orangePale, C.orange, 12, 1);
  txt(slide, "b-projection-head", "Trainable projection", 982, 242, 102, 38, { size: 17, bold: true, color: C.brown, align: "center" });
  txt(slide, "b-projection-copy", "One 128-D token\nper visible region", 982, 292, 102, 36, { size: 15.5, color: C.ink, align: "center" });
  down(slide, "b-down-attention", 802, 366, 22, 26, C.olive);
  rect(slide, "b-attention", 526, 402, 572, 148, C.olivePale, C.olive, 14, 1.15);
  txt(slide, "b-attention-title", "Masked attention pool", 544, 414, 536, 23, { size: 19, bold: true, color: C.olive, align: "center" });
  await addFormula(slide, formulaSvg, 592, 448, 440, 50);
  txt(slide, "b-attention-note", "mᵢ marks whether region i is visible; unavailable regions receive zero weight.", 552, 510, 520, 25, { size: 15.5, color: C.brown, align: "center" });
  down(slide, "b-down-output", 802, 560, 22, 25, C.olive);
  rect(slide, "b-output", 526, 600, 572, 100, C.grayPale, C.olive, 14, 1.1);
  txt(slide, "b-output-title", "Aggregate visible evidence → three-class DR prediction", 548, 611, 528, 21, { size: 18, bold: true, color: C.brown, align: "center" });
  rect(slide, "b-normal", 618, 652, 108, 30, C.white, C.orange, 10, 1);
  rect(slide, "b-npdr", 760, 652, 108, 30, C.white, C.olive, 10, 1);
  rect(slide, "b-pdr", 902, 652, 108, 30, C.white, C.magenta, 10, 1);
  txt(slide, "b-normal-text", "Normal", 618, 655, 108, 18, { size: 15.5, bold: true, color: C.brown, align: "center" });
  txt(slide, "b-npdr-text", "NPDR", 760, 655, 108, 18, { size: 15.5, bold: true, color: C.olive, align: "center" });
  txt(slide, "b-pdr-text", "PDR", 902, 655, 108, 18, { size: 15.5, bold: true, color: C.magenta, align: "center" });

  header(slide, "C", "Downstream paired-view audit", 1176, 138, 376, C.magenta);
  txt(slide, "c-intro", "One severity model; two visibility masks", 1188, 184, 352, 22, { size: 16, color: C.brown, bold: true, align: "center" });
  rect(slide, "c-full", 1188, 230, 150, 144, C.orangePale, C.orange, 12, 1);
  imageFrame(slide, "c-full-image", full, "Full UWF input for the first severity prediction.", 1227, 242, 72, 72, C.orange);
  txt(slide, "c-full-text", "Full-view\nprediction p_F", 1202, 323, 122, 34, { size: 15.2, bold: true, color: C.brown, align: "center" });
  rect(slide, "c-limited", 1390, 230, 150, 144, C.magentaPale, C.magenta, 12, 1);
  imageFrame(slide, "c-limited-image", cross, "Center plus cross UWF input for the second severity prediction.", 1429, 242, 72, 72, C.magenta);
  txt(slide, "c-limited-text", "Center + cross\nprediction p_L", 1404, 323, 122, 34, { size: 15.2, bold: true, color: C.magenta, align: "center" });
  down(slide, "c-down-compare", 1354, 387, 24, 26, C.magenta);
  rect(slide, "c-compare", 1188, 428, 352, 100, C.magentaPale, C.magenta, 12, 1.1);
  txt(slide, "c-compare-title", "Compare p_F and p_L", 1204, 440, 320, 20, { size: 18, bold: true, color: C.magenta, align: "center" });
  txt(slide, "c-compare-copy", "Probability, severity, and\nentropy differences", 1204, 472, 320, 36, { size: 16, color: C.ink, align: "center" });
  down(slide, "c-down-risk", 1354, 540, 24, 26, C.magenta);
  rect(slide, "c-risk", 1188, 580, 352, 68, C.white, C.magenta, 12, 1.1);
  txt(slide, "c-risk-title", "Rank limited-view underestimation risk", 1204, 592, 320, 20, { size: 17, bold: true, color: C.magenta, align: "center" });
  txt(slide, "c-risk-note", "Exploratory paired analysis", 1204, 616, 320, 18, { size: 15, italic: true, color: C.muted, align: "center" });
  rect(slide, "c-boundary", 1188, 668, 352, 48, C.grayPale, C.rust, 12, 1);
  txt(slide, "c-boundary-copy", "Requires both predictions; not a single-image triage rule.", 1200, 679, 328, 24, { size: 15, bold: true, color: C.rust, align: "center" });

  rect(slide, "bottom-rule", 48, 752, 1504, 1.2, C.line, C.line, 0, 0);
  rect(slide, "takeaway-frame", 48, 780, 1504, 58, C.grayPale, C.orange, 14, 1);
  txt(slide, "takeaway", "Core mechanism: visibility explicitly controls model-specific retinal evidence availability; paired risk is assessed only after comparing two severity predictions.", 72, 794, 1456, 28, { size: 19, bold: true, color: C.brown, align: "center" });
  addNotes(slide, "Figure 2 architecture.", "The one displayed equation is the core masked-attention operation. Full, limited, and regional-crop images all derive from the same local UWF source image. The masks are synthetic visibility restrictions, not real paired acquisitions. The paired audit begins only after p_F and p_L are available. Diagnostic sufficiency is the clinical motivation; model-specific retinal evidence availability is the operational construct.");

  const preview = await presentation.export({ slide, format: "png", scale: 2 });
  await writeBlob(path.join(BUILD, "preview_fig2.png"), preview);
  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(FIG2_OUT);
}

async function main() {
  const img = await createAssets();
  const formulaSvg = await bytes(FORMULA_SVG);
  await buildFigure1(img);
  if (process.env.FIGURE_ONLY !== "1") await buildFigure2(img, formulaSvg);
  console.log(JSON.stringify({ figure1: FIG1_OUT, figure2: process.env.FIGURE_ONLY === "1" ? null : FIG2_OUT, assets: img }, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
