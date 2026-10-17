from __future__ import annotations

import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path

from kushluk.models import DeliveryResult, Publication


def build_email_message(
    publication: Publication,
    *,
    sender: str,
    recipient: str,
    html_path: Path,
    pdf_path: Path | None = None,
) -> EmailMessage:
    message = EmailMessage()
    message["Subject"] = f"Kushluk · {publication.target_date} · {publication.edition_id}"
    message["From"] = sender
    message["To"] = recipient
    message.set_content(
        f"Kushluk {publication.target_date}\n"
        f"Edition {publication.edition_id}\n\n"
        "This edition is attached/rendered as HTML."
    )
    message.add_alternative(html_path.read_text(encoding="utf-8"), subtype="html")
    if pdf_path and pdf_path.exists():
        message.add_attachment(
            pdf_path.read_bytes(),
            maintype="application",
            subtype="pdf",
            filename=f"kushluk-{publication.edition_id}.pdf",
        )
    return message


def send_email_edition(
    publication: Publication,
    *,
    host: str | None,
    port: int,
    username: str | None,
    password: str | None,
    sender: str | None,
    recipient: str | None,
    starttls: bool,
    html_path: Path,
    pdf_path: Path | None = None,
) -> DeliveryResult:
    if not host or not sender or not recipient:
        return DeliveryResult(
            channel="email",
            status="failed",
            detail="Email delivery is not configured (host/from/to are required).",
        )

    message = build_email_message(
        publication,
        sender=sender,
        recipient=recipient,
        html_path=html_path,
        pdf_path=pdf_path,
    )
    try:
        with smtplib.SMTP(host, port, timeout=15) as smtp:
            smtp.ehlo()
            if starttls:
                smtp.starttls(context=ssl.create_default_context())
                smtp.ehlo()
            if username:
                smtp.login(username, password or "")
            smtp.send_message(message)
    except (OSError, smtplib.SMTPException) as exc:
        return DeliveryResult(
            channel="email",
            status="failed",
            detail=f"Email delivery failed ({type(exc).__name__}); check local SMTP configuration.",
        )
    return DeliveryResult(channel="email", status="sent", detail="Edition submitted to the configured email recipient.");
