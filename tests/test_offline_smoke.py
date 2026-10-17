"""Proof that hermetic CLI smoke works with no native PDF libraries."""
from tools.offline_smoke import run


def test_offline_cli_smoke_has_four_pages_without_outbound_io():
    report = run(pdf=False)
    assert report == {
        "status": "synthetic_offline_smoke_passed",
        "canonical_pages": 4,
        "pdf_validated": False,
        "network_or_delivery": False,
        "physical_verified": False,
    }
