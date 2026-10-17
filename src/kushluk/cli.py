from __future__ import annotations

import argparse
from datetime import date, datetime, time
import json
import re
from pathlib import Path
from zoneinfo import ZoneInfo

from kushluk.archive import list_editions
from kushluk.archive_compat import ArchiveCompatError, inspect_archive_root
from kushluk.config import Settings
from kushluk.doctor import core_ready, run_doctor
from kushluk.epub import EpubError, export_archived_epub
from kushluk.field_proof import FieldProofError, record_field_proof
from kushluk.host_trial_review import HostTrialReviewError, review_host_trial
from kushluk.local_profile import LocalProfileError, profile_path, write_local_profile
from kushluk.newsletter_discovery import NewsletterError, discover, save_proposals, set_mode
from kushluk.connectors.google_local import (
    GoogleProviderError, authorize, disconnect, discover_gmail, fetch_google_tasks,
)
from kushluk.claims import ClaimCheckError, check_crossref_claim
from kushluk.media import (
    MediaError, assign_media, import_local_media, read_asset, remove_local_media,
)
from kushluk.pipeline import run_pipeline
from kushluk.operations import OperationError, operate_file
from kushluk.opml import (
    OPMLImportError, read_opml, read_proposal, render_opml,
    write_private_file, write_proposal,
)
from kushluk.print_proof import make_print_proof
from kushluk.preview import PreviewError, make_preview
from kushluk.print_inspection import PrintInspectionError, inspect_print_pdf
from kushluk.recovery import deliver_archived
from kushluk.run_metrics import run_report, timing_plan
from kushluk.incident import build_incident_report, save_private_incident_report
from kushluk.local_notifications import notify_local
from kushluk.scheduled import pause_day, read_run_status, resume_day, run_once
from kushluk.schedule_templates import ScheduleTemplateError, export_templates
from kushluk.setup_web import run_setup_web
from kushluk.source_preflight import (
    SourcePreflightError, check_sources, save_private_preflight,
)
from kushluk.source_registry import (
    SourceApprovalError, approve_source, read_registry, revoke_source, set_source_mode,
)


