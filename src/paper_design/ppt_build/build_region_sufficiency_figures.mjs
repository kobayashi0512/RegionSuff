import fs from "node:fs/promises";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const ROOT = "/Users/tongyue/Documents/77f /7hao";
const FIG = `${ROOT}/paper_design/figures`;
const BUILD = `${ROOT}/paper_design/ppt_build`;
const OUT = `${ROOT}/RegionSufficiency_论文框架与算法图_RMB20.pptx`;

const W = 1280;
const H = 720;
const C = {
  paper: "#FFFDFC",
  pale: "#F7ECE6",
  peach: "#F5CFAA",
  orange: "#E49F5D",
  umber: "#965E4A",
  brown: "#704C2B",
  olive: "#8B9A7C",
  paleOlive: "#E5E8D9",
  rose: "#C74282",
  ink: "#3F3027",
  line: "#E8C6AA",
};

async function bytes(path) {
  const b = await fs.readFile(path);
  return b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength);
}

function box(slide, x, y, w, h, fill = "none", radius = "none", line = "none", width = 0) {
  const shape = slide.shapes.add({
    geometry: radius === "none" ? "rect" : "roundRect",
    position: { left: x, top: y, width: w, height: h },
    fill,
    line: { style: "solid", fill: line, width },
  });
  if (radius !== "none") shape.borderRadius = radius;
  return shape;
}

function text(slide, value, x, y, w, h, style = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    position: { left: x, top: y, width: w, height: h },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = value;
  shape.text.style = {
    fontSize: style.fontSize ?? 18,
    color: style.color ?? C.ink,
    bold: style.bold ?? false,
    italic: style.italic ?? false,
    alignment: style.alignment ?? "left",
    fontFace: style.fontFace ?? "Arial",
  };
  return shape;
}

function rule(slide, x, y, w, color = C.line, height = 2) {
  return box(slide, x, y, w, height, color, "none", color, 0);
}

function addNotes(slide, talk, sources) {
  slide.speakerNotes.textFrame.setText(
    `${talk}\n\n[Sources]\n${sources.map((s) => `- ${s}`).join("\n")}\n[/Sources]`
  );
  slide.speakerNotes.setVisible(true);
}

function addTag(slide, value, x, y, w, fill, color = "#FFFFFF") {
  box(slide, x, y, w, 34, fill, "rounded-xl", fill, 0);
  text(slide, value, x, y + 7, w, 20, { fontSize: 13, bold: true, color, alignment: "center" });
}

function addFigureSlide(slide, figureBytes, number, title, subtitle, talk, sources) {
  slide.background.fill = C.paper;
  text(slide, `FIGURE ${number}`, 46, 21, 150, 22, { fontSize: 12, bold: true, color: C.orange });
  text(slide, title, 46, 49, 950, 44, { fontSize: 28, bold: true, color: C.brown });
  text(slide, subtitle, 46, 92, 1030, 25, { fontSize: 14, color: C.umber });
  text(slide, String(number).padStart(2, "0"), 1160, 24, 72, 28, { fontSize: 18, bold: true, color: C.olive, alignment: "right" });
  rule(slide, 46, 125, 1186, C.line, 2);
  box(slide, 40, 142, 1200, 532, "#FFFFFF", "rounded-xl", C.line, 1);
  slide.images.add({
    blob: figureBytes,
    contentType: "image/png",
    alt: `${title}. High-resolution RegionSufficiency publication figure in an RMB 20-inspired palette.`,
    fit: "contain",
    position: { left: 48, top: 148, width: 1184, height: 520 },
  });
  addNotes(slide, talk, sources);
}

