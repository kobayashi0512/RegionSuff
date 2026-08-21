import fs from "node:fs/promises";
import path from "node:path";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

Error.stackTraceLimit = 0;

const WORKSPACE = "/Users/tongyue/Documents/77f /7hao/paper_design/ppt_build/figure1_user_optimization";
const INPUT = path.join(WORKSPACE, "template-starter.pptx");
const LAYOUT = path.join(WORKSPACE, "template-starter-layout/starter-slide-01.layout.json");
const OUTPUT = "/Users/tongyue/Documents/ppf/第四论文/图1_排版优化版.pptx";
const PREVIEW = path.join(WORKSPACE, "optimized-slide-01.png");
const AFTER_LAYOUT = path.join(WORKSPACE, "optimized-slide-01.layout.json");
const AFTER_INSPECT = path.join(WORKSPACE, "optimized.inspect.ndjson");

const C = {
  brown: "#704C2B",
  rust: "#965E4A",
  dark: "#3A2D25",
  orange: "#D0913C",
  green: "#8B9A7C",
  magenta: "#C14F75",
  paper: "#FFFDFC",
  white: "#FFFFFF",
  warmLine: "#C8A590",
  softLine: "#DCCFC7",
};

async function writeBlob(filePath, blob) {
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

const layout = JSON.parse(await fs.readFile(LAYOUT, "utf8"));
const byOrder = new Map(layout.elements.map((element) => [Number(element.order), element]));
const presentation = await PresentationFile.importPptx(await FileBlob.load(INPUT));
const slide = presentation.slides.getItem(0);

function objectFor(id) {
  const meta = byOrder.get(id);
  if (!meta) throw new Error(`Missing source element order ${id}`);
  const object = slide.elements.items.find((element) => Number(element.id) === Number(meta.id));
  if (!object) throw new Error(`Missing imported slide element id ${meta.id} (order ${id})`);
  return { meta, object };
}

function setBox(id, left, top, width, height) {
  const { meta, object } = objectFor(id);
  const box = { left, top, width, height };
  if (meta.kind === "image") object.frame = box;
  else object.position = box;
}

function move(id, dx, dy) {
  const meta = byOrder.get(id);
  const [left, top, width, height] = meta.bbox;
  setBox(id, left + dx, top + dy, width, height);
}

function moveRange(start, end, dx, dy) {
  for (let id = start; id <= end; id += 1) move(id, dx, dy);
}

function setText(id, text, style = {}) {
  const { object } = objectFor(id);
  object.text = text;
  object.text.style = {
    typeface: "Calibri",
    fontSize: 15,
    color: C.dark,
    alignment: "center",
    verticalAlignment: "middle",
    autoFit: "shrinkText",
    wrap: "square",
    lineSpacing: 0.98,
    insets: { top: 2, right: 4, bottom: 2, left: 4 },
    ...style,
  };
}

function setSurface(id, { fill, lineFill, lineWidth = 1, radius } = {}) {
  const { object } = objectFor(id);
  if (fill) object.fill = fill;
  if (lineFill) object.line = { style: "solid", fill: lineFill, width: lineWidth };
  if (radius !== undefined) object.borderRadius = radius;
}

function setZ(id, zIndex) {
  const { object } = objectFor(id);
  object.zIndex = zIndex;
}

// Title band: shorter wording and a clearer left-to-right narrative cue.
setBox(1, 48, 12, 1280, 48);
setText(1, "RegionSuff: auditing retinal evidence under limited fields of view", {
  fontSize: 34,
  bold: true,
  color: C.brown,
  alignment: "left",
  insets: { top: 0, right: 0, bottom: 0, left: 0 },
});
setBox(2, 50, 68, 1240, 28);
setText(2, "Hidden evidence gap  •  controlled evidence loss  •  visibility-conditioned aggregation  •  evidence chain", {
  fontSize: 17,
  color: C.rust,
  alignment: "left",
  insets: { top: 0, right: 0, bottom: 0, left: 0 },
});
setBox(3, 1390, 24, 150, 28);
setText(3, "FIGURE 1", {
  fontSize: 16,
  bold: true,
  color: C.green,
  alignment: "right",
  insets: { top: 0, right: 0, bottom: 0, left: 0 },
});

// Four equal outer panels and shared header geometry.
const panelX = [38, 428, 818, 1208];
const panelIds = [14, 18, 22, 26];
const headerIds = [15, 19, 23, 27];
const letterIds = [16, 20, 24, 28];
const titleIds = [17, 21, 25, 29];
const panelTitles = ["Hidden evidence gap", "Controlled evidence loss", "RegionSuff model", "Evidence chain"];
const panelAccent = [C.rust, C.orange, C.green, C.rust];

for (let i = 0; i < 4; i += 1) {
  setBox(panelIds[i], panelX[i], 116, 354, 692);
  setSurface(panelIds[i], { fill: "none" });
  setBox(headerIds[i], panelX[i] + 12, 128, 330, 56);
  setBox(letterIds[i], panelX[i] + 18, 137, 30, 34);
  setBox(titleIds[i], panelX[i] + 64, 136, 268, 36);
  setText(letterIds[i], String.fromCharCode(65 + i), {
    fontSize: 23,
    bold: true,
    color: panelAccent[i],
    alignment: "left",
    insets: { top: 0, right: 0, bottom: 0, left: 0 },
  });
  setText(titleIds[i], panelTitles[i], {
    fontSize: i === 1 ? 19 : 20,
    bold: true,
    color: C.dark,
    alignment: "left",
    insets: { top: 0, right: 0, bottom: 0, left: 0 },
  });
}

setBox(4, 400, 445, 22, 20);
setBox(5, 790, 445, 22, 20);
setBox(6, 1180, 445, 22, 20);

// Panel A — keep the image comparison dominant, then state the hidden mismatch and audit question.
setBox(30, 56, 198, 154, 28);
setText(30, "Full field", { fontSize: 14.5, bold: true });
setBox(31, 218, 198, 154, 28);
setText(31, "Center-only view", { fontSize: 14.5, bold: true });
moveRange(32, 51, 0, -6);

setBox(52, 64, 384, 302, 108);
setBox(53, 80, 399, 174, 32);
setText(53, "Technical gradability", { fontSize: 14.5, bold: true, alignment: "left" });
setBox(54, 274, 399, 74, 32);
setText(54, "PASS", { fontSize: 14.5, bold: true, color: C.green });
setBox(55, 80, 445, 174, 32);
setText(55, "Task-relevant evidence", { fontSize: 14.5, bold: true, alignment: "left" });
setBox(56, 246, 445, 102, 32);
setText(56, "INCOMPLETE", { fontSize: 13.5, bold: true, color: C.magenta });

setBox(57, 72, 528, 286, 172);
setBox(58, 92, 542, 246, 30);
setText(58, "Audit question", { fontSize: 15.5, bold: true, color: C.rust });
setBox(59, 88, 580, 254, 92);
setText(59, "How does a fixed DR classifier respond when visible retinal evidence is systematically restricted?", {
  fontSize: 15.5,
  color: C.dark,
  lineSpacing: 1.03,
  insets: { top: 4, right: 4, bottom: 4, left: 4 },
});
setSurface(57, { fill: "#FBF2ED", lineFill: C.rust, lineWidth: 1.1, radius: 16 });

// Panel B — two aligned perturbation families: regional masks and continuous apertures.
moveRange(60, 89, 0, -4);
setBox(90, 442, 304, 98, 28);
setText(90, "Full view", { fontSize: 13.5, bold: true });
setBox(91, 550, 304, 110, 28);
setText(91, "Center only", { fontSize: 13.5, bold: true });
setBox(92, 654, 304, 126, 28);
setText(92, "Center + cross", { fontSize: 13.5, bold: true });

setBox(93, 454, 342, 302, 70);
setBox(94, 468, 351, 274, 52);
setText(94, "Region masks define which 3×3 evidence tokens remain visible.", {
  fontSize: 15,
  bold: true,
  lineSpacing: 1,
});

moveRange(95, 103, 0, -30);
setBox(101, 447, 514, 112, 44);
setText(101, "Rectangle", { fontSize: 13.5, bold: true });
setBox(102, 552, 514, 108, 44);
setText(102, "Area-matched\ncircle", {
  fontSize: 12.6,
  bold: true,
  lineSpacing: 0.96,
  insets: { top: 1, right: 1, bottom: 1, left: 1 },
});
setBox(103, 662, 514, 104, 44);
setText(103, "Severe crop", { fontSize: 13.5, bold: true });

setBox(104, 454, 582, 302, 68);
setBox(105, 468, 592, 274, 48);
setText(105, "Pixel apertures vary visible area, location, and shape.", {
  fontSize: 14.5,
  bold: true,
});
setBox(106, 454, 676, 302, 34);
setText(106, "The original DR label is retained for every perturbed view.", {
  fontSize: 13.2,
  italic: true,
  color: C.rust,
});
setBox(106, 454, 674, 302, 46);
setSurface(106, { fill: "#FFF8EF", lineFill: "#E5B170", lineWidth: 0.8, radius: 10 });

// Panel C — one centered model pipeline with two equal outputs.
setBox(107, 842, 218, 104, 104);
setBox(108, 844, 220, 100, 100);
setBox(109, 877.33, 220, 0, 100);
setBox(110, 844, 253.33, 100, 0);
setBox(111, 910.67, 220, 0, 100);
setBox(112, 844, 286.67, 100, 0);
setBox(113, 964, 222, 184, 96);
setBox(114, 976, 236, 160, 36);
setText(114, "3×3 evidence bank", { fontSize: 16, bold: true });
setBox(115, 976, 274, 160, 26);
setText(115, "visibility mask m", { fontSize: 13.5, italic: true, color: C.rust });

setBox(7, 986, 326, 18, 26);
setBox(116, 842, 356, 306, 88);
setBox(117, 858, 364, 274, 44);
setText(117, "Frozen retinal image-quality encoder", { fontSize: 15.5, bold: true });
setBox(118, 858, 412, 274, 24);
setText(118, "shared across regions", { fontSize: 13.5, color: C.rust });

setBox(8, 986, 450, 18, 26);
setBox(119, 842, 480, 306, 98);
setBox(120, 858, 488, 274, 40);
setText(120, "Masked attention", { fontSize: 17, bold: true });
setBox(121, 858, 532, 274, 32);
setText(121, "normalizes over visible tokens only", { fontSize: 13.5, color: C.rust });

setBox(9, 907, 590, 16, 24);
setBox(10, 1067, 590, 16, 24);
for (const arrow of [7, 8, 9, 10]) setZ(arrow, 106);
setBox(122, 842, 626, 146, 92);
setBox(123, 1002, 626, 146, 92);
setBox(124, 852, 638, 126, 66);
setText(124, "DR severity\nNormal · NPDR · PDR", { fontSize: 14.5, bold: true, lineSpacing: 0.95 });
setBox(125, 1012, 638, 126, 66);
setText(125, "Paired-view audit\nunderestimation risk", {
  fontSize: 14.2,
  bold: true,
  color: C.magenta,
  lineSpacing: 0.95,
});

// Panel D — equal-height evidence cards, regular gaps, and a quieter boundary note.
const cardY = [216, 318, 420, 522];
const cardIds = [126, 129, 132, 135];
const headIds = [127, 130, 133, 136];
const subIds = [128, 131, 134, 137];
const heads = [
  "Internal robustness",
  "Functional intervention",
  "External severity evaluation",
  "Paired-view risk audit",
];
const subs = [
  "390 held-out images · five source-training seeds",
  "one-region occlusion aligned with attention",
  "2,597 MMRDR-UWF images · no adaptation",
  "fixed split and grouped nested evaluation",
];
const headColors = [C.orange, C.orange, C.green, C.magenta];

for (let i = 0; i < 4; i += 1) {
  setBox(cardIds[i], 1234, cardY[i], 302, 88);
  setBox(headIds[i], 1250, cardY[i] + 10, 270, 28);
  setText(headIds[i], heads[i], {
    fontSize: 15.5,
    bold: true,
    color: headColors[i],
    alignment: "left",
  });
  setBox(subIds[i], 1250, cardY[i] + 43, 270, 30);
  setText(subIds[i], subs[i], {
    fontSize: 13.1,
    color: C.dark,
    alignment: "left",
    lineSpacing: 0.96,
  });
}
setBox(11, 1378, 304, 14, 14);
setBox(12, 1378, 406, 14, 14);
setBox(13, 1378, 508, 14, 14);
for (const arrow of [11, 12, 13]) setZ(arrow, 125);
setBox(138, 1234, 638, 302, 118);
setBox(139, 1250, 650, 270, 94);
setText(139, "Synthetic evidence loss only\nNo clinician-adjudicated sufficiency labels\nPaired risk requires full and limited views", {
  fontSize: 13.2,
  bold: true,
  color: C.rust,
  lineSpacing: 1.02,
});
setSurface(138, { fill: "#FBF4F0", lineFill: C.warmLine, lineWidth: 1, radius: 12 });

// Concluding statement aligned to the full four-panel span.
setBox(140, 48, 820, 1504, 52);
setBox(141, 72, 830, 1456, 32);
setText(141, "Core finding: DR model behavior depends on the composition and topology of visible retinal evidence—not on image quality or visible area alone.", {
  fontSize: 15.8,
  bold: true,
  color: C.brown,
});
setSurface(140, { fill: C.paper, lineFill: "#E5B170", lineWidth: 1, radius: 12 });

// Preserve the provenance of the user-provided deck in the slide notes.
slide.speakerNotes.textFrame.setText(
  "[Sources]\n- User-provided editable Figure 1 deck: /Users/tongyue/Documents/ppf/第四论文/图1.pptx (accessed 2026-08-14).\n- All retinal images and scientific statements are inherited from the source deck; wording was shortened only for layout clarity."
);
slide.speakerNotes.setVisible(true);

await writeBlob(PREVIEW, await presentation.export({ slide, format: "png", scale: 2 }));
await fs.writeFile(AFTER_LAYOUT, await (await slide.export({ format: "layout" })).text());
const inspect = await presentation.inspect({
  kind: "slide,textbox,shape,image,notes",
  maxChars: 50000,
});
await fs.writeFile(AFTER_INSPECT, `${inspect.ndjson}\n`, "utf8");

const pptx = await PresentationFile.exportPptx(presentation);
await pptx.save(OUTPUT);

console.log(JSON.stringify({ output: OUTPUT, preview: PREVIEW, layout: AFTER_LAYOUT }, null, 2));