def _clock_time(value: str) -> time:
    if not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", value):
        raise argparse.ArgumentTypeError("Expected a local clock time HH:MM")
    return time.fromisoformat(value)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="kushluk")
    sub = parser.add_subparsers(dest="command", required=True)

    preview = sub.add_parser(
        "preview", help="Create a fixed synthetic four-page edition; no sources or delivery"
    )
    preview.add_argument("--output-dir", type=Path, required=True)
    preview.add_argument(
        "--pdf", action="store_true",
        help="Validate four-page A4 PDF (requires optional PDF dependencies)",
    )

    generate = sub.add_parser("generate", help="Generate one Kushluk edition")
    generate.add_argument("--date", dest="target_date", help="YYYY-MM-DD; defaults to today")
    generate.add_argument("--no-pdf", action="store_true", help="Skip PDF rendering")
    generate.add_argument(
        "--print-profile",
        choices=("a4-home", "letter-home", "a3-folded"),
        default=None,
        help="Default to saved home A4/Letter preference, or override explicitly",
    )
    generate.add_argument(
        "--print",
        dest="send_to_printer",
        action="store_true",
        help="Submit a validated PDF to CUPS",
    )
    generate.add_argument(
        "--email",
        dest="send_email",
        action="store_true",
        help="Send the generated edition using configured SMTP delivery",
    )
    generate.add_argument(
        "--email-on-print-failure",
        action="store_true",
        help="Send email only if requested printing fails",
    )

    media_import = sub.add_parser(
        "media-import", help="Explicitly approve and import one LOCAL raster; never fetch URLs"
    )
    media_import.add_argument("--file", type=Path, required=True)
    media_import.add_argument("--store", type=Path, required=True)
    media_import.add_argument("--license-id", required=True)
    media_import.add_argument("--credit", required=True)
    media_import.add_argument("--alt", required=True)
    media_import.add_argument("--caption", default="")
    media_import.add_argument("--source-url")
    media_import.add_argument("--scope", choices=("private_print", "shareable"), required=True)
    media_import.add_argument("--approve-print", action="store_true", default=False)
    media_import.add_argument("--focal-x", type=float, default=0.5)
    media_import.add_argument("--focal-y", type=float, default=0.5)
    media_import.add_argument("--crop-policy", choices=("focal-crop", "contain"),
                              default="focal-crop")

    media_info = sub.add_parser("media-info", help="Inspect one owner-approved local image")
    media_info.add_argument("--store", type=Path, required=True)
    media_info.add_argument("--asset-id", required=True)

    media_assign = sub.add_parser(
        "media-assign", help="Explicitly pin one approved local image to one story ID"
    )
    media_assign.add_argument("--store", type=Path, required=True)
    media_assign.add_argument("--asset-id", required=True)
    media_assign.add_argument("--story-id", required=True)

    media_remove = sub.add_parser(
        "media-remove", help="Revoke local source approval (archives remain separately owned)"
    )
    media_remove.add_argument("--store", type=Path, required=True)
    media_remove.add_argument("--asset-id", required=True)

    check = sub.add_parser(
        "crossref-check",
        help="Verify ONLY DOI bibliographic title/year; not article findings",
    )
    check.add_argument("--doi", required=True)
    check.add_argument("--title", required=True)
    check.add_argument("--year", type=int)

    google_connect = sub.add_parser(
        "google-connect",
        help="Interactive local OAuth for one Google provider (never shares grants)",
    )
    google_connect.add_argument("--provider", choices=("gmail", "tasks"), required=True)
    google_connect.add_argument("--oauth-client", type=Path, required=True)
    google_connect.add_argument("--vault", type=Path, required=True)

    google_disconnect = sub.add_parser(
        "google-disconnect",
        help="Remove one local Google grant (also revoke remotely in Google Account)",
    )
    google_disconnect.add_argument("--provider", choices=("gmail", "tasks"), required=True)
    google_disconnect.add_argument("--vault", type=Path, required=True)

    gmail_review = sub.add_parser(
        "gmail-discover",
        help="Consent-gated bounded Gmail header metadata review; no bodies or ingestion",
    )
    gmail_review.add_argument("--vault", type=Path, required=True)
    gmail_review.add_argument("--output", type=Path, required=True)
    gmail_review.add_argument("--days", type=int, default=30)
    gmail_review.add_argument("--acknowledge-metadata-read", action="store_true")

    tasks_preview = sub.add_parser(
        "google-tasks-preview",
        help="Count read-only tasks due or overdue; no content output or mutation",
    )
    tasks_preview.add_argument("--vault", type=Path, required=True)
    tasks_preview.add_argument("--date", required=True, help="YYYY-MM-DD")

    discover_mail = sub.add_parser(
        "newsletter-discover",
        help="Review bounded local header export; no mailbox access or source activation",
    )
    discover_mail.add_argument("--snapshot", type=Path, required=True)
    discover_mail.add_argument("--output", type=Path, required=True)
    discover_mail.add_argument("--days", type=int, default=30)

    mail_mode = sub.add_parser(
        "newsletter-set-mode",
        help="Store explicit newsletter rights intent; all ingestion modes remain disabled",
    )
    mail_mode.add_argument("--proposal", type=Path, required=True)
    mail_mode.add_argument("--id", required=True)
    mail_mode.add_argument(
        "--mode", required=True,
        choices=("ignore", "reference-only", "derivative", "private-direct"),
    )
    mail_mode.add_argument("--acknowledge", action="store_true")

    run = sub.add_parser("run", help="Idempotent local scheduled edition run (at most once)")
    run.add_argument("--date", dest="target_date", help="YYYY-MM-DD; defaults to today locally")
    run.add_argument("--print", dest="send_to_printer", action="store_true")
    run.add_argument("--email", dest="send_email", action="store_true")
    run.add_argument("--email-on-print-failure", action="store_true")
    run.add_argument("--notify-local", action="store_true",
                     help="Explicitly submit failure notice to current desktop session")
    run.add_argument(
        "--print-profile", choices=("a4-home", "letter-home", "a3-folded"),
        default=None, help="Default to saved home A4/Letter preference",
    )

    run.add_argument(
        "--latest-start", metavar="HH:MM", type=_clock_time,
        help="Last permitted local START, not a promise of completed printing",
    )
    run.add_argument(
        "--ready-by", metavar="HH:MM", type=_clock_time,
        help="Optional clock target for measuring PDF archive readiness, not physical print",
    )
    run.add_argument(
        "--expected-start", metavar="HH:MM", type=_clock_time,
        help="Expected OS timer trigger to measure wake/launch delay; not an SLA",
    )

    for command, help_text in (
        ("pause-day", "Pause future run starts for one local edition date"),
        ("resume-day", "Resume future run starts; never starts or reprints by itself"),
    ):
        control = sub.add_parser(command, help=help_text)
        control.add_argument("--date", dest="target_date",
                             help="YYYY-MM-DD; defaults to today in local timezone")

    operation = sub.add_parser(
        "operate", help="Invoke stable local JSON operations schema v1 (no remote service)"
    )
    operation.add_argument("--request", type=Path, required=True,
                           help="Local JSON request file, <= 4 KiB; use mode 0600")

    export = sub.add_parser(
        "schedule-export",
        help="Write disabled systemd/launchd units; never install/enable services",
    )
    export.add_argument("--platform", choices=("systemd", "launchd"), required=True)
    export.add_argument("--executable", type=Path, required=True,
                        help="Absolute path to installed Kushluk executable")
    export.add_argument("--working-dir", type=Path, required=True,
                        help="Absolute existing location for local settings and archives")
    export.add_argument("--output-dir", type=Path, required=True,
                        help="New/empty directory for reviewable templates")
    export.add_argument("--start", type=_clock_time, default=time(7, 30),
                        help="OS local scheduler clock, HH:MM (default 07:30)")
    export.add_argument("--latest-start", type=_clock_time, default=time(7, 45),
                        help="Last allowed local start, HH:MM (default 07:45)")

    report = sub.add_parser(
        "run-report", help="Read typed, privacy-safe run timing and submission status"
    )
    report.add_argument("--date", dest="target_date", help="YYYY-MM-DD, local today by default")

    incident = sub.add_parser(
        "incident-report", help="Local typed failure report; no remote escalation or retry"
    )
    incident.add_argument("--date", dest="target_date", help="YYYY-MM-DD, local today by default")
    incident.add_argument("--output", type=Path, help="Create private report file; never overwrite")

    local_notice = sub.add_parser(
        "notify-local", help="Preview or explicitly send one local desktop failure alert"
    )
    local_notice.add_argument("--date", dest="target_date",
                              help="YYYY-MM-DD, local today by default")
    local_notice.add_argument("--send", action="store_true",
                              help="Explicit OS notification; absent means read-only preview")

    plan = sub.add_parser(
        "timing-plan", help="Recommend a start clock from measured validated-archive latency"
    )
    plan.add_argument("--date", dest="target_date", help="Future local date, today by default")
    plan.add_argument("--ready-by", type=_clock_time, default=time(8, 0))
    plan.add_argument("--margin-minutes", type=int, default=10)
    plan.add_argument("--history-days", type=int, default=30)

    run_status = sub.add_parser("run-status", help="Read durable local edition run state")
    run_status.add_argument("--date", dest="target_date", help="YYYY-MM-DD")

    deliver = sub.add_parser(
        "deliver-archived", help="Explicit print/email resend from archive (never regenerate)"
    )
    deliver.add_argument("--date", dest="target_date", required=True, help="YYYY-MM-DD")
    deliver.add_argument("--channel", choices=("print", "email"), required=True)
    deliver.add_argument(
        "--request-id", required=True,
        help="Operator-chosen identifier, stable across repeated invocations",
    )
    deliver.add_argument(
        "--acknowledge-possible-duplicate", action="store_true",
        help="I inspected prior delivery status and accept the risk of another submission",
    )
    deliver.add_argument(
        "--print-profile", choices=("a4-home", "letter-home", "a3-folded"),
        default="a4-home", help="Explicit archived print format; no surprise conversion",
    )

    proof = sub.add_parser(
        "print-proof", help="Generate offline A4, Letter and A3 sample PDFs (never prints)"
    )
    proof.add_argument(
        "--output-dir", type=Path, default=Path("output/print-proof"),
        help="Where synthetic print-verification files are written",
    )

    sources_import = sub.add_parser(
        "sources-import-opml", help="Offline OPML preview/proposal, never activates feeds"
    )
    sources_import.add_argument("file", type=Path, help="Existing local .opml file")
    sources_import.add_argument(
        "--output", type=Path, help="Create private proposed-only JSON, never overwrite"
    )
    sources_export = sub.add_parser(
        "sources-export-opml", help="Export an unactivated JSON source proposal as OPML"
    )
    sources_export.add_argument("file", type=Path, help="Existing proposed-only JSON file")
    sources_export.add_argument("--output", type=Path, required=True)

    approval = sub.add_parser(
        "sources-approve", help="Approve one disabled OPML proposal feed for reference-only use"
    )
    approval.add_argument("proposal", type=Path)
    approval.add_argument("--index", type=int, required=True, help="1-based feed position")
    approval.add_argument("--acknowledge-feed-access", action="store_true",
                          help="I have permission to retrieve this specific feed")
    approval.add_argument("--registry", type=Path, help="Private local source registry path")

    revoke = sub.add_parser("sources-revoke", help="Disable a previously approved feed")
    revoke.add_argument("--id", dest="source_id", required=True)
    revoke.add_argument("--registry", type=Path)

    mode = sub.add_parser("sources-set-mode", help="Record a feed's rights mode (unsupported modes disabled)")
    mode.add_argument("--id", dest="source_id", required=True)
    mode.add_argument("--mode", required=True,
                      choices=("ignore", "reference-only", "derivative", "private-direct"))
    mode.add_argument("--acknowledge-rights-boundary", action="store_true")
    mode.add_argument("--registry", type=Path)

    preflight = sub.add_parser(
        "sources-preflight", help="Offline approved-source inventory; network is opt-in"
    )
    preflight.add_argument("--registry", type=Path)
    preflight.add_argument("--network", action="store_true",
                           help="Explicitly contact up to five approved RSS feeds")
    preflight.add_argument("--limit", type=int, default=5,
                           help="Maximum approved feeds to contact (1–10)")
    preflight.add_argument("--output", type=Path,
                           help="New private diagnostic JSON file; never overwrite")

    listed = sub.add_parser("sources-list", help="Show approved RSS source IDs, no URLs")
    listed.add_argument("--registry", type=Path)

    epub = sub.add_parser("export-epub", help="Offline EPUB3 export of an archived edition")
    epub.add_argument("--date", dest="target_date", required=True, help="YYYY-MM-DD")
    epub.add_argument("--language", default="und",
                      help="Edition language tag (e.g. en, de, tr, de-DE); und if unknown")
    epub.add_argument("--output", type=Path,
                      help="New private EPUB path (default: edition.epub in archive)")

    inspection = sub.add_parser(
        "inspect-print", help="Offline structural/text geometry proof and optional page PNGs"
    )
    inspection.add_argument("--pdf", type=Path, required=True)
    inspection.add_argument("--output-dir", type=Path, required=True)
    inspection.add_argument("--profile", choices=("a4-home", "letter-home", "a3-folded"),
                            default="a4-home")
    inspection.add_argument("--rasterize", action="store_true")
    inspection.add_argument("--dpi", type=int, default=100)

    host_review = sub.add_parser(
        "host-trial-review",
        help="Read-only five-day host trial evidence cross-check; never approves hardware",
    )
    host_review.add_argument("--start-date", required=True, help="First local YYYY-MM-DD date")
    host_review.add_argument("--days", type=int, default=5, help="Consecutive days (5–14)")
    host_review.add_argument("--receipts-dir", type=Path, required=True)
    host_review.add_argument("--archive-root", type=Path,
                             help="Private archive root; defaults to configured local archive")

    field = sub.add_parser(
        "record-field-proof", help="Record self-attested physical printer, reader or host trial"
    )
    field.add_argument("--kind", choices=("paper-a4", "paper-letter", "paper-a3",
                                 "epub-reader", "host-resume"),
                       required=True)
    field.add_argument("--artifact", type=Path, required=True)
    field.add_argument("--output", type=Path, required=True, help="New private receipt filename")
    field.add_argument("--device", required=True, help="Observed hardware/host model")
    field.add_argument("--operator", required=True, help="Human observer identifier")
    field.add_argument("--observations", required=True, help="Actual measured observations")
    field.add_argument("--result", choices=("pass", "fail", "blocked"), required=True)
    field.add_argument("--evidence", action="append", type=Path, default=[])
    field.add_argument("--inspection", type=Path, help="Matching inspect-print JSON for paper")
    field.add_argument("--acknowledge-direct-observation", action="store_true")

    setup = sub.add_parser(
        "setup", help="Create a private offline home profile without storing credentials"
    )
    setup.add_argument("--home-name", help="Local display label, e.g. My Home")
    setup.add_argument("--latitude", type=float, help="Latitude for local weather")
    setup.add_argument("--longitude", type=float, help="Longitude for local weather")
    setup.add_argument("--timezone", help="IANA timezone, e.g. Europe/Berlin")
    setup.add_argument("--printer", help="Optional CUPS printer queue name")
    setup.add_argument("--paper-size", choices=("a4", "letter"), default="a4",
                       help="Home paper preference (DIN A4 or US Letter; default A4)")
    setup.add_argument("--output", type=Path, help="New private profile path")
    setup.add_argument(
        "--non-interactive", action="store_true",
        help="Fail if any required value is missing instead of prompting",
    )

    web_setup = sub.add_parser(
        "setup-web", help="Local-only browser setup; no server outside 127.0.0.1"
    )
    web_setup.add_argument("--no-open", action="store_true",
                           help="Print local URL instead of opening the browser")
    web_setup.add_argument("--output", type=Path,
                           help="New private profile path, never overwrite")

    archive_check = sub.add_parser(
        "archive-check",
        help="Read-only v1/v2 archive metadata compatibility counts; never migrate",
    )
    archive_check.add_argument("--archive-root", type=Path, required=True)
    archive_check.add_argument("--limit", type=int, default=100)

    archive = sub.add_parser("archive-list", help="List recent local Kushluk editions")
    archive.add_argument("--limit", type=int, default=20)

    sub.add_parser("doctor", help="Check local Kushluk runtime readiness")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "archive-check":
        try:
            result = inspect_archive_root(args.archive_root, limit=args.limit)
        except (ArchiveCompatError, OSError) as exc:
            reason = str(exc) if isinstance(exc, ArchiveCompatError) else "archive_check_failed"
            print(json.dumps({"status": "rejected", "error": reason}))
            return 2
        print(json.dumps(result, sort_keys=True))
        return 0 if not result["truncated"] else 1

    if args.command == "preview":
        try:
            manifest = make_preview(args.output_dir, pdf=args.pdf)
        except (PreviewError, OSError) as exc:
            reason = str(exc) if isinstance(exc, PreviewError) else "preview_write_failed"
            print(json.dumps({"status": "rejected", "error": reason}))
            return 2
        print(json.dumps({
            "status": "synthetic_preview_created",
            "logical_pages": 4,
            "pdf_validated": manifest["pdf_validated"],
            "synthetic_only": True,
            "physical_verified": False,
            "network_requests": 0, "delivery_submissions": 0,
        }))
        return 0

    if args.command == "setup-web":
        run_setup_web(path=args.output, open_browser=not args.no_open)
        return 0

    if args.command == "setup":
        def supply(value, prompt):
            if value is not None:
                return value
            if args.non_interactive:
                raise LocalProfileError("Missing required setup value")
            try:
                return input(prompt).strip()
            except EOFError as exc:
                raise LocalProfileError("Interactive input unavailable") from exc

        try:
            name = supply(args.home_name, "Home label: ")
            latitude = float(supply(args.latitude, "Latitude: "))
            longitude = float(supply(args.longitude, "Longitude: "))
            zone = supply(args.timezone, "IANA timezone (e.g. Europe/Berlin): ")
            target = args.output or profile_path()
            write_local_profile(
                target, home_name=name, latitude=latitude,
                longitude=longitude, timezone=zone,
                printer=args.printer, paper_size=args.paper_size,
            )
        except (LocalProfileError, ValueError) as exc:
            reason = str(exc) if isinstance(exc, LocalProfileError) else "Invalid coordinates"
            print(json.dumps({"status": "rejected", "error": reason}))
            return 2
        print(json.dumps({
            "status": "local_profile_created",
            "output": str(target),
            "contains_credentials": False,
            "contacts_network": False,
            "source_permissions_modified": False,
        }))
        return 0

    if args.command == "crossref-check":
        try:
            result = check_crossref_claim(
                args.doi, asserted_title=args.title, asserted_year=args.year,
            )
        except ClaimCheckError as exc:
            print(json.dumps({"status": "rejected", "error": str(exc)}))
            return 2
        print(json.dumps(result.as_dict()))
        return 0 if result.state == "bibliographic-match-claims-unverified" else 1

    if args.command in ("google-connect", "google-disconnect", "gmail-discover", "google-tasks-preview"):
        try:
            if args.command == "google-connect":
                authorize(args.provider, oauth_client=args.oauth_client, vault=args.vault)
                result = {"status": "local_oauth_grant_created",
                          "provider": args.provider, "separate_scopes": True}
            elif args.command == "google-disconnect":
                disconnect(args.provider, vault=args.vault)
                result = {
                    "status": "local_google_token_deleted",
                    "provider": args.provider, "remote_grant_revoked": False,
                }
            elif args.command == "gmail-discover":
                if not args.acknowledge_metadata_read:
                    raise GoogleProviderError("explicit_gmail_metadata_consent_required")
                result = discover_gmail(args.vault, days=args.days)
                save_proposals(args.output, result["sources"])
                result = {
                    "status": "review_only", "candidates": len(result["sources"]),
                    "scanned_messages": result["scanned_messages"],
                    "partial_scan": result["partial_scan"], "ingestion_enabled": False,
                }
            else:
                items = fetch_google_tasks(args.vault, target_date=date.fromisoformat(args.date))
                result = {"status": "read_only", "eligible_task_count": len(items),
                          "mutations": False, "titles_exposed": False}
        except (GoogleProviderError, NewsletterError, OSError, ValueError) as exc:
            msg = str(exc) if isinstance(exc, (GoogleProviderError, NewsletterError)) else "provider_operation_failed"
            print(json.dumps({"status": "rejected", "error": msg}))
            return 2
        print(json.dumps(result))
        return 0

    if args.command in ("newsletter-discover", "newsletter-set-mode"):
        try:
            if args.command == "newsletter-discover":
                entries = discover(args.snapshot, days=args.days)
                save_proposals(args.output, entries)
                result = {
                    "status": "review_only", "candidates": len(entries),
                    "ingestion_enabled": False, "private_proposal": True,
                }
            else:
                result = set_mode(
                    args.proposal, newsletter_id=args.id, mode=args.mode,
                    acknowledge=args.acknowledge,
                )
        except (NewsletterError, OSError, ValueError) as exc:
            print(json.dumps({
                "status": "rejected",
                "error": str(exc) if isinstance(exc, NewsletterError) else "newsletter_operation_failed",
            }))
            return 2
        print(json.dumps(result))
        return 0

    if args.command in ("media-assign", "media-remove"):
        try:
            if args.command == "media-assign":
                assign_media(args.store, story_id=args.story_id, asset_id=args.asset_id)
                status = "approved_local_assignment"
            else:
                remove_local_media(args.store, args.asset_id)
                status = "revoked_from_local_store"
        except (MediaError, OSError, ValueError) as exc:
            print(json.dumps({"status": "rejected", "error": (
                str(exc) if isinstance(exc, MediaError) else "media_operation_failed"
            )}))
            return 2
        print(json.dumps({"status": status, "asset_id": args.asset_id,
                          "existing_archives_unchanged": True}))
        return 0

    if args.command in ("media-import", "media-info"):
        try:
            if args.command == "media-import":
                result = import_local_media(
                    args.file, args.store, license_id=args.license_id,
                    attribution=args.credit, alt_text=args.alt,
                    caption=args.caption, permission_scope=args.scope,
                    approved_for_print=args.approve_print,
                    source_url=args.source_url, focal_x=args.focal_x,
                    focal_y=args.focal_y, crop_policy=args.crop_policy,
                )
            else:
                result, _ = read_asset(args.store, args.asset_id)
        except (MediaError, OSError, ValueError) as exc:
            print(json.dumps({"status": "rejected", "error": (
                str(exc) if isinstance(exc, MediaError) else "media_operation_failed"
            )}))
            return 2
        print(json.dumps({
            "status": "approved_local_media", "asset_id": result.asset_id,
            "license_id": result.license_id, "scope": result.permission_scope,
            "width_px": result.width_px, "height_px": result.height_px,
        }))
        return 0

    settings = Settings.from_env()

    if args.command == "schedule-export":
        try:
            produced = export_templates(
                platform=args.platform, executable=args.executable,
                working_dir=args.working_dir, output_dir=args.output_dir,
                start=args.start.strftime("%H:%M"),
                latest_start=args.latest_start.strftime("%H:%M"),
            )
        except ScheduleTemplateError as exc:
            print(json.dumps({"status": "rejected", "error": str(exc)}))
            return 2
        print(json.dumps({"status": "templates_created_not_installed",
                          "files": produced, "schedule_enabled": False,
                          "printing_enabled": False, "host_verified": False}))
        return 0

    if args.command == "operate":
        try:
            outcome = operate_file(settings, args.request)
        except OperationError as exc:
            print(json.dumps({"schema_version": 1, "status": "rejected",
                              "error": str(exc)}))
            return 2
        print(json.dumps(outcome, ensure_ascii=False))
        return 0 if outcome["status"] in {
            "completed", "already_completed", "not_run", "paused", "already_paused",
            "resumed", "not_paused", "submitted",
        } else 2

    if args.command == "generate":
        if args.no_pdf and args.print_profile == "a3-folded":
            parser.error("A3 folded imposition requires PDF rendering")
        target = date.fromisoformat(args.target_date) if args.target_date else date.today()
        result = run_pipeline(
            settings,
            target_date=target,
            make_pdf=not args.no_pdf,
            send_to_printer=args.send_to_printer,
            send_email=args.send_email,
            email_on_print_failure=args.email_on_print_failure,
            print_profile=args.print_profile,
        )
        print(f"Edition: {result.publication.edition_id}")
        print(f"Markdown: {result.markdown_path}")
        print(f"HTML: {result.html_path}")
        print(f"PDF: {result.pdf_path or 'not rendered'}")
        chosen = args.print_profile or (
            "letter-home" if settings.paper_size == "letter" else "a4-home"
        )
        print(f"Print profile: {chosen}")
        print(f"Printable PDF: {result.printable_pdf_path or 'not rendered'}")
        print(f"Archive: {result.archive_dir}")
        if result.warnings:
            print("Warnings:")
            for warning in result.warnings:
                print(f"- {warning}")
        if result.print_result:
            print(f"Print: {result.print_result.detail}")
        if result.email_result:
            print(f"Email: {result.email_result.detail}")
        failed_delivery = (
            (result.print_result is not None and not result.print_result.success)
            or (result.email_result is not None and result.email_result.status == "failed")
        )
        return 2 if failed_delivery else 0

    if args.command in {"run-report", "timing-plan", "incident-report", "notify-local"}:
        target = (date.fromisoformat(args.target_date) if args.target_date
                  else datetime.now(ZoneInfo(settings.timezone)).date())
        if args.command == "run-report":
            report = run_report(settings, target_date=target)
        elif args.command == "notify-local":
            report = notify_local(settings, target_date=target, send=args.send)
        elif args.command == "incident-report":
            report = build_incident_report(settings, target_date=target)
            if args.output is not None:
                try:
                    save_private_incident_report(args.output, report)
                except (OSError, ValueError):
                    print(json.dumps({"status": "rejected", "error": "incident_export_failed"}))
                    return 2
                print(json.dumps({"status": "private_incident_report_written",
                                  "remote_report_sent": False,
                                  "delivery_attempted": False}))
                return 0
        else:
            try:
                report = timing_plan(
                    settings, target_date=target, ready_by=args.ready_by,
                    margin_minutes=args.margin_minutes, history_days=args.history_days,
                )
            except ValueError:
                print(json.dumps({"status": "rejected", "error": "invalid_timing_options"}))
                return 2
        print(json.dumps(report, ensure_ascii=False))
        return 0

    if args.command in {"run", "run-status", "pause-day", "resume-day"}:
        local_today = datetime.now(ZoneInfo(settings.timezone)).date()
        target = date.fromisoformat(args.target_date) if args.target_date else local_today
        if args.command == "run-status":
            outcome = read_run_status(settings, target_date=target)
        elif args.command == "pause-day":
            outcome = pause_day(settings, target_date=target)
        elif args.command == "resume-day":
            outcome = resume_day(settings, target_date=target)
        else:
            outcome = run_once(
                settings, target_date=target,
                send_to_printer=args.send_to_printer,
                send_email=args.send_email,
                email_on_print_failure=args.email_on_print_failure,
                print_profile=args.print_profile,
                latest_start=args.latest_start,
                ready_by=args.ready_by,
                expected_start=args.expected_start,
            )
        result = outcome.as_dict()
        if args.command == "run" and args.notify_local:
            result["local_notification"] = notify_local(
                settings, target_date=target, send=True,
            )
        print(json.dumps(result, ensure_ascii=False))
        return 0 if outcome.status in {
            "completed", "already_completed", "not_run", "paused",
            "already_paused", "resumed", "not_paused",
        } else 2

    if args.command == "deliver-archived":
        outcome = deliver_archived(
            settings,
            target_date=date.fromisoformat(args.target_date),
            channel=args.channel,
            request_id=args.request_id,
            acknowledge_possible_duplicate=args.acknowledge_possible_duplicate,
            print_profile=args.print_profile,
        )
        print(json.dumps(outcome.as_dict(), ensure_ascii=False))
        return 0 if outcome.status == "submitted" else 2

    if args.command == "print-proof":
        artifacts = make_print_proof(args.output_dir)
        print(json.dumps(artifacts, ensure_ascii=False))
        return 0

    if args.command == "sources-import-opml":
        try:
            feeds = read_opml(args.file)
            if args.output is not None:
                write_proposal(args.output, feeds)
        except OPMLImportError as exc:
            print(json.dumps({"status": "rejected", "error": str(exc)}))
            return 2
        print(json.dumps({
            "status": "proposed-only", "feed_count": len(feeds),
            "activated": 0, "network_requests": 0,
            "output": str(args.output) if args.output else None,
        }, ensure_ascii=False))
        return 0

    if args.command == "sources-export-opml":
        try:
            feeds = read_proposal(args.file)
            write_private_file(args.output, render_opml(feeds))
        except OPMLImportError as exc:
            print(json.dumps({"status": "rejected", "error": str(exc)}))
            return 2
        print(json.dumps({
            "status": "exported", "feed_count": len(feeds),
            "activated": 0, "network_requests": 0,
            "output": str(args.output),
        }, ensure_ascii=False))
        return 0

    if args.command in {"sources-approve", "sources-revoke", "sources-list", "sources-set-mode"}:
        try:
            if args.command == "sources-approve":
                identifier, total, new = approve_source(
                    args.proposal, args.index,
                    acknowledge=args.acknowledge_feed_access, path=args.registry,
                )
                payload = {
                    "status": "approved" if new else "already-approved",
                    "id": identifier, "approved_count": total,
                    "mode": "reference-only", "article_copying_permitted": False,
                }
            elif args.command == "sources-set-mode":
                chosen, enabled = set_source_mode(
                    args.source_id, args.mode, acknowledge=args.acknowledge_rights_boundary,
                    path=args.registry,
                )
                payload = {
                    "status": "active" if enabled else "disabled",
                    "mode": chosen, "enabled": enabled,
                    "body_copying_enabled": False,
                }
            elif args.command == "sources-revoke":
                total, changed = revoke_source(args.source_id, path=args.registry)
                payload = {
                    "status": "revoked" if changed else "not-found",
                    "approved_count": total,
                }
            else:
                rows = read_registry(args.registry)
                payload = {
                    "status": "ok", "approved_count": len(rows),
                    "ids": [row["id"] for row in rows],
                    "sources": [
                        {"id": row["id"], "mode": row["mode"], "enabled": row["enabled"]}
                        for row in rows
                    ],
                }
        except SourceApprovalError as exc:
            print(json.dumps({"status": "rejected", "error": str(exc)}))
            return 2
        print(json.dumps(payload, ensure_ascii=False))
        return 0

    if args.command == "sources-preflight":
        try:
            result = check_sources(
                path=args.registry, network=args.network, limit=args.limit,
            )
            if args.output is not None:
                save_private_preflight(result, args.output)
        except (SourcePreflightError, SourceApprovalError) as exc:
            print(json.dumps({"status": "rejected", "error": str(exc)}))
            return 2
        print(json.dumps(result, ensure_ascii=False))
        return 0 if result["failed_sources"] == 0 else 2

    if args.command == "export-epub":
        try:
            target = date.fromisoformat(args.target_date)
            path = args.output or (
                settings.archive_dir / f"{target:%Y%m%d}-001" / "edition.epub"
            )
            result = export_archived_epub(
                settings.archive_dir, target, path, language=args.language,
            )
        except (EpubError, ValueError) as exc:
            code = str(exc) if isinstance(exc, EpubError) else "invalid_date"
            print(json.dumps({"status": "rejected", "error": code}))
            return 2
        print(json.dumps(result, ensure_ascii=False))
        return 0

    if args.command == "inspect-print":
        try:
            report = inspect_print_pdf(
                args.pdf, args.output_dir, profile=args.profile,
                rasterize=args.rasterize, dpi=args.dpi,
            )
        except PrintInspectionError as exc:
            print(json.dumps({"status": "rejected", "error": str(exc)}))
            return 2
        print(json.dumps({
            "status": report["automated_status"],
            "structural_errors": len(report["structural_errors"]),
            "raster_status": report["raster_status"],
            "human_visual_review_required": True,
            "physical_verified": False,
            "report": str(args.output_dir / "inspection.json"),
        }))
        return 2 if report["structural_errors"] else 0

    if args.command == "host-trial-review":
        try:
            start = date.fromisoformat(args.start_date)
            report = review_host_trial(
                archive_root=args.archive_root or settings.archive_dir,
                receipts_dir=args.receipts_dir, start_date=start, days=args.days,
                timezone=settings.timezone,
            )
        except (HostTrialReviewError, ValueError) as exc:
            code = str(exc) if isinstance(exc, HostTrialReviewError) else "invalid_start_date"
            print(json.dumps({"status": "rejected", "error": code}))
            return 2
        print(json.dumps(report, ensure_ascii=False))
        return 0

    if args.command == "record-field-proof":
        try:
            receipt = record_field_proof(
                kind=args.kind, artifact=args.artifact, output=args.output,
                device=args.device, operator=args.operator, observations=args.observations,
                result=args.result, evidence=args.evidence,
                acknowledge=args.acknowledge_direct_observation,
                inspection=args.inspection,
            )
        except FieldProofError as exc:
            print(json.dumps({"status": "rejected", "error": str(exc)}))
            return 2
        print(json.dumps({
            "status": "operator_report_recorded",
            "kind": receipt["kind"], "reported_result": receipt["operator_reported_result"],
            "independently_verified": False, "release_gate_accepted": False,
            "output": str(args.output),
        }))
        return 0

    if args.command == "archive-list":
        for item in list_editions(settings.archive_dir, limit=max(1, args.limit)):
            print(
                f"{item['edition_id']} · {item.get('target_date') or '?'} · "
                f"{item.get('location_name') or '?'} · {item['path']}"
            )
        return 0

    if args.command == "doctor":
        checks = run_doctor(settings)
        for check in checks:
            print(f"{check.status.upper():8} {check.name:10} {check.detail}")
        return 0 if core_ready(checks) else 2

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
