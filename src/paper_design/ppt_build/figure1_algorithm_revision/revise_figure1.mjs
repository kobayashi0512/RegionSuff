import fs from "node:fs/promises";
import path from "node:path";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

Error.stackTraceLimit = 0;

const WORKSPACE = "/Users/tongyue/Documents/77f /7hao/paper_design/ppt_build/figure1_algorithm_revision";
const INPUT = path.join(WORKSPACE, "template-starter.pptx");
const LAYOUT = path.join(WORKSPACE, "template-starter-layout/starter-slide-01.layout.json");
const OUTPUT = "/Users/tongyue/Documents/ppf/第四论文/图1_算法公式修订版.pptx";
const PREVIEW = path.join(WORKSPACE, "figure1-revised-slide-01.png");
const AFTER_LAYOUT = path.join(WORKSPACE, "figure1-revised-slide-01.layout.json");
const ASSETS = path.join(WORKSPACE, "assets");

const FONT = "Times New Roman";
const MIN_PX = 16;
const COLOR = {
  dark: "#3A2D25",
  brown: "#704C2B",
  rust: "#965E4A",
  orange: "#D0913C",
  orangePale: "#F7E7D4",
  green: "#8B9A7C",
  greenPale: "#F1F4ED",
  magenta: "#C14F75",
  warmWhite: "#FFFDFC",
  panelLine: "#A55D42",
};

