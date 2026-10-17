"""WeasyPrint rendered-box inspection: count, per-page text bounds and footer overlap.

Unlike bare pypdf page count this inspects actual laid-out text on each sheet.
It is still automated geometry evidence, not a human/physical print signoff.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class LayoutInspection:
    page_count: int
    issues: list[str] = field(default_factory=list)
    min_text_font_css_px: float | None = None

    @property
    def ok(self) -> bool:
        return not self.issues


def inspect_html_fit(path: Path, *, minimum_font_px: float = 9.0) -> LayoutInspection:
    from weasyprint import HTML

    pages = HTML(filename=str(path)).render().pages
    result = LayoutInspection(page_count=len(pages))
    if len(pages) != 4:
        result.issues.append(f"Expected four rendered sheets; got {len(pages)}.")
    small = []
    for number, page in enumerate(pages, 1):
        root = page._page_box
        boxes = []

        def walk(node):
            boxes.append(node)
            for child in getattr(node, "children", ()):
                walk(child)

        walk(root)
        sections = [
            box for box in boxes if box.element_tag == "section"
            and getattr(box, "element", None) is not None
            and box.element.get("data-page") is not None
        ]
        declared = {section.element.get("data-page") for section in sections}
        if declared != {str(number)}:
            result.issues.append(f"Rendered page {number} has wrong/fragmented sheet markers.")
        # Text/letter-bearing boxes, not decorative backgrounds, decide safe margins.
        texts = [box for box in boxes if type(box).__name__ == "TextBox"
                 and (getattr(box, "text", "") or "").strip()]
        for box in texts:
            left, top = box.position_x, box.position_y
            right, bottom = left + box.width, top + box.height
            if left < 16 or right > page.width - 16:
                result.issues.append(f"Page {number} text extends beyond horizontal safety.")
                break
            if top < 16 or bottom > page.height - 16:
                result.issues.append(f"Page {number} text extends beyond vertical safety.")
                break
            px = box.style["font_size"]
            if isinstance(px, (float, int)):
                small.append(float(px))
        footers = [box for box in boxes if box.element_tag == "footer"]
        articles = [box for box in boxes if box.element_tag == "article"]
        if footers:
            top_footer = min(f.position_y for f in footers)
            for article in articles:
                if article.position_y + article.height > top_footer + 2:
                    result.issues.append(f"Page {number} article overlaps footer.")
                    break
    if small:
        result.min_text_font_css_px = round(min(small), 2)
        if result.min_text_font_css_px < minimum_font_px:
            result.issues.append("Rendered text falls below editorial font-size floor.")
    return result
