# Model-weight provenance

| Asset | Role | Local provenance / license note | Archive policy |
|---|---|---|---|
| RetinaRadar EfficientNet-B0 checkpoint | Frozen regional image-quality encoder used by RegionSuff | Local model card declares Apache-2.0; this project treats it as an image-quality encoder, not a disease foundation model | Included in `RegionSuff-model-weights.tar.gz` Release asset |
| RetinaRadar Inception-v4 checkpoint | Retained local model asset used in exploratory work | Same local RetinaRadar provenance record | Included in `RegionSuff-model-weights.tar.gz` Release asset |
| `model.safetensors` | Retained local model weight asset | Preserve source provenance in the manifest; do not redistribute separately | Included in `RegionSuff-model-weights.tar.gz` Release asset |
| MIRAGE configuration | Auxiliary configuration only; no MIRAGE large weight file is locally retained | Local card declares CC-BY-NC-ND-4.0 | Small configuration is stored in the repository; no large MIRAGE checkpoint is archived |

Exact byte sizes and SHA-256 digests are in `ASSET_MANIFEST.tsv`.
