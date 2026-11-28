"""Tests for the Firebase Hybrid AI Hackathon surface."""

from __future__ import annotations

import io
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from kinguard import service
from kinguard.docvision import read as docvision_read
from kinguard.tools import onboarding_tools
from kinguard.webauth import DEMO_TOKEN


@pytest.fixture(scope="module")
def client() -> TestClient:
    from kinguard.server import app

    return TestClient(app)


def test_firebase_config_unconfigured_by_default(client: TestClient, monkeypatch) -> None:
    for var in (
        "KINGUARD_FIREBASE_API_KEY",
        "KINGUARD_FIREBASE_PROJECT_ID",
        "KINGUARD_FIREBASE_APP_ID",
        "KINGUARD_FIREBASE_MODEL",
    ):
        monkeypatch.delenv(var, raising=False)

    res = client.get("/api/firebase-config")
    assert res.status_code == 200
    body = res.json()
    assert body["configured"] is False
    assert body["firebase_config"] is None
    assert body["cloud_fallback_model"] == "gemini-3.5-flash-lite"


def test_firebase_config_returns_public_fields_and_never_leaks_secrets(
    client: TestClient, monkeypatch
) -> None:
    monkeypatch.setenv("KINGUARD_FIREBASE_API_KEY", "AIzaSyPublicTestKey")
    monkeypatch.setenv("KINGUARD_FIREBASE_AUTH_DOMAIN", "kinguard-hack.firebaseapp.com")
    monkeypatch.setenv("KINGUARD_FIREBASE_PROJECT_ID", "kinguard-hack")
    monkeypatch.setenv("KINGUARD_FIREBASE_APP_ID", "1:12345:web:abcdef")
    monkeypatch.setenv("KINGUARD_FIREBASE_RECAPTCHA_SITE_KEY", "6LeTestSiteKey")
    monkeypatch.setenv("KINGUARD_FIREBASE_APPCHECK_DEBUG", "true")
    monkeypatch.setenv("KINGUARD_LINK_SECRET", "super-secret-do-not-expose")

    res = client.get("/api/firebase-config")
    assert res.status_code == 200
    body = res.json()
    assert body["configured"] is True
    assert body["firebase_config"]["projectId"] == "kinguard-hack"
    assert body["recaptcha_site_key"] == "6LeTestSiteKey"
    assert body["app_check_debug"] is True
    assert "super-secret-do-not-expose" not in res.text


def test_dashboard_and_handoff_wire_firebase_ai_logic_once(client: TestClient) -> None:
    app_html = client.get("/app").text
    assert app_html.count('src="/hybrid.js"') == 1
    shared = client.get("/hybrid.js")
    assert shared.status_code == 200
    assert 'SDK_VERSION = "13.4.0"' in shared.text
    assert "InferenceMode.PREFER_ON_DEVICE" in shared.text
    assert "ReCaptchaEnterpriseProvider" in shared.text
    assert "initializeDeviceModel" in shared.text
    pid = onboarding_tools.create_parent_profile(
        name="Test Parent", age=72, city="Thoothukudi", lat=8.76, lon=78.14,
        chronic_conditions=["Hypertension"], allergies=[],
    )["profile"]["parent_id"]
    onboarding_tools.record_emergency_disclosure_consent(pid)
    case = service.open_case(pid)

    with patch.dict("os.environ", {"KINGUARD_LINK_SECRET": "test-link-secret-for-handoff"}):
        ro_mint = client.post(
            f"/api/cases/{case.case_id}/handoff-link",
            headers={"Authorization": f"Bearer {DEMO_TOKEN}"},
        )
        assert ro_mint.status_code == 200
        ro_html = client.get(ro_mint.json()["url"]).text
        assert "<script" not in ro_html.lower()

        rw_mint = client.post(
            f"/api/cases/{case.case_id}/handoff-link?allow_notes=true",
            headers={"Authorization": f"Bearer {DEMO_TOKEN}"},
        )
        assert rw_mint.status_code == 200
        handoff_url = rw_mint.json()["url"]
        handoff_html = client.get(handoff_url).text
        assert "KinGuardHybrid.create" in handoff_html
        assert "src=/hybrid.js" in handoff_html
        assert "dxextract" in handoff_html


