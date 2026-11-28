"""Behavioral regressions from the submission audit; no live providers."""
import shutil
import subprocess
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from kinguard import service, webauth
from kinguard.provenance.store import CHAIN_HEAD, ReceiptConflictError, get_store, receipt_sk, save_receipt
from kinguard.tools import onboarding_tools


def parent():
    return onboarding_tools.create_parent_profile(
        name="Synthetic audit parent", age=72, city="Test", lat=8.7, lon=78.1,
        chronic_conditions=[], allergies=[],
    )["profile"]["parent_id"]


def test_new_case_requires_authorized_parent_and_has_no_denied_side_effects(monkeypatch):
    from kinguard.server import app
    client = TestClient(app)
    pid = parent()
    payload = {"parent_id": pid, "symptoms": ["chest pain"], "reported_by": "audit"}
    assert client.post("/api/intake", json=payload).status_code == 401
    monkeypatch.setattr(webauth, "verify_google_identity", lambda _: {
        "email": "stranger@example.com", "sub": "stranger",
    })
    headers = {"Authorization": "Bearer test.identity.token"}
    assert client.post("/api/intake", json=payload, headers=headers).status_code == 403
    assert service.latest_case_for_parent(pid) is None
    onboarding_tools.record_family_contact(
        pid, name="Family", relationship="son", whatsapp_e164="+14155550142",
        timezone_name="UTC", is_primary=True, consent_purposes=["status_updates"],
        email="stranger@example.com",
    )
    response = client.post("/api/intake", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["severity"] == "HIGH"


@pytest.mark.parametrize("remove_all", [False, True])
def test_tail_deletion_fails_api_and_loaded_chain_verification(remove_all):
    from kinguard.server import app
    case = service.open_case(parent())
    service.append_receipt(case.case_id, kind="audit", actor="test", payload={})
    chain = service.get_chain(case.case_id)
    assert chain.verify().ok
    rows = chain.receipts if remove_all else chain.receipts[-1:]
    for receipt in rows:
        get_store().delete("CASE#" + case.case_id, receipt_sk(receipt.seq))
    assert not service.get_chain(case.case_id).verify().ok
    response = TestClient(app).get(f"/api/cases/{case.case_id}/verify")
    assert response.status_code != 200 or response.json()["verified"] is False


def test_missing_checkpoint_is_not_silently_recreated_for_legacy_records():
    case = service.open_case(parent())
    get_store().delete("CASE#" + case.case_id, CHAIN_HEAD)
    chain = service.get_chain(case.case_id)
    assert not chain.verify().ok
    receipt = chain.append("audit", "test", {})
    with pytest.raises(ReceiptConflictError):
        save_receipt(receipt)
    assert len(service.get_chain(case.case_id).receipts) == 1


def test_tail_deletion_cannot_be_hidden_by_appending_a_replacement():
    case = service.open_case(parent())
    last = service.append_receipt(case.case_id, kind="audit", actor="test", payload={})
    get_store().delete("CASE#" + case.case_id, receipt_sk(last.seq))
    replacement = service.get_chain(case.case_id).append("replacement", "test", {})
    with pytest.raises(ReceiptConflictError):
        save_receipt(replacement)
    assert not service.verify_case(case.case_id).ok


def test_real_browser_functions_preserve_symptoms_and_discard_stale_ai():
    node = shutil.which("node")
    assert node, "Node is required to run browser behavior regressions"
    root = Path(__file__).resolve().parents[1]
    script = r'''
const assert = require('node:assert/strict');
const html = require('node:fs').readFileSync('kinguard/webui/index.html','utf8');
const extract = (start,end) => html.slice(html.indexOf(start),html.indexOf(end));
eval(extract('function maskPII(', 'function onIntakeTextInput('));
assert.equal(maskPII('amma at flat 5, chest pain, sweating'),
             'amma at [REDACTED_ADDRESS], chest pain, sweating');
assert.equal(maskPII('fell by the door, chest pain'), 'fell by the door, chest pain');
const masked = maskPII('flat 12A, chest pain; email a@example.com phone 9876543210');
assert.ok(masked.includes('chest pain'));
assert.ok(!masked.includes('9876543210') && !masked.includes('a@example.com'));
const S = {caseId:'A',brief:{brief:{note:'A'}},hybrid:{ready:true}};
const render = () => {};
eval(extract('function requestContext(', 'async function api('));
const pending = [];
S.hybrid.model = {generateContent:()=>new Promise((resolve,reject)=>pending.push({resolve,reject}))};
eval(extract('async function runHybridExplain(', 'function vDocUploadCard('));
eval(extract('function resetCaseScopedState(', 'function useCase('));
const reply = text => ({response:{text:()=>text,inferenceSource:'on_device'}});
(async()=>{
  const old = runHybridExplain('brief','en');
  resetCaseScopedState(); S.caseId='B'; S.brief={brief:{note:'B'}};
  const current = runHybridExplain('brief','en');
  pending[0].resolve(reply('A')); await old;
  assert.equal(S.hybrid.explainOut,null); assert.equal(S.hybrid.explainBusy,true);
  pending[1].resolve(reply('B')); await current;
  assert.equal(S.hybrid.explainOut,'B'); assert.equal(S.hybrid.explainBusy,false);
  const first = runHybridExplain('brief','en');
  const second = runHybridExplain('brief','hi');
  pending[3].resolve(reply('new Hindi')); await second;
  pending[2].reject(new Error('old failure')); await first;
  assert.equal(S.hybrid.explainOut,'new Hindi'); assert.equal(S.hybrid.explainErr,null);
  const API=''; let calls=0;
  const document={getElementById:()=>({value:'chest pain'})};
  const navigator={onLine:true};
  const fetch=async(url,opts)=>{calls++;assert.equal(opts.headers.Authorization,'Bearer family');
    assert.equal(JSON.parse(opts.body).free_text,'chest pain');
    return {ok:true,json:async()=>({case_id:'new',severity:'HIGH'})};};
  const load=async()=>{};
  eval(extract('async function submitHybridIntake(', 'function vHybridExplainCard('));
  S.token=null; await submitHybridIntake(); assert.equal(calls,0);
  S.token='family'; S.parentId='parent-B';
  S.hybrid.intakeNorm={sourceText:'chest pain',symptoms:['chest pain'],source:'on_device'};
  await submitHybridIntake(); assert.equal(calls,1);
})().catch(e=>{console.error(e);process.exitCode=1});
'''
    result = subprocess.run([node, "-e", script], cwd=root, capture_output=True,
                            text=True, encoding="utf-8", timeout=30, check=False)
    assert result.returncode == 0, result.stdout + result.stderr


def test_firestore_checkpoint_and_receipt_share_transaction(monkeypatch):
    """Exercise the real adapter against an atomic transaction double, no cloud calls."""
    from google.cloud import firestore

    from kinguard.provenance.chain import ReceiptChain
    from kinguard.provenance.store import FirestoreStore

    rows = {}

    class Snapshot:
        def __init__(self, value):
            self.value = value
            self.exists = value is not None

        def to_dict(self):
            return self.value

    class Ref:
        def __init__(self, key):
            self.key = key

        def get(self, transaction):
            assert not transaction.pending, "all reads must precede writes"
            return Snapshot(rows.get(self.key))

    class Transaction:
        fail = False

        def __init__(self):
            self.pending = {}

        def create(self, ref, data):
            assert ref.key not in rows
            self.pending[ref.key] = data

        def set(self, ref, data):
            if self.fail:
                raise RuntimeError("checkpoint write failed")
            self.pending[ref.key] = data

    class Client:
        def collection(self, _):
            return self

        def document(self, key):
            return Ref(key)

        def transaction(self):
            return Transaction()

    def transactional(fn):
        def commit(tx):
            result = fn(tx)
            rows.update(tx.pending)
            return result
        return commit

    monkeypatch.setattr(firestore, "transactional", transactional)
    store = FirestoreStore.__new__(FirestoreStore)
    store._client = Client()
    chain = ReceiptChain("transaction-test")
    first = chain.append("first", "test", {}).model_dump(mode="json")
    Transaction.fail = True
    with pytest.raises(RuntimeError, match="checkpoint write failed"):
        store.append_receipt_row("CASE#transaction-test", first)
    assert rows == {}
    Transaction.fail = False
    assert store.append_receipt_row("CASE#transaction-test", first)
    assert not store.append_receipt_row("CASE#transaction-test", first)
    second = chain.append("second", "test", {}).model_dump(mode="json")
    assert store.append_receipt_row("CASE#transaction-test", second)
    head = rows["CASE#transaction-test__CHAIN_HEAD"]
    assert head["count"] == 2 and head["hash"] == second["hash"]
    assert len(rows) == 3
