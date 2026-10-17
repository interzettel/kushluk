"""Read-only accessible morning status page, sourced from bounded run receipts."""
from __future__ import annotations

from datetime import date
from html import escape

from kushluk.config import Settings
from kushluk.incident import build_incident_report
from kushluk.run_metrics import run_report

_STATES = {
    "completed": ("Edition prepared", "The local run completed."),
    "needs_review": ("Needs your attention", "A run or delivery needs inspection."),
    "in_progress": ("Run in progress", "Do not start another run."),
    "paused": ("Paused", "No automatic run is expected while paused."),
    "not_run": ("Not started", "No run receipt exists for this date."),
}
_SUBMISSIONS = {
    "submission_accepted": "Submitted to queue; delivery not verified",
    "submission_failed": "Submission failed",
    "submission_uncertain": "Submission uncertain: check external queue",
    "not_requested": "Not requested",
    "not_submitted": "Not submitted",
    "unknown": "Not established",
}
_NOTICES = {
    "manual_review_no_auto_retry": (
        "A previous run may have reached the printer or mail queue. "
        "Inspect that queue before any explicit resend."
    ),
    "delivery_needs_attention": "Inspect external print/mail queues before resending.",
    "archive_ready_late": "Review the local timing history before adjusting a schedule.",
    "no_run_receipt": "Check the local scheduler. Nothing was started by this page.",
    "schedule_paused": "The date is paused. This page will not resume it.",
    "run_in_progress": "Wait for the current run. Do not create another job.",
    "printer_queue_not_physical_proof": "Check actual paper and duplex separately.",
    "smtp_accepted_not_recipient_proof": "Email arrival has not been confirmed.",
    "archive_complete_delivery_not_implied": "The archive is ready, not physically delivered.",
    "status_requires_review": "Inspect the local run; no automatic recovery occurs.",
}


def morning_status(settings: Settings, *, target_date: date) -> dict:
    """Bounded, fixed-shape software observations. Never creates any files."""
    report = run_report(settings, target_date=target_date)
    incident = build_incident_report(settings, target_date=target_date)
    state = report["status"]
    if state not in _STATES:
        state = "needs_review"
    deliv = report["delivery"]
    print_state = deliv.get("print", "unknown")
    email_state = deliv.get("email", "unknown")
    notice_code = incident["error_code"]
    return {
        "date": target_date.isoformat(),
        "state": state,
        "archive_reported_ready": report["timing"]["validated_archived"] is True,
        "print_state": print_state if print_state in _SUBMISSIONS else "unknown",
        "email_state": email_state if email_state in _SUBMISSIONS else "unknown",
        "notice_code": notice_code if notice_code in _NOTICES else "status_requires_review",
        "physical_verified": False,
        "recipient_verified": False,
        "run_triggered_by_page": False,
        "remote_data_sent": False,
    }


def render_morning_status(data: dict) -> str:
    """Strict label lookup: untrusted receipt content never interpolates into HTML."""
    state = data["state"] if data.get("state") in _STATES else "needs_review"
    label, description = _STATES[state]
    print_state = _SUBMISSIONS.get(data.get("print_state"), "Not established")
    email_state = _SUBMISSIONS.get(data.get("email_state"), "Not established")
    code = data.get("notice_code")
    note = _NOTICES.get(code, _NOTICES["status_requires_review"])
    date_text = escape(str(data["date"]), quote=True)
    archive = "Validated A4 archive reported" if data["archive_reported_ready"] else (
        "Validated archive not established"
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Kuşluk — Morning status</title>
<style>
*{{box-sizing:border-box}}
body{{margin:0;background:#f4f1e9;color:#21372e;font:16px/1.6 system-ui,sans-serif}}
main{{max-width:780px;margin:auto;padding:clamp(20px,5vw,64px)}}
header{{border-bottom:2px solid #244936;padding-bottom:20px}}
.eyebrow{{letter-spacing:.16em;font-size:.76rem;text-transform:uppercase;color:#3f6254}}
h1{{font:600 clamp(2rem,5vw,3.5rem)/1.1 Georgia,serif;margin:.35rem 0}}
h2{{font:600 1.35rem/1.3 Georgia,serif}}
p{{max-width:60ch}}
section{{background:#fffdf8;border:1px solid #c9cfc1;padding:18px 22px;margin-top:18px}}
dl{{display:grid;grid-template-columns:minmax(130px,1fr) 2fr;gap:12px 20px}}
dt{{font-weight:650}}dd{{margin:0}}
a{{color:#164936}}a:focus-visible{{outline:3px solid #1c6a4d;outline-offset:3px}}
small{{color:#486358}}.footer{{margin-top:30px}}
@media(max-width:560px){{dl{{display:block}}dt{{margin-top:14px}}dd{{margin-bottom:12px}}}}
</style>
</head>
<body><main id="main">
<header>
<div class="eyebrow">Kuşluk / Local reader-owned edition / {date_text}</div>
<h1>Morning status</h1>
<p>Read-only software evidence from your own computer.</p>
</header>
<section aria-labelledby="edition-state">
<h2 id="edition-state">{escape(label)}</h2>
<p>{escape(description)}</p>
<dl>
<dt>Edition archive</dt><dd>{escape(archive)}</dd>
<dt>Printer</dt><dd>{escape(print_state)}</dd>
<dt>Email</dt><dd>{escape(email_state)}</dd>
</dl>
</section>
<section aria-labelledby="next-action">
<h2 id="next-action">What to do next</h2>
<p>{escape(note)}</p>
</section>
<p class="footer"><strong>Important:</strong> A queued print does not mean physical paper was
printed. An accepted email does not prove arrival. This page never starts a run,
sends a notification, changes printer settings, or transmits private data.</p>
<nav aria-label="Local setup navigation">
<a href="/printer">Printer settings</a> ·
<a href="/sources">Source review</a> ·
<a href="/">Home setup</a>
</nav>
<small>All device and reader acceptance gates remain separate from this view.</small>
</main></body></html>"""
