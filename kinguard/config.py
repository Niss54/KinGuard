"""Central configuration. Everything env-driven so the same code runs locally,
against the Firestore emulator, and on Cloud Run."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_ROOT / ".local.env")
load_dotenv(_ROOT / ".env.local")
load_dotenv(_ROOT / ".env")


def _env(name: str, default: str | None = None) -> str | None:
    return os.getenv(name) or default


def _flag(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    # Vertex AI / Gemini
    project_id: str = field(default_factory=lambda: os.getenv("GOOGLE_CLOUD_PROJECT", "kinguard-hack"))
    location: str = field(default_factory=lambda: os.getenv("GOOGLE_CLOUD_LOCATION", "global"))
    model: str = field(default_factory=lambda: _env("KINGUARD_MODEL", "gemini-3.5-flash"))

    # Storage
    store_backend: str = field(default_factory=lambda: _env("KINGUARD_STORE_BACKEND", "firestore"))
    firestore_database: str = field(default_factory=lambda: _env("KINGUARD_FIRESTORE_DATABASE", "(default)"))
    emulator_host: str | None = field(default_factory=lambda: os.getenv("FIRESTORE_EMULATOR_HOST"))

    # Pub/Sub
    pubsub_enabled: bool = field(default_factory=lambda: _flag("KINGUARD_PUBSUB_ENABLED", False))
    topic_intake: str = field(default_factory=lambda: _env("KINGUARD_TOPIC_INTAKE", "kinguard-intake-events"))
    topic_case_updates: str = field(default_factory=lambda: _env("KINGUARD_TOPIC_CASE_UPDATES", "kinguard-case-updates"))
    topic_claim_status: str = field(default_factory=lambda: _env("KINGUARD_TOPIC_CLAIM_STATUS", "kinguard-claim-status"))

    # Provenance
    signing_key_b64: str | None = field(default_factory=lambda: _env("KINGUARD_SIGNING_KEY_B64"))

    # WhatsApp — sandbox only for the hackathon window.
    whatsapp_mode: str = field(default_factory=lambda: _env("KINGUARD_WHATSAPP_MODE", "sandbox"))
    whatsapp_phone_number_id: str | None = field(default_factory=lambda: os.getenv("WHATSAPP_PHONE_NUMBER_ID") or None)
    whatsapp_access_token: str | None = field(default_factory=lambda: os.getenv("WHATSAPP_ACCESS_TOKEN") or None)

    # Insurer / TPA — simulated for the hackathon window.
    tpa_mode: str = field(default_factory=lambda: _env("KINGUARD_TPA_MODE", "simulated"))
    tpa_endpoint: str | None = field(default_factory=lambda: _env("KINGUARD_TPA_ENDPOINT"))

    # The one store that outlives a case. A full Agent Engine resource name,
    # projects/<p>/locations/<l>/reasoningEngines/<id>. Absent, lessons are not
    # written and not read, and every check-in falls back to the profile.
    memory_bank: str | None = field(default_factory=lambda: _env("KINGUARD_MEMORY_BANK"))

    @property
    def use_memory_store(self) -> bool:
        return self.store_backend.lower() == "memory"


@lru_cache(maxsize=1)
def settings() -> Settings:
    return Settings()
