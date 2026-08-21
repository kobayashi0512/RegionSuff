#!/usr/bin/env python3
"""Build the audited RegionSuff manuscript (version 1.3).

The file is rebuilt from the VOCT-style reference layout.  Every quantitative
statement is tied to a locked results.json file.  All equations are native
editable Word math objects (OMML) and deliberately carry no equation numbers.
"""
from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import nsdecls, qn
from docx.shared import Cm, Inches, Pt, RGBColor
from lxml import etree


ROOT = Path("/Users/tongyue/Documents/77f /7hao")
BASE_DIR = ROOT / "paper_design/manuscript_build"
sys.path.insert(0, str(BASE_DIR))
import build_manuscript as base  # noqa: E402

REFERENCE = Path("/Users/tongyue/Documents/ppf/第二论文/VOCT_2.0.docx")
OUTPUT = Path("/Users/tongyue/Documents/ppf/第四论文/RegionSuff_1.3.docx")
FIG = ROOT / "paper_design/revision_1_2/figures"
AUDIT = ROOT / "paper_design/revision_1_2/CONSISTENCY_AUDIT.md"

INK = "000000"


def set_font(run, size=12, bold=False, italic=False, color=INK, underline=False, name="Times New Roman"):
    base.set_run_font(run, name=name, size=size, bold=bold, italic=italic, color=color)
    run.underline = underline
    run._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), name)
    return run


def style_document(doc):
    names = [s.name for s in doc.styles]
    for name in ("Normal", "Normal (Web)"):
        if name not in names:
            doc.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        st = doc.styles[name]
        st.font.name = "Times New Roman"
        st.font.size = Pt(12)
        st.font.color.rgb = RGBColor(0, 0, 0)
        st._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), "Times New Roman")
        st.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        st.paragraph_format.line_spacing = 1.15
        st.paragraph_format.space_after = Pt(6)
        st.paragraph_format.first_line_indent = None
    for name in ("Heading 1", "Heading 2", "Heading 3"):
        if name in names:
            st = doc.styles[name]
            st.font.name = "Times New Roman"
            st.font.size = Pt(14)
            st.font.bold = True
            st.font.color.rgb = RGBColor(0, 0, 0)
            st._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), "Times New Roman")
            st.paragraph_format.space_before = Pt(10)
            st.paragraph_format.space_after = Pt(6)
            st.paragraph_format.keep_with_next = True
    for section in doc.sections:
        for part in (section.header, section.footer):
            for p in part.paragraphs:
                p.clear()


def add_title(doc):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(18)
    p.paragraph_format.line_spacing = 1.15
    set_font(p.add_run("RegionSuff: Visibility-Conditioned Regional Evidence Auditing under Limited Fields of View in Ultra-Widefield Fundus Imaging"), size=16, bold=True)

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    set_font(p.add_run("Kaiwen Deng"), size=12.5)
    set_font(p.add_run(", Liwei Liu*"), size=12.5)

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(16)
    set_font(p.add_run("School of Railway Intelligent Engineering, Dalian Jiaotong University, Dalian, 116028, China"), size=12.5)

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(3)
    set_font(p.add_run("*Corresponding author"), size=12)
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(18)
    set_font(p.add_run("Email: "), size=12, bold=True)
    set_font(p.add_run("Liwei Liu ("), size=12)
    set_font(p.add_run("liutree80@163.com"), size=12, color="0563C1", underline=True)
    set_font(p.add_run(")"), size=12)


def add_heading(doc, text, level=1, page_break=False):
    p = doc.add_paragraph(style="Heading 2" if level == 1 else "Heading 3")
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.left_indent = Cm(0)
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.page_break_before = page_break
    set_font(p.add_run(text), size=14, bold=True)
    return p


def add_text(doc, text, size=12):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.first_line_indent = None
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(6)
    set_font(p.add_run(text), size=size)
    base.set_paragraph_keep(p, keep_lines=True)
    return p


def add_key_value(doc, key, value, size=12):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(6)
    set_font(p.add_run(key + " "), size=size, bold=True)
    set_font(p.add_run(value), size=size)
    return p


def add_figure(doc, path, number, caption, alt_text):
    if not path.exists():
        raise FileNotFoundError(path)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    run = p.add_run()
    run.add_picture(str(path), width=Inches(5.65))
    for docpr in p._p.xpath(".//wp:docPr"):
        docpr.set("name", f"Figure {number}")
        docpr.set("descr", alt_text)
    cp = doc.add_paragraph()
    cp.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    cp.paragraph_format.line_spacing = 1.0
    cp.paragraph_format.space_before = Pt(2)
    cp.paragraph_format.space_after = Pt(6)
    set_font(cp.add_run(f"Figure {number}. "), size=10.5, bold=True)
    set_font(cp.add_run(caption), size=10.5)
    base.set_paragraph_keep(cp, keep_lines=True)
    return p


def add_table(doc, number, caption, headers, rows, widths=None, font=8.5):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    if widths is None:
        widths = [Cm(14.6 / len(headers))] * len(headers)
    scale = min(1.0, 14.6 / sum(w.cm for w in widths))
    widths = [Cm(w.cm * scale) for w in widths]
    for cell, header, width in zip(table.rows[0].cells, headers, widths):
        cell.width = width
        base.set_cell_shading(cell, "E7E6E6")
        base.set_cell_border(cell, top={"val": "single", "sz": "8", "color": "000000"}, bottom={"val": "single", "sz": "6", "color": "000000"})
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(0)
        set_font(p.add_run(header), size=font, bold=True)
    base.set_repeat_table_header(table.rows[0])
    for ridx, row in enumerate(rows):
        cells = table.add_row().cells
        for cidx, (cell, value, width) in enumerate(zip(cells, row, widths)):
            cell.width = width
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            base.set_cell_shading(cell, "FFFFFF")
            base.set_cell_border(cell, bottom={"val": "single", "sz": "3", "color": "BFBFBF" if ridx < len(rows) - 1 else "000000"})
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if cidx < 2 else WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(0)
            set_font(p.add_run(str(value)), size=font, bold=(cidx == 0))
        base.set_cant_split(table.rows[-1])
    cp = doc.add_paragraph()
    cp.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    cp.paragraph_format.space_before = Pt(2)
    cp.paragraph_format.space_after = Pt(7)
    set_font(cp.add_run(f"Table {number}. "), size=10.5, bold=True)
    set_font(cp.add_run(caption), size=10.5)
    return table


# ----- Native Word equations (OMML) -----

def m_el(tag, text=None):
    e = OxmlElement("m:" + tag)
    if text is not None:
        e.text = text
    return e


