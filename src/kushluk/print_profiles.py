"""Profile-specific print geometry; source editions remain four logical A4 pages."""
from __future__ import annotations

from pathlib import Path

from kushluk.validation import validate_pdf


def impose_a3_folded(source_pdf: Path, destination_pdf: Path) -> Path:
    """Impose four A4 pages onto two A3 landscape sides: outside 4|1, inside 2|3.

    Coordinates are in PDF points. The canonical A4 pages are not modified.
    Duplex edge/feed direction still requires a physical printer acceptance test.
    """
    from pypdf import PdfReader, PdfWriter, Transformation
    from pypdf._page import PageObject

    valid = validate_pdf(source_pdf, expected_pages=4)
    if not valid.ok:
        raise ValueError("Cannot impose unvalidated four-page A4 edition: " + "; ".join(valid.errors))

    reader = PdfReader(str(source_pdf))
    first = reader.pages[0]
    width = float(first.mediabox.width)
    height = float(first.mediabox.height)
    writer = PdfWriter()
    for left, right in ((3, 0), (1, 2)):
        sheet = PageObject.create_blank_page(width=2 * width, height=height)
        sheet.merge_transformed_page(
            reader.pages[left], Transformation().translate(tx=0, ty=0), expand=False
        )
        sheet.merge_transformed_page(
            reader.pages[right], Transformation().translate(tx=width, ty=0), expand=False
        )
        writer.add_page(sheet)
    writer.add_metadata({"/Title": "Kushluk A3 folded / 4|1 2|3"})
    destination_pdf.parent.mkdir(parents=True, exist_ok=True)
    with destination_pdf.open("wb") as stream:
        writer.write(stream)
    result = validate_a3_booklet(destination_pdf)
    if result:
        destination_pdf.unlink(missing_ok=True)
        raise ValueError("A3 imposition failed: " + "; ".join(result))
    return destination_pdf


def validate_a3_booklet(path: Path) -> list[str]:
    """Check sheet geometry plus logical marker pairing, never just page count."""
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    errors: list[str] = []
    if len(reader.pages) != 2:
        return [f"Expected two A3 sheet sides, found {len(reader.pages)}."]
    for side, markers in enumerate(((4, 1), (2, 3)), start=1):
        page = reader.pages[side - 1]
        box = page.mediabox
        width, height = float(box.width), float(box.height)
        if abs(width - 1190.55) > 2 or abs(height - 841.89) > 2:
            errors.append(f"Side {side} is not landscape A3.")
        text = " ".join((page.extract_text() or "").split())
        for marker in markers:
            if f"{marker} / 4" not in text:
                errors.append(f"Side {side} does not contain logical page {marker}.")
    return errors
