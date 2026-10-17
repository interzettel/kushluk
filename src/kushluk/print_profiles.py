"""Profile-specific print geometry; source editions remain four logical A4 pages."""
from __future__ import annotations

from pathlib import Path

from kushluk.validation import validate_pdf


def resolve_home_print_profile(paper_size: str, profile: str | None = None) -> str:
    """Resolve a saved home choice only when no explicit profile was requested."""
    if profile is None:
        if paper_size not in {"a4", "letter"}:
            raise ValueError("invalid_home_paper_size")
        return "letter-home" if paper_size == "letter" else "a4-home"
    if profile not in {"a4-home", "letter-home", "a3-folded"}:
        raise ValueError("invalid_print_profile")
    return profile


LETTER_WIDTH = 612.0
LETTER_HEIGHT = 792.0


def impose_letter_home(source_pdf: Path, destination_pdf: Path) -> Path:
    """Make a four-page US Letter print variant from the canonical A4 PDF.

    Scale and center each *complete A4 page* uniformly inside a 12 pt
    non-printable safety inset. Do not stretch the page or rewrite its source.
    This is a print variant, not a reflowed Letter editorial layout.
    """
    from pypdf import PdfReader, PdfWriter, Transformation
    from pypdf._page import PageObject

    validated = validate_pdf(source_pdf, expected_pages=4)
    if not validated.ok:
        raise ValueError("Cannot convert an unvalidated A4 source to Letter")
    if source_pdf.resolve() == destination_pdf.resolve():
        raise ValueError("Letter output must not overwrite the canonical A4 source")
    reader = PdfReader(str(source_pdf))
    writer = PdfWriter()
    inset = 12.0
    for page in reader.pages:
        box = page.mediabox
        source_width = float(box.width)
        source_height = float(box.height)
        factor = min(
            (LETTER_WIDTH - 2 * inset) / source_width,
            (LETTER_HEIGHT - 2 * inset) / source_height,
        )
        offset_x = (LETTER_WIDTH - factor * source_width) / 2
        offset_y = (LETTER_HEIGHT - factor * source_height) / 2
        sheet = PageObject.create_blank_page(width=LETTER_WIDTH, height=LETTER_HEIGHT)
        sheet.merge_transformed_page(
            page, Transformation().scale(factor).translate(tx=offset_x, ty=offset_y),
            expand=False,
        )
        writer.add_page(sheet)
    writer.add_metadata({"/Title": "Kushluk US Letter — four-page home print"})
    destination_pdf.parent.mkdir(parents=True, exist_ok=True)
    if destination_pdf.is_symlink() or destination_pdf.exists():
        raise ValueError("Letter output path must be new")
    try:
        with destination_pdf.open("xb") as stream:
            writer.write(stream)
        errors = validate_letter_home(destination_pdf)
        if errors:
            raise ValueError("Invalid Letter print variant: " + "; ".join(errors))
    except BaseException:
        destination_pdf.unlink(missing_ok=True)
        raise
    return destination_pdf


def validate_letter_home(path: Path) -> list[str]:
    """Check MediaBox geometry and logical page order, not physical printing."""
    from pypdf import PdfReader

    if path.is_symlink() or not path.is_file():
        return ["Missing or unsafe Letter PDF."]
    try:
        reader = PdfReader(str(path))
        if len(reader.pages) != 4:
            return ["US Letter output must contain four logical pages."]
        errors = []
        for index, page in enumerate(reader.pages, 1):
            box = page.mediabox
            if (abs(float(box.width) - LETTER_WIDTH) > 1
                    or abs(float(box.height) - LETTER_HEIGHT) > 1):
                errors.append(f"Page {index} does not have US Letter geometry.")
            text = " ".join((page.extract_text() or "").split())
            if f"{index} / 4" not in text:
                errors.append(f"Page {index} does not have its canonical page marker.")
        return errors
    except (OSError, ValueError, TypeError):
        return ["Could not inspect Letter PDF."]


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
        if all(f"{marker} / 4" in text for marker in markers):
            if text.index(f"{markers[0]} / 4") > text.index(f"{markers[1]} / 4"):
                errors.append(f"Side {side} has reversed left/right booklet order.")
    return errors
