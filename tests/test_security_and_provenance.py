"""Security, ownership, concurrency, and Hybrid AI surface regression tests."""

from __future__ import annotations

import base64
import importlib.util
import io
import pathlib
import sys
from concurrent.futures import ThreadPoolExecutor

import pytest
from cryptography.hazmat.primitives import serialization
from fastapi.testclient import TestClient

from kinguard import service
from kinguard.provenance.chain import ReceiptChain, verify_chain
from kinguard.provenance.signing import Signer, generate_key_b64
from kinguard.provenance.store import ReceiptConflictError, get_store, receipt_sk, save_receipt
from kinguard.tools import onboarding_tools, provenance_tools, triage_tools
from kinguard.webauth import DEMO_TOKEN


@pytest.fixture(scope="module")
def client() -> TestClient:
    from kinguard.server import app

    return TestClient(app)


def _new_parent(name: str) -> str:
    return onboarding_tools.create_parent_profile(
        name=name,
        age=72,
        city="Thoothukudi",
        lat=8.7642,
        lon=78.1400,
        chronic_conditions=["Hypertension"],
        allergies=[],
    )["profile"]["parent_id"]


def test_cross_patient_intake_onto_existing_case_is_rejected(client: TestClient) -> None:
    parent_a = _new_parent("Parent A")
    parent_b = _new_parent("Parent B")

    opened = triage_tools.run_triage(
        parent_id=parent_a,
        symptoms=["fever"],
        free_text="mild fever",
        reported_by="family",
        lat=0.0,
        lon=0.0,
        case_id="",
    )
    case_a = opened["case_id"]
    before_count = len(service.get_chain(case_a).receipts)

    # Direct tool call with mismatched parent_id and case_id must fail closed.
    direct = triage_tools.run_triage(
        parent_id=parent_b,
        symptoms=["chest pain"],
        free_text="chest pain",
        reported_by="attacker",
        lat=0.0,
        lon=0.0,
        case_id=case_a,
    )
    assert direct["status"] == "error"
    assert direct["status_code"] == 403

    # Unauthenticated HTTP write targeting an existing case must be refused (401).
    unauth = client.post(
        "/api/intake",
        json={
            "parent_id": parent_b,
            "case_id": case_a,
            "symptoms": ["chest pain"],
            "free_text": "cross patient payload",
            "reported_by": "stranger",
        },
    )
    assert unauth.status_code == 401

    # Authenticated caller with mismatched parent_id/case_id must be refused (403).
    authed = client.post(
        "/api/intake",
        headers={"Authorization": f"Bearer {DEMO_TOKEN}"},
        json={
            "parent_id": parent_b,
            "case_id": case_a,
            "symptoms": ["chest pain"],
            "free_text": "cross patient payload",
            "reported_by": "family",
        },
    )
    assert authed.status_code == 403
    assert len(service.get_chain(case_a).receipts) == before_count
    assert service.verify_case(case_a).ok


def test_intake_with_unknown_case_id_returns_404(client: TestClient) -> None:
    parent_a = _new_parent("Parent Unknown Case")
    res = client.post(
        "/api/intake",
        headers={"Authorization": f"Bearer {DEMO_TOKEN}"},
        json={
            "parent_id": parent_a,
            "case_id": "case-does-not-exist",
            "symptoms": ["fever"],
            "free_text": "",
            "reported_by": "family",
        },
    )
    assert res.status_code == 404


def test_adk_session_and_run_routes_require_authentication(client: TestClient) -> None:
    for method, path, body in (
        ("GET", "/list-apps", None),
        ("GET", "/apps/kinguard/users/demo/sessions", None),
        ("POST", "/apps/kinguard/users/demo/sessions", {}),
        ("POST", "/run", {"app_name": "kinguard", "user_id": "demo", "session_id": "s1"}),
    ):
        resp = client.request(method, path, json=body)
        assert resp.status_code == 401, f"{method} {path} exposed without auth ({resp.status_code})"

    headers = {"Authorization": f"Bearer {DEMO_TOKEN}"}
    assert client.get("/list-apps", headers=headers).status_code == 200
    assert client.get("/apps/kinguard/users/demo/sessions", headers=headers).status_code == 200


