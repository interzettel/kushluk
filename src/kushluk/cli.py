from __future__ import annotations

import argparse
from datetime import date

from kushluk.archive import list_editions
from kushluk.config import Settings
from kushluk.doctor import core_ready, run_doctor
from kushluk.pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="kushluk")
    sub = parser.add_subparsers(dest="command", required=True)

    generate = sub.add_parser("generate", help="Generate one Kushluk edition")
    generate.add_argument("--date", dest="target_date", help="YYYY-MM-DD; defaults to today")
    generate.add_argument("--no-pdf", action="store_true", help="Skip PDF rendering")
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

    archive = sub.add_parser("archive-list", help="List recent local Kushluk editions")
    archive.add_argument("--limit", type=int, default=20)

    sub.add_parser("doctor", help="Check local Kushluk runtime readiness")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    settings = Settings.from_env()

    if args.command == "generate":
        target = date.fromisoformat(args.target_date) if args.target_date else date.today()
        result = run_pipeline(
            settings,
            target_date=target,
            make_pdf=not args.no_pdf,
            send_to_printer=args.send_to_printer,
            send_email=args.send_email,
            email_on_print_failure=args.email_on_print_failure,
        )
        print(f"Edition: {result.publication.edition_id}")
        print(f"Markdown: {result.markdown_path}")
        print(f"HTML: {result.html_path}")
        print(f"PDF: {result.pdf_path or 'not rendered'}")
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
