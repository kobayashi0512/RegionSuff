#!/usr/bin/env python3
"""Build the complete RegionSufficiency manuscript from locked local results."""
from __future__ import annotations

import sys
import io
from pathlib import Path

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor
from matplotlib.font_manager import FontProperties
from matplotlib.mathtext import math_to_image
from PIL import Image


ROOT = Path("/Users/tongyue/Documents/77f /7hao")
BASE_DIR = ROOT / "paper_design/manuscript_build"
sys.path.insert(0, str(BASE_DIR))
import build_manuscript as base  # noqa: E402

REFERENCE = Path("/Users/tongyue/Documents/ppf/第二论文/VOCT_2.0.docx")
FIG = ROOT / "paper_design/figures"
OUTPUT = ROOT / "RegionSufficiency_优化实验筛选版_连续视野增强.docx"

INK, BROWN, UMBER, ORANGE, OLIVE, ROSE = base.INK, base.BROWN, base.UMBER, base.ORANGE, base.OLIVE, base.ROSE
PAPER, PALE = base.PAPER, base.PALE


def set_font(run, size=12, bold=False, italic=False, color="000000", underline=False, name="Times New Roman"):
    base.set_run_font(run, name=name, size=size, bold=bold, italic=italic, color=color)
    run.underline = underline
    run._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), name)
    return run


def style_voct_document(doc):
    """Apply the typography of VOCT_2.0 without disturbing its page geometry."""
    for name in ("Normal", "Normal (Web)"):
        if name not in [s.name for s in doc.styles]:
            if name == "Normal (Web)":
                doc.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
            else:
                continue
        style = doc.styles[name]
        style.font.name = "Times New Roman"
        style.font.size = Pt(12)
        style.font.color.rgb = RGBColor(0, 0, 0)
        style._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), "Times New Roman")
        style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        style.paragraph_format.line_spacing = 1.15
        style.paragraph_format.space_after = Pt(6)
        style.paragraph_format.first_line_indent = None
    for name in ("Heading 1", "Heading 2", "Heading 3"):
        if name in [s.name for s in doc.styles]:
            style = doc.styles[name]
            style.font.name = "Times New Roman"
            style.font.size = Pt(14)
            style.font.bold = True
            style.font.color.rgb = RGBColor(0, 0, 0)
            style._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), "Times New Roman")
            style.paragraph_format.space_before = Pt(10)
            style.paragraph_format.space_after = Pt(6)
            style.paragraph_format.keep_with_next = True
    # The reference has no running header or visible page-number footer.
    for section in doc.sections:
        for part in (section.header, section.footer):
            for p in part.paragraphs:
                p.clear()


def add_text(doc, text, cite=None, first_line=False):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.first_line_indent = None
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(text)
    set_font(r, size=12)
    if cite:
        r = p.add_run(cite)
        set_font(r, size=12)
    base.set_paragraph_keep(p, keep_lines=True)
    return p


def add_bullet(doc, text):
    p = doc.add_paragraph(style="List Bullet" if "List Bullet" in [s.name for s in doc.styles] else None)
    p.paragraph_format.left_indent = Cm(0.6)
    p.paragraph_format.first_line_indent = Cm(-0.35)
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run(text)
    set_font(r, size=12)
    return p


def add_title(doc):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(34)
    p.paragraph_format.space_after = Pt(42)
    p.paragraph_format.line_spacing = 1.15
    r = p.add_run("RegionSufficiency: Visibility-Conditioned Regional Evidence Aggregation for Diagnostic Sufficiency in Ultra-Widefield Fundus Imaging")
    set_font(r, size=16, bold=True)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run("Liwei Liu*")
    set_font(r, size=16)
    r = p.add_run(", Kaiwen Deng")
    set_font(r, size=16)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_after = Pt(42)
    r = p.add_run("School of Railway Intelligent Engineering, Dalian Jiaotong University, Dalian, 116028, China")
    set_font(r, size=16)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run("*Corresponding author")
    set_font(r, size=16)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_after = Pt(38)
    r = p.add_run("Email: ")
    set_font(r, size=16, bold=True)
    r = p.add_run("Liwei Liu (")
    set_font(r, size=16)
    r = p.add_run("liutree80@163.com")
    set_font(r, size=16, color="0563C1", underline=True)
    r = p.add_run(")")
    set_font(r, size=16)


def add_heading(doc, text, level=1, page_break=False):
    p = doc.add_paragraph(style="Heading 2" if level == 1 else "Heading 3")
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    set_font(r, size=14, bold=True)
    return p


def add_key_value(doc, key, value):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(key + " ")
    set_font(r, size=12, bold=True)
    r = p.add_run(value)
    set_font(r, size=12)
    return p


def add_figure(doc, path, number, caption):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(path), width=Inches(5.65))
    cp = doc.add_paragraph()
    cp.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    cp.paragraph_format.line_spacing = 1.0
    cp.paragraph_format.space_before = Pt(2)
    cp.paragraph_format.space_after = Pt(6)
    r = cp.add_run(f"Figure {number}. ")
    set_font(r, size=10.5, bold=True)
    r = cp.add_run(caption)
    set_font(r, size=10.5)
    base.set_paragraph_keep(cp, keep_lines=True)
    return p


def add_table(doc, number, caption, headers, rows, widths=None, font=8.1):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    if widths is None:
        widths = [Cm(14.6 / len(headers))] * len(headers)
    total_cm = sum(w.cm for w in widths)
    scale = min(1.0, 14.6 / total_cm)
    widths = [Cm(w.cm * scale) for w in widths]
    for cell, header, width in zip(table.rows[0].cells, headers, widths):
        cell.width = width
        base.set_cell_shading(cell, "E7E6E6")
        base.set_cell_border(cell, top={"val": "single", "sz": "8", "color": "000000"}, bottom={"val": "single", "sz": "6", "color": "000000"})
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(header)
        set_font(r, size=max(font, 8.5), bold=True)
    base.set_repeat_table_header(table.rows[0])
    for ridx, row in enumerate(rows):
        cells = table.add_row().cells
        for cidx, (cell, value, width) in enumerate(zip(cells, row, widths)):
            cell.width = width
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            base.set_cell_shading(cell, "FFFFFF")
            base.set_cell_border(cell, bottom={"val": "single", "sz": "3", "color": "BFBFBF" if ridx < len(rows) - 1 else "000000"})
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if cidx == 0 else WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(str(value))
            set_font(r, size=max(font, 8.5), bold=(cidx == 0))
        base.set_cant_split(table.rows[-1])
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(7)
    r = p.add_run(f"Table {number}. ")
    set_font(r, size=10.5, bold=True)
    r = p.add_run(caption)
    set_font(r, size=10.5)
    return table


