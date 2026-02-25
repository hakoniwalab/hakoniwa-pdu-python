"""Optional hakopy loader.

This module provides a ``hakopy`` object even when the real dependency is not
installed, so modules can still be imported in test environments.
"""

from __future__ import annotations

from importlib import import_module


def _missing_hakopy_error() -> ModuleNotFoundError:
    return ModuleNotFoundError(
        "No module named 'hakopy'. Install hakopy to use shared-memory/service features."
    )


class _HakopyStub:
    """Fallback object used when hakopy is unavailable."""

    def __getattr__(self, name):
        if name.startswith("HAKO_"):
            return 0

        def _missing(*_args, **_kwargs):
            raise _missing_hakopy_error()

        return _missing


try:
    hakopy = import_module("hakopy")
except ModuleNotFoundError:
    hakopy = _HakopyStub()