def test_intake_records_hybrid_normalizer_provenance_without_weakening_red_flags(
    client: TestClient,
) -> None:
    pid = onboarding_tools.create_parent_profile(
        name="Hybrid Triage Test", age=71, city="Thoothukudi", lat=8.76, lon=78.14,
        chronic_conditions=["Hypertension"], allergies=[],
    )["profile"]["parent_id"]

    # Even if client normaliser returns zero terms or claims non-urgency, raw
    # free_text still triggers the deterministic RED_FLAGS escalation floor.
    res = client.post(
        "/api/intake",
        headers={"Authorization": f"Bearer {DEMO_TOKEN}"},
        json={
            "parent_id": pid,
            "symptoms": [],
            "free_text": "amma has chest pain and sweating, says probably gas",
            "reported_by": "family_web_intake",
            "client_normalizer_source": "on_device",
            "client_normalizer_note": "Extracted locally via Gemini Nano",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["severity"] == "HIGH"
    assert body["client_normalizer_source"] == "on_device"

    trail = service.get_chain(body["case_id"]).receipts
    kinds = [r.kind for r in trail]
    assert "triage.decision" in kinds
    assert "intake.hybrid_normalized" in kinds


def test_web_document_ingest_requires_family_session_and_rejects_bad_mime(
    client: TestClient,
) -> None:
    pid = onboarding_tools.create_parent_profile(
        name="Upload Guard Test", age=70, city="Thoothukudi", lat=8.76, lon=78.14,
        chronic_conditions=[], allergies=[],
    )["profile"]["parent_id"]
    case = service.open_case(pid)

    unauth = client.post(
        f"/api/cases/{case.case_id}/documents/ingest",
        files={"file": ("doc.png", io.BytesIO(b"x" * 1000), "image/png")},
    )
    assert unauth.status_code == 401

    bad_mime = client.post(
        f"/api/cases/{case.case_id}/documents/ingest",
        headers={"Authorization": f"Bearer {DEMO_TOKEN}"},
        files={"file": ("evil.txt", io.BytesIO(b"hello" * 300), "text/plain")},
    )
    assert bad_mime.status_code == 400


def test_web_document_ingest_routes_lab_report_cleanly(
    client: TestClient, monkeypatch
) -> None:
    pid = onboarding_tools.create_parent_profile(
        name="Upload Lab Test", age=71, city="Thoothukudi", lat=8.76, lon=78.14,
        chronic_conditions=[], allergies=[],
    )["profile"]["parent_id"]
    case = service.open_case(pid)

    fake_reading = docvision_read.Reading(
        ok=True,
        kind="lab_report",
        engine="gemini",
        confidence=0.98,
        payload={
            "collected_on": "2026-11-20",
            "observations": [
                {"name": "Troponin I", "value": "0.94", "unit": "ng/mL", "flag": "high"}
            ],
        },
    )
    monkeypatch.setattr(docvision_read, "read", lambda data, mime: fake_reading)

    with patch("kinguard.comms.storage.store") as mock_store:
        mock_store.return_value = type(
            "Stored", (), {"stored": True, "object_name": "artifacts/test.png", "detail": "ok"}
        )()
        res = client.post(
            f"/api/cases/{case.case_id}/documents/ingest",
            headers={"Authorization": f"Bearer {DEMO_TOKEN}"},
            files={"file": ("lab.png", io.BytesIO(b"\x89PNG" + b"0" * 1200), "image/png")},
        )

    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ingested"
    assert body["kind"] == "lab_report"
    assert body["observations"] == 1