EQUATIONS = {
    1: r"\mathcal{R}(x)=\{r_i=\operatorname{Crop}(x,b_i)\}_{i=1}^{K},\quad K=9",
    2: r"z_i=P\!\left(E(r_i)\right)\in\mathbb{R}^{d}",
    3: r"e_i=w_a^{\mathsf{T}}\tanh(W_a z_i+b_a)+b_s",
    4: r"a_i(m)=\frac{m_i\exp(e_i)}{\sum_{j=1}^{K}m_j\exp(e_j)}",
    5: r"h(m)=\sum_{i=1}^{K}a_i(m)z_i",
    6: r"p(m)=\operatorname{softmax}(W_c h(m)+b_c)",
    7: r"\mathcal{L}_{\mathrm{cls}}=-\frac{1}{N}\sum_{n=1}^{N}\sum_{c=0}^{C-1}w_c\,\mathbf{1}[y_n=c]\log p_{n,c}(m_n)",
    8: r"\widetilde{m}_i\sim\operatorname{Bernoulli}(1-\rho),\quad \rho=0.30,\quad \sum_{i=1}^{K}\widetilde{m}_i\geq1",
    9: r"\widehat{y}(m)=\mathrm{arg\,max}_{c}\,p_c(m),\qquad s(m)=\sum_{c=0}^{2}c\,p_c(m)",
    10: r"u(m_L,y)=\mathbf{1}[\widehat{y}(m_L)<y]",
    11: r"\operatorname{MAE}=\frac{1}{N}\sum_{n=1}^{N}|\widehat{y}_n-y_n|,\qquad \operatorname{Under}=\frac{1}{N}\sum_{n=1}^{N}u_n",
    12: r"\mathrm{MacroF1}=\frac{1}{C}\sum_{c=1}^{C}\frac{2\,\mathrm{Precision}_c\mathrm{Recall}_c}{\mathrm{Precision}_c+\mathrm{Recall}_c}",
    13: r"H(p)=-\sum_{c=0}^{2}p_c\log(p_c+\varepsilon)",
    14: r"D_{\mathrm{SKL}}(p_F,p_L)=\frac{1}{2}\!\left[D_{\mathrm{KL}}(p_F\Vert p_L)+D_{\mathrm{KL}}(p_L\Vert p_F)\right]",
    15: r"\phi=[p_F,p_L,p_F-p_L,|p_F-p_L|,s_F,s_L,s_F-s_L,H_F,H_L,D_{\mathrm{SKL}}]\in\mathbb{R}^{18}",
    16: r"\widetilde{\phi}=(\phi-\mu_{\phi})\oslash\sigma_{\phi},\qquad q(\phi)=\sigma(\beta^{\mathsf{T}}\widetilde{\phi}+b)",
    17: r"\tau_{\alpha}=\mathrm{arg\,max}_{\tau}\;\frac{n_{\tau}}{N}\quad\mathrm{s.t.}\quad \operatorname{UCP}(k_{\tau},n_{\tau};0.95)\leq\alpha",
    18: r"\operatorname{Coverage}(\tau)=\frac{n_{\tau}}{N},\qquad \operatorname{Risk}(\tau)=\frac{k_{\tau}}{n_{\tau}}",
    19: r"\Delta_i=\mathrm{MacroF1}_{\mathrm{full}}-\mathrm{MacroF1}_{\mathrm{mask}(i)}",
    20: r"\Delta_b^{*}=T\!\left(\{(y_{j_b},\widehat{y}_{L,j_b})\}\right)-T\!\left(\{(y_{j_b},\widehat{y}_{F,j_b})\}\right),\quad b=1,\ldots,B",
}

CORE_EQUATIONS = {2, 3, 4, 5, 6, 15, 16, 17}


def equation_image(n):
    buf = io.BytesIO()
    prop = FontProperties(family="STIXGeneral", size=16)
    math_to_image(f"${EQUATIONS[n]}$", buf, prop=prop, dpi=300, format="png", color="black")
    buf.seek(0)
    return buf


def add_eq(doc, n, equation, explanation):
    if n not in CORE_EQUATIONS:
        return None
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.left_indent = Pt(0)
    p.paragraph_format.right_indent = Pt(0)
    p.paragraph_format.space_before = Pt(5)
    p.paragraph_format.space_after = Pt(5)
    p.paragraph_format.keep_together = True
    r = p.add_run()
    image_stream = equation_image(n)
    with Image.open(image_stream) as image_obj:
        aspect_ratio = image_obj.width / image_obj.height
    image_stream.seek(0)
    nominal_width = aspect_ratio * (21 / 72)
    if nominal_width > 4.35:
        r.add_picture(image_stream, width=Inches(4.35))
    else:
        r.add_picture(image_stream, height=Pt(21))
    if explanation.startswith(("The ", "Class-weighted", "For each", "A logistic")):
        explanation = explanation[0].lower() + explanation[1:]
    add_text(doc, "Here, " + explanation if explanation else "", first_line=False)
    return p


def add_reference(doc, n, text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.62)
    p.paragraph_format.first_line_indent = Cm(-0.62)
    p.paragraph_format.space_after = Pt(2.2)
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run(f"[{n}] {text}")
    set_font(r, size=12)
    base.set_paragraph_keep(p, keep_lines=True)


