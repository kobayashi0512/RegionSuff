import fs from 'node:fs/promises';
import { Presentation, PresentationFile } from '@oai/artifact-tool';

const FIGURE_DIR = '/Users/tongyue/Documents/77f /7hao/paper_design/figures_v6_callout_fixed';
const BUILD_DIR = '/Users/tongyue/Documents/77f /7hao/paper_design/figures_v2/ppt_build';
const OUTPUT = '/Users/tongyue/Documents/ppf/第四论文/RegionSuff_结果图3-8_标注引导线修正版.pptx';

const figures = [
  ['Figure3_Controlled_Visibility_RMB20_v3_large_font.png', 'Figure 3 — controlled evidence loss'],
  ['Figure4_Ablations_RMB20_v3_large_font.png', 'Figure 4 — component ablations'],
  ['Figure5_Attention_Occlusion_RMB20_v6_callout_fixed.png', 'Figure 5 — attention intervention'],
  ['Figure6_External_Replication_RMB20_v4_overlap_fixed.png', 'Figure 6 — external UWF evaluation'],
  ['Figure7_Selective_Risk_RMB20_v3_large_font.png', 'Figure 7 — paired-view underestimation audit'],
  ['Figure8_Continuous_Aperture_Optimization_RMB20_v3_large_font.png', 'Figure 8 — pixel-aperture training'],
];

async function writeBlob(filePath, blob) {
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

function fitContain(imageWidth, imageHeight, frame) {
  const scale = Math.min(frame.width / imageWidth, frame.height / imageHeight);
  const width = imageWidth * scale;
  const height = imageHeight * scale;
  return {
    left: frame.left + (frame.width - width) / 2,
    top: frame.top + (frame.height - height) / 2,
    width,
    height,
  };
}

async function dimensions(filePath) {
  // The vector redraws are 2000×1160 (Figures 3–7) and 2000×900 (Figure 8).
  // Keep this mapping explicit so a future replacement does not distort a panel.
  return filePath.includes('Figure8_') ? { width: 2000, height: 900 } : { width: 2000, height: 1160 };
}

async function main() {
  await fs.mkdir(BUILD_DIR, { recursive: true });
  const presentation = Presentation.create({ slideSize: { width: 1280, height: 720 } });
  const frame = { left: 24, top: 18, width: 1232, height: 684 };

  for (let index = 0; index < figures.length; index += 1) {
    const [filename, title] = figures[index];
    const figurePath = `${FIGURE_DIR}/${filename}`;
    const figureBytes = await fs.readFile(figurePath);
    const sourceSize = await dimensions(figurePath);
    const slide = presentation.slides.add();
    slide.background.fill = '#FFFDFC';

    slide.images.add({
      blob: figureBytes,
      contentType: 'image/png',
      alt: title,
      fit: 'contain',
      position: fitContain(sourceSize.width, sourceSize.height, frame),
    });

    slide.speakerNotes.textFrame.setText(
      `[Sources]\n- Exact values reproduced from the locked RegionSuff experiment registry in /Users/tongyue/Documents/77f /7hao/experiments.\n- ${title}; publication redraw generated from the local result files without value changes.`
    );
    slide.speakerNotes.setVisible(true);

    await writeBlob(`${BUILD_DIR}/slide-${String(index + 1).padStart(2, '0')}.png`, await presentation.export({ slide, format: 'png', scale: 1 }));
    await fs.writeFile(`${BUILD_DIR}/slide-${String(index + 1).padStart(2, '0')}.layout.json`, await (await slide.export({ format: 'layout' })).text());
  }

  await writeBlob(`${BUILD_DIR}/deck-montage.webp`, await presentation.export({ format: 'webp', montage: true, scale: 1 }));
  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(OUTPUT);
  console.log(`Wrote ${OUTPUT}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
