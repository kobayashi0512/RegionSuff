from pathlib import Path
import shutil

from docx import Document
from docx.oxml.ns import qn


SOURCE = Path('/Users/tongyue/Documents/ppf/第四论文/RegionSuff_2.2.docx')
OUTPUT = Path('/Users/tongyue/Documents/ppf/第四论文/RegionSuff_2.3.docx')


def clear_paragraph(paragraph):
    """Remove paragraph content while preserving paragraph properties/style."""
    p = paragraph._p
    p_pr = p.pPr
    for child in list(p):
        if child is not p_pr:
            p.remove(child)


def set_paragraph_text(paragraph, text, bold_prefix=None):
    clear_paragraph(paragraph)
    if bold_prefix and text.startswith(bold_prefix):
        run = paragraph.add_run(bold_prefix)
        run.bold = True
        paragraph.add_run(text[len(bold_prefix):])
    else:
        paragraph.add_run(text)


def find_heading(doc, text):
    for paragraph in doc.paragraphs:
        if paragraph.text.strip() == text:
            return paragraph
    raise ValueError(f'Heading not found: {text}')


def has_image(paragraph):
    return bool(paragraph._p.xpath('.//a:blip'))


def fix_pair_probability_equation(doc):
    """Restore the punctuation separating the two displayed probability identities."""
    equation_paragraph = next(
        p for p in doc.paragraphs if p._p.xpath('.//m:oMathPara')
    )
    math_text_nodes = equation_paragraph._p.xpath('.//m:t')
    if not math_text_nodes:
        raise ValueError('Paired-view probability equation was not found.')
    math_text_nodes[-1].text = ').'


def main():
    shutil.copy2(SOURCE, OUTPUT)
    doc = Document(OUTPUT)

    # Section 2.1: move the study logic into the prose and keep the caption concise.
    p20_index = next(i for i, p in enumerate(doc.paragraphs) if p.text.startswith('Using publicly available, de-identified data'))
    p20 = doc.paragraphs[p20_index]
    set_paragraph_text(
        p20,
        'Using publicly available, de-identified data, we conducted a retrospective computational study without additional image acquisition. Model performance was evaluated on a held-out test set under three prespecified visibility settings: full-view, center-only, and center-plus-cross. Macro-F1 for three-class DR grading was the primary endpoint. Accuracy, ordinal severity mean absolute error (MAE), and underestimation rate were secondary endpoints. Source-domain training was repeated across five random seeds to characterize optimization variability. Where per-image predictions were available, view contrasts were summarized with image-level paired bootstrap 95% confidence intervals. [28]'
    )
    p21 = doc.paragraphs[p20_index + 1]
    set_paragraph_text(
        p21,
        'The study workflow is summarized in Figure 1. We first distinguish technical gradability from the availability of task-relevant retinal evidence. We then impose region-level masks and pixel-space apertures on the same UWF image to vary the composition, area, location, shape, and topology of visible evidence while keeping the source DR label fixed. RegionSuff performs visibility-conditioned regional aggregation for three-class DR prediction. Finally, internal testing, one-region occlusion, independent MMRDR-UWF evaluation, and paired-view analysis examine whether prediction changes are consistent with the available retinal evidence. The masks are controlled interventions rather than real paired conventional-field and UWF acquisitions; the operational construct is model-specific retinal evidence availability.'
    )

    p23 = next(p for p in doc.paragraphs if p.text.startswith('Figure 1.'))
    set_paragraph_text(
        p23,
        'Figure 1. Overview of the RegionSuff framework. (A) Technical image quality does not guarantee task-relevant retinal evidence. (B) Region-level masks and pixel-space apertures impose controlled restrictions on visible evidence. (C) RegionSuff aggregates visible regional representations with visibility-conditioned attention for three-class DR prediction. (D) Paired full-view and limited-view predictions are compared in an exploratory underestimation audit. All restrictions are synthetic and the source DR label remains unchanged.',
        'Figure 1.'
    )

    p24 = next(p for p in doc.paragraphs if p.text.startswith('For the paired-view audit'))
    set_paragraph_text(
        p24,
        'For the paired-view audit, the same fitted RegionSuff severity model was evaluated under full-view and limited-view masks, producing:'
    )

    p26 = next(p for p in doc.paragraphs if p.text.startswith('A separate downstream risk model'))
    set_paragraph_text(
        p26,
        'The two probability vectors were then compared by a separate downstream risk model. This analysis characterizes prediction shifts under restricted views and requires both visibility conditions; it is not an independent single-image triage rule.'
    )

    # Section 2.6: introduce Figure 2 in the running text and reduce its caption to a summary.
    p48 = next(p for p in doc.paragraphs if p.text.startswith('During source training'))
    set_paragraph_text(
        p48,
        'During source training, each of the nine regional tokens was independently masked with probability ρ=0.30. If an all-empty mask was sampled, the first row-major region (index 0) was restored in the locked Exp35/Exp36 implementation; the event probability was 0.3⁹≈2.0×10⁻⁵ per training image. A sensitivity run restored the geometric center token instead and, together with validation-list deduplication, produced nearly unchanged test results. Deterministic full-view, center-only, and center-plus-cross masks were reserved for evaluation.'
    )

    image_paragraph = next(p for p in doc.paragraphs if has_image(p) and p.text.strip() == '')
    intro = image_paragraph.insert_paragraph_before(
        'The complete information flow is shown in Figure 2. A single UWF image is partitioned into nine regional crops; the shared frozen encoder and trainable projection convert each visible crop into one regional token. The visibility mask is applied inside the attention pool, so unavailable regions contribute no weight and the remaining tokens are normalized before DR severity prediction. The same fitted severity model is then evaluated under full and limited views before the paired-view audit compares the two outputs.',
        style=p48.style.name,
    )

    p50 = next(p for p in doc.paragraphs if p.text.startswith('Figure 2.'))
    set_paragraph_text(
        p50,
        'Figure 2. RegionSuff information flow. A single UWF image is partitioned into a 3×3 regional evidence bank; visible regions follow a shared frozen regional encoder and trainable projection before visibility-conditioned attention produces the three-class DR prediction. The fitted severity model is subsequently evaluated under full and limited views for exploratory paired-view auditing. Black tiles denote excluded retinal evidence; the paired audit requires two model predictions.',
        'Figure 2.'
    )

    # Use the long form consistently in the surrounding method text.
    p37 = next(p for p in doc.paragraphs if 'The shared feature path is summarized in Fig. 2B.' in p.text)
    set_paragraph_text(p37, p37.text.replace('Fig. 2B.', 'Figure 2B.'))

    fix_pair_probability_equation(doc)

    doc.save(OUTPUT)
    print(f'Wrote {OUTPUT}')


if __name__ == '__main__':
    main()
