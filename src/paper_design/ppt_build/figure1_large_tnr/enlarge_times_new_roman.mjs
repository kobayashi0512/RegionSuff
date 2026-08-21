import fs from "node:fs/promises";
import path from "node:path";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

Error.stackTraceLimit = 0;

const WORKSPACE = "/Users/tongyue/Documents/77f /7hao/paper_design/ppt_build/figure1_large_tnr";
const INPUT = path.join(WORKSPACE, "template-starter.pptx");
const LAYOUT = path.join(WORKSPACE, "template-starter-layout/starter-slide-01.layout.json");
const OUTPUT = "/Users/tongyue/Documents/ppf/第四论文/图1_放大新罗马版.pptx";
const PREVIEW = path.join(WORKSPACE, "large-tnr-slide-01.png");
const AFTER_LAYOUT = path.join(WORKSPACE, "large-tnr-slide-01.layout.json");

const FONT = "Times New Roman";
const MIN_PX = 16; // 12 pt at 96 dpi.
const COLOR = {
  dark: "#3A2D25",
  brown: "#704C2B",
  rust: "#965E4A",
  orange: "#D0913C",
  green: "#8B9A7C",
  magenta: "#C14F75",
  letterA: "#C5A99A",
  letterB: "#DAB57A",
  letterC: "#ADB8A2",
  letterD: "#C5A99A",
};