def mr(text, normal=False):
    r = m_el("r")
    rpr = m_el("rPr")
    if normal:
        rpr.append(m_el("nor"))
    r.append(rpr)
    t = m_el("t", text)
    if text[:1].isspace() or text[-1:].isspace():
        t.set(qn("xml:space"), "preserve")
    r.append(t)
    return r


def sub(base_text, sub_text):
    e = m_el("sSub")
    pr = m_el("sSubPr"); pr.append(m_el("ctrlPr")); e.append(pr)
    b = m_el("e"); b.append(deepcopy(base_text) if hasattr(base_text, "tag") else mr(base_text)); e.append(b)
    s = m_el("sub"); s.append(deepcopy(sub_text) if hasattr(sub_text, "tag") else mr(sub_text)); e.append(s)
    return e


def sup(base_text, sup_text):
    e = m_el("sSup")
    pr = m_el("sSupPr"); pr.append(m_el("ctrlPr")); e.append(pr)
    b = m_el("e"); b.append(deepcopy(base_text) if hasattr(base_text, "tag") else mr(base_text)); e.append(b)
    s = m_el("sup"); s.append(deepcopy(sup_text) if hasattr(sup_text, "tag") else mr(sup_text)); e.append(s)
    return e


def subsup(base_text, sub_text, sup_text):
    e = m_el("sSubSup")
    pr = m_el("sSubSupPr"); pr.append(m_el("ctrlPr")); e.append(pr)
    b = m_el("e"); b.append(deepcopy(base_text) if hasattr(base_text, "tag") else mr(base_text)); e.append(b)
    s = m_el("sub"); s.append(deepcopy(sub_text) if hasattr(sub_text, "tag") else mr(sub_text)); e.append(s)
    u = m_el("sup"); u.append(deepcopy(sup_text) if hasattr(sup_text, "tag") else mr(sup_text)); e.append(u)
    return e


def frac(num_nodes, den_nodes):
    e = m_el("f"); e.append(m_el("fPr"))
    n = m_el("num"); [n.append(x) for x in num_nodes]; e.append(n)
    d = m_el("den"); [d.append(x) for x in den_nodes]; e.append(d)
    return e


def add_eq(doc, nodes):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(5)
    p.paragraph_format.space_after = Pt(5)
    p.paragraph_format.keep_together = True
    omp = m_el("oMathPara")
    om = m_el("oMath")
    for node in nodes:
        om.append(node)
    omp.append(om)
    p._p.append(omp)
    return p


def add_reference(doc, n, text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.62)
    p.paragraph_format.first_line_indent = Cm(-0.62)
    p.paragraph_format.space_after = Pt(2.2)
    p.paragraph_format.line_spacing = 1.0
    set_font(p.add_run(f"[{n}] {text}"), size=12)
    base.set_paragraph_keep(p, keep_lines=True)


