from __future__ import annotations

import argparse
from datetime import date, datetime
import json
from pathlib import Path
from zoneinfo import ZoneInfo

from kushluk.archive import list_editions
from kushluk.config import Settings
from kushluk.doctor import core_ready, run_doctor
from kushluk.pipeline import run_pipeline
from kushluk.print_proof import make_print_proof
from kushluk.recovery import deliver_archived
from kushluk.scheduled import read_run_status, run_once


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="kushluk")
    sub = parser.add_subparsers(dest="command", required=True)

    generate = sub.add_parser("generate", help="Generate one Kushluk edition")
    generate.add_argument("--date", dest="target_date", help="YYYY-MM-DD; defaults to today")
    generate.add_argument("--no-pdf", action="store_true", help="Skip PDF rendering")
    generate.add_argument(
        "--print-profile",
        choices=("a4-home", "a3-folded"),
        default="a4-home",
        help="Select output sheet geometry (default: a4-home)",
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

    run = sub.add_parser("run", help="Idempotent local scheduled edition run (at most once)")
    run.add_argument("--date", dest="target_date", help="YYYY-MM-DD; defaults to today locally")
    run.add_argument("--print", dest="send_to_printer", action="store_true")
    run.add_argument("--email", dest="send_email", action="store_true")
    run.add_argument("--email-on-print-failure", action="store_true")
    run.add_argument(
        "--print-profile", choices=("a4-home", "a3-folded"), default="a4-home"
    )

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
        "--print-profile", choices=("a4-home", "a3-folded"), default="a4-home"
    )

    proof = sub.add_parser(
        "print-proof", help="Generate offline A4/A3 sample PDFs (never prints)"
    )
    proof.add_argument(
        "--output-dir", type=Path, default=Path("output/print-proof"),
        help="Where synthetic print-verification files are written",
    )

    archive = sub.add_parser("archive-list", help="List recent local Kushluk editions")
    archive.add_argument("--limit", type=int, default=20)

    sub.add_parser("doctor", help="Check local Kushluk runtime readiness")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    settings = Settings.from_env()

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
        print(f"Print profile: {args.print_profile}")
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

    if args.command in {"run", "run-status"}:
        local_today = datetime.now(ZoneInfo(settings.timezone)).date()
        target = date.fromisoformat(args.target_date) if args.target_date else local_today
        if args.command == "run-status":
            outcome = read_run_status(settings, target_date=target)
        else:
            outcome = run_once(
                settings,
                target_date=target,
                send_to_printer=args.send_to_printer,
                send_email=args.send_email,
                email_on_print_failure=args.email_on_print_failure,
                print_profile=args.print_profile,
            )
        print(json.dumps(outcome.as_dict(), ensure_ascii=False))
        return 0 if outcome.status in {"completed", "already_completed", "not_run"} else 2

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