async function writeBlob(filePath, blob) {
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

const layout = JSON.parse(await fs.readFile(LAYOUT, "utf8"));
const byOrder = new Map(layout.elements.map((element) => [Number(element.order), element]));
const presentation = await PresentationFile.importPptx(await FileBlob.load(INPUT));
const slide = presentation.slides.getItem(0);

function objectFor(order) {
  const meta = byOrder.get(order);
  if (!meta) throw new Error(`Missing source element order ${order}`);
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
  const { object } = objectFor(order);
  object.fill = fill;
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
  text.autoFit = "shrinkText";
  text.wrap = "square";
}

function setText(order, value) {
  const { object } = objectFor(order);
  object.text = value;
}

function setGrid(orderV1, orderH1, orderV2, orderH2, x, y, size) {
  const step = size / 3;
  setBox(orderV1, x + step, y, 0, size);
  setBox(orderH1, x, y + step, size, 0);
  setBox(orderV2, x + step * 2, y, 0, size);
  setBox(orderH2, x, y + step * 2, size, 0);
}

function setMask(order, x, y, size) {
  setBox(order, x, y, size, size);
}

// First enforce Times New Roman and the 12 pt minimum on every visible text object.
for (const meta of layout.elements) {
  if (typeof meta.text === "string" && meta.text.length > 0) styleText(Number(meta.order), MIN_PX);
}

// Global hierarchy.
styleText(1, 34, { bold: true, color: COLOR.brown, alignment: "left" });
styleText(2, 17, { color: COLOR.rust, alignment: "left" });
styleText(3, 16, { bold: true, color: COLOR.green, alignment: "right" });

// Panel letters are deliberately quiet; panel titles remain the hierarchy anchors.
const panelLetters = [16, 20, 24, 28];
const panelTitles = [17, 21, 25, 29];
const panelX = [38, 428, 818, 1208];
const letterColors = [COLOR.letterA, COLOR.letterB, COLOR.letterC, COLOR.letterD];
for (let i = 0; i < 4; i += 1) {
  setBox(panelLetters[i], panelX[i] + 18, 141, 22, 28);
  styleText(panelLetters[i], 16, {
    bold: false,
    color: letterColors[i],
    alignment: "left",
    verticalAlignment: "middle",
    insets: { top: 0, right: 0, bottom: 0, left: 0 },
  });
  setBox(panelTitles[i], panelX[i] + 52, 136, 282, 36);
  styleText(panelTitles[i], i === 1 ? 19 : 20, {
    bold: true,
    color: COLOR.dark,
    alignment: "left",
    verticalAlignment: "middle",
    insets: { top: 0, right: 0, bottom: 0, left: 0 },
  });
}

// Panel A: enlarge both retinal views from 124 px to 140 px.
setBox(30, 50, 194, 160, 30);
setBox(31, 218, 194, 160, 30);
styleText(30, 16, { bold: true });
styleText(31, 16, { bold: true });

setBox(32, 58, 228, 144, 144);
setFill(32, "none");
setBox(33, 60, 230, 140, 140);
setGrid(34, 35, 36, 37, 60, 230, 140);

setBox(38, 228, 228, 144, 144);
setFill(38, "none");
setBox(39, 230, 230, 140, 140);
const aStep = 140 / 3;
setMask(40, 230, 230, aStep);
setMask(41, 230 + aStep, 230, aStep);
setMask(42, 230 + aStep * 2, 230, aStep);
setMask(43, 230, 230 + aStep, aStep);
setMask(44, 230 + aStep * 2, 230 + aStep, aStep);
setMask(45, 230, 230 + aStep * 2, aStep);
setMask(46, 230 + aStep, 230 + aStep * 2, aStep);
setMask(47, 230 + aStep * 2, 230 + aStep * 2, aStep);
setGrid(48, 49, 50, 51, 230, 230, 140);

setBox(52, 64, 384, 302, 108);
setBox(53, 78, 399, 166, 36);
setBox(54, 252, 399, 96, 36);
setBox(55, 78, 445, 150, 38);
setText(55, "Task evidence");
setBox(56, 228, 445, 124, 38);
for (const order of [53, 54, 55, 56]) styleText(order, 16, { bold: true });
styleText(54, 16, { bold: true, color: COLOR.green });
styleText(56, 16, { bold: true, color: COLOR.magenta });

setBox(57, 72, 528, 286, 172);
setBox(58, 92, 540, 246, 34);
setBox(59, 88, 580, 254, 100);
styleText(58, 17, { bold: true, color: COLOR.rust });
styleText(59, 16, { lineSpacing: 1.02, insets: { top: 3, right: 4, bottom: 3, left: 4 } });

// Panel B: enlarge the three regional-mask examples from 78 px to 96 px.
const bImageX = [444, 556, 668];
const bBgOrders = [60, 66, 80];
const bImageOrders = [61, 67, 81];
for (let i = 0; i < 3; i += 1) {
  setBox(bBgOrders[i], bImageX[i] - 2, 204, 100, 100);
  setBox(bImageOrders[i], bImageX[i], 206, 96, 96);
}
setGrid(62, 63, 64, 65, 444, 206, 96);

const bStep = 32;
setMask(68, 556, 206, bStep);
setMask(69, 588, 206, bStep);
setMask(70, 620, 206, bStep);
setMask(71, 556, 238, bStep);
setMask(72, 620, 238, bStep);
setMask(73, 556, 270, bStep);
setMask(74, 588, 270, bStep);
setMask(75, 620, 270, bStep);
setGrid(76, 77, 78, 79, 556, 206, 96);

setMask(82, 668, 206, bStep);
setMask(83, 732, 206, bStep);
setMask(84, 668, 270, bStep);
setMask(85, 732, 270, bStep);
setGrid(86, 87, 88, 89, 668, 206, 96);

setBox(90, 438, 306, 108, 30);
setBox(91, 548, 306, 120, 30);
setBox(92, 658, 306, 118, 30);
for (const order of [90, 91, 92]) styleText(order, 16, { bold: true });

setBox(93, 454, 342, 302, 70);
setBox(94, 468, 352, 274, 56);
setText(94, "Region masks specify which 3×3 evidence tokens remain visible.");
styleText(94, 16, { bold: true, lineSpacing: 0.98 });

setBox(101, 447, 514, 112, 48);
setBox(102, 552, 514, 108, 48);
setBox(103, 662, 514, 104, 48);
for (const order of [101, 102, 103]) styleText(order, 16, { bold: true, lineSpacing: 0.95 });
setBox(104, 454, 582, 302, 68);
setBox(105, 468, 594, 274, 50);
styleText(105, 16, { bold: true, lineSpacing: 0.98 });
setBox(106, 454, 676, 302, 50);
styleText(106, 16, { italic: true, color: COLOR.rust, lineSpacing: 0.96 });

// Panel C: enlarge the evidence-bank retinal input from 100 px to 116 px.
setBox(107, 832, 206, 124, 124);
setBox(108, 836, 210, 116, 116);
setGrid(109, 110, 111, 112, 836, 210, 116);
setBox(113, 964, 222, 184, 96);
setBox(114, 980, 228, 156, 38);
setBox(115, 980, 270, 156, 30);
styleText(114, 17, { bold: true });
styleText(115, 16, { italic: true, color: COLOR.rust });

setBox(7, 986, 332, 18, 24);
setBox(116, 842, 356, 306, 88);
setBox(117, 858, 367, 274, 46);
setBox(118, 858, 417, 274, 26);
styleText(117, 17, { bold: true, lineSpacing: 0.96 });
styleText(118, 16, { color: COLOR.rust });
setBox(8, 986, 456, 18, 24);
setBox(119, 842, 480, 306, 98);
setBox(120, 858, 492, 274, 42);
setBox(121, 858, 538, 274, 34);
styleText(120, 19, { bold: true });
styleText(121, 16, { color: COLOR.rust });
setBox(9, 907, 594, 16, 24);
setBox(10, 1067, 594, 16, 24);
setBox(122, 842, 630, 146, 96);
setBox(123, 1002, 630, 146, 96);
setBox(124, 850, 640, 130, 74);
setBox(125, 1010, 640, 130, 74);
styleText(124, 16, { bold: true, lineSpacing: 0.92 });
styleText(125, 16, { bold: true, color: COLOR.magenta, lineSpacing: 0.92 });

// Panel D: taller cards accommodate the 12 pt minimum without crowding.
const cardY = [216, 318, 420, 522];
const cardOrders = [126, 129, 132, 135];
const headOrders = [127, 130, 133, 136];
const subOrders = [128, 131, 134, 137];
const subCopy = [
  "390 held-out images · five seeds",
  "one-region occlusion versus attention",
  "2,597 MMRDR-UWF images · no adaptation",
  "fixed split plus grouped nested evaluation",
];
for (let i = 0; i < 4; i += 1) {
  setBox(cardOrders[i], 1234, cardY[i], 302, 88);
  setBox(headOrders[i], 1250, cardY[i] + 8, 270, 30);
  setBox(subOrders[i], 1250, cardY[i] + 42, 270, 36);
  setText(subOrders[i], subCopy[i]);
  styleText(headOrders[i], 17, { bold: true, alignment: "left" });
  styleText(subOrders[i], 16, { alignment: "left", lineSpacing: 0.96 });
}
setBox(11, 1378, 304, 14, 14);
setBox(12, 1378, 406, 14, 14);
setBox(13, 1378, 508, 14, 14);
setBox(138, 1234, 638, 302, 118);
setBox(139, 1250, 650, 270, 94);
setText(139, "Synthetic evidence loss only\nNo clinician-adjudicated sufficiency labels\nPaired risk requires two views");
styleText(139, 16, { bold: true, color: COLOR.rust, lineSpacing: 0.95 });

styleText(141, 16, { bold: true, color: COLOR.brown });

// Preserve source notes and document the layout revision.
slide.speakerNotes.append(
  "\nRevision 2026-08-14: retinal examples enlarged; all visible text set to Times New Roman with a minimum of 12 pt; panel letters muted."
);
slide.speakerNotes.setVisible(true);

await writeBlob(PREVIEW, await presentation.export({ slide, format: "png", scale: 2 }));
await fs.writeFile(AFTER_LAYOUT, await (await slide.export({ format: "layout" })).text());
const pptx = await PresentationFile.exportPptx(presentation);
await pptx.save(OUTPUT);

console.log(JSON.stringify({ output: OUTPUT, preview: PREVIEW, layout: AFTER_LAYOUT }, null, 2));