def build():
    doc = Document(str(REFERENCE))
    base.clear_document_body(doc)
    style_document(doc)
    add_title(doc)

    add_heading(doc, "Abstract:", 1)
    add_text(doc, "Retinal artificial-intelligence systems commonly treat technical gradability as evidence that an image is suitable for an intended diagnostic task. Yet a sharp, well-illuminated fundus image can omit macular, optic-disc, or peripheral findings needed for diabetic retinopathy (DR) grading. Conventional image-quality assessment characterizes photographic degradation but does not explicitly audit whether the visible field contains task-relevant evidence.", size=10.5)
    add_text(doc, "We developed RegionSuff, a visibility-conditioned regional framework for auditing DR inference under controlled evidence loss in ultra-widefield (UWF) images. RegionSuff partitions the retinal foreground into a 3×3 evidence bank, extracts features with a frozen retinal image-quality encoder, and normalizes attention only across visible tokens. Development used 1,630 UWF-DR records with filename-derived group-disjoint partitions and five random seeds. Independent same-modality evaluation used the official 2,597-image MMRDR-UWF test subset without target-domain training or model selection. Region masks and pixel apertures varied the composition, area, location, and shape of visible evidence; a paired-view risk analysis examined limited-view underestimation.", size=10.5)
    add_text(doc, "Internally, center-only macro-F1 was 0.790 compared with 0.830 for the full view, while center-plus-cross recovered 0.829. Externally, the corresponding values were 0.600, 0.625, and 0.642. Controlled perturbations showed that visible area, location, shape, and topology were not interchangeable, and central-region removal produced the largest performance loss. The paired risk head achieved fixed-split AUROC 0.740, but grouped nested AUROC was 0.653 with substantial coverage variability. These findings support RegionSuff as an evidence-aware audit of model behavior under synthetic evidence loss. They do not establish clinician-adjudicated diagnostic sufficiency or a deployable single-view triage rule.", size=10.5)
    add_key_value(doc, "Keywords:", "RegionSuff; evidence availability; ultra-widefield fundus imaging; diabetic retinopathy; masked attention; limited-view underestimation", size=10.5)

    add_heading(doc, "1. Introduction", 1)
    add_text(doc, "Diabetic retinopathy is a major cause of preventable visual loss, and retinal photography supports teleophthalmic screening and autonomous AI systems. Large studies demonstrate strong population-level discrimination, but a disease model still produces a class even when a particular acquisition omits evidence required for that decision. [1–5]")
    add_text(doc, "Most deployment pipelines address this problem indirectly through image-quality assessment. Focus, illumination, contrast, artifacts, and global gradability determine whether an image enters the diagnostic model. These checks remain essential, yet they answer whether the captured structures are visible clearly—not whether the captured field contains the structures or lesions needed for a specified task. A technically gradable image can therefore be evidentially incomplete. [6–12]")
    add_text(doc, "This distinction is important in UWF imaging. Conventional color fundus photography commonly covers 30–60°, whereas UWF systems extend toward approximately 200° and can reveal peripheral DR lesions associated with progression. Restricting the observed field can alter estimated disease burden even when the retained pixels are sharp. [13–16]")
    add_text(doc, "Uncertainty and attention do not directly encode non-observation. Entropy measures ambiguity among outputs, not which retinal regions were absent. Attention distributes weight over available features, but high attention is not automatically a causal explanation. A useful audit should therefore represent visibility explicitly, perturb evidence availability in a controlled manner, and test whether observed performance changes survive domain shift. [19,20,29,30]")
    add_text(doc, "Against this background, we developed RegionSuff, a visibility-conditioned regional framework that measures how a fixed DR model behaves as retinal evidence is removed in a controlled and traceable manner. The central hypothesis was that model behavior would depend on the composition and topology of the observed retina rather than on visible area alone. Region-level masks test topology, pixel apertures test continuous area, location, and shape, one-region occlusion tests the functional alignment of attention, and an independent UWF cohort tests same-modality external replication.")
    add_text(doc, "An exploratory paired full/limited-view model additionally tested whether prediction shifts could rank limited-view underestimation and whether risk thresholds transported under grouped nested evaluation. The target construct throughout is model-specific evidence availability. Because the datasets provide neither real paired acquisitions nor clinician-adjudicated sufficiency labels, the analyses are not interpreted as a clinical diagnostic-sufficiency test.")
    add_heading(doc, "2. Methodology", 1)
    add_heading(doc, "2.1 Study design, endpoints, and reporting boundary", 2)
    add_text(doc, "This retrospective computational study used de-identified released datasets and introduced no new image acquisition. The principal model-audit endpoint was held-out three-class DR macro-F1 across a fixed set of full, center, and center-plus-cross views. Secondary endpoints were accuracy, ordinal severity MAE, and underestimation rate. Five source-training seeds quantified optimization dispersion. Image-level paired bootstrap intervals were used for view contrasts where stored predictions were available. [28]")
    add_text(doc, "The target construct is model-specific evidence availability for DR severity. Controlled masks are synthetic interventions, not paired 45° and UWF acquisitions. No dataset contains clinician-adjudicated sufficiency labels. The paired risk module requires both full and limited predictions and is therefore an analysis tool, not a deployable single-image triage head.")
    add_figure(doc, FIG / "Figure1_Study_Overview_RMB20_v1_2.png", 1,
               "Study overview. (A) Technical gradability and task-relevant evidence availability are distinct. (B) Region-level and pixel-level perturbations alter visible evidence while preserving the source label. (C) RegionSuff aggregates only visible regional tokens. (D) The evidence chain combines internal testing, intervention, external severity evaluation, and paired-view risk analysis. The study is an audit under synthetic evidence loss, not a clinician-labeled or single-view deployment system.",
               "Four-panel overview contrasting gradability with evidence availability, showing controlled region and aperture masks, the RegionSuff pipeline, and the internal, interventional, external, and risk-audit evidence chain.")

    add_heading(doc, "2.2 Datasets, records, and label harmonization", 2)
    add_table(doc, 1, "Datasets, released records, model partitions, and strictly separated experimental roles.",
              ["Dataset", "Released records", "Model partition", "Labels used", "Role"],
              [
                  ["UWF-DR", "1,630", "Train 876; validation 364; test 390", "Normal 496; NPDR 634; PDR 500", "Development, perturbation analysis, and internal testing"],
                  ["MMRDR-UWF", "2,597", "Official UWF test subset", "Grade 0→Normal; 1–3→NPDR; 4→PDR", "Independent same-modality severity evaluation; no adaptation"],
              ], [Cm(2.6), Cm(2.4), Cm(3.3), Cm(3.5), Cm(4.2)], font=8.5)
    add_text(doc, "UWF-DR provides 1,630 released 512×512 records captured with Optomap Daytona and labeled Normal, NPDR, or PDR. The authors supplied image filenames and labels but not a dedicated patient-identifier column. We derived a grouping key from the first two underscore-separated filename fields, yielding 783 non-overlapping groups in our registry and partitions of 876, 364, and 390 records. [21]")
    add_text(doc, "Audit of the released lists found 1,608 unique filenames among 1,630 records: 11 filenames were repeated and two repeated filenames had conflicting labels. Group membership remained disjoint and the 390-record test partition contained no duplicate filename. A sensitivity run retained one validation row per filename, resolved the two conflicts by majority vote with severe-class tie-breaking, and left the test set unchanged; full, center, and center-plus-cross macro-F1 were 0.833, 0.790, and 0.832, respectively, closely matching the primary analysis.")
    add_text(doc, "MMRDR includes CFP, OCT, and UWF modalities. We used only the official 2,597-image UWF testing subset and mapped the original five DR grades to the source three-class task: grade 0 to Normal, grades 1–3 to NPDR, and grade 4 to PDR. The resulting counts were 800, 1,411, and 386. No MMRDR label entered source training, early stopping, calibration, or model selection. [22]")

    add_heading(doc, "2.3 Retinal foreground and controlled evidence loss", 2)
    add_text(doc, "After pixel intensities were scaled to [0,1], a retinal foreground box was estimated by thresholding mean intensity at 0.035 and taking the bounding rectangle of positive pixels; if foreground occupied less than 8% of the image, the full frame was used. Region-level views selected tokens from a 3×3 row-major grid: full retained all nine regions, center retained region 5, and center-plus-cross retained regions 2, 4, 5, 6, and 8.")
    add_text(doc, "Pixel-level apertures were applied before feature extraction while the original retinal box and 3×3 feature coordinates remained fixed. Centered rectangles and circles used fractions 0.35, 0.45, 0.55, 0.65, 0.75, and 0.90; a 0.55 rectangle was translated left, right, superiorly, or inferiorly. For a rectangle, the retained width and height were f times the retinal box. For a circle, the normalized radius was f/√π, giving the same nominal aperture area f² as the rectangle. Actual retained retinal tissue may still differ because of retinal shape, borders, and black background.")

    add_heading(doc, "2.4 Regional representation", 2)
    add_text(doc, "Each retinal box was divided into K=9 rectangular regions. Each crop was resized to 256×256, center-cropped to 224×224, and normalized with ImageNet channel statistics. A local RetinaRadar EfficientNet-B0 checkpoint produced a frozen global representation for every region. The checkpoint has 17 quality-related outputs covering laterality, image type, artifacts, clarity, illumination, contrast, field, and usability; it is not a disease foundation model. Only the projection, attention, and DR classifier were trained. The exact local checkpoint checksum is reported in the code-and-result archive and Reference 23. [18,23]")
    add_eq(doc, [sub("z", "i"), mr(" = P(E("), sub("r", "i"), mr(")) ∈ "), sup("R", "128")])
    add_text(doc, "Here, rᵢ is region i, E is the frozen EfficientNet-B0 encoder, and P is a trainable linear layer followed by layer normalization and ReLU. The resulting 128-dimensional vector zᵢ is the regional token.")

    add_heading(doc, "2.5 Visibility-conditioned attention and severity loss", 2)
    add_text(doc, "The attention network applies a 128→48 linear layer, tanh activation, and a scalar output to each regional token. Scores are computed for every region, after which unavailable logits are set to −10⁴ before softmax. The equations below use the mathematically equivalent visible-set form.")
    add_eq(doc, [sub("e", "i"), mr(" = "), sup(sub("w", "a"), "T"), mr(" tanh("), sub("W", "a"), sub("z", "i"), mr(" + "), sub("b", "a"), mr(") + "), sub("b", "s")])
    add_eq(doc, [sub("a", "i"), mr("(m) = "), frac([sub("m", "i"), mr(" exp("), sub("e", "i"), mr(")")], [subsup("∑", "j=1", "K"), sub("m", "j"), mr(" exp("), sub("e", "j"), mr(")")])])
    add_eq(doc, [mr("h(m) = "), subsup("∑", "i=1", "K"), sub("a", "i"), mr("(m)"), sub("z", "i"), mr(",     p(m) = softmax("), sub("W", "c"), mr("h(m) + "), sub("b", "c"), mr(")")])
    add_text(doc, "The binary vector m identifies visible regions. The normalized attention aᵢ(m) is zero for an unavailable region and sums to one over visible regions. The image representation h(m) is classified into Normal, NPDR, or PDR probabilities p(m). The unweighted cross-entropy objective was used because the final implementation did not apply class weights.")
    add_eq(doc, [sub("L", "CE"), mr(" = −"), frac([mr("1")], [mr("B")]), mr(" "), subsup("∑", "n=1", "B"), mr(" log "), sub("p", "n,yₙ"), mr("("), sub("m", "n"), mr(")")])

    add_heading(doc, "2.6 Stochastic visibility masking", 2)
    add_text(doc, "During source training, each of the nine tokens was independently hidden with probability ρ=0.30. In the locked Exp35/Exp36 implementation, an all-empty draw restored the first row-major region (index 0). This event has probability 0.3⁹≈0.00002 per training image. A correction sensitivity restored the geometric center token instead and, together with validation-list deduplication, yielded nearly unchanged test results. Deterministic full, center, and center-plus-cross masks were used only for evaluation.")
    add_figure(doc, FIG / "Figure2_Method_Architecture_RMB20_v1_2.png", 2,
               "RegionSuff model and evaluation protocols. (A) The retinal foreground is divided into a 3×3 evidence bank; deterministic evaluation masks and stochastic training masks define visibility. (B) A shared frozen retinal image-quality encoder and trainable projection produce regional tokens. (C) Evidence scores are normalized only across visible tokens and aggregated for DR severity. (D) Paired full/limited predictions form an 18-dimensional exploratory underestimation-risk feature. The bottom strip separates source fitting, internal testing, paired risk analysis, and external severity evaluation.",
               "Four-panel architecture diagram showing evidence construction, frozen regional encoding, masked attention equations, severity and paired-risk outputs, and distinct internal, nested-risk, and external protocols.")

    add_heading(doc, "2.7 Severity and underestimation endpoints", 2)
    add_text(doc, "Predicted classes were coded ordinally as 0=Normal, 1=NPDR, and 2=PDR. Severity MAE was the mean absolute difference between predicted and reference class. Underestimation was the event that the predicted class was lower than the reference class.")
    add_eq(doc, [mr("ŷ(m) = "), sub("arg max", "c∈{0,1,2}"), mr(" "), sub("p", "c"), mr("(m),     s(m) = "), subsup("∑", "c=0", "2"), mr(" c"), sub("p", "c"), mr("(m),     u(m) = 𝟙[ŷ(m) < y]")])

    add_heading(doc, "2.8 Paired-view evidence-gap risk", 2)
    add_text(doc, "For each image, the paired audit compared full-view probabilities pF with center-plus-cross probabilities pL. The 18-dimensional feature contains four probability blocks (12 values), three expected-severity terms, two entropies, and one symmetric Kullback–Leibler divergence.")
    add_eq(doc, [mr("H(p) = −"), subsup("∑", "c=0", "2"), sub("p", "c"), mr(" log("), sub("p", "c"), mr("+ε),     "), sub("D", "SKL"), mr("("), sub("p", "F"), mr(","), sub("p", "L"), mr(") = "), frac([mr("1")], [mr("2")]), mr("[KL("), sub("p", "F"), mr("∥"), sub("p", "L"), mr(")+KL("), sub("p", "L"), mr("∥"), sub("p", "F"), mr(")]")])
    add_eq(doc, [mr("g = ["), sub("p", "F"), mr(", "), sub("p", "L"), mr(", "), sub("p", "F"), mr("−"), sub("p", "L"), mr(", |"), sub("p", "F"), mr("−"), sub("p", "L"), mr("|, "), sub("s", "F"), mr(", "), sub("s", "L"), mr(", "), sub("s", "F"), mr("−"), sub("s", "L"), mr(", "), sub("H", "F"), mr(", "), sub("H", "L"), mr(", "), sub("D", "SKL"), mr("] ∈ "), sup("R", "18")])
    add_eq(doc, [mr("g̃ = (g−"), sub("μ", "g"), mr(") ⊘ "), sub("σ", "g"), mr(",     q(g) = sigmoid("), sup("β", "T"), mr("g̃+b)")])
    add_text(doc, "Here, ε=10⁻⁸ was used for numerical stability, H is predictive entropy, and DSKL is the average of the two directed KL divergences. The standardization moments μg and σg were estimated only from the risk-development partition. The logistic model used L2 regularization (C=0.1), balanced class weights, and liblinear optimization. In the fixed-split analysis, the same validation predictions were used to fit the logistic model and choose the risk threshold; the held-out test ranking is informative, but the threshold claim is exploratory because model fitting and calibration were not separated.")

    add_heading(doc, "2.9 Risk-controlled thresholds and nested audit", 2)
    add_text(doc, "For a target accepted underestimation risk α, candidate thresholds accepted samples with q≤τ. The largest accepted set whose one-sided 95% Clopper–Pearson upper bound did not exceed α was selected. [27]")
    add_eq(doc, [sub("τ", "α"), mr(" = max{τ : "), sub("U", "CP"), mr("("), sub("k", "τ"), mr(","), sub("n", "τ"), mr(";0.95) ≤ α}")])
    add_text(doc, "Here, nτ is the number of accepted threshold-development cases and kτ is the corresponding number of underestimations. The stricter audit used four outer filename-grouped folds on the original train+validation pool. Within each outer-training fold, a group split supplied a severity-model fitting subset and an inner risk-development subset; risk ranking and thresholds were evaluated once on the outer test fold. Because the inner subset supplied severity early stopping, logistic-risk fitting, and threshold selection, this remains a nested robustness audit rather than a fully separated or prospective calibration design.")

    add_heading(doc, "2.10 Training, controls, and model selection", 2)
    add_text(doc, "Regional-feature mean and standard deviation were estimated from source training regions only. Trainable heads used AdamW with learning rate 1.5×10⁻³ and weight decay 3×10⁻⁴, for at most 180 epochs with patience 25. Full-view validation macro-F1—not center-plus-cross performance—selected the epoch in the locked implementation. Five seeds (0–4) were run for the primary configuration. The held-out test set was evaluated after each seed-specific model was frozen.")
    add_text(doc, "Single-split controls varied pooling (mean, max, attention), token-mask probability (0, 0.15, 0.30, 0.45, 0.60), grid size (1×1 through 4×4), and regional representation (RetinaRadar, ImageNet ResNet-50, 67-dimensional handcrafted statistics, and random ResNet-50). The 0.30 mask ratio and 3×3 grid are reference configurations inherited from the experimental registry; the non-monotonic single-split sensitivity does not justify calling them unique optima. A separate five-seed 4×4 run and per-seed paired bootstrap compared 4×4 with 3×3.")
    add_text(doc, "For the supplementary pixel-aperture training variant, one additional representation was generated per source-training record. Aperture shape was sampled uniformly from rectangle and circle; fraction was sampled uniformly from 0.45 to 0.80; and position was sampled uniformly from center, left, right, superior, and inferior. These representations were concatenated with the original source-training bank, while token masking remained active. Epoch selection again used full-view source-validation macro-F1, and this variant was evaluated only on four fixed internal stress apertures.")
    add_text(doc, "For this paired optimization analysis, both the baseline and augmented heads were retrained with the geometric-center fallback for all-empty token masks and with a dedicated random-mask sequence. Its baseline is therefore the protocol-matched comparator for the augmentation arm; it is not a reuse of the independently trained aperture-sensitivity models reported in Section 3.2.")

    add_heading(doc, "2.11 Attention intervention", 2)
    add_text(doc, "Attention was interpreted only with an intervention. Each test image was re-evaluated nine times, removing one region while holding the trained model and label fixed. Regional importance was the reduction in full-view macro-F1. Spearman correlation compared the nine mean attention weights with the nine occlusion losses; the small number of regions limits inferential power. [20]")

    add_heading(doc, "2.12 External evaluation and statistical analysis", 2)
    add_text(doc, "The five source-trained 3×3 severity heads were applied to MMRDR-UWF without target-label training, calibration, early stopping, or model selection. Point metrics are mean±sample SD across source seeds. Within each seed, view differences used 2,000 paired image-level bootstrap resamples, preserving image identity between views. [28]")
    add_text(doc, "An exploratory external quality proxy combined retinal coverage, within-retina contrast, and first-difference sharpness. It is not a clinical image-quality label. All p values are two-sided and are reported descriptively without multiplicity adjustment. Seed SD represents optimization variability; paired bootstrap intervals represent image-sampling uncertainty conditional on a fitted seed and must not be interpreted as interchangeable.")

    add_heading(doc, "3. Results", 1)
    add_heading(doc, "3.1 Internal filename-group-held-out performance", 2)
    add_text(doc, "Across five seeds, full-view macro-F1 was 0.830±0.017. Center-only evidence reduced macro-F1 to 0.790±0.012 and increased underestimation from 0.070±0.007 to 0.093±0.006. Center-plus-cross recovered macro-F1 to 0.829±0.017, while severity MAE was 0.182±0.016. These values are optimization dispersion across the same 390-record test partition, not independent image-level confidence intervals.")
    add_table(doc, 2, "Internal held-out results across five source-training seeds. Values are mean±sample SD.",
              ["View", "Accuracy", "Macro-F1", "Severity MAE", "Under. rate"],
              [["Full", "0.829±0.017", "0.830±0.017", "0.180±0.018", "0.070±0.007"],
               ["Center", "0.789±0.012", "0.790±0.012", "0.228±0.013", "0.093±0.006"],
               ["Center + cross", "0.828±0.017", "0.829±0.017", "0.182±0.016", "0.075±0.012"]],
              [Cm(3.0), Cm(2.6), Cm(2.6), Cm(2.8), Cm(3.2)], font=8.5)

    add_heading(doc, "3.2 Evidence effects depend on area, location, shape, and topology", 2)
    add_text(doc, "Centered pixel apertures generally improved as fraction increased, but neither shape followed a monotonic trajectory at every step and variability was large at small fractions. Rectangular macro-F1 ranged from 0.643±0.150 at fraction 0.35 to 0.814±0.022 at 0.90; circular macro-F1 ranged from 0.584±0.114 to 0.819±0.018. At the matched nominal area f² for f=0.55, the circle yielded macro-F1 0.750±0.046 versus 0.678±0.085 for the rectangle, showing that equal nominal area did not equal equivalent evidence.")
    add_text(doc, "Translating the 0.55 rectangle changed mean macro-F1 little (0.672–0.678) but altered underestimation markedly: the inferior aperture reached 0.159±0.099 compared with 0.050±0.017 at the center. Region topology showed a clearer and more stable pattern: center-only was lower than full in all five seeds, whereas center-plus-cross nearly restored full-view performance.")
    add_figure(doc, FIG / "Figure3_Controlled_Visibility_RMB20_v1_2.png", 3,
               "Controlled evidence-loss tests. (A) Five-seed macro-F1 across centered rectangle and circle fractions. (B) fixed-size translated rectangles; magenta labels give mean underestimation. (C) rectangle and circle at matched nominal aperture area; actual retinal overlap and evidence topology may differ. (D) per-seed internal macro-F1 for full, center, and center-plus-cross region masks. Error bars denote seed SD.",
               "Four plots showing continuous aperture fraction, location-specific F1 and underestimation, area-matched shape comparison, and paired seed trajectories for region topology.")

    add_heading(doc, "3.3 Component controls are informative but non-monotonic", 2)
    add_text(doc, "With the same 3×3 attention head, the frozen RetinaRadar representation achieved center-plus-cross macro-F1 0.837, compared with 0.772 for ImageNet ResNet-50, 0.604 for handcrafted statistics, and 0.161 for a random ResNet-50. This descriptive control supports domain-relevant retinal features but does not isolate the checkpoint's training data or label contributions.")
    add_text(doc, "Attention pooling improved full-view macro-F1 from 0.799 for mean and 0.810 for max to 0.840; center-plus-cross values were 0.820, 0.824, and 0.837. Mask-ratio results were non-monotonic: 0.60 reached the highest single-split test macro-F1, so 0.30 should be treated as the reference configuration rather than a proven optimum. Single-split grid results also favored 4×4 slightly, but the five-seed paired 4×4−3×3 bootstrap intervals all crossed zero.")
    add_table(doc, 3, "Single-split descriptive controls. Test values did not redefine the multi-seed primary result.",
              ["Component", "Variant", "Full F1", "Center F1", "Center + cross F1"],
              [
                  ["Pooling", "Mean", "0.799", "0.759", "0.820"], ["", "Max", "0.810", "0.778", "0.824"], ["", "Attention", "0.840", "0.793", "0.837"],
                  ["Mask ratio", "0.00", "0.837", "0.801", "0.847"], ["", "0.15", "0.817", "0.795", "0.820"], ["", "0.30", "0.840", "0.793", "0.837"], ["", "0.45", "0.834", "0.795", "0.843"], ["", "0.60", "0.853", "0.798", "0.856"],
                  ["Grid / attention", "1×1", "0.781", "0.781", "0.781"], ["", "2×2", "0.824", "0.824", "0.824"], ["", "3×3", "0.840", "0.793", "0.837"], ["", "4×4", "0.842", "0.837", "0.842"],
                  ["Encoder", "RetinaRadar", "0.840", "—", "0.837"], ["", "ImageNet ResNet-50", "0.780", "—", "0.772"], ["", "Handcrafted", "0.605", "—", "0.604"], ["", "Random ResNet-50", "0.161", "—", "0.161"],
              ], [Cm(2.8), Cm(3.4), Cm(2.5), Cm(2.5), Cm(3.4)], font=8.5)
    add_figure(doc, FIG / "Figure4_Ablations_RMB20_v1_2.png", 4,
               "Component controls. (A) Regional representation. (B) aggregation operator. (C) single-split mask-ratio sensitivity; 0.30 marks the reference configuration, not a unique optimum. (D) per-seed paired image-bootstrap differences in center-plus-cross macro-F1 for 4×4 minus 3×3; every 95% interval crosses zero.",
               "Four-panel component-control figure comparing encoders, pooling operators, mask ratios, and per-seed paired bootstrap intervals for 4-by-4 versus 3-by-3 grids.")

    add_heading(doc, "3.4 Attention is directionally supported by model intervention", 2)
    add_text(doc, "The middle-center region received mean attention 0.398 and caused the largest macro-F1 loss when removed (0.065). Removing middle-left and middle-right reduced macro-F1 by 0.018 and 0.011. Several peripheral removals caused near-zero or slightly negative changes, indicating that attention was not merely a smooth centrality prior.")
    add_text(doc, "Across nine regions, the rank correlation between mean attention and occlusion loss was ρ=0.60 (p=0.088). The direction supports functional alignment, but the p value and nine-region sample do not warrant a definitive explanation claim. Class-stratified attention was center-dominant for Normal and NPDR; PDR shifted more weight laterally while retaining a central maximum.")
    add_figure(doc, FIG / "Figure5_Attention_Occlusion_RMB20_v1_2.png", 5,
               "Attention and model intervention. (A) Mean learned regional attention. (B) Macro-F1 change after hiding each region. (C) Attention versus occlusion loss with descriptive Spearman association. (D) Held-out attention stratified by true DR class. The analysis tests model-level functional alignment and is not lesion localization.",
               "Heatmaps of mean attention and one-region occlusion loss, a scatter plot of attention versus loss, and class-stratified attention heatmaps.")

    add_heading(doc, "3.5 Independent MMRDR-UWF severity evaluation", 2)
    add_text(doc, "Domain shift reduced absolute performance, but the evidence-topology ordering was reproduced. External full-view macro-F1 was 0.625±0.010, center fell to 0.600±0.004, and center-plus-cross reached 0.642±0.005. Center-plus-cross also had the lowest severity MAE (0.378±0.006) and underestimation (0.260±0.005).")
    add_text(doc, "Within-seed paired bootstrap differences for center versus full were negative or crossed zero. Center-plus-cross point differences were positive in all five seeds and ranged from approximately 0.007 to 0.025. This does not imply that peripheral retina should be discarded; it may reflect suppression of device borders or source-target nuisance variation by the structured mask. The external quality proxy showed no uniform monotonic performance gradient and remains descriptive.")
    add_table(doc, 4, "Independent MMRDR-UWF results across five source-trained seeds. Values are mean±sample SD; no target labels entered fitting or selection.",
              ["View", "Accuracy", "Macro-F1", "Severity MAE", "Under. rate", "Δ F1 vs full"],
              [["Full", "0.627±0.010", "0.625±0.010", "0.400±0.013", "0.272±0.013", "Reference"],
               ["Center", "0.602±0.004", "0.600±0.004", "0.432±0.005", "0.284±0.016", "−0.025±0.013"],
               ["Center + cross", "0.644±0.004", "0.642±0.005", "0.378±0.006", "0.260±0.005", "+0.017±0.006"]],
              [Cm(2.5), Cm(2.3), Cm(2.4), Cm(2.4), Cm(2.6), Cm(2.8)], font=8.5)
    add_figure(doc, FIG / "Figure6_External_Replication_RMB20_v1_2.png", 6,
               "Independent same-modality UWF evaluation. (A) internal and external macro-F1 across views. (B) external ordinal error and underestimation. (C) per-seed 2,000-resample paired bootstrap differences versus full view. (D) exploratory lowest/highest quartiles of an unlabeled coverage/contrast/sharpness proxy. External labels were used only for severity evaluation.",
               "Four-panel external evaluation comparing internal and MMRDR performance, external errors, paired bootstrap view differences, and exploratory quality-proxy strata.")

    add_heading(doc, "3.6 Paired-view risk ranking and threshold transport", 2)
    add_text(doc, "The fixed-split paired risk head achieved test AUROC 0.740 and average precision 0.139 at an underestimation prevalence of 0.077. Severity gap alone reached AUROC 0.677 and symmetric KL 0.539. Because the risk model and Clopper–Pearson threshold both used the same validation predictions, fixed-split coverage values are reported as exploratory: 0.628, 0.918, and 0.997 at nominal risk targets 5%, 10%, and 20%.")
    add_text(doc, "The grouped nested audit yielded lower and more variable performance. Mean outer-fold AUROC was 0.653±0.034. At target 5%, coverage was 0.567±0.274 and accepted risk 0.050±0.033; fold-specific coverage ranged from 0.365 to 0.958. At target 10%, coverage was 0.812±0.165 and accepted risk 0.092±0.034. Threshold transport, rather than ranking alone, is therefore the central limitation.")
    add_table(doc, 5, "Paired underestimation-risk analysis. The fixed-split rows are exploratory because one validation set was used for both risk fitting and threshold calibration; nested rows are mean±SD across four outer filename-grouped folds.",
              ["Protocol", "Risk AUROC", "Target", "Coverage", "Accepted risk"],
              [["Fixed exploratory", "0.740", "5%", "0.628", "0.029"], ["", "", "10%", "0.918", "0.075"], ["", "", "20%", "0.997", "0.077"],
               ["Nested grouped", "0.653±0.034", "5%", "0.567±0.274", "0.050±0.033"], ["", "", "10%", "0.812±0.165", "0.092±0.034"], ["", "", "20%", "0.980±0.014", "0.097±0.040"]],
              [Cm(3.6), Cm(3.0), Cm(2.2), Cm(3.2), Cm(3.6)], font=8.5)
    add_figure(doc, FIG / "Figure7_Selective_Risk_RMB20_v1_2.png", 7,
               "Paired-view underestimation audit. (A) AUROC under fixed exploratory and grouped nested protocols; values are not pooled because the protocols differ. (B) exploratory fixed-split test coverage at nominal risk targets. (C) nested mean accepted risk with fold SD. (D) nested outer-fold coverage–risk points. The module requires paired full/limited predictions.",
               "Four plots separating exploratory fixed-split risk ranking and thresholds from grouped nested accepted-risk and coverage variability.")

    add_heading(doc, "3.7 Pixel-aperture training and safety trade-off", 2)
    add_text(doc, "A supplementary source-only variant concatenated one random pixel-aperture representation per training image with the unmasked source representation. Both arms were retrained under the same corrected empty-mask fallback and with a dedicated random-mask sequence; the baseline values below are therefore protocol-matched within this optimization experiment and are not the independently trained estimates in Section 3.2. Across five seeds, macro-F1 and severity MAE improved in every held-out aperture. The largest gain occurred for the 0.35 rectangle, where macro-F1 increased from 0.519±0.160 to 0.794±0.013 and MAE fell from 0.446±0.123 to 0.221±0.014.")
    add_text(doc, "The safety endpoint was asymmetric. Underestimation fell from 0.272±0.092 to 0.097±0.007 at the severe 0.35 rectangle, but increased at the 0.55 rectangle, 0.75 rectangle, and 0.55 circle by 0.030, 0.018, and 0.019. The augmentation is therefore a useful stress-robustness result with an explicit trade-off, not a uniformly safer replacement for the primary model.")
    add_table(doc, 6, "Protocol-matched retrained baseline and source-only aperture-training results on held-out pixel-aperture stresses. Values are mean±sample SD across five seeds; Δ is augmented minus baseline.",
              ["Aperture", "F1 base", "F1 aug.", "MAE base", "MAE aug.", "Under base", "Under aug.", "Δ Under"],
              [["Rect. 0.35", "0.519±0.160", "0.794±0.013", "0.446±0.123", "0.221±0.014", "0.272±0.092", "0.097±0.007", "−0.175"],
               ["Rect. 0.55", "0.688±0.055", "0.802±0.017", "0.334±0.058", "0.208±0.018", "0.059±0.019", "0.089±0.008", "+0.030"],
               ["Rect. 0.75", "0.731±0.027", "0.811±0.015", "0.306±0.041", "0.199±0.016", "0.063±0.005", "0.081±0.008", "+0.018"],
               ["Circle 0.55", "0.752±0.051", "0.804±0.011", "0.264±0.050", "0.206±0.011", "0.070±0.013", "0.090±0.005", "+0.019"]],
              [Cm(2.4), Cm(2.0), Cm(2.0), Cm(2.0), Cm(2.0), Cm(2.0), Cm(2.0), Cm(1.8)], font=8.0)
    add_figure(doc, FIG / "Figure8_Continuous_Aperture_Optimization_RMB20_v1_2.png", 8,
               "Pixel-aperture training against its protocol-matched retrained baseline. (A) Macro-F1, (B) ordinal severity MAE, and (C) underestimation across four held-out apertures. Error bars denote seed SD and annotations give augmented-minus-baseline change. F1 and MAE improve consistently, whereas underestimation improves only for the most severe aperture.",
               "Three grouped bar charts comparing baseline and pixel-aperture training for macro-F1, severity MAE, and underestimation, highlighting opposite underestimation changes across apertures.")

    add_heading(doc, "4. Discussion", 1, page_break=True)
    add_heading(doc, "4.1 Principal findings", 2)
    add_text(doc, "This study isolates a hidden assumption in retinal AI: a technically acceptable acquisition is often treated as if it contained all evidence needed for the requested diagnosis. RegionSuff makes evidence availability explicit and tests the same severity model as area, location, shape, and topology change. The central finding is not that one crop is universally best; it is that these visibility attributes are not interchangeable and can alter model behavior even when the image record and source label are held fixed.")
    add_text(doc, "Four observations support that conclusion. Center-only evidence degraded internal and external performance, while center-plus-cross restored or exceeded the nominal full view. Features from the retinal image-quality encoder outperformed general, handcrafted, and random controls. The region with the highest attention caused the largest intervention loss, providing directional functional support. Pixel-aperture training substantially improved discrimination and ordinal error under severe evidence loss, but its underestimation trade-off shows why no single performance metric should define safety.")

    add_heading(doc, "4.2 Relationship to image quality", 2)
    add_text(doc, "Image-quality assessment and evidence availability are complementary. Quality asks whether observed structures are clear enough to interpret; evidence auditing asks what structures and disease cues were observed. A future acquisition system should treat them as separate axes and define sufficiency relative to a clinical task, because requirements for referable-DR screening, fine grading, or peripheral-lesion surveillance are different. [6–12]")

    add_heading(doc, "4.3 Interpreting the external center-plus-cross result", 2)
    add_text(doc, "Center-plus-cross exceeded the nominal full view on MMRDR-UWF. One plausible explanation is that, under domain shift, a full frame contains disease evidence together with device-specific borders, illumination patterns, and peripheral nuisance variation; a structured mask may suppress part of that nuisance. This remains an inference from the observed ordering, not evidence that clinicians should discard peripheral retina. Prospective same-eye, multi-device acquisitions and clinician sufficiency labels are needed to separate evidence from nuisance.")

    add_heading(doc, "4.4 Attention and paired-view risk", 2)
    add_text(doc, "The occlusion experiment prevents attention from being presented as explanation by visual plausibility alone. The observed ρ=0.60 was directionally consistent but did not reach conventional statistical significance (p=0.088) and is therefore treated as descriptive. Lesion-level annotations would permit stronger tests of whether attention and intervention correspond to hemorrhage, neovascularization, or peripheral lesions.")
    add_text(doc, "The paired-view risk head illustrates the difference between risk ranking and a transportable policy. Fixed-split AUROC was useful for hypothesis generation, but threshold calibration reused the risk-fitting validation predictions. Nested grouped evaluation lowered AUROC and revealed wide coverage variation. A deployable system would need a single-view risk feature, a truly independent calibration cohort, prespecified recapture or referral actions, subgroup auditing, and temporal monitoring. [25–27]")

    add_heading(doc, "4.5 Strengths", 2)
    add_text(doc, "Strengths include filename-derived grouped model partitions, a held-out internal test set, five training seeds, region and pixel perturbation families, encoder/pooling/grid/mask controls, intervention-based attention analysis, independent same-modality UWF evaluation, paired bootstrap contrasts, nested grouped risk auditing, and a direct audit of duplicate and conflicting source-list entries. Reporting also includes non-monotonic sensitivities, underestimation trade-offs, threshold variability, and source metadata limitations.")

    add_heading(doc, "5. Limitations", 1)
    add_text(doc, "First, no dataset provides clinician-adjudicated diagnostic-sufficiency labels; the study audits a DR model under synthetic evidence loss. Second, filenames rather than a dedicated patient-ID field supplied grouping keys, and the released UWF-DR lists contain repeated and conflicting entries. The held-out test was duplicate-free and a deduplicated-validation sensitivity was stable, but independent reproduction with explicit patient identifiers is needed. Third, geometric masks do not reproduce camera optics, gaze, eyelash artifacts, or true paired acquisitions. Fourth, RetinaRadar is a local image-quality checkpoint with incomplete public provenance and must not be described as a disease foundation model. Fifth, five external DR levels were collapsed to three for label harmonization.")
    add_text(doc, "Sixth, only one independent same-modality UWF cohort was available. Seventh, the external quality proxy is unlabeled and is not a clinical quality endpoint. Eighth, the paired risk head requires both full and limited predictions and cannot triage a lone limited image. Ninth, the inner risk-development subset also supported severity early stopping, risk fitting, and threshold selection, so fully separated prospective calibration remains necessary. Tenth, seed SD and image-level bootstrap intervals quantify different uncertainty sources, and neither substitutes for multicenter prospective validation.")

    add_heading(doc, "6. Conclusion", 1)
    add_text(doc, "A sharp fundus image can still omit evidence relevant to a requested disease decision. RegionSuff provides an explicit, visibility-conditioned way to audit that failure mode. Internal perturbations and independent UWF evaluation show that visible area, location, shape, and topology have distinct effects on DR model behavior, while the optimization and risk analyses identify important underestimation and threshold-transport trade-offs. These findings support evidence-aware model auditing, but clinician-adjudicated labels, explicit patient metadata, real paired acquisitions, and independently calibrated single-view risk models are required before any diagnostic-sufficiency deployment claim.")

    add_heading(doc, "Declarations", 1)
    add_heading(doc, "Author contributions", 2)
    add_text(doc, "K.D. (Kaiwen Deng): Conceptualization, Methodology, Software, Investigation, Data Curation, Formal Analysis, Validation, Visualization, and Writing—Original Draft. L.L. (Liwei Liu): Supervision, Project Administration, Resources, and Writing—Review & Editing.")
    add_heading(doc, "Ethics statement", 2)
    add_text(doc, "This work is a secondary computational analysis of de-identified released datasets and involved no new participant recruitment, intervention, or data collection. Ethical approvals and consent or waiver procedures are reported by the source dataset publications. [21,22]")
    add_heading(doc, "Data availability", 2)
    add_text(doc, "UWF-DR is available from Figshare (https://doi.org/10.6084/m9.figshare.31259494). MMRDR is available from Figshare (https://doi.org/10.6084/m9.figshare.29423747.v2). Reuse must follow source licenses and data terms.")
    add_heading(doc, "Code and result availability", 2)
    add_text(doc, "The project archive contains the analysis scripts, frozen experiment outputs, paired-bootstrap results, validation-list audit, manuscript builder, and PNG/PDF/SVG figure sources. Original Exp01–Exp60 outputs were not overwritten while preparing version 1.3.")
    add_heading(doc, "Competing interests", 2)
    add_text(doc, "The authors declare no competing interests.")

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
        "Peng S, Yang S, Zhao X, et al. A fundus image dataset for intelligent diabetic retinopathy system. Sci Data. 2026;13:777. doi:10.1038/s41597-026-07093-7. Dataset doi:10.6084/m9.figshare.31259494.",
        "Tang Z, Wang L, Guo Z, et al. A multimodal retinal image dataset for diabetic retinopathy detection using foundation models. Sci Data. 2026;13:639. doi:10.1038/s41597-026-07005-9.",
        "RetinaRadar. Multi-label retinal image-quality EfficientNet-B0 checkpoint and local inference metadata. Software/model artifact, 2025. Local SHA-256: da24fd822a8560a6856cd0432e084897acb6254647ebeceb493a400a1e9c7913.",
        "Deng J, Dong W, Socher R, Li LJ, Li K, Fei-Fei L. ImageNet: A large-scale hierarchical image database. Proc IEEE Conf Comput Vis Pattern Recognit. 2009:248–255. doi:10.1109/CVPR.2009.5206848.",
        "Geifman Y, El-Yaniv R. Selective classification for deep neural networks. Adv Neural Inf Process Syst. 2017;30:4878–4887.",
        "Geifman Y, El-Yaniv R. SelectiveNet: A deep neural network with an integrated reject option. Proc 36th Int Conf Mach Learn. 2019;97:2151–2159.",
        "Clopper CJ, Pearson ES. The use of confidence or fiducial limits illustrated in the case of the binomial. Biometrika. 1934;26:404–413. doi:10.1093/biomet/26.4.404.",
        "Efron B, Tibshirani RJ. An Introduction to the Bootstrap. New York: Chapman & Hall/CRC; 1993.",
        "Guo C, Pleiss G, Sun Y, Weinberger KQ. On calibration of modern neural networks. Proc 34th Int Conf Mach Learn. 2017;70:1321–1330.",
        "Hendrycks D, Gimpel K. A baseline for detecting misclassified and out-of-distribution examples in neural networks. Proc Int Conf Learn Represent. 2017.",
    ]
    for i, ref in enumerate(refs, 1):
        add_reference(doc, i, ref)

    doc.core_properties.title = "RegionSuff: Visibility-Conditioned Regional Evidence Auditing under Limited Fields of View in Ultra-Widefield Fundus Imaging"
    doc.core_properties.subject = "Evidence-availability auditing for limited-view UWF fundus imaging"
    doc.core_properties.keywords = "RegionSuff, evidence availability, UWF, diabetic retinopathy, masked attention, underestimation"
    doc.core_properties.comments = "Version 1.3: full narrative and formula audit; abstract and introduction tightened; risk-feature definitions and protocol-matched optimization baseline clarified; figure 1 retained outside the introduction."
    doc.core_properties.author = "Kaiwen Deng; Liwei Liu"
    doc.core_properties.last_modified_by = "Codex"
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(OUTPUT))
    print(OUTPUT)


if __name__ == "__main__":
    build()
