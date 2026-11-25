"""The decision trace — the deciding, made visible.

Read-only over the chain. Every step is a receipt that already exists.
"""

from kinguard.trace.compose import compose_trace

__all__ = ["compose_trace"]