async function writeBlob(filePath, blob) {
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

async function readBytes(filePath) {
  const bytes = await fs.readFile(filePath);
  return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
}

const layout = JSON.parse(await fs.readFile(LAYOUT, "utf8"));
const byOrder = new Map(layout.elements.map((element) => [Number(element.order), element]));
const presentation = await PresentationFile.importPptx(await FileBlob.load(INPUT));
const slide = presentation.slides.getItem(0);

function objectFor(order) {
  const meta = byOrder.get(order);
  if (!meta) throw new Error(`Missing inherited element order ${order}`);
  const object = slide.elements.items.find((element) => Number(element.id) === Number(meta.id));
  if (!object) throw new Error(`Missing imported element ${meta.id} at order ${order}`);
  return { meta, object };
}

function setBox(order, left, top, width, height) {
  const { meta, object } = objectFor(order);
  const box = { left, top, width, height };
  if (meta.kind === "image") object.frame = box;
  else object.position = box;
}

function setFill(order, fill) {
  objectFor(order).object.fill = fill;
}

function setLine(order, fill, width = 1) {
  objectFor(order).object.line = { style: "solid", fill, width };
}

function setText(order, value) {
  objectFor(order).object.text = value;
}

function styleText(order, size = MIN_PX, options = {}) {
  const { object } = objectFor(order);
  const text = object.text;
  text.typeface = FONT;
  text.fontSize = Math.max(MIN_PX, size);
  if (options.bold !== undefined) text.bold = options.bold;
  if (options.italic !== undefined) text.italic = options.italic;
  if (options.color !== undefined) text.color = options.color;
  if (options.alignment !== undefined) text.alignment = options.alignment;
  if (options.verticalAlignment !== undefined) text.verticalAlignment = options.verticalAlignment;
  if (options.lineSpacing !== undefined) text.lineSpacing = options.lineSpacing;
  if (options.insets !== undefined) text.insets = options.insets;
  text.autoFit = "none";
  text.wrap = "square";
}

function styleArrow(order, left, top) {
  setBox(order, left, top, 18, 24);
  setFill(order, COLOR.green);
  setLine(order, COLOR.green, 0.5);
}

// Preserve the user's typography contract and update the one-line narrative cue.
setText(2, "Hidden evidence gap  •  controlled evidence loss  •  visibility-conditioned inference  •  paired-view audit");
styleText(2, 17, { color: COLOR.rust, alignment: "left" });

// Panel B: exact pixel-space apertures applied to the same embedded UWF source image.
const apertureFrames = [95, 96, 97];
const frameX = [444, 556, 668];
for (let i = 0; i < 3; i += 1) {
  setBox(apertureFrames[i], frameX[i], 426, 96, 96);
  setFill(apertureFrames[i], COLOR.orangePale);
  setLine(apertureFrames[i], COLOR.orange, 1.2);
}
for (const order of [98, 99, 100]) {
  setFill(order, "none");
  setLine(order, "none", 0);
  setBox(order, 0, 0, 1, 1);
}

const apertureSpecs = [
  {
    file: "uwf_rect_055.png",
    alt: "The same UWF source image with a centered rectangular aperture retaining f equals 0.55.",
    left: 448,
  },
  {
    file: "uwf_circle_055.png",
    alt: "The same UWF source image with an area-matched central circular aperture retaining f equals 0.55.",
    left: 560,
  },
  {
    file: "uwf_rect_035.png",
    alt: "The same UWF source image with a severe centered rectangular aperture retaining f equals 0.35.",
    left: 672,
  },
];
for (const spec of apertureSpecs) {
  slide.images.add({
    blob: await readBytes(path.join(ASSETS, spec.file)),
    contentType: "image/png",
    alt: spec.alt,
    fit: "contain",
    position: { left: spec.left, top: 430, width: 88, height: 88 },
    geometry: "rect",
  });
}

setText(101, "Centered rectangle\nf = 0.55 · area/location test");
setText(102, "Area-matched circle\nf = 0.55 · shape test");
setText(103, "Severe rectangular aperture\nf = 0.35 · stress test");
setBox(101, 436, 524, 112, 78);
setBox(102, 548, 524, 112, 78);
setBox(103, 660, 524, 112, 78);
for (const order of [101, 102, 103]) {
  styleText(order, MIN_PX, {
    bold: true,
    color: COLOR.dark,
    alignment: "center",
    verticalAlignment: "top",
    lineSpacing: 0.88,
    insets: { top: 0, right: 1, bottom: 0, left: 1 },
  });
}

setBox(104, 454, 608, 302, 58);
setFill(104, "none");
setLine(104, COLOR.orange, 1);
setBox(105, 464, 614, 282, 46);
setText(105, "A_rectangle = f²;   r_circle = f/√π\nA_circle = πr_circle² = f²");
styleText(105, MIN_PX, {
  bold: true,
  color: COLOR.brown,
  alignment: "center",
  verticalAlignment: "middle",
  lineSpacing: 0.94,
  insets: { top: 0, right: 2, bottom: 0, left: 2 },
});

setBox(106, 454, 678, 302, 58);
setText(106, "Pixel-space apertures applied to the same source image;\nthe DR label remains unchanged.");
styleText(106, MIN_PX, {
  italic: true,
  color: COLOR.rust,
  alignment: "center",
  verticalAlignment: "middle",
  lineSpacing: 0.92,
  insets: { top: 2, right: 5, bottom: 2, left: 5 },
});

// Panel C: the RegionSuff inference chain, using only inherited boxes and arrows.
setBox(107, 832, 204, 124, 124);
setBox(108, 836, 208, 116, 116);
const step = 116 / 3;
setBox(109, 836 + step, 208, 0, 116);
setBox(110, 836, 208 + step, 116, 0);
setBox(111, 836 + step * 2, 208, 0, 116);
setBox(112, 836, 208 + step * 2, 116, 0);
setBox(113, 964, 218, 184, 96);
setText(114, "3×3 evidence bank");
setText(115, "visibility mask m\nm ∈ {0,1}⁹");
setBox(114, 978, 226, 156, 34);
setBox(115, 972, 266, 168, 34);
styleText(114, 17, { bold: true, alignment: "center", verticalAlignment: "middle" });
styleText(115, MIN_PX, { italic: true, color: COLOR.rust, alignment: "center", verticalAlignment: "middle" });

styleArrow(7, 986, 318);
setBox(116, 842, 342, 306, 72);
setFill(116, "none");
setLine(116, COLOR.panelLine, 1);
setText(117, "Frozen regional representation");
setText(118, "zᵢ = P(E(rᵢ)) ∈ ℝ¹²⁸");
setBox(117, 856, 348, 278, 30);
setBox(118, 856, 378, 278, 30);
styleText(117, 17, { bold: true, alignment: "center", verticalAlignment: "middle" });
styleText(118, MIN_PX, { color: COLOR.rust, alignment: "center", verticalAlignment: "middle" });

styleArrow(8, 986, 416);
setBox(119, 842, 440, 306, 124);
setFill(119, "none");
setLine(119, COLOR.green, 1.2);
setText(120, "Visibility-conditioned attention");
setText(121, "eᵢ = wₐᵀ tanh(Wₐ zᵢ + bₐ) + bₛ\naᵢ(m) = mᵢ exp(eᵢ) / Σⱼ mⱼ exp(eⱼ)");
setBox(120, 852, 448, 286, 30);
setBox(121, 850, 482, 290, 72);
styleText(120, 17, { bold: true, alignment: "center", verticalAlignment: "middle" });
styleText(121, MIN_PX, {
  color: COLOR.dark,
  alignment: "center",
  verticalAlignment: "middle",
  lineSpacing: 0.92,
  insets: { top: 1, right: 2, bottom: 1, left: 2 },
});

styleArrow(9, 986, 568);
setBox(122, 842, 592, 306, 88);
setFill(122, "none");
setLine(122, COLOR.green, 1);
setBox(124, 850, 598, 290, 76);
setText(124, "Evidence aggregation and classification\nh(m) = Σᵢ aᵢ(m)zᵢ\np(m) = softmax(W_c h(m) + b_c)");
styleText(124, MIN_PX, {
  bold: true,
  color: COLOR.dark,
  alignment: "center",
  verticalAlignment: "middle",
  lineSpacing: 0.88,
  insets: { top: 0, right: 3, bottom: 0, left: 3 },
});

styleArrow(10, 986, 684);
setBox(123, 842, 708, 306, 74);
setFill(123, "none");
setLine(123, COLOR.magenta, 1.2);
setBox(125, 850, 714, 290, 62);
setText(125, "Primary DR severity prediction\np(m) → ŷ(m) ∈ {Normal, NPDR, PDR}");
styleText(125, MIN_PX, {
  bold: true,
  color: COLOR.magenta,
  alignment: "center",
  verticalAlignment: "middle",
  lineSpacing: 0.92,
  insets: { top: 1, right: 2, bottom: 1, left: 2 },
});

// Panel D: evidence chain and the paired risk audit after p_F and p_L exist.
const dCards = [126, 129, 132];
const dHeads = [127, 130, 133];
const dSubs = [128, 131, 134];
const dY = [210, 298, 386];
const dTitles = ["Internal robustness", "Functional intervention", "External UWF replication"];
const dCopy = [
  "390 held-out images · five seeds",
  "one-region occlusion versus attention",
  "2,597 MMRDR-UWF images · no adaptation",
];
for (let i = 0; i < dCards.length; i += 1) {
  setBox(dCards[i], 1234, dY[i], 302, 76);
  setFill(dCards[i], "none");
  setBox(dHeads[i], 1250, dY[i] + 7, 270, 28);
  setBox(dSubs[i], 1250, dY[i] + 38, 270, 30);
  setText(dHeads[i], dTitles[i]);
  setText(dSubs[i], dCopy[i]);
  styleText(dHeads[i], 17, { bold: true, alignment: "left", verticalAlignment: "middle" });
  styleText(dSubs[i], MIN_PX, { alignment: "left", verticalAlignment: "middle" });
}
setBox(11, 1378, 286, 14, 12);
setBox(12, 1378, 374, 14, 12);
setBox(13, 1378, 462, 14, 12);

setBox(135, 1234, 474, 302, 164);
setFill(135, "none");
setLine(135, COLOR.magenta, 1.2);
setBox(136, 1250, 482, 270, 30);
setText(136, "Paired-view underestimation audit");
styleText(136, 17, { bold: true, color: COLOR.magenta, alignment: "left", verticalAlignment: "middle" });
setBox(137, 1248, 516, 274, 112);
setText(137, "m_F, m_L → p_F, p_L\ng = [p_F, p_L, p_F−p_L, |p_F−p_L|,\ns_F, s_L, s_F−s_L, H_F, H_L, D_SKL] ∈ ℝ¹⁸\nq(g) = sigmoid(βᵀg̃ + b)");
styleText(137, MIN_PX, {
  color: COLOR.dark,
  alignment: "left",
  verticalAlignment: "middle",
  lineSpacing: 0.86,
  insets: { top: 1, right: 2, bottom: 1, left: 2 },
});

setBox(138, 1234, 650, 302, 112);
setFill(138, "none");
setBox(139, 1248, 658, 274, 96);
setText(139, "Synthetic evidence loss only\nNo clinician-adjudicated sufficiency labels\nPaired risk requires full and limited predictions");
styleText(139, MIN_PX, {
  bold: true,
  color: COLOR.rust,
  alignment: "center",
  verticalAlignment: "middle",
  lineSpacing: 0.9,
  insets: { top: 2, right: 4, bottom: 2, left: 4 },
});

// Record provenance and mathematical interpretation in the slide notes.
slide.speakerNotes.append(
  "\nRevision 2026-08-17: abstract aperture icons replaced by deterministic masks of the same embedded UWF image; Panel C now shows z_i, e_i, a_i(m), h(m), p(m), and the primary DR output; Panel D computes paired risk only after p_F and p_L.\n[Sources]\n- UWF visual: image embedded in the user's source Figure 1 deck.\n- Equations and terminology: RegionSuff_1.3 manuscript Sections 2.3-2.8 and local RegionSuff experiment implementations."
);
slide.speakerNotes.setVisible(true);

await writeBlob(PREVIEW, await presentation.export({ slide, format: "png", scale: 2 }));
await fs.writeFile(AFTER_LAYOUT, await (await slide.export({ format: "layout" })).text());
const pptx = await PresentationFile.exportPptx(presentation);
await pptx.save(OUTPUT);

console.log(JSON.stringify({ output: OUTPUT, preview: PREVIEW, layout: AFTER_LAYOUT }, null, 2));
