"""`uv run python -m kinguard.provenance.keygen` — mint a signing key."""

from kinguard.provenance.signing import generate_key_b64

if __name__ == "__main__":
    print("KINGUARD_SIGNING_KEY_B64=" + generate_key_b64())