def test_concurrent_receipt_appends_never_overwrite_and_verify_cleanly() -> None:
    parent_id = _new_parent("Concurrent Parent")
    case = service.open_case(parent_id)

    def _worker(i: int) -> int:
        r = service.append_receipt(
            case.case_id,
            kind="test.concurrent",
            actor=f"worker-{i}",
            payload={"i": i},
        )
        return r.seq

    with ThreadPoolExecutor(max_workers=8) as pool:
        seqs = list(pool.map(_worker, range(16)))

    assert len(set(seqs)) == 16
    chain = service.get_chain(case.case_id)
    # 1 initial case.opened + 16 concurrent receipts = 17
    assert len(chain.receipts) == 17
    assert [r.seq for r in chain.receipts] == list(range(17))
    assert service.verify_case(case.case_id).ok


def test_save_receipt_refuses_to_overwrite_existing_slot() -> None:
    chain = ReceiptChain("case-conflict")
    r0 = chain.append("a", "agent", {"v": 1})
    save_receipt(r0)
    with pytest.raises(ReceiptConflictError):
        save_receipt(r0)


def test_swapping_public_key_and_resigning_fails_pinned_verification(client: TestClient) -> None:
    parent_id = _new_parent("Pinned Key Parent")
    triage = triage_tools.run_triage(
        parent_id=parent_id,
        symptoms=["fever"],
        free_text="mild fever",
        reported_by="family",
        lat=0.0,
        lon=0.0,
        case_id="",
    )
    case_id = triage["case_id"]
    chain = service.get_chain(case_id)
    target = chain.receipts[-1]

    rogue_pem = base64.b64decode(generate_key_b64())
    rogue_key = serialization.load_pem_private_key(rogue_pem, password=None)
    rogue_signer = Signer(private_key=rogue_key, ephemeral=True)  # type: ignore[arg-type]

    target.payload["severity"] = "HIGH"
    target.public_key = rogue_signer.public_key_b64
    target.hash = target.compute_hash()
    target.signature = rogue_signer.sign(target.signing_input())
    get_store().put(f"CASE#{case_id}", receipt_sk(target.seq), target.model_dump(mode="json"))

    res = verify_chain(service.get_chain(case_id).receipts)
    assert not res.ok
    assert "pinned" in (res.reason or "")

    api_res = client.get(f"/api/cases/{case_id}/verify").json()
    assert api_res["verified"] is False
    assert "pinned" in (api_res["reason"] or "")


def test_webui_and_handoff_app_check_debug_pii_masking_and_stale_guards(client: TestClient) -> None:
    html = client.get("/app").text
    shared = client.get("/hybrid.js").text
    assert "CustomProvider" in shared
    assert "appCheckActive" in shared
    assert 'src="/hybrid.js"' in html
    assert "maskPII(text)" in html
    assert "sourceText" in html
    assert "resetCaseScopedState" in html

    # Check handoff form App Check debug handling too
    pid = _new_parent("Handoff AppCheck Parent")
    onboarding_tools.record_emergency_disclosure_consent(pid)
    case = service.open_case(pid)
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("KINGUARD_LINK_SECRET", "test-handoff-secret")
        mint = client.post(
            f"/api/cases/{case.case_id}/handoff-link?allow_notes=true",
            headers={"Authorization": f"Bearer {DEMO_TOKEN}"},
        )
        assert mint.status_code == 200
        handoff_html = client.get(mint.json()["url"]).text
        assert "src=/hybrid.js" in handoff_html
        assert "KinGuardHybrid.create" in handoff_html


def test_demo_token_config_matches_webui_env_example_and_deploy_script(client: TestClient) -> None:
    root = pathlib.Path(__file__).resolve().parents[1]
    env_example = (root / ".env.example").read_text(encoding="utf-8")
    deploy_sh = (root / "infra" / "deploy_cloud_run.sh").read_text(encoding="utf-8")
    html = client.get("/app").text

    assert DEMO_TOKEN == "kinguard-demo-family-token"
    assert "KINGUARD_DEMO_TOKEN=kinguard-demo-family-token" in env_example
    assert "KINGUARD_DEMO_TOKEN=${KINGUARD_DEMO_TOKEN:-kinguard-demo-family-token}" in deploy_sh
    assert 'S.token="kinguard-demo-family-token"' in html


