from kushluk.config import Settings
from kushluk import doctor
from kushluk.doctor import core_ready, run_doctor


def test_doctor_core_is_ready_with_fixture(tmp_path):
    fixture = tmp_path / "calendar.json"
    fixture.write_text('{"events": []}', encoding="utf-8")
    settings = Settings(
        output_dir=tmp_path / "output",
        archive_dir=tmp_path / "archive",
        calendar_fixture=fixture,
    )
    checks = run_doctor(settings)
    assert core_ready(checks)
    names = {check.name for check in checks}
    assert {"python", "output", "archive", "calendar", "pdf", "printer", "email"} <= names


def test_doctor_detects_unloadable_native_pdf_libraries(monkeypatch):
    monkeypatch.setattr(doctor.importlib.util, "find_spec", lambda name: object())

    def fake_import(name):
        if name == "weasyprint":
            raise OSError("cannot load library 'pango'")
        return object()

    monkeypatch.setattr(doctor.importlib, "import_module", fake_import)
    check = doctor._pdf_check()
    assert check.name == "pdf"
    assert check.status == "optional"
    assert "Pango" in check.detail
    assert "unusable" in check.detail
