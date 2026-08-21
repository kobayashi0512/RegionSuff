import fs from "node:fs/promises";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const OUT = "/Users/tongyue/Documents/77f /7hao/RegionSuff_Figure1_Study_Overview_Editable.pptx";
const BUILD = "/Users/tongyue/Documents/77f /7hao/paper_design/ppt_build/figure1_editable";
const FUNDUS = "/Users/tongyue/Documents/77f /7hao/datasets/UWF_DR_1630/extracted/Ultra-wide-field (SLO) fundus image dataset for intelligent diabetic retinopathy system/diabetic retinopathy/PDR512/5_313_2020-10-21_1_L.png";

const C = {
  paper: "#FFFDFC",
  paper2: "#FBF7F1",
  peach: "#F7ECE6",
  apricot: "#F5CFAA",
  orange: "#E49F5D",
  orange2: "#F1C89A",
  ochre: "#C58B47",
  umber: "#965E4A",
  brown: "#704C2B",
  olive: "#8B9A7C",
  olive2: "#E5E8D9",
  rose: "#B95372",
  gray: "#D8D0C8",
  gray2: "#EEE9E3",
  ink: "#3F3027",
  white: "#FFFFFF",
  black: "#000000",
};

async function imageBytes(path) {
  const b = await fs.readFile(path);
  return b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength);
}

function addShape(slide, name, geometry, left, top, width, height, fill, lineFill, lineWidth = 1.4, radius = undefined) {
  return slide.shapes.add({
    name,
    geometry,
    position: { left, top, width, height },
    fill,
    line: { style: "solid", fill: lineFill, width: lineWidth },
    ...(radius ? { borderRadius: radius } : {}),
  });
}

