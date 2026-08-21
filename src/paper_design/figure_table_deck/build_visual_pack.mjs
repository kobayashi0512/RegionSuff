import fs from "node:fs/promises";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const OUT = "/Users/tongyue/Documents/ppf/第四论文/RegionSuff_图表总览_v1.9.pptx";
const BUILD = "/Users/tongyue/Documents/77f /7hao/paper_design/figure_table_deck";
const DOC_ASSETS = `${BUILD}/assets_docx`;
const FIG1 = "/Users/tongyue/Documents/77f /7hao/paper_design/fig_optimization/render_fig1_terms_qa/slide-1.png";
const FIG2 = "/Users/tongyue/Documents/77f /7hao/paper_design/fig_optimization/render_fig2_terms_qa/slide-1.png";

const W = 1600;
const H = 900;
const FONT = "Times New Roman";
const C = {
  page: "#FFFDF8", ink: "#332720", brown: "#704C2B", rust: "#965E4A",
  orange: "#C68A32", orangePale: "#F8E7CD", olive: "#78866B", olivePale: "#EDF1E8",
  magenta: "#B84067", magentaPale: "#F9EDF1", line: "#D8CABB", grayPale: "#F4F0EA",
  white: "#FFFFFF", muted: "#6F6259",
};

async function writeBlob(filePath, blob) {
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

async function readBytes(filePath) {
  const buffer = await fs.readFile(filePath);
  return buffer.buffer.slice(buffer.byteOffset, buffer.byteOffset + buffer.byteLength);
}

function rect(slide, name, left, top, width, height, fill = "none", lineFill = "none", radius = 0, lineWidth = 0) {
  return slide.shapes.add({
    geometry: radius ? "roundRect" : "rect", name,
    position: { left, top, width, height }, fill,
    line: { style: "solid", fill: lineFill, width: lineWidth }, borderRadius: radius || undefined,
  });
}

function text(slide, name, value, left, top, width, height, options = {}) {
  const shape = rect(slide, name, left, top, width, height, "none", "none", 0, 0);
  shape.text = value;
  shape.text.style = {
    typeface: FONT,
    fontSize: options.size ?? 18,
    color: options.color ?? C.ink,
    bold: options.bold ?? false,
    italic: options.italic ?? false,
    alignment: options.align ?? "left",
    verticalAlignment: options.valign ?? "middle",
    lineSpacing: options.lineSpacing ?? 0.95,
    insets: options.insets ?? { top: 0, right: 0, bottom: 0, left: 0 },
    autoFit: "none",
    wrap: "square",
  };
  return shape;
}

function notes(slide, body) {
  slide.speakerNotes.textFrame.setText(`[Sources]\n- ${body}\n- Manuscript source: RegionSuff_1.9.docx.\n`);
  slide.speakerNotes.setVisible(true);
}

function addFooter(slide, index) {
  rect(slide, "footer-rule", 48, 846, 1504, 1.1, C.line, C.line, 0, 0);
  text(slide, "footer-left", "RegionSuff visual package · manuscript order", 48, 856, 480, 20, { size: 13, color: C.muted });
  text(slide, "footer-right", String(index).padStart(2, "0"), 1440, 856, 112, 20, { size: 13, color: C.muted, align: "right" });
}

async function addFigureSlide(presentation, { number, title, caption, imagePath, source, index }) {
  const slide = presentation.slides.add();
  slide.background.fill = C.page;
  text(slide, "title", `Figure ${number}. ${title}`, 48, 28, 1280, 35, { size: 28, bold: true, color: C.brown });
  text(slide, "tag", "FIGURE", 1370, 32, 182, 23, { size: 15, bold: true, color: C.olive, align: "right" });
  rect(slide, "title-rule", 48, 78, 1504, 1.2, C.line, C.line, 0, 0);
  rect(slide, "figure-frame", 58, 100, 1484, 670, C.white, C.line, 10, 1);
  slide.images.add({
    blob: await readBytes(imagePath), contentType: "image/png", alt: `Figure ${number}: ${title}`,
    fit: "contain", position: { left: 70, top: 112, width: 1460, height: 646 }, geometry: "rect",
  });
  rect(slide, "caption-frame", 58, 786, 1484, 44, C.grayPale, C.orange, 10, 1);
  text(slide, "caption", caption, 78, 794, 1444, 28, { size: 14.5, color: C.brown, align: "center" });
  addFooter(slide, index);
  notes(slide, `${source}\n- Display asset: ${imagePath}`);
}

function cellStyle(table, rows, columns, baseSize = 16, bodyAlign = "center") {
  table.borders.assign({ style: "solid", fill: C.line, width: 0.8 });
  for (let r = 0; r < rows; r += 1) {
    for (let c = 0; c < columns; c += 1) {
      const cell = table.getCell(r, c);
      const isHeader = r === 0;
      const isFirst = c === 0;
      cell.fill = isHeader ? C.brown : (r % 2 === 0 ? C.grayPale : C.white);
      cell.text.style = {
        typeface: FONT,
        fontSize: isHeader ? baseSize : baseSize - 0.5,
        color: isHeader ? C.white : C.ink,
        bold: isHeader || isFirst,
        alignment: isHeader ? "center" : (isFirst ? "left" : bodyAlign),
        verticalAlignment: "middle",
        lineSpacing: 0.94,
        insets: { top: 4, right: 7, bottom: 4, left: 7 },
        wrap: "square",
      };
    }
  }
}

function addTableSlide(presentation, { number, title, caption, values, widths, keyNote, index }) {
  const slide = presentation.slides.add();
  slide.background.fill = C.page;
  text(slide, "title", `Table ${number}. ${title}`, 48, 28, 1280, 35, { size: 28, bold: true, color: C.brown });
  text(slide, "tag", "TABLE", 1370, 32, 182, 23, { size: 15, bold: true, color: C.olive, align: "right" });
  rect(slide, "title-rule", 48, 78, 1504, 1.2, C.line, C.line, 0, 0);
  text(slide, "caption", caption, 62, 99, 1476, 32, { size: 15.5, color: C.rust, italic: true, align: "center" });

  const rows = values.length;
  const columns = values[0].length;
  const tableTop = 150;
  const tableHeight = number === 3 ? 500 : number === 6 ? 330 : 330;
  const table = slide.tables.add({ rows, columns, left: 64, top: tableTop, width: 1472, height: tableHeight, values, columnWidths: widths });
  cellStyle(table, rows, columns, number === 3 || number === 6 ? 14.7 : 16);
  table.rows[0].height = number === 3 ? 32 : 42;
  for (let r = 1; r < rows; r += 1) table.rows[r].height = number === 3 ? 28 : number === 6 ? 52 : 72;

  rect(slide, "note-frame", 64, 720, 1472, 82, C.olivePale, C.olive, 12, 1);
  text(slide, "note-label", "Reading note", 86, 732, 150, 19, { size: 15, bold: true, color: C.olive });
  text(slide, "note-copy", keyNote, 86, 756, 1428, 32, { size: 16, color: C.ink, align: "center" });
  addFooter(slide, index);
  notes(slide, `Table ${number}: ${title}\n- Values transcribed from RegionSuff_1.9.docx, Table ${number}.`);
}

async function main() {
  const presentation = Presentation.create({ slideSize: { width: W, height: H } });

  const cover = presentation.slides.add();
  cover.background.fill = C.page;
  rect(cover, "accent", 48, 84, 14, 650, C.orange, C.orange, 0, 0);
  text(cover, "eyebrow", "REGIONSUFF · MANUSCRIPT VISUAL PACKAGE", 90, 145, 1120, 26, { size: 17, bold: true, color: C.olive });
  text(cover, "title", "Complete Figures and Tables", 90, 205, 1200, 66, { size: 44, bold: true, color: C.brown });
  text(cover, "subtitle", "Paper-order reference deck for RegionSuff v1.9", 92, 292, 970, 34, { size: 22, color: C.rust });
  rect(cover, "scope", 90, 386, 900, 156, C.grayPale, C.line, 14, 1);
  text(cover, "scope-head", "What this deck contains", 122, 414, 330, 24, { size: 18, bold: true, color: C.brown });
  text(cover, "scope-copy", "8 publication figures · 6 manuscript tables\nFigure 1 and Figure 2 use the terminology-unified versions.\nAll remaining graphics and all tabulated values follow RegionSuff_1.9.", 122, 454, 820, 70, { size: 19, color: C.ink, lineSpacing: 1.04 });
  rect(cover, "stat-one", 1110, 190, 340, 122, C.orangePale, C.orange, 14, 1);
  text(cover, "stat-one-num", "8", 1138, 206, 88, 52, { size: 42, bold: true, color: C.orange, align: "center" });
  text(cover, "stat-one-label", "Main figures", 1246, 221, 166, 28, { size: 20, bold: true, color: C.brown, align: "center" });
  rect(cover, "stat-two", 1110, 344, 340, 122, C.olivePale, C.olive, 14, 1);
  text(cover, "stat-two-num", "6", 1138, 360, 88, 52, { size: 42, bold: true, color: C.olive, align: "center" });
  text(cover, "stat-two-label", "Main tables", 1246, 375, 166, 28, { size: 20, bold: true, color: C.brown, align: "center" });
  text(cover, "version", "Source manuscript: RegionSuff_1.9.docx", 90, 738, 800, 24, { size: 17, color: C.muted });
  addFooter(cover, 1);
  notes(cover, "Deck scope and ordering reference.");

  const sourceFigure = (n) => `${DOC_ASSETS}/image${n}.png`;
  const figures = [
    { number: 1, title: "Study overview", imagePath: FIG1, source: "Figure 1, terminology-unified revision.", caption: "Study overview: the analysis distinguishes photographic quality from model-specific evidence availability, then tests this construct with controlled visibility restrictions." },
    { number: 2, title: "RegionSuff architecture", imagePath: FIG2, source: "Figure 2, terminology-unified revision.", caption: "Architecture: actual regional crops follow the shared encoder–projection–masked-attention path; paired-view risk is computed only after two severity predictions." },
    { number: 3, title: "Controlled evidence-loss tests", imagePath: sourceFigure(3), source: "Figure 3 from RegionSuff_1.9.docx.", caption: "Five-seed aperture, location, shape, and regional-topology tests show that visible area alone does not determine model behavior." },
    { number: 4, title: "Component controls", imagePath: sourceFigure(4), source: "Figure 4 from RegionSuff_1.9.docx.", caption: "Regional representation, aggregation, masking, and grid-resolution controls; reference settings are not presented as unique optima." },
    { number: 5, title: "Attention and model intervention", imagePath: sourceFigure(5), source: "Figure 5 from RegionSuff_1.9.docx.", caption: "Attention is tested against one-region occlusion rather than being interpreted as lesion localization or a causal explanation by itself." },
    { number: 6, title: "Independent same-modality UWF evaluation", imagePath: sourceFigure(6), source: "Figure 6 from RegionSuff_1.9.docx.", caption: "Independent MMRDR-UWF evaluation without target-label adaptation; paired bootstrap contrasts quantify image-sampling uncertainty within each source-trained seed." },
    { number: 7, title: "Paired-view underestimation audit", imagePath: sourceFigure(7), source: "Figure 7 from RegionSuff_1.9.docx.", caption: "The paired risk module is exploratory: fixed-split and nested grouped protocols are presented separately because their calibration conditions differ." },
    { number: 8, title: "Pixel-aperture training versus protocol-matched baseline", imagePath: sourceFigure(8), source: "Figure 8 from RegionSuff_1.9.docx.", caption: "Aperture training improves F1 and ordinal severity MAE across held-out stresses, whereas underestimation improvement is asymmetric across apertures." },
  ];

  const tables = [
    { number: 1, title: "Datasets and experimental roles", caption: "Released records, group-disjoint development partitions, labels used, and strictly separated roles.", widths: [180, 150, 340, 270, 532], keyNote: "UWF-DR supplies development and internal testing. MMRDR-UWF is an independent same-modality severity evaluation set, with no target-domain adaptation.", values: [
      ["Dataset", "Released\nrecords", "Model partition", "Labels used", "Role"],
      ["UWF-DR", "1,630", "Train 876; validation 364; test 390", "Normal 496; NPDR 634; PDR 500", "Development, perturbation analysis, and internal testing"],
      ["MMRDR-UWF", "2,597", "Official UWF test subset", "Grade 0 → Normal; 1–3 → NPDR; 4 → PDR", "Independent same-modality severity evaluation; no adaptation"],
    ] },
    { number: 2, title: "Internal held-out results across five source-training seeds", caption: "Values are mean ± sample SD. Macro-F1 is the primary endpoint.", widths: [240, 308, 308, 308, 308], keyNote: "Center-only inference reduces macro-F1 and raises severity MAE. Restoring the four axial neighboring regions largely recovers full-view performance.", values: [
      ["View", "Accuracy", "Macro-F1", "Severity MAE", "Under. rate"],
      ["Full", "0.829 ± 0.017", "0.830 ± 0.017", "0.180 ± 0.018", "0.070 ± 0.007"],
      ["Center", "0.789 ± 0.012", "0.790 ± 0.012", "0.228 ± 0.013", "0.093 ± 0.006"],
      ["Center + cross", "0.828 ± 0.017", "0.829 ± 0.017", "0.182 ± 0.016", "0.075 ± 0.012"],
    ] },
    { number: 3, title: "Single-split descriptive controls", caption: "Test values did not redefine the multi-seed primary result.", widths: [260, 235, 325, 325, 327], keyNote: "The mask-ratio and grid controls are non-monotonic single-split sensitivities. The five-seed primary analysis remains the basis for the main claims.", values: [
      ["Component", "Variant", "Full F1", "Center F1", "Center + cross F1"],
      ["Pooling", "Mean", "0.799", "0.759", "0.820"],
      ["", "Max", "0.810", "0.778", "0.824"],
      ["", "Attention", "0.840", "0.793", "0.837"],
      ["Mask ratio", "0.00", "0.837", "0.801", "0.847"],
      ["", "0.15", "0.817", "0.795", "0.820"],
      ["", "0.30", "0.840", "0.793", "0.837"],
      ["", "0.45", "0.834", "0.795", "0.843"],
      ["", "0.60", "0.853", "0.798", "0.856"],
      ["Grid / attention", "1×1", "0.781", "0.781", "0.781"],
      ["", "2×2", "0.824", "0.824", "0.824"],
      ["", "3×3", "0.840", "0.793", "0.837"],
      ["", "4×4", "0.842", "0.837", "0.842"],
      ["Encoder", "RetinaRadar", "0.840", "—", "0.837"],
      ["", "ImageNet ResNet-50", "0.780", "—", "0.772"],
      ["", "Handcrafted", "0.605", "—", "0.604"],
      ["", "Random ResNet-50", "0.161", "—", "0.161"],
    ] },
    { number: 4, title: "Independent MMRDR-UWF results across five source-trained seeds", caption: "Values are mean ± sample SD; no target labels entered fitting or model selection.", widths: [190, 250, 250, 250, 250, 282], keyNote: "On the independent UWF cohort, center-plus-cross inference has the highest macro-F1 and lowest severity MAE among the three views; this is a same-modality replication, not a domain-adapted result.", values: [
      ["View", "Accuracy", "Macro-F1", "Severity MAE", "Under. rate", "Δ F1 vs full"],
      ["Full", "0.627 ± 0.010", "0.625 ± 0.010", "0.400 ± 0.013", "0.272 ± 0.013", "Reference"],
      ["Center", "0.602 ± 0.004", "0.600 ± 0.004", "0.432 ± 0.005", "0.284 ± 0.016", "−0.025 ± 0.013"],
      ["Center + cross", "0.644 ± 0.004", "0.642 ± 0.005", "0.378 ± 0.006", "0.260 ± 0.005", "+0.017 ± 0.006"],
    ] },
    { number: 5, title: "Paired underestimation-risk analysis", caption: "Fixed-split rows are exploratory; nested rows are mean ± sample SD across four outer filename-grouped folds.", widths: [300, 235, 205, 330, 402], keyNote: "Fixed-split risk ranking is stronger than nested grouped performance. Coverage transport varies markedly, so no deployable threshold is claimed.", values: [
      ["Protocol", "Risk AUROC", "Target", "Coverage", "Accepted risk"],
      ["Fixed exploratory", "0.740", "5%", "0.628", "0.029"],
      ["", "", "10%", "0.918", "0.075"],
      ["", "", "20%", "0.997", "0.077"],
      ["Nested grouped", "0.653 ± 0.034", "5%", "0.567 ± 0.274", "0.050 ± 0.033"],
      ["", "", "10%", "0.812 ± 0.165", "0.092 ± 0.034"],
      ["", "", "20%", "0.980 ± 0.014", "0.097 ± 0.040"],
    ] },
    { number: 6, title: "Pixel-aperture training against a protocol-matched baseline", caption: "Values are mean ± sample SD across five seeds; Δ is augmented minus baseline.", widths: [174, 185, 185, 185, 185, 185, 185, 188], keyNote: "Pixel-aperture augmentation consistently improves F1 and severity MAE. Underestimation improves only for the most severe rectangular aperture and is higher for the less severe stresses.", values: [
      ["Aperture", "F1 base", "F1 aug.", "MAE base", "MAE aug.", "Under base", "Under aug.", "Δ Under"],
      ["Rect. 0.35", "0.519 ± 0.160", "0.794 ± 0.013", "0.446 ± 0.123", "0.221 ± 0.014", "0.272 ± 0.092", "0.097 ± 0.007", "−0.175"],
      ["Rect. 0.55", "0.688 ± 0.055", "0.802 ± 0.017", "0.334 ± 0.058", "0.208 ± 0.018", "0.059 ± 0.019", "0.089 ± 0.008", "+0.030"],
      ["Rect. 0.75", "0.731 ± 0.027", "0.811 ± 0.015", "0.306 ± 0.041", "0.199 ± 0.016", "0.063 ± 0.005", "0.081 ± 0.008", "+0.018"],
      ["Circle 0.55", "0.752 ± 0.051", "0.804 ± 0.011", "0.264 ± 0.050", "0.206 ± 0.011", "0.070 ± 0.013", "0.090 ± 0.005", "+0.019"],
    ] },
  ];

  let idx = 2;
  await addFigureSlide(presentation, { ...figures[0], index: idx++ });
  await addTableSlide(presentation, { ...tables[0], index: idx++ });
  await addFigureSlide(presentation, { ...figures[1], index: idx++ });
  await addTableSlide(presentation, { ...tables[1], index: idx++ });
  await addFigureSlide(presentation, { ...figures[2], index: idx++ });
  await addTableSlide(presentation, { ...tables[2], index: idx++ });
  await addFigureSlide(presentation, { ...figures[3], index: idx++ });
  await addFigureSlide(presentation, { ...figures[4], index: idx++ });
  await addTableSlide(presentation, { ...tables[3], index: idx++ });
  await addFigureSlide(presentation, { ...figures[5], index: idx++ });
  await addTableSlide(presentation, { ...tables[4], index: idx++ });
  await addFigureSlide(presentation, { ...figures[6], index: idx++ });
  await addTableSlide(presentation, { ...tables[5], index: idx++ });
  await addFigureSlide(presentation, { ...figures[7], index: idx++ });

  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(OUT);
  console.log(JSON.stringify({ output: OUT, slides: presentation.slides.items.length }, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
