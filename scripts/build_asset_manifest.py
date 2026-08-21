"""Write a SHA-256 manifest for large GitHub Release assets and their local sources."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path('/Users/tongyue/Documents/77f /7hao')
REPO = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parents[1] / 'metadata' / 'ASSET_MANIFEST.tsv'

ASSETS = [
    ('data', 'UWF_DR_1630-source.zip', ROOT / 'datasets/UWF_DR_1630/Ultra-wide-field (SLO) fundus image dataset for intelligent diabetic retinopathy system.zip'),
    ('data', 'MSHF_dataset_2.0.zip', ROOT / 'datasets/MSHF_IQA/MSHF_dataset_2.0.zip'),
    ('data', 'SUSTech_SYSU.zip', ROOT / 'datasets/SUSTech_SYSU_Figshare/SUSTech_SYSU.zip'),
    ('data', 'Disease_Grading.zip', ROOT / 'datasets/IDRiD_Zenodo/Disease_Grading.zip'),
    ('data', 'RFMiD2_0.zip', ROOT / 'datasets/RFMiD2_0.zip'),
    ('weight', 'RegionSuff-model-weights.tar.gz', Path(__file__).resolve().parents[1] / 'archives/RegionSuff-model-weights.tar.gz'),
    ('archive', 'RegionSuff-project-history.tar.gz', Path(__file__).resolve().parents[1] / 'archives/RegionSuff-project-history.tar.gz'),
]
ASSETS.extend(
    ('data', f'MMRDR.zip.{i:03d}', ROOT / f'datasets/MMRDR_figshare/parts/MMRDR.zip.{i:03d}')
    for i in range(1, 10)
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(16 * 1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def portable_path(path: Path) -> str:
    for base, label in ((ROOT, '7hao'), (REPO, 'repository')):
        try:
            return f'{label}/{path.relative_to(base)}'
        except ValueError:
            pass
    return path.name


def main():
    lines = ['kind\trelease_asset\tsource_path\tbytes\tsha256']
    for kind, asset, path in ASSETS:
        if not path.exists():
            raise FileNotFoundError(path)
        lines.append(f'{kind}\t{asset}\t{portable_path(path)}\t{path.stat().st_size}\t{sha256(path)}')
    OUT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'Wrote {OUT} ({len(ASSETS)} assets)')


if __name__ == '__main__':
    main()