def test_intake_signal_requires_family_session_and_demo_seed_episode_works(
    client: TestClient,
) -> None:
    parent_id = _new_parent("Signal Auth Parent")
    unauth = client.post(
        "/api/intake-signal",
        json={
            "parent_id": parent_id,
            "channel": "er_desk_webhook",
            "raw_text": "unauthenticated test",
            "reported_by": "stranger",
        },
    )
    assert unauth.status_code == 401
    assert service.latest_case_for_parent(parent_id) is None

    authed = client.post(
        "/api/intake-signal",
        headers={"Authorization": f"Bearer {DEMO_TOKEN}"},
        json={
            "parent_id": parent_id,
            "channel": "er_desk_webhook",
            "raw_text": "chest pain",
            "reported_by": "er_desk",
            "symptoms": ["chest pain"],
        },
    )
    assert authed.status_code == 200
    assert authed.json()["signal"]["case_id"]

    seeded = client.post("/api/demo/seed?episode=true")
    assert seeded.status_code == 200
    assert seeded.json()["case_id"]


def test_verify_unknown_case_returns_404_not_true(client: TestClient) -> None:
    resp = client.get("/api/cases/nonexistent-case-xyz/verify")
    assert resp.status_code == 404
    tool_res = provenance_tools.verify_case_chain("nonexistent-case-xyz")
    assert tool_res["verified"] is False
    assert tool_res["receipt_count"] == 0


def test_document_ingest_rejects_oversized_and_empty_uploads(client: TestClient) -> None:
    parent_id = _new_parent("Upload Size Parent")
    case = service.open_case(parent_id)
    headers = {"Authorization": f"Bearer {DEMO_TOKEN}"}

    empty = client.post(
        f"/api/cases/{case.case_id}/documents/ingest",
        headers=headers,
        files={"file": ("empty.png", io.BytesIO(b""), "image/png")},
    )
    assert empty.status_code == 400

    too_big = client.post(
        f"/api/cases/{case.case_id}/documents/ingest",
        headers=headers,
        files={"file": ("huge.png", io.BytesIO(b"\x89PNG" + b"0" * (10 * 1024 * 1024 + 8)), "image/png")},
    )
    assert too_big.status_code == 413


def test_booker_validates_target_urls_and_blocks_private_ssrf() -> None:
    booker_dir = pathlib.Path(__file__).resolve().parents[1] / "booker"
    sys.path.insert(0, str(booker_dir))
    try:
        spec = importlib.util.spec_from_file_location("kinguard_booker_app", booker_dir / "app.py")
        assert spec and spec.loader
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    finally:
        if str(booker_dir) in sys.path:
            sys.path.remove(str(booker_dir))

    bclient = TestClient(mod.app)
    for route in ("/prepare", "/commit"):
        for bad_url in (
            "javascript:alert(1)",
            "http://127.0.0.1:8080/admin",
            "http://169.254.169.254/latest/meta-data",
            "http://metadata.google.internal/",
        ):
            r = bclient.post(route, json={"url": bad_url})
            assert r.status_code == 200
            assert r.json()["outcome"] == "unavailable"


def test_webui_scheme_guards_and_accurate_hybrid_copy(client: TestClient) -> None:
    html = client.get("/app").text
    assert "safeCheckoutUrl" in html
    assert "safeUpiUrl" in html
    assert "window.open('${esc(x.checkout_url)}'" not in html
    assert "Normalise messy Tamil" not in html
    assert "Normalise Tamil, Tanglish, Hindi, or English locally" not in html


def test_local_env_secrets_are_ignored_by_git_and_docker() -> None:
    root = pathlib.Path(__file__).resolve().parents[1]
    gitignore = (root / ".gitignore").read_text(encoding="utf-8")
    dockerignore = (root / ".dockerignore").read_text(encoding="utf-8")
    for pattern in (".env", ".env.local", ".local.env"):
        assert pattern in gitignore, f"{pattern} missing from .gitignore"
        assert pattern in dockerignore, f"{pattern} missing from .dockerignore"
