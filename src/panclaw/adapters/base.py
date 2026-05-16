from __future__ import annotations

import importlib
import os
from typing import Any


def dry_run(payload: dict[str, Any], message: str, **data: Any) -> dict[str, Any]:
    if payload.get("dry_run", True):
        return {"status": "dry_run", "message": message, **data}
    return {}


def blocked(message: str, **data: Any) -> dict[str, Any]:
    return {"status": "blocked", "message": message, **data}


def not_configured(message: str, **data: Any) -> dict[str, Any]:
    return {"status": "not_configured", "message": message, **data}


def require_env(name: str) -> str | None:
    value = os.environ.get(name)
    return value if value else None


def require_enabled(name: str) -> bool:
    return os.environ.get(name, "0") in {"1", "true", "TRUE", "yes", "YES"}


def optional_import(module_name: str, package_hint: str) -> tuple[Any | None, dict[str, Any] | None]:
    try:
        return importlib.import_module(module_name), None
    except ImportError:
        return None, not_configured(
            f"Optional dependency is not installed: {package_hint}",
            package_hint=package_hint,
        )