async function main() {
  await fs.mkdir(BUILD, { recursive: true });
  const fig1 = await bytes(`${FIG}/Figure1_Study_Overview_RMB20.png`);
  const fig2 = await bytes(`${FIG}/Figure2_Method_Architecture_RMB20.png`);
  const palette = await bytes(`${FIG}/RMB20_Publication_Palette.png`);

  const deck = Presentation.create({ slideSize: { width: W, height: H } });

  // 01 — Cover
  {
    const s = deck.slides.add();
    s.background.fill = C.paper;
    box(s, 0, 0, 26, H, C.umber);
    box(s, 26, 0, 8, H, C.orange);
    text(s, "PAPER FIGURE DECK", 76, 62, 350, 26, { fontSize: 13, bold: true, color: C.orange });
    text(s, "RegionSufficiency", 76, 118, 590, 62, { fontSize: 46, bold: true, color: C.brown });
    text(s, "论文总体框架图与算法模块图", 76, 190, 600, 42, { fontSize: 28, bold: true, color: C.umber });
    text(s, "Visibility-conditioned regional evidence aggregation under limited fields of view", 76, 248, 600, 72, { fontSize: 21, color: C.ink });
    rule(s, 76, 346, 230, C.orange, 5);
    text(s, "RMB 20-inspired publication system", 76, 371, 420, 26, { fontSize: 15, bold: true, color: C.olive });
    text(s, "Figure 1 · Study overview\nFigure 2 · Method architecture", 76, 420, 430, 70, { fontSize: 19, color: C.ink });

    box(s, 716, 66, 500, 560, C.pale, "rounded-3xl", C.line, 1);
    s.images.add({ blob: fig1, contentType: "image/png", alt: "Thumbnail of Figure 1 study overview", fit: "contain", position: { left: 742, top: 95, width: 448, height: 250 } });
    s.images.add({ blob: fig2, contentType: "image/png", alt: "Thumbnail of Figure 2 method architecture", fit: "contain", position: { left: 742, top: 355, width: 448, height: 250 } });
    addTag(s, "STUDY STORY", 790, 312, 132, C.orange);
    addTag(s, "ALGORITHM", 974, 312, 132, C.olive);
    s.images.add({ blob: palette, contentType: "image/png", alt: "RMB 20-inspired publication palette", fit: "contain", position: { left: 76, top: 545, width: 560, height: 86 } });
    text(s, "High-resolution figures are placed as slide graphics; editable SVG/PDF source files remain in paper_design/figures.", 76, 653, 1100, 24, { fontSize: 13, color: C.umber });
    addNotes(
      s,
      "开场只说一句：这套图先回答“为什么清晰图仍可能证据不足”，再回答“算法如何只聚合真正可见的区域证据”。",
      [
        "Local project-generated Figure 1 and Figure 2; underlying experiment registry: /Users/tongyue/Documents/77f /7hao/experiments/",
        "Color system: project RMB 20-inspired publication palette; no third-party graphic asset is embedded on this slide.",
      ]
    );
  }

  // 02 — Figure 1
  {
    const s = deck.slides.add();
    addFigureSlide(
      s,
      fig1,
      1,
      "A clear image can still be diagnostically insufficient",
      "Problem → cohorts and views → RegionSufficiency → evidence-aware action",
      "讲图顺序严格从左到右：先区分 image quality 与 diagnostic sufficiency；再说明内部 UWF-DR 开发和 MMRDR-UWF 独立外测；随后指出 3×3 区域证据模型；最后落到 severity、低估风险以及 accept/defer。不要把 accept/defer 讲成已经临床验证的安全系统。",
      [
        "Local figure: /Users/tongyue/Documents/77f /7hao/paper_design/figures/Figure1_Study_Overview_RMB20.png",
        "Internal cohort and model evidence: /Users/tongyue/Documents/77f /7hao/experiments/exp36_multiseed_deep_region/results.json",
        "External MMRDR-UWF evidence: /Users/tongyue/Documents/77f /7hao/experiments/exp53_mmrdr_uwf_external_fov/results.json",
      ]
    );
  }

  // 03 — Figure 2
  {
    const s = deck.slides.add();
    addFigureSlide(
      s,
      fig2,
      2,
      "Visibility-conditioned regions expose the evidence gap",
      "View construction → frozen regional representation → masked attention → severity and paired-view risk audit",
      "先讲 A：视网膜切成 3×3，并由 mask 明确哪些区域可见；再讲 B：同一个冻结 RetinaRadar 编码器处理所有区域，只训练投影；接着讲 C：full 与 limited 使用同一注意力和分类器，区别只在可见 mask；最后讲 D：严重度概率进入 18 维 paired evidence-gap vector，再由验证集拟合的风险头与 Clopper–Pearson 阈值做 accept/defer。强调风险头当前依赖 full/limited 配对，只是研究审计，不是单张有限视野部署头。",
      [
        "Local figure: /Users/tongyue/Documents/77f /7hao/paper_design/figures/Figure2_Method_Architecture_RMB20.png",
        "Final frozen model configuration: /Users/tongyue/Documents/77f /7hao/experiments/exp42_final_manuscript_summary/results.json",
        "Selective risk protocol: /Users/tongyue/Documents/77f /7hao/experiments/exp40_final_region_selective_risk/results.json",
        "Nested threshold audit: /Users/tongyue/Documents/77f /7hao/experiments/exp47_nested_risk_calibration/results.json",
      ]
    );
  }

  // 04 — Placement guide
  {
    const s = deck.slides.add();
    s.background.fill = C.paper;
    text(s, "PAPER PLACEMENT", 58, 38, 260, 22, { fontSize: 12, bold: true, color: C.orange });
    text(s, "两张图在论文里各自承担什么任务？", 58, 72, 960, 46, { fontSize: 31, bold: true, color: C.brown });
    rule(s, 58, 132, 1164, C.line, 2);

    box(s, 58, 170, 542, 390, C.pale, "rounded-2xl", C.umber, 1);
    addTag(s, "FIGURE 1", 88, 194, 112, C.orange);
    text(s, "Introduction", 88, 252, 390, 32, { fontSize: 24, bold: true, color: C.brown });
    text(s, "插在首次提出 RegionSufficiency 之后", 88, 292, 440, 30, { fontSize: 17, bold: true, color: C.umber });
    text(s, "它负责把全文故事讲清楚：\n\n• 什么是灯下黑问题\n• 两个主数据集怎么分工\n• 方法只看可见区域证据\n• 四组实验最终回答什么", 88, 340, 445, 180, { fontSize: 18, color: C.ink });

    box(s, 680, 170, 542, 390, C.paleOlive, "rounded-2xl", C.olive, 1);
    addTag(s, "FIGURE 2", 710, 194, 112, C.olive);
    text(s, "Materials and Methods", 710, 252, 430, 32, { fontSize: 24, bold: true, color: C.brown });
    text(s, "插在 2.4 RegionSufficiency architecture", 710, 292, 465, 30, { fontSize: 17, bold: true, color: C.umber });
    text(s, "它负责把算法复现清楚：\n\n• 区域、mask 和随机遮挡\n• 冻结编码器与可训练投影\n• masked attention 的共享权重\n• 18维风险向量和阈值校准", 710, 340, 445, 180, { fontSize: 18, color: C.ink });

    box(s, 58, 596, 1164, 72, "#FFFFFF", "rounded-xl", C.line, 1);
    text(s, "一句话原则", 86, 619, 145, 24, { fontSize: 16, bold: true, color: C.rose });
    text(s, "Figure 1 讲“为什么要做”；Figure 2 讲“到底怎么做”。两张图不重复，前后构成完整叙事。", 240, 617, 930, 28, { fontSize: 18, bold: true, color: C.ink });
    addNotes(
      s,
      "这一页是排版与讲述提示，不需要放进正式论文。用于答辩或组会时提醒自己：Figure 1 不能陷入算法细节，Figure 2 不能重新讲临床动机。",
      ["Local manuscript structure: /Users/tongyue/Documents/77f /7hao/RegionSufficiency_论文稿件_已插入框架与算法图.docx"]
    );
  }

  for (const [index, slide] of deck.slides.items.entries()) {
    const stem = `${BUILD}/slide-${String(index + 1).padStart(2, "0")}`;
    const png = await deck.export({ slide, format: "png", scale: 1 });
    await fs.writeFile(`${stem}.png`, new Uint8Array(await png.arrayBuffer()));
    const layout = await slide.export({ format: "layout" });
    await fs.writeFile(`${stem}.layout.json`, await layout.text());
  }
  const montage = await deck.export({ format: "webp", montage: true, scale: 1 });
  await fs.writeFile(`${BUILD}/deck-montage.webp`, new Uint8Array(await montage.arrayBuffer()));
  const pptx = await PresentationFile.exportPptx(deck);
  await pptx.save(OUT);
  console.log(OUT);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