function addText(slide, name, text, left, top, width, height, opts = {}) {
  const box = slide.shapes.add({
    name,
    geometry: "textbox",
    position: { left, top, width, height },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  box.text = text;
  box.text.style = {
    fontFamily: "Arial",
    fontSize: opts.fontSize ?? 16,
    bold: opts.bold ?? false,
    italic: opts.italic ?? false,
    color: opts.color ?? C.ink,
    alignment: opts.alignment ?? "left",
    verticalAlignment: opts.verticalAlignment ?? "middle",
  };
  return box;
}

function addPanel(slide, x, y, w, h, letter, title, headerFill, edge) {
  addShape(slide, `panel-${letter}`, "roundRect", x, y, w, h, C.paper2, edge, 2, 18);
  addShape(slide, `panel-${letter}-header`, "roundRect", x + 12, y + 12, w - 24, 60, headerFill, edge, 1.3, 12);
  addText(slide, `panel-${letter}-letter`, letter, x + 24, y + 23, 34, 38, { fontSize: 22, bold: true, color: edge });
  addText(slide, `panel-${letter}-title`, title, x + 60, y + 21, w - 86, 42, { fontSize: 24, bold: true, alignment: "center" });
}

function addArrow(slide, name, left, top, width, height, color, direction = "right") {
  return addShape(slide, name, direction === "right" ? "rightArrow" : "downArrow", left, top, width, height, color, color, 0.5);
}

function addGrid(slide, x, y, size, color = C.white, width = 1.4) {
  for (const k of [1, 2]) {
    slide.shapes.add({
      name: `grid-v-${x}-${k}`,
      geometry: "line",
      position: { left: x + (size * k) / 3, top: y, width: 0, height: size },
      fill: "none",
      line: { style: "solid", fill: color, width },
    });
    slide.shapes.add({
      name: `grid-h-${y}-${k}`,
      geometry: "line",
      position: { left: x, top: y + (size * k) / 3, width: size, height: 0 },
      fill: "none",
      line: { style: "solid", fill: color, width },
    });
  }
}

function addMaskOverlays(slide, x, y, size, mode) {
  const s = size / 3;
  const hidden = [];
  if (mode === "center") {
    for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) if (!(r === 1 && c === 1)) hidden.push([r, c]);
  } else if (mode === "cross") {
    hidden.push([0, 0], [0, 2], [2, 0], [2, 2]);
  }
  for (const [r, c] of hidden) {
    addShape(slide, `mask-${mode}-${r}-${c}-${x}`, "rect", x + c * s, y + r * s, s + 0.5, s + 0.5, C.black, C.black, 0);
  }
}

function addImageFrame(slide, fundus, x, y, size, mode, alt) {
  addShape(slide, `image-bg-${x}-${y}`, "rect", x - 2, y - 2, size + 4, size + 4, C.black, mode === "full" ? C.olive : C.rose, 1.6);
  slide.images.add({
    blob: fundus,
    contentType: "image/png",
    alt,
    fit: "cover",
    position: { left: x, top: y, width: size, height: size },
    geometry: "rect",
  });
  if (mode !== "full") addMaskOverlays(slide, x, y, size, mode);
  addGrid(slide, x, y, size, C.white, size >= 100 ? 1.4 : 1.0);
}

async function main() {
  await fs.mkdir(BUILD, { recursive: true });
  const fundus = await imageBytes(FUNDUS);
  const deck = Presentation.create({ slideSize: { width: 1600, height: 900 } });
  const slide = deck.slides.add();
  slide.background.fill = C.paper;

  // Main title and subtitle.
  addText(slide, "figure-title", "RegionSuff: evidence auditing under limited retinal fields of view", 48, 24, 1200, 52, { fontSize: 36, bold: true, color: C.brown });
  addText(slide, "figure-subtitle", "Study rationale, controlled perturbations, visibility-conditioned model, and evidence chain", 50, 72, 1080, 30, { fontSize: 16, color: C.umber });
  addText(slide, "figure-number", "FIGURE 1", 1390, 31, 150, 30, { fontSize: 18, bold: true, color: C.olive, alignment: "right" });

  const xs = [38, 428, 818, 1208];
  const panelY = 118;
  const panelW = 354;
  const panelH = 690;

  // Connectors first, so they remain behind all modules.
  for (let i = 0; i < 3; i++) addArrow(slide, `flow-${i}`, xs[i] + panelW + 8, 445, 22, 20, C.brown, "right");
  addArrow(slide, "c-down-1", 984, 330, 18, 28, C.olive, "down");
  addArrow(slide, "c-down-2", 984, 470, 18, 28, C.olive, "down");
  addArrow(slide, "c-down-left", 920, 626, 16, 24, C.olive, "down");
  addArrow(slide, "c-down-right", 1052, 626, 16, 24, C.rose, "down");
  for (const yy of [318, 432, 546]) addArrow(slide, `d-chain-${yy}`, 1374, yy, 14, 22, C.gray, "down");

  addPanel(slide, xs[0], panelY, panelW, panelH, "A", "Hidden evidence gap", C.peach, C.umber);
  addPanel(slide, xs[1], panelY, panelW, panelH, "B", "Controlled evidence loss", C.apricot, C.ochre);
  addPanel(slide, xs[2], panelY, panelW, panelH, "C", "RegionSuff model", C.olive2, C.olive);
  addPanel(slide, xs[3], panelY, panelW, panelH, "D", "Evidence chain", C.peach, C.umber);

  // Panel A — quality is not evidence completeness.
  addText(slide, "a-full-label", "Full field", xs[0] + 28, 205, 132, 34, { fontSize: 16, bold: true, alignment: "center" });
  addText(slide, "a-limited-label", "Restricted field", xs[0] + 194, 205, 132, 34, { fontSize: 16, bold: true, alignment: "center" });
  addImageFrame(slide, fundus, xs[0] + 34, 244, 124, "full", "Nominal full-field UWF fundus image");
  addImageFrame(slide, fundus, xs[0] + 200, 244, 124, "center", "Sharp UWF fundus image with only the center region visible");

  addShape(slide, "a-contrast-box", "roundRect", xs[0] + 26, 390, 302, 112, C.white, C.gray, 1.2, 10);
  addText(slide, "a-quality-1", "Technical gradability", xs[0] + 42, 405, 190, 32, { fontSize: 16, bold: true });
  addText(slide, "a-quality-2", "PASS", xs[0] + 238, 405, 68, 32, { fontSize: 17, bold: true, color: C.olive, alignment: "right" });
  addText(slide, "a-evidence-1", "Task evidence", xs[0] + 42, 451, 132, 32, { fontSize: 16, bold: true });
  addText(slide, "a-evidence-2", "INCOMPLETE", xs[0] + 168, 451, 140, 32, { fontSize: 16, bold: true, color: C.rose, alignment: "right" });

  addShape(slide, "a-question-box", "roundRect", xs[0] + 34, 544, 286, 168, C.peach, C.umber, 1.4, 14);
  addText(slide, "a-question-head", "Research question", xs[0] + 56, 560, 242, 34, { fontSize: 18, bold: true, color: C.umber, alignment: "center" });
  addText(slide, "a-question-body", "How does a fixed DR classifier respond when retinal evidence is removed in a controlled and traceable way?", xs[0] + 60, 598, 234, 92, { fontSize: 17, alignment: "center" });

  // Panel B — region topology and pixel apertures.
  const bThumbY = 224;
  const bThumbSize = 78;
  addImageFrame(slide, fundus, xs[1] + 24, bThumbY, bThumbSize, "full", "Full-view regional evidence");
  addImageFrame(slide, fundus, xs[1] + 138, bThumbY, bThumbSize, "center", "Center-only regional evidence");
  addImageFrame(slide, fundus, xs[1] + 252, bThumbY, bThumbSize, "cross", "Center-plus-cross regional evidence");
  addText(slide, "b-full", "Full", xs[1] + 18, 305, 90, 28, { fontSize: 16, bold: true, alignment: "center" });
  addText(slide, "b-center", "Center", xs[1] + 128, 305, 98, 28, { fontSize: 16, bold: true, alignment: "center" });
  addText(slide, "b-cross", "Center + cross", xs[1] + 230, 305, 124, 28, { fontSize: 16, bold: true, alignment: "center" });

  addShape(slide, "b-topology-box", "roundRect", xs[1] + 26, 350, 302, 70, C.white, C.ochre, 1.2, 10);
  addText(slide, "b-topology-text", "Regional topology: which 3×3 evidence tokens remain visible?", xs[1] + 46, 363, 262, 44, { fontSize: 17, bold: true, alignment: "center" });

  const ay = 468;
  const axx = [xs[1] + 40, xs[1] + 143, xs[1] + 246];
  for (let i = 0; i < 3; i++) addShape(slide, `aperture-frame-${i}`, "roundRect", axx[i], ay, 70, 70, C.gray2, C.orange, 1.2, 9);
  addShape(slide, "aperture-rect", "rect", axx[0] + 16, ay + 16, 38, 38, C.orange2, C.umber, 1.1);
  addShape(slide, "aperture-circle", "ellipse", axx[1] + 12, ay + 12, 46, 46, C.orange2, C.umber, 1.1);
  addShape(slide, "aperture-small", "rect", axx[2] + 24, ay + 24, 22, 22, C.orange2, C.umber, 1.1);
  addText(slide, "aperture-label-1", "Rectangle", axx[0] - 19, ay + 76, 108, 32, { fontSize: 16, bold: true, alignment: "center" });
  addText(slide, "aperture-label-2", "Matched circle", axx[1] - 15, ay + 76, 100, 48, { fontSize: 16, bold: true, alignment: "center" });
  addText(slide, "aperture-label-3", "Severe crop", axx[2] - 10, ay + 76, 90, 48, { fontSize: 16, bold: true, alignment: "center" });

  addShape(slide, "b-dimensions", "roundRect", xs[1] + 28, 642, 298, 58, C.apricot, C.ochre, 1.1, 10);
  addText(slide, "b-dimensions-text", "Composition · area · location · shape · topology", xs[1] + 44, 654, 266, 34, { fontSize: 17, bold: true, alignment: "center" });
  addText(slide, "b-label-note", "The source DR label is unchanged", xs[1] + 54, 714, 246, 32, { fontSize: 16, italic: true, color: C.umber, alignment: "center" });

  // Panel C — visibility-conditioned evidence aggregation.
  addImageFrame(slide, fundus, xs[2] + 28, 220, 96, "full", "Retinal foreground divided into a 3 by 3 evidence bank");
  addShape(slide, "c-bank", "roundRect", xs[2] + 150, 222, 174, 92, C.white, C.olive, 1.3, 12);
  addText(slide, "c-bank-title", "3×3 evidence bank", xs[2] + 164, 236, 146, 34, { fontSize: 18, bold: true, alignment: "center" });
  addText(slide, "c-bank-sub", "visibility mask m", xs[2] + 166, 274, 142, 24, { fontSize: 16, color: C.umber, alignment: "center" });

  addShape(slide, "c-encoder", "roundRect", xs[2] + 32, 362, 290, 94, C.gray2, C.umber, 1.3, 12);
  addText(slide, "c-encoder-title", "Frozen retinal image-quality encoder", xs[2] + 50, 374, 254, 48, { fontSize: 18, bold: true, alignment: "center" });
  addText(slide, "c-encoder-sub", "shared across regions", xs[2] + 58, 425, 238, 22, { fontSize: 16, color: C.umber, alignment: "center" });

  addShape(slide, "c-attention", "roundRect", xs[2] + 32, 502, 290, 100, C.olive2, C.olive, 1.4, 12);
  addText(slide, "c-attention-title", "Masked attention over visible regions", xs[2] + 48, 512, 258, 50, { fontSize: 18, bold: true, alignment: "center" });
  addText(slide, "c-attention-sub", "unavailable regions receive zero weight", xs[2] + 54, 566, 246, 22, { fontSize: 16, color: C.umber, alignment: "center" });

  addShape(slide, "c-output-grade", "roundRect", xs[2] + 26, 658, 142, 78, C.white, C.olive, 1.3, 10);
  addShape(slide, "c-output-risk", "roundRect", xs[2] + 188, 658, 142, 78, C.white, C.rose, 1.3, 10);
  addText(slide, "c-grade", "DR grading\nNormal · NPDR · PDR", xs[2] + 35, 670, 124, 54, { fontSize: 16, bold: true, alignment: "center" });
  addText(slide, "c-risk", "Paired-view\nrisk audit", xs[2] + 200, 671, 118, 52, { fontSize: 16, bold: true, color: C.rose, alignment: "center" });

  // Panel D — evidence chain dominates; boundary is concise.
  const evidence = [
    ["Internal robustness", "390 held-out images · five seeds", C.orange],
    ["Functional intervention", "one-region occlusion vs attention", C.ochre],
    ["External severity evaluation", "2,597 MMRDR-UWF images · no adaptation", C.olive],
    ["Paired-view risk analysis", "fixed split + grouped nested audit", C.rose],
  ];
  let dy = 218;
  for (let i = 0; i < evidence.length; i++) {
    const [head, sub, edge] = evidence[i];
    addShape(slide, `d-evidence-${i}`, "roundRect", xs[3] + 28, dy, 298, 92, C.white, edge, 1.4, 10);
    addText(slide, `d-evidence-head-${i}`, head, xs[3] + 46, dy + 10, 260, 32, { fontSize: 18, bold: true, color: edge });
    addText(slide, `d-evidence-sub-${i}`, sub, xs[3] + 46, dy + 45, 260, 34, { fontSize: 16 });
    dy += 114;
  }
  addShape(slide, "d-boundary", "roundRect", xs[3] + 28, 680, 298, 94, C.peach, C.umber, 1.3, 10);
  addText(slide, "d-boundary-text", "Scope: synthetic evidence restriction\nNo clinician sufficiency labels\nPaired risk requires two views", xs[3] + 46, 692, 262, 70, { fontSize: 16, bold: true, color: C.umber, alignment: "center" });

  addShape(slide, "core-claim-box", "roundRect", 154, 826, 1292, 48, C.white, C.orange2, 1.1, 10);
  addText(slide, "core-claim", "Core claim: DR model behavior depends on the composition and topology of visible retinal evidence—not on photographic quality or visible area alone.", 184, 834, 1232, 32, { fontSize: 17, bold: true, color: C.brown, alignment: "center" });

  slide.speakerNotes.textFrame.setText([
    "Figure 1. Study overview. (A) Technical gradability and task-relevant evidence availability are distinct. (B) Regional masks and pixel apertures impose controlled evidence restrictions while retaining the source DR label. (C) RegionSuff encodes a 3×3 evidence bank and aggregates only visible regions through masked attention. (D) Evaluation comprises internal robustness, intervention-based attention analysis, external UWF severity evaluation, and paired-view underestimation analysis. All visibility restrictions are synthetic, and the paired risk module requires both full-view and limited-view predictions.",
    "[Sources]",
    "- User-provided Figure 1 reference: /var/folders/fl/1np9q85x7y36vr4jdrs1vpvc0000gq/T/codex-clipboard-d623375a-49a6-4f73-99fa-60a0fc42805a.png",
    "- UWF-DR source image: /Users/tongyue/Documents/77f /7hao/datasets/UWF_DR_1630/extracted/Ultra-wide-field (SLO) fundus image dataset for intelligent diabetic retinopathy system/diabetic retinopathy/PDR512/5_313_2020-10-21_1_L.png",
    "- Figure content and caption: RegionSuff manuscript materials supplied by the user.",
    "[/Sources]",
  ]);
  slide.speakerNotes.setVisible(true);

  const slidePng = await deck.export({ slide, format: "png", scale: 1 });
  await fs.writeFile(`${BUILD}/slide-1.png`, new Uint8Array(await slidePng.arrayBuffer()));
  const layout = await slide.export({ format: "layout" });
  await fs.writeFile(`${BUILD}/slide-1.layout.json`, await layout.text());
  const snapshot = await deck.inspect({ kind: "slide,textbox,shape,image,notes", maxChars: 20000 });
  await fs.writeFile(`${BUILD}/inspect.ndjson`, snapshot.ndjson);
  const pptx = await PresentationFile.exportPptx(deck);
  await pptx.save(OUT);
  console.log(OUT);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
