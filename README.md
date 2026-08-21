# RegionSuff

**Visibility-Conditioned Auditing of Model-Specific Retinal Evidence under Limited Fields of View in Ultra-Widefield Fundus Imaging**

RegionSuff is a retrospective model-audit framework for asking a narrow but important question in retinal artificial intelligence: when a fundus image is technically gradable, does the fitted diabetic-retinopathy (DR) classifier still have the retinal evidence that it uses for the requested decision?

The framework represents a UWF image as a 3×3 regional evidence bank. A frozen retinal image-quality encoder extracts one token per region, and visibility-conditioned masked attention aggregates only the tokens permitted by the current region-level mask. Controlled pixel-space apertures then test how visible area, location, shape, and topology affect fixed-model behavior. A downstream paired-view risk model compares full-view and center-plus-cross predictions to audit limited-view underestimation.

## Main findings in the current manuscript

- On the held-out UWF-DR test set, macro-F1 was 0.830 for full-view, 0.790 for center-only, and 0.829 for center-plus-cross inference.
- On the independent same-modality MMRDR-UWF cohort, macro-F1 was 0.625, 0.600, and 0.642, respectively.
- Equal nominal aperture area did not guarantee equal model behavior; area, location, shape, and topology were not interchangeable.
- One-region occlusion was directionally aligned with learned attention (Spearman rho = 0.60; p = 0.088; nine regions).
- The fixed-split downstream paired-view risk model reached AUROC 0.740; nested grouped evaluation was lower (0.653), so threshold transport remains exploratory.

## Repository layout

```text
manuscript/  Current manuscript with repository link
figures/     Editable Figure 1 and Figure 2 sources and high-resolution exports
src/         Experiment scripts and manuscript/figure builders
results/     Textual experiment summaries, tables, logs, and JSON outputs
metadata/    Data and weight provenance, SHA-256 manifests, and archive guide
scripts/     Reproducibility and manifest utilities
```

Large data, weights, and full experiment-history archives are kept as assets of the repository's `v0.1.0-archive` Release rather than ordinary Git objects. This is necessary because GitHub blocks normal Git files larger than 100 MiB. See [metadata/ARCHIVE_LAYOUT.md](metadata/ARCHIVE_LAYOUT.md) and [metadata/DATASETS.md](metadata/DATASETS.md).

## Scope and interpretation

RegionSuff studies **model-specific retinal evidence availability** under synthetic visibility restrictions. It does not claim clinician-adjudicated diagnostic sufficiency, a real paired-acquisition study, or a deployable single-image triage rule.

## Reproducibility

The scripts are preserved as the analysis provenance for experiments Exp01–Exp62. They retain the original research paths and environment assumptions; `metadata/ARCHIVE_LAYOUT.md` documents the released archives required to recreate the local layout. Final tables and figures in the manuscript are backed by the frozen JSON, CSV, log, and report outputs in `results/`.

## Data and weights

Source data and third-party model assets retain their original licenses and access terms. They are included only in this private research archive; do not redistribute them independently. Dataset download sources, checksums, and asset names are listed in `metadata/DATASETS.md` and `metadata/WEIGHTS.md`.

## Citation

The manuscript is under preparation. Until a DOI is assigned, cite the repository URL and the manuscript in `manuscript/`.
