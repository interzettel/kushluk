from __future__ import annotations

from importlib.resources import files
import base64
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from kushluk.models import Publication
from kushluk.media import MediaError, render_bytes


def render_html(
    publication: Publication, output_path: Path, *, media_store: Path | None = None,
) -> Path:
    template_dir = files("kushluk").joinpath("templates")
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("edition.html")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image_data = {}
    if media_store is not None:
        for placement in publication.media:
            if placement.story_id not in {s.id for s in publication.stories}:
                continue
            try:
                content = render_bytes(media_store, placement)
            except (MediaError, OSError):
                continue  # Never embed a stale, revoked or unsafe image.
            image_data[placement.story_id] = {
                "uri": "data:image/png;base64," + base64.b64encode(content).decode("ascii"),
                "caption": placement.caption,
                "credit": placement.attribution,
                "license": placement.license_id,
                "alt": placement.alt_text,
            }
    output_path.write_text(
        template.render(
            publication=publication, stories_by_id={s.id: s for s in publication.stories},
            images_by_story=image_data,
        ),
        encoding="utf-8",
    )
    return output_path


def render_pdf(html_path: Path, pdf_path: Path) -> Path:
    try:
        from weasyprint import HTML
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(
            "PDF rendering needs the optional 'pdf' dependency: pip install -e '.[pdf]'"
        ) from exc

    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    HTML(filename=str(html_path)).write_pdf(str(pdf_path))
    return pdf_path