def build():
    doc = Document(str(REFERENCE))
    base.clear_document_body(doc)
    style_voct_document(doc)
    add_title(doc)

    add_heading(doc, "Abstract:", 1)
    add_text(doc, "Automated fundus-image analysis usually assumes that an acquired image already contains enough evidence for the requested diagnosis. This assumption can fail even when an image is sharp and apparently gradable, because the macula, optic disc, or peripheral disease evidence may be absent from the field of view. We therefore distinguish diagnostic sufficiency from generic photographic quality and formulate it as visibility-conditioned inference.", first_line=False)
    add_text(doc, "RegionSufficiency divides ultra-widefield (UWF) fundus images into a 3×3 regional evidence bank, extracts frozen retinal-quality representations, and normalizes attention only across visible tokens. Random regional removal during training exposes the classifier to controlled evidence loss. Development used 1,630 UWF-DR images with patient-grouped splits and five random seeds. Independent same-modality replication used the official 2,597-image MMRDR-UWF test subset without target-label training, calibration, early stopping, or model selection. A continuous-aperture training variant was additionally screened for robustness to pixel-space evidence loss.", first_line=False)
    add_text(doc, "Internal macro-F1 was 0.830±0.017 for the full view, 0.790±0.012 for the center view, and 0.829±0.017 for the center-plus-cross view. External MMRDR-UWF macro-F1 was 0.625±0.010, 0.600±0.004, and 0.642±0.005, respectively. Occluding the central region caused the largest macro-F1 loss (0.065), and regional attention was directionally aligned with occlusion loss (Spearman ρ=0.60, p=0.088). In the most severe held-out 35% centered rectangular aperture, continuous-aperture training increased macro-F1 from 0.519±0.160 to 0.794±0.013 and reduced ordinal MAE from 0.446±0.123 to 0.221±0.014; larger apertures showed the same F1/MAE benefit with a modest underestimation trade-off.", first_line=False)
    add_text(doc, "These findings show that diagnostic sufficiency depends on the composition and topology of visible retinal evidence rather than on photographic quality or field area alone. RegionSufficiency exposes this hidden failure mode and provides a robustness extension for severe continuous-view loss, although prospective clinician-adjudicated labels and a deployable single-view risk head remain necessary.", first_line=False)
    add_key_value(doc, "Keywords:", "diagnostic sufficiency; ultra-widefield fundus imaging; diabetic retinopathy; limited field of view; masked attention; selective prediction")

    add_heading(doc, "1. Introduction", 1)
    add_text(doc, "Diabetic retinopathy (DR) is a major cause of preventable visual loss, and retinal photography has enabled both teleophthalmic screening and autonomous artificial-intelligence systems. Modern classifiers can identify referable DR across large and multiethnic cohorts, but their reported discrimination does not by itself guarantee that an individual acquisition contains all evidence required for the requested judgment. [1–5]")
    add_text(doc, "Most practical pipelines place image-quality assessment before disease inference. They measure focus, illumination, contrast, artifacts, or overall gradability and then accept or reject an image. Large quality datasets and quality-aware diagnosis methods have improved this step. Nevertheless, photographic quality and diagnostic sufficiency are not identical: a focused, well-exposed image can still omit the macula, optic disc, or peripheral lesions needed for a particular task. [6–12]")
    add_text(doc, "This distinction is especially relevant to UWF imaging. Standard color fundus photography usually captures 30–60°; UWF extends toward approximately 200° and can reveal predominantly peripheral DR lesions that are associated with disease progression. A classifier that receives a restricted field can therefore underestimate the full-eye burden even when the visible pixels are technically excellent. [13–16]")
    add_text(doc, "Existing full-image networks, global uncertainty scores, and attention maps do not directly solve this problem. A network generally returns a class for every image. Entropy reports ambiguity, but it does not encode which retinal regions were unavailable. Attention assigns weights to observed features; it does not distinguish low importance from non-observation, and attention should not be equated with causal explanation without intervention. [17–20]")
    add_text(doc, "We introduce RegionSufficiency, a task formulation and regional algorithm for asking whether the currently visible retinal evidence is sufficient for a specified disease judgment. The key operation is visibility-conditioned aggregation: unavailable regions are removed before attention normalization, and random region masking teaches the classifier to operate under evidence loss. Controlled masks vary area, location, shape, and topology while holding the patient and label fixed. An independent UWF dataset then tests whether the observed topology effects survive domain shift.")
    add_text(doc, "Accordingly, this study makes five contributions. First, it separates diagnostic sufficiency from generic image quality and defines limited-view disease underestimation as a measurable endpoint. Second, it introduces a visibility-conditioned regional evidence model with explicit masks, retinal-quality representations, masked attention, and stochastic evidence removal. Third, it audits evidence topology through continuous field size, location, shape, regional granularity, and intervention-based attention tests rather than relying on a single central crop. Fourth, it screens a pixel-space continuous-aperture augmentation that improves robustness to severe evidence loss while making its safety trade-off explicit. Finally, it evaluates the main view effects on an independent patient-level UWF test set and reports both fixed and nested selective-risk calibration, including unstable or unfavorable findings.")
    add_figure(doc, FIG / "Figure1_Study_Overview_RMB20.png", 1, "Study overview. (A) A conventional quality gate can accept a clear image whose disease-relevant evidence is incomplete. (B) UWF-DR supplies development data and MMRDR-UWF supplies independent same-modality replication. (C) RegionSufficiency converts the retina into a visible evidence set and masks unavailable units before aggregation. (D) The study links controlled evidence topology, internal multi-seed testing, external UWF replication, and selective-risk auditing. Geometric views are experimental proxies, not recommendations to crop clinical images.")

    add_heading(doc, "2. Methodology", 1, page_break=True)
    add_heading(doc, "2.1 Study design, endpoints, and reporting boundary", 2)
    add_text(doc, "This retrospective computational study used de-identified public datasets. No new participant recruitment or image acquisition was performed. The primary endpoint was patient-held-out macro-F1 for three-class DR severity under the center-plus-cross mask. Secondary endpoints were accuracy, ordinal severity mean absolute error (MAE), underestimation rate, and selective accepted underestimation risk. All model-development decisions were made using source validation data. MMRDR-UWF labels were accessed only for final evaluation.")
    add_text(doc, "Claims are deliberately bounded. The study evaluates a model-specific notion of sufficiency for DR severity, not a universal clinical definition. Controlled masks are geometric proxies rather than real paired 45°/UWF photographs. The paired-view risk component uses both full and limited predictions and is therefore an analysis tool, not a deployable single-image triage head.")

    add_heading(doc, "2.2 Datasets and label harmonization", 2)
    add_table(doc, 1, "Datasets, label mapping, and strictly separated experimental roles.",
              ["Dataset", "Images", "Patients/split", "Labels used here", "Role and leakage control"],
              [
                  ["UWF-DR", "1,630", "809 patients; train 876, validation 364, test 390", "Normal 496; NPDR 634; PDR 500", "Development, ablation, controlled masks; patient grouping"],
                  ["MMRDR-UWF", "2,597", "Official patient-level test subset", "Grade 0→Normal (800); grades 1–3→NPDR (1,411); grade 4→PDR (386)", "Independent UWF replication; no target-label training or selection"],
              ], [Cm(2.5), Cm(1.4), Cm(3.7), Cm(4.0), Cm(4.6)], font=7.7)
    add_text(doc, "UWF-DR contains 1,630 scanning-laser UWF images released with patient identity and Normal/NPDR/PDR labels. The patient-grouped development split contained 876 training images (260/351/265), 364 validation images (107/146/111), and 390 test images (129/137/124). [21]")
    add_text(doc, "MMRDR contains CFP, OCT, and UWF modalities. We used only the official UWF testing split because it was partitioned at patient level by the dataset authors. Its original five-level DR grades were mapped to the source three-class task: grade 0 to Normal, grades 1–3 to NPDR, and grade 4 to PDR. The external set contained 800/1,411/386 images after mapping. [22]")

    add_heading(doc, "2.3 Controlled field-of-view generation", 2)
    add_text(doc, "Two complementary perturbation families were constructed from each UWF image. Region-level perturbations selected subsets of a 3×3 evidence bank: full (nine regions), center (one region), and center-plus-cross (center plus its four axial neighbors). Pixel-level perturbations retained a centered rectangle or circle with linear fractions 0.35, 0.45, 0.55, 0.65, 0.75, or 0.90; translated a 0.55 rectangle left, right, superiorly, or inferiorly; and compared shapes at a matched linear fraction. Blacked-out pixels were applied before feature extraction.")
    add_text(doc, "These perturbations do not reproduce optical differences between cameras. Their purpose is causal stress testing: the underlying patient and ground-truth severity remain fixed while the observable evidence changes.")

    add_heading(doc, "2.4 Region bank and frozen retinal representation", 2)
    add_text(doc, "After retinal foreground normalization, each image was partitioned into K=9 rectangular regions with row-major indices. Let rᵢ denote the i-th region and bᵢ=(xᵢ¹,yᵢ¹,xᵢ²,yᵢ²) its normalized box. A released RetinaRadar EfficientNet-B0 quality-assessment checkpoint supplied a fixed retinal representation. It predicts laterality, image type, artifacts, clarity, illumination, contrast, field, and usability; it is not a disease model. Only the regional projection, attention aggregator, and DR classifier were trained. EfficientNet-B0 was selected because the local checkpoint was available and frozen; the encoder ablation compares this representation with ImageNet, handcrafted, and random controls. [18,23,24]")
    add_eq(doc, 1, "R(x) = {rᵢ = Crop(x,bᵢ)}ᵢ₌₁ᴷ,   K = 9", "R(x) is the region bank. Crop extracts a fixed spatial unit using normalized box bᵢ; the patient image x and label y do not change across masks.")
    add_eq(doc, 2, "zᵢ = P(E(rᵢ)) ∈ ℝᵈ", "zᵢ is the token for region i, E is the frozen RetinaRadar EfficientNet-B0 encoder, and P is the trainable projection implemented as a linear layer followed by layer normalization and ReLU activation. The projected dimension is d=128.")

    add_heading(doc, "2.5 Visibility-conditioned attention", 2)
    add_text(doc, "For a view mask m∈{0,1}ᴷ, mᵢ=1 means region i is available. The score network first evaluates every regional token, after which masking occurs before softmax normalization. Therefore an unavailable region receives exactly zero weight and cannot affect the representation.")
    add_eq(doc, 3, "eᵢ = wₐᵀ tanh(Wₐzᵢ + bₐ)", "eᵢ is the unnormalized evidence score for region i; Wₐ and bₐ define the 48-unit attention hidden layer, while wₐ and the scalar output bias bₛ map it to one score.")
    add_eq(doc, 4, "aᵢ(m) = mᵢ exp(eᵢ) / [Σⱼ₌₁ᴷ mⱼ exp(eⱼ) + ε]", "aᵢ(m) is masked attention. The implementation sets invisible logits to −10⁴ before softmax; the displayed expression is the mathematically equivalent visible-set form. At least one region is always restored, so the denominator is nonzero.")
    add_eq(doc, 5, "h(m) = Σᵢ₌₁ᴷ aᵢ(m)zᵢ", "h(m) is the image-level representation formed only from visible regional evidence.")
    add_eq(doc, 6, "p(m) = softmax(Wch(m)+bc)", "p(m)=[p₀,p₁,p₂] contains class probabilities for Normal, NPDR, and PDR.")
    add_eq(doc, 7, "Lcls = −(1/N)ΣₙΣc wc 1[yₙ=c] log pₙ,c(mₙ)", "Class-weighted cross-entropy trains the projection, attention, and classifier while the encoder remains frozen.")
    add_text(doc, "The trainable projection, attention network, and three-class classifier were optimized with ordinary cross-entropy loss; the RetinaRadar encoder remained frozen. The final Exp30 implementation did not apply class weights, so the objective is stated in prose rather than as a separate formula.")

    add_heading(doc, "2.6 Stochastic evidence masking", 2)
    add_text(doc, "During training, each of the nine regions was independently hidden with probability ρ=0.30. If all nine regions were hidden in a sampled mask, the center region was restored before the forward pass. This exactly follows the final Exp30 implementation, changes evidence availability rather than disease labels, and prevents the aggregator from depending on one permanently visible token.")
    add_eq(doc, 8, "m̃ᵢ ~ Bernoulli(1−ρ),   ρ=0.30,   conditioned on Σᵢm̃ᵢ≥1", "m̃ is the stochastic training mask. The final 30% rate was prespecified in the locked experiment registry; sensitivity from 0 to 60% is reported.")
    add_figure(doc, FIG / "Figure2_Method_Architecture_RMB20.png", 2, "RegionSufficiency architecture. (A) UWF images are divided into a 3×3 evidence bank; deterministic evaluation masks and 30% random training masks define visibility. (B) A shared frozen RetinaRadar EfficientNet-B0 encoder and trainable projection produce regional tokens. (C) Masked attention aggregates only visible tokens for Normal/NPDR/PDR prediction. (D) Paired full/limited predictions form an 18-dimensional evidence-gap vector for an underestimation-risk model. The risk component is an audit that requires paired views.")

    add_heading(doc, "2.7 Disease severity and underestimation", 2)
    add_text(doc, "The predicted class was the maximum-probability class among Normal, NPDR, and PDR, coded ordinally as 0, 1, and 2. Expected severity was the probability-weighted class index. A limited-view case was counted as underestimated when its predicted ordinal class was lower than the reference label. Macro-F1, accuracy, severity mean absolute error, and underestimation rate were calculated by their standard definitions; because these are evaluation criteria rather than new algorithmic components, they are stated in prose instead of being displayed as separate equations.")
    add_eq(doc, 9, "ŷ(m)=argmaxc pc(m);   s(m)=Σc₌₀² c·pc(m)", "ŷ is the categorical prediction and s(m) is expected ordinal severity on the 0–2 scale.")
    add_eq(doc, 10, "u(mL,y)=1[ŷ(mL)<y]", "The safety event u equals one when the limited-view prediction is less severe than the reference label.")
    add_eq(doc, 11, "MAE=(1/N)Σₙ|ŷₙ−yₙ|;   Under=(1/N)Σₙuₙ", "MAE penalizes ordinal distance; Under is the proportion of cases whose disease severity is underestimated.")
    add_eq(doc, 12, "Macro-F1=(1/C)Σc 2·Precisionc·Recallc/(Precisionc+Recallc)", "Macro-F1 weights each class equally and is the primary endpoint because the three severity classes are not equally frequent.")

    add_heading(doc, "2.8 Paired-view evidence-gap risk", 2)
    add_text(doc, "The paired risk audit compares probability vectors under full (pF) and limited (pL) evidence. In addition to their direct difference, the feature vector contains expected severity, entropy, and symmetric Kullback–Leibler divergence. This design asks whether the model's own evidence shift predicts a clinically undesirable downward severity error.")
    add_eq(doc, 13, "H(p)=−Σc pc log(pc+ε)", "H(p) is predictive entropy; larger values indicate a more diffuse class distribution.")
    add_eq(doc, 14, "DSKL(pF,pL)=½[KL(pF∥pL)+KL(pL∥pF)]", "Symmetric KL quantifies the magnitude of the full-to-limited distribution shift without privileging either direction.")
    add_eq(doc, 15, "φ=[pF,pL,pF−pL,|pF−pL|,sF,sL,sF−sL,HF,HL,DSKL]∈ℝ¹⁸", "The 18 dimensions are 12 probability features, three severity features, two entropies, and one symmetric-KL feature.")
    add_text(doc, "In this vector, H denotes predictive entropy and DSKL is the symmetric Kullback–Leibler divergence between the full-view and limited-view class distributions. The severity terms are their probability-weighted ordinal scores.")
    add_eq(doc, 16, "q(φ)=σ(βᵀφ+b)", "The evidence-gap vector is standardized with validation-set means and standard deviations before a logistic model estimates the probability q of limited-view underestimation. The fitted model used L2 regularization with C=0.1 and balanced class weights, matching the final risk-head implementation.")

    add_heading(doc, "2.9 Risk-controlled selective acceptance", 2)
    add_text(doc, "At target risk α, samples were sorted by predicted risk q. The largest threshold was selected whose one-sided 95% exact binomial upper bound did not exceed α on calibration data. Samples with q≤τα were accepted and the remainder deferred. This is a risk–coverage trade-off rather than probability calibration or a generic misclassification/OOD score alone. [25–27,29,30]")
    add_eq(doc, 17, "τₐ=max{τ : UCP(kτ,nτ;0.95)≤α};   accept ⇔ q≤τₐ", "nτ and kτ are accepted calibration cases and accepted underestimations; UCP is the one-sided Clopper–Pearson upper confidence bound.")
    add_text(doc, "A test image was accepted when q≤τα and otherwise deferred. Coverage was the accepted fraction, and accepted risk was the proportion of underestimation events among accepted cases. These two standard reporting quantities are described in prose rather than displayed as additional equations.")
    add_eq(doc, 18, "Coverage(τ)=nτ/N;   Risk(τ)=kτ/nτ", "Coverage measures retained workload; selective risk measures underestimation among accepted cases.")

    add_heading(doc, "2.10 Training, model selection, and ablations", 2)
    add_text(doc, "Feature normalization was fitted on source training data only. Validation full-view macro-F1 controlled early stopping and model selection, matching the actual locked training implementation. The held-out internal test set was then evaluated across seeds 0–4 under full, center, and center-plus-cross masks. The frozen registry selected 3×3 regions, RetinaRadar features, attention pooling, and ρ=0.30. If validation scores tied within 0.005, the smaller model and lower validation underestimation were preferred.")
    add_text(doc, "Ablations changed one component at a time: grid granularity (1×1, 2×2, 3×3, 4×4), pooling (mean, max, attention), training mask ratio (0, 0.15, 0.30, 0.45, 0.60), and regional representation (RetinaRadar, ImageNet ResNet-50, 67-dimensional handcrafted statistics, random ResNet-50). A separate five-seed 4×4 experiment and paired bootstrap assessed whether the finer grid consistently improved the prespecified 3×3 model.")

    add_heading(doc, "2.11 Attention intervention", 2)
    add_text(doc, "Attention was not accepted as an explanation solely because a heatmap appeared plausible. Each of the nine regions was removed in turn from every held-out image while model weights and labels remained fixed. Region importance was defined as the macro-F1 loss after occlusion, and Spearman correlation compared the rankings of mean attention and intervention loss. [19,20]")
    add_eq(doc, 19, "Δi = Macro-F1full − Macro-F1mask(i)", "Δi is the causal performance loss caused by hiding region i. Positive values indicate that the region contributed useful held-out evidence.")

    add_heading(doc, "2.12 External evaluation and statistical analysis", 2)
    add_text(doc, "All five source-trained 3×3 models were applied to the MMRDR-UWF official test split without MMRDR training, calibration, early stopping, or model selection. Point metrics were summarized as mean±standard deviation across source seeds. View comparisons used 2,000 paired image-level bootstrap resamples, preserving the same external images for each view within a seed. [28]")
    add_eq(doc, 20, "Δ*b = T({(yjb,ŷL,jb)}) − T({(yjb,ŷF,jb)}),   b=1,…,B", "For each bootstrap b, the same sampled image indices jb are used for limited and full views. Percentiles of Δ*b give paired 95% intervals.")
    add_text(doc, "The exploratory MMRDR quality proxy combined retinal coverage, within-retina contrast, and first-difference sharpness. It had no clinician quality label and is reported only as a domain-shift diagnostic. A four-fold outer GroupKFold analysis on source train+validation patients further evaluated selective-threshold transport: each outer-training fold was divided into independent model-fit and calibration groups, and the original source test set remained untouched.")

    add_heading(doc, "2.13 Continuous-aperture robustness extension", 2)
    add_text(doc, "After the regional model was locked, we screened a robustness-only training variant for pixel-space evidence loss. One synthetic centered or translated rectangle/circle aperture with a linear fraction sampled uniformly from 0.45 to 0.80 was applied to each training image before re-extracting the frozen RetinaRadar regional features. The original and aperture-perturbed regional feature banks were then concatenated, while the same 3×3 masked-attention head, 30% stochastic region masking, patient split, five seeds, and validation early-stopping rule were retained. The aperture variant was evaluated only on held-out pixel-space scenarios and was not allowed to change the locked primary model or external test analysis.")
    add_text(doc, "This extension is interpreted as robustness training rather than a claim that a geometric aperture reproduces a clinical camera. It was retained for the new manuscript because it improved the prespecified severe-aperture macro-F1 and ordinal-MAE stress endpoints; the change in underestimation rate at larger apertures is reported rather than hidden.")

    add_heading(doc, "3. Results", 1, page_break=True)
    add_heading(doc, "3.1 Patient-grouped internal performance", 2)
    add_text(doc, "Across five random seeds, full-view macro-F1 was 0.830±0.017. Restricting evidence to the center reduced macro-F1 to 0.790±0.012 and increased underestimation from 0.070±0.007 to 0.093±0.006. Center-plus-cross recovered macro-F1 to 0.829±0.017, severity MAE to 0.182±0.016, and underestimation to 0.075±0.012 (Table 2). The center-plus-cross topology therefore retained most full-view discrimination despite exposing only five of nine region tokens.")
    add_table(doc, 2, "Internal held-out results across five patient-grouped random seeds. Values are mean±SD.",
              ["View", "Accuracy", "Macro-F1", "Severity MAE", "Underestimation"],
              [
                  ["Full", "0.829±0.017", "0.830±0.017", "0.180±0.018", "0.070±0.007"],
                  ["Center", "0.789±0.012", "0.790±0.012", "0.228±0.013", "0.093±0.006"],
                  ["Center + cross", "0.828±0.017", "0.829±0.017", "0.182±0.016", "0.075±0.012"],
              ], [Cm(3.7), Cm(3.0), Cm(3.0), Cm(3.0), Cm(3.5)], font=8.3)

    add_heading(doc, "3.2 Area, location, shape, and topology are not interchangeable", 2)
    add_text(doc, "Pixel-space experiments produced an overall rise in macro-F1 as visible fraction approached 0.90, but the trajectory was non-monotonic and highly variable at small fractions (Figure 3A). For rectangular masks, macro-F1 changed from 0.643±0.150 at fraction 0.35 to 0.814±0.022 at 0.90; for circles it changed from 0.584±0.114 to 0.819±0.018. At fraction 0.55, the circle reached 0.750±0.046 whereas the rectangle reached 0.678±0.085, showing that equal linear extent did not imply equal evidence topology or visible pixel area.")
    add_text(doc, "Translating the 0.55 rectangle yielded similar mean macro-F1 values (0.673–0.675 outside the center) but large seed variability and different underestimation behavior: inferior translation produced underestimation 0.159±0.099 compared with 0.050±0.017 for the centered window. Thus location effects were more visible in safety-oriented errors than in the mean F1 alone. Region-bank masks showed the clearest topology result: center-plus-cross consistently recovered the loss caused by the center-only mask.")
    add_figure(doc, FIG / "Figure3_Controlled_Visibility_RMB20.png", 3, "Controlled visibility tests. (A) Five-seed macro-F1 across continuous centered rectangle and circle fractions. (B) Macro-F1 for fixed-size translated rectangles. (C) Matched linear fraction with different shape; shape changes topology and visible pixel area. (D) Paired five-seed region-bank results. Error bars denote SD. These experiments are mechanism stress tests and not clinical camera equivalence studies.")

    add_heading(doc, "3.3 Ablations support retinal regional representation and attention, but not a single monotonic hyperparameter optimum", 2)
    add_text(doc, "With the same 3×3 attention head, the frozen RetinaRadar representation achieved center-plus-cross macro-F1 0.837, compared with 0.772 for ImageNet ResNet-50, 0.604 for handcrafted regional statistics, and 0.161 for random ResNet-50. This control indicates that retinal pretraining, rather than the small attention head alone, supplied useful regional features (Figure 4A).")
    add_text(doc, "Attention pooling improved full-view macro-F1 from 0.799 (mean) and 0.810 (max) to 0.840, while center-plus-cross performance was 0.820, 0.824, and 0.837, respectively. Mask-ratio sensitivity was non-monotonic; ρ=0.30 was retained because it was locked before final multi-seed reporting, not because it was the largest single-split test value. The 4×4 model averaged 0.842±0.016 under center-plus-cross, compared with 0.829±0.017 for 3×3, but every per-seed paired 95% macro-F1 interval crossed zero. The 3×3 model was therefore retained as the prespecified and more interpretable configuration.")
    add_table(doc, 3, "Single-split component ablations; test values are descriptive and did not override the locked final configuration.",
              ["Component", "Variant", "Full macro-F1", "Center macro-F1", "Center + cross macro-F1"],
              [
                  ["Pooling", "Mean", "0.799", "0.759", "0.820"], ["", "Max", "0.810", "0.778", "0.824"], ["", "Attention", "0.840", "0.793", "0.837"],
                  ["Mask ratio", "0.00 / 0.15 / 0.30 / 0.45 / 0.60", "0.837 / 0.817 / 0.840 / 0.834 / 0.853", "0.801 / 0.795 / 0.793 / 0.795 / 0.798", "0.847 / 0.820 / 0.837 / 0.843 / 0.856"],
                  ["Encoder", "RetinaRadar / ImageNet / handcrafted / random", "0.840 / 0.780 / 0.605 / 0.161", "—", "0.837 / 0.772 / 0.604 / 0.161"],
              ], [Cm(2.4), Cm(5.1), Cm(2.9), Cm(2.9), Cm(3.4)], font=7.4)
    add_figure(doc, FIG / "Figure4_Ablations_RMB20.png", 4, "Ablations and controls. (A) Frozen regional representation comparison. (B) Mean, max, and attention aggregation. (C) Training-mask sensitivity with the prespecified 0.30 configuration marked. (D) Per-seed paired bootstrap differences between 4×4 and 3×3 under center-plus-cross; all 95% intervals cross zero.")

    add_heading(doc, "3.4 Attention aligns directionally with interventional importance", 2)
    add_text(doc, "The middle-center region received mean attention 0.398 and caused the largest macro-F1 loss when occluded (0.065). Removing middle-left caused loss 0.018 and middle-right loss 0.011. Several peripheral regions produced near-zero or slightly negative loss, showing that learned attention was not simply a smooth centrality prior. Across nine regions, attention rank and occlusion-loss rank had Spearman ρ=0.60 (p=0.088). The direction is mechanistically supportive, but the region count is too small for a definitive statistical claim.")
    add_text(doc, "Class-stratified held-out attention remained center-dominant for Normal and NPDR. PDR shifted more weight toward the middle-left and middle-right regions while retaining a central maximum. This pattern is compatible with distributed severe-disease evidence, but it is an aggregation analysis rather than lesion localization because no lesion-level labels entered training.")
    add_figure(doc, FIG / "Figure5_Attention_Occlusion_RMB20.png", 5, "Attention intervention. (A) Mean regional attention. (B) Macro-F1 loss after independently hiding each region. (C) Attention versus intervention loss, with the observed Spearman association. (D) Mean attention stratified by true held-out class. Attention is interpreted only together with the occlusion intervention.")

    add_heading(doc, "3.5 Independent MMRDR-UWF replication", 2)
    add_text(doc, "The source-trained models showed an expected domain-shift decrease on MMRDR-UWF, but the relative evidence topology replicated. Full-view external macro-F1 was 0.625±0.010; center fell to 0.600±0.004; center-plus-cross increased to 0.642±0.005. Center-plus-cross also reduced severity MAE from 0.400±0.013 to 0.378±0.006 and underestimation from 0.272±0.013 to 0.260±0.005 (Table 4).")
    add_text(doc, "Paired bootstrap intervals for center-versus-full macro-F1 were predominantly negative or touched zero. Center-plus-cross was positive in all five seeds, with seed-specific point differences from 0.007 to 0.025. This counter-intuitive advantage over the nominal full view is not interpreted as evidence that cropping improves clinical diagnosis. It may reflect suppression of peripheral device artifacts, different framing, or a favorable evidence-to-noise ratio under domain shift.")
    add_text(doc, "The unlabeled external quality proxy did not induce a uniform monotonic performance gradient across seeds. The highest proxy quartile improved over the lowest in four seeds but changed little in one. This reinforces the need for clinician-adjudicated quality and sufficiency labels rather than relying on handcrafted quality proxies.")
    add_table(doc, 4, "Independent MMRDR-UWF results across five source-trained seeds. Values are mean±SD; no MMRDR labels entered training or model selection.",
              ["View", "Accuracy", "Macro-F1", "Severity MAE", "Underestimation", "Δ macro-F1 vs full"],
              [
                  ["Full", "0.627±0.010", "0.625±0.010", "0.400±0.013", "0.272±0.013", "Reference"],
                  ["Center", "0.602±0.004", "0.600±0.004", "0.432±0.005", "0.284±0.016", "−0.025±0.013"],
                  ["Center + cross", "0.644±0.004", "0.642±0.005", "0.378±0.006", "0.260±0.005", "+0.017±0.006"],
              ], [Cm(2.8), Cm(2.4), Cm(2.5), Cm(2.5), Cm(2.7), Cm(3.0)], font=7.9)
    add_figure(doc, FIG / "Figure6_External_Replication_RMB20.png", 6, "Independent same-modality UWF replication. (A) Internal and external macro-F1. (B) External ordinal error and underestimation. (C) Per-seed paired 2,000-resample bootstrap differences versus full view. (D) Exploratory lowest/highest quartiles of an unlabeled external quality proxy. External labels were used only for evaluation.")

    add_heading(doc, "3.6 Paired-view selective underestimation risk", 2)
    add_text(doc, "On the fixed held-out internal test set, the 18-dimensional risk head achieved AUROC 0.740 and average precision 0.139 at an event prevalence of 0.077. Severity gap alone reached AUROC 0.677, whereas symmetric KL alone reached 0.539. At a target accepted risk of 5%, the calibrated threshold retained 62.8% of cases and observed accepted underestimation 2.9%; at targets of 10% and 20%, coverage was 91.8% and 99.7% with observed risk 7.5% and 7.7%.")
    add_text(doc, "The nested grouped audit was less optimistic. Mean risk AUROC was 0.653±0.034. At target 5%, accepted coverage was 56.7%±27.4% and accepted risk 5.0%±3.3%; individual folds ranged from 36.5% to 95.8% coverage and 0.8% to 8.7% accepted risk. At target 10%, accepted risk was 9.2%±3.4%. These results show that threshold transport, not ranking alone, is the main barrier to a stable deployment policy.")
    add_table(doc, 5, "Selective underestimation-risk results. Fixed values use the locked validation/test split; nested values are mean±SD across four grouped outer folds.",
              ["Protocol", "Risk AUROC", "Target", "Accepted coverage", "Accepted underestimation risk"],
              [
                  ["Fixed held-out", "0.740", "5%", "0.628", "0.029"], ["", "", "10%", "0.918", "0.075"], ["", "", "20%", "0.997", "0.077"],
                  ["Nested grouped", "0.653±0.034", "5%", "0.567±0.274", "0.050±0.033"], ["", "", "10%", "0.812±0.165", "0.092±0.034"], ["", "", "20%", "0.980±0.014", "0.097±0.040"],
              ], [Cm(3.6), Cm(3.0), Cm(2.2), Cm(3.5), Cm(4.0)], font=8.0)
    add_figure(doc, FIG / "Figure7_Selective_Risk_RMB20.png", 7, "Selective risk. (A) Underestimation-risk discrimination for the paired model and direct scores. (B) Coverage retained at increasing risk targets. (C) Observed accepted risk versus target. (D) Nested outer-fold coverage–risk points. Error bars denote SD across outer folds. The paired risk head is an evidence-loss audit, not a deployable single-view model.")

    add_heading(doc, "3.7 Continuous-aperture training improves severe evidence-loss robustness", 2)
    add_text(doc, "The promoted optimization was not a replacement of the locked RegionSufficiency model for the primary endpoint; it was a robustness extension evaluated under held-out pixel-space apertures. Under the most severe centered rectangular aperture, retaining only 35% of the retinal linear extent, pixel-aperture training increased macro-F1 from 0.519±0.160 to 0.794±0.013 and reduced severity MAE from 0.446±0.123 to 0.221±0.014. The improvement was consistent across all five seeds and substantially reduced the large seed-to-seed spread seen in the baseline stress test.")
    add_text(doc, "At 55%, 75%, and circular 55% apertures, the same training variant improved macro-F1 by 0.114, 0.081, and 0.052 and reduced severity MAE by 0.126, 0.107, and 0.058, respectively. Underestimation fell markedly for the severe 35% rectangle, from 0.272±0.092 to 0.097±0.007, but increased by 0.018–0.030 at the larger apertures. We therefore retain this result as a robustness finding with an explicit safety trade-off, not as evidence of uniformly superior deployment behavior.")
    add_table(doc, 6, "Held-out continuous-aperture stress test before and after pixel-aperture training. Values are mean±SD across five seeds; Δ is augmented minus baseline.",
              ["Aperture", "F1 base", "F1 aug.", "Δ F1", "MAE base", "MAE aug.", "Δ Under"],
              [
                  ["Rectangle 0.35", "0.519±0.160", "0.794±0.013", "+0.275", "0.446±0.123", "0.221±0.014", "−0.175"],
                  ["Rectangle 0.55", "0.688±0.055", "0.802±0.017", "+0.114", "0.334±0.058", "0.208±0.018", "+0.030"],
                  ["Rectangle 0.75", "0.731±0.027", "0.811±0.015", "+0.081", "0.306±0.041", "0.199±0.016", "+0.018"],
                  ["Circle 0.55", "0.752±0.051", "0.804±0.011", "+0.052", "0.264±0.050", "0.206±0.011", "+0.019"],
              ], [Cm(2.5), Cm(2.4), Cm(2.4), Cm(2.0), Cm(2.2), Cm(2.2), Cm(2.7)], font=7.1)
    add_figure(doc, FIG / "Figure8_Continuous_Aperture_Optimization_RMB20.png", 8, "Promoted continuous-aperture robustness experiment. Pixel-aperture training improves held-out macro-F1 and ordinal MAE across four severe visibility scenarios. The underestimation panel shows the favorable reduction at the 35% rectangle and the modest increases at larger apertures; these trade-offs are part of the result.")

    add_heading(doc, "4. Discussion", 1, page_break=True)
    add_heading(doc, "4.1 Principal findings", 2)
    add_text(doc, "This study addresses a hidden assumption in retinal AI: that an image deemed technically acceptable also contains sufficient evidence for the requested diagnosis. RegionSufficiency makes evidence availability explicit. Its central empirical result is not that a particular crop is universally optimal; it is that field area, location, shape, and topology produce different disease-model behavior even when the patient and label are unchanged.")
    add_text(doc, "Four observations support this conclusion. First, center-only evidence consistently degraded internal and external performance, whereas center-plus-cross recovered or exceeded the nominal full-view result. Second, retinal-quality regional features materially outperformed ImageNet, handcrafted, and random controls. Third, learned attention received directional support from an intervention: the region with the highest mean attention caused the largest held-out performance loss when removed. Fourth, pixel-aperture training substantially reduced the failure of the model under severe continuous evidence loss, but did not remove every safety trade-off.")

    add_heading(doc, "4.2 Relationship to image quality and quality-aware diagnosis", 2)
    add_text(doc, "Image-quality assessment remains necessary: blur, illumination, contrast, and artifacts can invalidate disease predictions. Our proposal is complementary rather than competing. A quality model asks whether visible structures are captured clearly; a sufficiency model asks whether the visible structures include enough task-relevant evidence. Recent quality-aware systems condition diagnosis on degradation, but the visibility mask provides a separate semantic variable—what was observed—that cannot be reconstructed from sharpness or entropy alone. [6–12]")
    add_text(doc, "This distinction suggests a two-axis acquisition policy. An image can be high-quality and sufficient, high-quality but insufficient, low-quality yet partially informative, or both low-quality and insufficient. Future prospective labels should ask graders to annotate these axes separately and specify the target decision, because sufficiency for referable-DR screening may differ from sufficiency for fine five-level grading or lesion surveillance.")

    add_heading(doc, "4.3 Why the external center-plus-cross view exceeded the full view", 2)
    add_text(doc, "The external result requires caution. Under source-to-target shift, the nominal full image contains both disease evidence and device-specific nuisance variation. A structured mask can remove peripheral artifacts or border geometry and increase the signal-to-noise ratio seen by a source-trained model. Thus center-plus-cross outperforming full view is plausible as a model-domain interaction, but it is not evidence that clinicians should discard peripheral information. The correct next experiment is a prospective same-eye, multi-device study with clinician sufficiency labels and explicit foreground/border controls.")

    add_heading(doc, "4.4 Interpretability and selective prediction", 2)
    add_text(doc, "Attention visualization is often overinterpreted. By pairing the heatmap with one-region occlusion, we test whether high-weight regions are also functionally important. The observed ρ=0.60 is encouraging but not conclusive, and the p value is reported without dichotomization. Lesion-level masks would permit stronger tests such as whether attention and intervention localize neovascularization or peripheral hemorrhage.")
    add_text(doc, "Selective prediction provides a natural response to insufficiency: accept low-risk cases and defer the remainder. The fixed split showed favorable risk–coverage behavior, but nested grouped calibration exposed large variation. This gap is important. A useful risk ranker is not automatically a safe operational threshold. Prospective deployment would require single-view features, independent calibration, subgroup auditing, temporal monitoring, and a predefined recapture/referral action. [25–27]")

    add_heading(doc, "4.5 Strengths", 2)
    add_text(doc, "The study uses patient grouping, a locked primary endpoint, five random seeds, controlled within-image perturbations, encoder/pooling/grid/mask controls, intervention-based attention validation, an independent patient-level UWF test set, paired bootstrap inference, a held-out continuous-aperture robustness screen, and both fixed and nested selective-risk analyses. Equally important, unfavorable findings—including non-monotonic mask sensitivity, unstable continuous-mask seeds, the continuous-aperture underestimation trade-off, and nested threshold variability—are reported rather than hidden.")

    add_heading(doc, "5. Limitations", 1)
    add_text(doc, "First, no dataset provides a clinician-adjudicated label for diagnostic sufficiency. Ground truth is disease severity, and sufficiency is inferred from model behavior under evidence loss. Second, geometric masks do not reproduce optics, centering, eyelash artifacts, or paired-device acquisition. Third, the continuous-aperture augmentation uses one synthetic aperture per training image and does not establish real-camera robustness. Fourth, the main task collapses five DR levels into three classes to harmonize datasets. Fifth, RetinaRadar is a locally released quality encoder with incomplete public provenance; it is used frozen and must not be described as a disease foundation model. Sixth, only one independent same-modality UWF test set is used. Seventh, the quality-proxy strata are not clinical quality labels. Eighth, paired-view risk requires the full view and therefore cannot triage a lone limited acquisition. Ninth, bootstrap intervals quantify uncertainty within the available test set and do not replace prospective multicenter validation.")

    add_heading(doc, "6. Conclusion", 1)
    add_text(doc, "A fundus image can be visually clear yet diagnostically insufficient. RegionSufficiency converts this overlooked failure mode into a visibility-conditioned regional inference problem. Internal and independent UWF experiments show that evidence topology matters beyond visible area alone, intervention supports the central learned evidence pattern, and continuous-aperture training improves robustness to severe synthetic evidence loss. Paired selective-risk results identify a path toward deferral, while nested calibration and the larger-aperture safety trade-off show why prospective, single-view validation remains necessary.")

    add_heading(doc, "Declarations", 1)
    add_heading(doc, "Author contributions", 2)
    add_text(doc, "K.D. (Kaiwen Deng): Conceptualization, Methodology, Software, Investigation, Data Curation, Formal Analysis, Validation, Visualization, and Writing—Original Draft. L.L. (Liwei Liu): Supervision, Project Administration, Resources, and Writing—Review & Editing.", first_line=False)
    add_heading(doc, "Ethics statement", 2)
    add_text(doc, "This work is a secondary computational analysis of de-identified public datasets and involved no new participant recruitment, intervention, or data collection. Ethical approvals and consent/waiver procedures for the source cohorts are reported in the original dataset publications. [21,22]", first_line=False)
    add_heading(doc, "Data availability", 2)
    add_text(doc, "UWF-DR is available from Figshare (https://doi.org/10.6084/m9.figshare.31259494). MMRDR is available from Figshare (https://doi.org/10.6084/m9.figshare.29423747.v2). Reuse must follow the source licenses and data terms.", first_line=False)
    add_heading(doc, "Code and result availability", 2)
    add_text(doc, "The project archive accompanying this manuscript contains the analysis scripts, frozen experiment registry, machine-readable results, paired-bootstrap outputs, figure-generation source, and editable vector figures. No original experiment output was overwritten during manuscript assembly.", first_line=False)
    add_heading(doc, "Competing interests", 2)
    add_text(doc, "The authors declare no competing interests.", first_line=False)

    add_heading(doc, "References", 1, page_break=True)
    refs = [
        "Wilkinson CP, Ferris FL III, Klein RE, et al. Proposed international clinical diabetic retinopathy and diabetic macular edema disease severity scales. Ophthalmology. 2003;110:1677–1682. doi:10.1016/S0161-6420(03)00475-5.",
        "Wong TY, Cheung CMG, Larsen M, Sharma S, Simó R. Diabetic retinopathy. Nat Rev Dis Primers. 2016;2:16012. doi:10.1038/nrdp.2016.12.",
        "Gulshan V, Peng L, Coram M, et al. Development and validation of a deep learning algorithm for detection of diabetic retinopathy in retinal fundus photographs. JAMA. 2016;316:2402–2410. doi:10.1001/jama.2016.17216.",
        "Ting DSW, Cheung CYL, Lim G, et al. Development and validation of a deep learning system for diabetic retinopathy and related eye diseases using retinal images from multiethnic populations with diabetes. JAMA. 2017;318:2211–2223. doi:10.1001/jama.2017.18152.",
        "Abràmoff MD, Lavin PT, Birch M, Shah N, Folk JC. Pivotal trial of an autonomous AI-based diagnostic system for detection of diabetic retinopathy in primary care offices. npj Digit Med. 2018;1:39. doi:10.1038/s41746-018-0040-6.",
        "Saha SK, Fernando B, Cuadros J, Xiao D, Kanagasingam Y. Automated quality assessment of colour fundus images for diabetic retinopathy screening in telemedicine. J Digit Imaging. 2018;31:869–878. doi:10.1007/s10278-018-0084-9.",
        "Fu H, Wang B, Shen J, et al. Evaluation of retinal image quality assessment networks in different color-spaces. In: MICCAI 2019. LNCS 11764:48–56. doi:10.1007/978-3-030-32239-7_6.",
        "Gonçalves MB, Nakayama LF, Ferraz D, et al. Image quality assessment of retinal fundus photographs for diabetic retinopathy in the machine learning era: a review. Eye. 2024;38:426–433. doi:10.1038/s41433-023-02717-3.",
        "Jin K, Gao Z, Jiang X, et al. MSHF: A multi-source heterogeneous fundus dataset for image quality assessment. Sci Data. 2023;10:286. doi:10.1038/s41597-023-02188-x.",
        "Liu R, Wang X, Wu Q, et al. DeepDRiD: Diabetic retinopathy-grading and image quality estimation challenge. Patterns. 2022;3:100512. doi:10.1016/j.patter.2022.100512.",
        "Che H, Chen S, Chen H. Image quality-aware diagnosis via meta-knowledge co-embedding. Proc IEEE/CVF Conf Comput Vis Pattern Recognit. 2023.",
        "Oh R, Park UC, Park KH, Park SJ, Yoon CK. Deep learning-based automatic image quality assessment in ultra-widefield fundus photographs. BMJ Open. 2025;15:e100058. doi:10.1136/bmjopen-2025-100058.",
        "Silva PS, Cavallerano JD, Haddad NMN, et al. Peripheral lesions identified on ultrawide field imaging predict increased risk of diabetic retinopathy progression over 4 years. Ophthalmology. 2015;122:949–956. doi:10.1016/j.ophtha.2015.01.008.",
        "Ashrafkhorasani M, Habibi A, Nittala MG, et al. Peripheral retinal lesions in diabetic retinopathy on ultra-widefield imaging. Saudi J Ophthalmol. 2024;38:123–131. doi:10.4103/sjopt.sjopt_151_23.",
        "Rajalakshmi R, Mohammed R, Vengatesan K, et al. Wide-field imaging with smartphone based fundus camera: grading severity and locating peripheral lesions in diabetic retinopathy. Eye. 2024. doi:10.1038/s41433-024-02928-2.",
        "Rajalakshmi R, Prathiba V, Arulmalar S, Usha M. Review of retinal cameras for global coverage of diabetic retinopathy screening. Eye. 2021;35:162–172.",
        "He K, Zhang X, Ren S, Sun J. Deep residual learning for image recognition. Proc IEEE Conf Comput Vis Pattern Recognit. 2016:770–778. doi:10.1109/CVPR.2016.90.",
        "Tan M, Le QV. EfficientNet: Rethinking model scaling for convolutional neural networks. Proc 36th Int Conf Mach Learn. 2019;97:6105–6114.",
        "Ilse M, Tomczak JM, Welling M. Attention-based deep multiple instance learning. Proc 35th Int Conf Mach Learn. 2018;80:2127–2136.",
        "Jain S, Wallace BC. Attention is not Explanation. Proc NAACL-HLT. 2019:3543–3556. doi:10.18653/v1/N19-1357.",
        "Peng S, Yang S, Zhao X, et al. A fundus image dataset for intelligent diabetic retinopathy system. Sci Data. 2026. doi:10.1038/s41597-026-07093-7. Dataset doi:10.6084/m9.figshare.31259494.",
        "Tang Z, Wang L, Guo Z, et al. A multimodal retinal image dataset for diabetic retinopathy detection using foundation models. Sci Data. 2026;13:639. doi:10.1038/s41597-026-07005-9.",
        "RetinaRadar. Multi-label retinal image quality assessment, EfficientNet-B0 checkpoint and local model card. Software/model release, 2025. Apache-2.0.",
        "Deng J, Dong W, Socher R, Li LJ, Li K, Fei-Fei L. ImageNet: A large-scale hierarchical image database. Proc IEEE Conf Comput Vis Pattern Recognit. 2009:248–255. doi:10.1109/CVPR.2009.5206848.",
        "Geifman Y, El-Yaniv R. Selective classification for deep neural networks. Adv Neural Inf Process Syst. 2017;30:4878–4887.",
        "Geifman Y, El-Yaniv R. SelectiveNet: A deep neural network with an integrated reject option. Proc 36th Int Conf Mach Learn. 2019;97:2151–2159.",
        "Clopper CJ, Pearson ES. The use of confidence or fiducial limits illustrated in the case of the binomial. Biometrika. 1934;26:404–413. doi:10.1093/biomet/26.4.404.",
        "Efron B, Tibshirani RJ. An Introduction to the Bootstrap. New York: Chapman & Hall/CRC; 1993.",
        "Guo C, Pleiss G, Sun Y, Weinberger KQ. On calibration of modern neural networks. Proc 34th Int Conf Mach Learn. 2017;70:1321–1330.",
        "Hendrycks D, Gimpel K. A baseline for detecting misclassified and out-of-distribution examples in neural networks. Proc Int Conf Learn Represent. 2017.",
    ]
    for i, ref in enumerate(refs, 1): add_reference(doc, i, ref)

    doc.core_properties.title = "RegionSufficiency: Visibility-Conditioned Regional Evidence Aggregation for Diagnostic Sufficiency in Ultra-Widefield Fundus Imaging"
    doc.core_properties.subject = "Visibility-conditioned regional evidence aggregation for limited-view fundus imaging"
    doc.core_properties.keywords = "fundus imaging, diagnostic sufficiency, UWF, regional attention, selective prediction"
    doc.core_properties.comments = "Complete evidence-traceable manuscript assembled from locked local experiment outputs and formatted to the VOCT_2.0 reference layout."
    doc.core_properties.author = "Liwei Liu; Kaiwen Deng"
    doc.core_properties.last_modified_by = "Kaiwen Deng"
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(OUTPUT))
    print(OUTPUT)


if __name__ == "__main__":
    build()
