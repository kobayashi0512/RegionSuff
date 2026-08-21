from __future__ import annotations

import argparse
import hashlib
import shutil
import tempfile
import zipfile
from pathlib import Path

from lxml import etree


NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def find_figure_media(docx: Path) -> dict[str, str]:
    """Return media targets for the Figure 1 and Figure 2 drawing paragraphs."""
    with zipfile.ZipFile(docx) as archive:
        relationships = etree.fromstring(archive.read("word/_rels/document.xml.rels"))
        relmap = {
            node.get("Id"): node.get("Target")
            for node in relationships
            if node.get("Type", "").endswith("/image")
        }
        body = etree.fromstring(archive.read("word/document.xml"))
        paragraphs = body.xpath(".//w:body/w:p", namespaces=NS)

        figure_media: dict[str, str] = {}
        for index, paragraph in enumerate(paragraphs):
            embeds = paragraph.xpath(".//a:blip/@r:embed", namespaces=NS)
            if not embeds:
                continue
            window = " ".join(
                "".join(p.xpath(".//w:t/text()", namespaces=NS)).strip()
                for p in paragraphs[index + 1 : min(index + 3, len(paragraphs))]
            )
            if window.startswith("Figure 1."):
                figure_media["Figure 1"] = "word/" + relmap[embeds[0]].lstrip("/")
            elif window.startswith("Figure 2."):
                figure_media["Figure 2"] = "word/" + relmap[embeds[0]].lstrip("/")

    expected = {"Figure 1", "Figure 2"}
    missing = expected.difference(figure_media)
    if missing:
        raise RuntimeError(f"Could not identify image relationships for: {sorted(missing)}")
    return figure_media


def replace_media(source: Path, output: Path, replacements: dict[str, Path]) -> None:
    with zipfile.ZipFile(source) as archive:
        source_hashes = {
            name: sha256_bytes(archive.read(name))
            for name in archive.namelist()
            if name.startswith("word/media/")
        }

    with tempfile.TemporaryDirectory(prefix="regionsuff_docx_") as temp_dir:
        staging = Path(temp_dir) / output.name
        with zipfile.ZipFile(source) as source_archive, zipfile.ZipFile(
            staging, "w", compression=zipfile.ZIP_DEFLATED
        ) as destination_archive:
            for item in source_archive.infolist():
                payload = source_archive.read(item.filename)
                replacement_path = replacements.get(item.filename)
                if replacement_path is not None:
                    payload = replacement_path.read_bytes()
                destination_archive.writestr(item, payload)

        with zipfile.ZipFile(staging) as output_archive:
            output_hashes = {
                name: sha256_bytes(output_archive.read(name))
                for name in output_archive.namelist()
                if name.startswith("word/media/")
            }

        changed = {
            name
            for name, digest in source_hashes.items()
            if output_hashes.get(name) != digest
        }
        if changed != set(replacements):
            raise RuntimeError(
                "Unexpected DOCX media changes. "
                f"Expected {sorted(replacements)}, observed {sorted(changed)}"
            )

        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(staging, output)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Replace only the Figure 1 and Figure 2 media in a Word manuscript."
    )
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--figure1", type=Path, required=True)
    parser.add_argument("--figure2", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    for path in (args.source, args.figure1, args.figure2):
        if not path.is_file():
            raise FileNotFoundError(path)
    if args.output.resolve() == args.source.resolve():
        raise RuntimeError("Output must be a new DOCX; the source manuscript is preserved.")

    mappings = find_figure_media(args.source)
    replacements = {
        mappings["Figure 1"]: args.figure1,
        mappings["Figure 2"]: args.figure2,
    }
    replace_media(args.source, args.output, replacements)

    print("Figure 1 ->", mappings["Figure 1"])
    print("Figure 2 ->", mappings["Figure 2"])
    print("Output ->", args.output)


if __name__ == "__main__":
    main()
