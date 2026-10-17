"""Explicit, idempotent human-authorized delivery from validated archived editions."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import tempfile

from kushluk.config import Settings
from kushluk.delivery import send_email_edition
from kushluk.models import Publication
from kushluk.print_profiles import validate_a3_booklet
from kushluk.printing import print_pdf
from kushluk.validation import validate_pdf


@dataclass(slots=True)
class ArchiveDeliveryOutcome:
    edition_id: str
    channel: str
    request_id: str
    status: str
    failure_code: str | None = None

    def as_dict(self) -> dict[str, str | int | None]:
        return {
            "schema_version": 1,
            "edition_id": self.edition_id,
            "channel": self.channel,
            "request_id": self.request_id,
            "status": self.status,
            "failure_code": self.failure_code,
        }


def _save_receipt(path: Path, payload: dict) -> None:
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent,
            prefix=".kushluk-delivery-", delete=False,
        ) as stream:
            temporary = Path(stream.name)
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _require_archived_regular_file(path: Path, *, max_bytes: int) -> None:
    """Fail closed on symlinks, nonfiles and out-of-bounds archive inputs."""
    if path.is_symlink() or not path.is_file():
        raise ValueError("Unsafe or missing archived file")
    size = path.stat().st_size
    if not 0 < size <= max_bytes:
        raise ValueError("Archived file size outside limits")


def deliver_archived(
    settings: Settings,
    *,
    target_date: date,
    channel: str,
    request_id: str,
    acknowledge_possible_duplicate: bool = False,
    print_profile: str = "a4-home",
) -> ArchiveDeliveryOutcome:
    """One explicit delivery attempt per operator-supplied request ID.

    Does not import, regenerate, or rewrite a publication. In ambiguous CUPS/SMTP
    failures the receipt blocks the same request ID; a new request ID requires
    another deliberate operator decision after inspecting the external queue.
    """
    edition_id = f"{target_date:%Y%m%d}-001"
    if channel not in {"print", "email"}:
        raise ValueError("Channel must be 'print' or 'email'.")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", request_id):
        raise ValueError("Request ID must be 1-64 letters/digits/_/- without paths.")
    if print_profile not in {"a4-home", "a3-folded"}:
        raise ValueError("Unknown print profile.")
    if not acknowledge_possible_duplicate:
        return ArchiveDeliveryOutcome(
            edition_id, channel, request_id, "blocked", "operator_acknowledgement_required"
        )

    archive = settings.archive_dir / edition_id
    receipt = archive / f"manual-{channel}-{request_id}.json"
    # Check duplicates before doing any work or reading personal edition contents.
    if receipt.exists():
        return ArchiveDeliveryOutcome(
            edition_id, channel, request_id, "already_attempted", "duplicate_request_id"
        )

    try:
        if settings.archive_dir.is_symlink() or archive.is_symlink() or not archive.is_dir():
            raise ValueError("Unsafe archived edition directory")
        metadata_path = archive / "metadata.json"
        _require_archived_regular_file(metadata_path, max_bytes=2 * 1024 * 1024)
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if not isinstance(metadata, dict):
            raise ValueError("Invalid publication metadata.")
        if metadata.get("edition_id") != edition_id or metadata.get("target_date") != (
            target_date.isoformat()
        ):
            raise ValueError("Edition identity mismatch.")
        if metadata.get("schema_version") != 2:
            raise ValueError("Unsupported archived edition schema.")
        pages = metadata.get("pages", [])
        if not isinstance(pages, list) or [p.get("number") for p in pages] != [1, 2, 3, 4]:
            raise ValueError("Archive is not the expected four-page publication.")
        pdf = archive / "edition.pdf"
        _require_archived_regular_file(pdf, max_bytes=30 * 1024 * 1024)
        validation = validate_pdf(pdf)
        if not validation.ok:
            raise ValueError("Canonical archived PDF failed four-page validation.")
        html = archive / "edition.html"
        if channel == "email":
            _require_archived_regular_file(html, max_bytes=5 * 1024 * 1024)
        if channel == "email" and not settings.email_configured:
            return ArchiveDeliveryOutcome(
                edition_id, channel, request_id, "blocked", "email_not_configured"
            )
        if channel == "print" and print_profile == "a3-folded":
            pdf = archive / "edition.a3-folded.pdf"
            _require_archived_regular_file(pdf, max_bytes=30 * 1024 * 1024)
            if validate_a3_booklet(pdf):
                raise ValueError("Archived A3 booklet failed validation.")
        pdf_hash = sha256(pdf.read_bytes()).hexdigest()
    except Exception as exc:
        # PDF parsers may raise custom exceptions; always fail closed and redact.
        # Never expose paths, URLs, document contents or provider exception text.
        return ArchiveDeliveryOutcome(
            edition_id, channel, request_id, "blocked",
            f"archive_preflight_{type(exc).__name__}",
        )

    receipt_content = {
        "schema_version": 1,
        "edition_id": edition_id,
        "channel": channel,
        "request_id": request_id,
        "print_profile": print_profile if channel == "print" else None,
        "pdf_sha256": pdf_hash,
        "status": "submission_unknown",
    }
    try:
        # Atomic exclusive ownership across concurrent CLI invocations.
        fd = os.open(receipt, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(receipt_content, stream, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError:
        return ArchiveDeliveryOutcome(
            edition_id, channel, request_id, "already_attempted", "duplicate_request_id"
        )

    try:
        if channel == "print":
            result = print_pdf(
                pdf, settings.printer, execute=True,
                media="A3" if print_profile == "a3-folded" else "A4",
                duplex_edge="short" if print_profile == "a3-folded" else "long",
                require_duplex=print_profile == "a3-folded",
            )
            accepted = result.success
        else:
            # SMTP uses the archived HTML/PDF; only the identity fields are needed
            # in the envelope, never new editorial or source retrieval.
            publication = Publication(
                edition_id=edition_id,
                target_date=target_date.isoformat(),
                timezone=str(metadata.get("timezone", settings.timezone)),
                generated_at=str(metadata.get("generated_at", "")),
                location_name=str(metadata.get("location_name", "")),
                practical=[], stories=[],
            )
            result = send_email_edition(
                publication,
                host=settings.smtp_host, port=settings.smtp_port,
                username=settings.smtp_username, password=settings.smtp_password,
                sender=settings.smtp_from, recipient=settings.email_to,
                starttls=settings.smtp_starttls,
                html_path=html, pdf_path=pdf,
            )
            accepted = result.status == "sent"
        status = "submitted" if accepted else "needs_review"
        receipt_content["status"] = status
        receipt_content["failure_code"] = None if accepted else f"{channel}_submission_failed"
        _save_receipt(receipt, receipt_content)
        return ArchiveDeliveryOutcome(
            edition_id, channel, request_id, status,
            None if accepted else f"{channel}_submission_failed",
        )
    except Exception as exc:
        receipt_content["status"] = "needs_review"
        receipt_content["failure_code"] = f"unexpected_{type(exc).__name__}"
        _save_receipt(receipt, receipt_content)
        return ArchiveDeliveryOutcome(
            edition_id, channel, request_id, "needs_review",
            f"unexpected_{type(exc).__name__}",
        )
