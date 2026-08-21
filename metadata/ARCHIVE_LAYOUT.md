# Archive layout and restoration guide

This private archive separates normal Git content from large GitHub Release assets.

## Git repository content

- `manuscript/`: the current manuscript.
- `figures/`: editable Figure 1 and Figure 2 source decks plus PNG exports.
- `src/`: experiment scripts and manuscript/figure-generation scripts.
- `results/`: textual reports, result JSON files, tables, logs, and experiment decision summaries.
- `metadata/`: provenance and integrity records.

## GitHub Release assets (`v0.1.0-archive`)

| Asset family | Content | Restore location |
|---|---|---|
| `RegionSuff-project-history.tar.gz` | Full RegionSuff experiment, paper-design, and manuscript-build history | research workspace root |
| `RegionSuff-model-weights.tar.gz` | Frozen RetinaRadar and other locally retained model assets | `models/` |
| `MMRDR.zip.001` … `MMRDR.zip.009` | Split MMRDR source archive | `datasets/MMRDR_figshare/parts/` |
| `UWF_DR_1630-source.zip` | UWF-DR source archive | `datasets/UWF_DR_1630/` |
| `MSHF_dataset_2.0.zip` | MSHF IQA source archive | `datasets/MSHF_IQA/` |
| `SUSTech_SYSU.zip` | SUSTech/SYSU source archive | `datasets/SUSTech_SYSU_Figshare/` |
| `Disease_Grading.zip` | IDRiD source archive | `datasets/IDRiD_Zenodo/` |
| `RFMiD2_0.zip` | RFMiD 2.0 source archive | `datasets/RFMiD2_0/` |

## MMRDR reconstruction

Download every `MMRDR.zip.00*` asset into one directory, then concatenate in order:

```bash
cat MMRDR.zip.001 MMRDR.zip.002 MMRDR.zip.003 MMRDR.zip.004 MMRDR.zip.005 \\
  MMRDR.zip.006 MMRDR.zip.007 MMRDR.zip.008 MMRDR.zip.009 > MMRDR.zip
unzip -t MMRDR.zip
```

Verify every asset against `metadata/ASSET_MANIFEST.tsv` before extracting. The archive deliberately preserves original downloaded source packages; extracted image directories are reproducible from those packages and are not duplicated as separate release assets.

## Important

The GitHub repository is private during manuscript preparation. Third-party dataset and model reuse must comply with each source's own terms, license, and any required attribution.
