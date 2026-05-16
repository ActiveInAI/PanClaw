from __future__ import annotations

import importlib
import json
import os
import time
import uuid
from pathlib import Path
from typing import Any, Callable

from .contracts import RiskLevel, SkillResult
from .registry import require_skill


class SkillExecutionError(RuntimeError):
    pass


def _load_entrypoint(entrypoint: str) -> Callable[[dict[str, Any]], dict[str, Any]]:
    module_name, func_name = entrypoint.split(":", 1)
    module = importlib.import_module(module_name)
    func = getattr(module, func_name)
    if not callable(func):
        raise SkillExecutionError(f"Entrypoint is not callable: {entrypoint}")
    return func


def _validate_required(payload: dict[str, Any], schema: dict[str, Any]) -> tuple[str, ...]:
    missing: list[str] = []
    for key in schema.get("required", []):
        if key not in payload:
            missing.append(key)
    return tuple(missing)


def _approval_ok(approval_token: str | None) -> bool:
    expected = os.environ.get("PANCLAW_APPROVAL_TOKEN")
    return bool(expected and approval_token and approval_token == expected)


def _write_audit(event: dict[str, Any]) -> None:
    audit_path = Path(os.environ.get("PANCLAW_AUDIT_LOG", "logs/audit.jsonl"))
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    with audit_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")


def run_skill(
    skill_id: str,
    payload: dict[str, Any] | None = None,
    *,
    actor: str = "local",
    approval_token: str | None = None,
) -> SkillResult:
    payload = dict(payload or {})
    skill = require_skill(skill_id)
    audit_id = str(uuid.uuid4())
    started = time.time()
    dry_run = bool(payload.get("dry_run", True))

    missing = _validate_required(payload, skill.input_schema)
    if missing:
        result = SkillResult(
            skill_id=skill_id,
            status="schema_failed",
            message=f"Missing required input: {', '.join(missing)}",
            audit_id=audit_id,
        )
        _write_audit({"audit_id": audit_id, "skill_id": skill_id, "actor": actor, "status": result.status, "missing": missing})
        return result

    requires_gate = skill.approval_required or skill.risk_level in {
        RiskLevel.HIGH,
        RiskLevel.REGULATED,
        RiskLevel.DESTRUCTIVE,
    }
    if requires_gate and not dry_run and not _approval_ok(approval_token):
        result = SkillResult(
            skill_id=skill_id,
            status="approval_required",
            message="This skill requires approval. Set dry_run=true or provide PANCLAW_APPROVAL_TOKEN.",
            audit_id=audit_id,
            warnings=("No external action was executed.",),
        )
        _write_audit({"audit_id": audit_id, "skill_id": skill_id, "actor": actor, "status": result.status, "dry_run": dry_run})
        return result

    if dry_run:
        payload["dry_run"] = True

    try:
        handler = _load_entrypoint(skill.entrypoint)
        data = handler(payload)
        status = str(data.pop("status", "ok"))
        message = str(data.pop("message", "Skill completed."))
        warnings = tuple(data.pop("warnings", ()))
        result = SkillResult(skill_id=skill_id, status=status, message=message, data=data, audit_id=audit_id, warnings=warnings)
    except Exception as exc:  # noqa: BLE001 - router must convert adapter failures.
        result = SkillResult(
            skill_id=skill_id,
            status="failed",
            message=str(exc),
            audit_id=audit_id,
            warnings=("Adapter raised an exception; no success was assumed.",),
        )

    _write_audit(
        {
            "audit_id": audit_id,
            "skill_id": skill_id,
            "actor": actor,
            "status": result.status,
            "risk_level": skill.risk_level.value,
            "dry_run": dry_run,
            "duration_ms": int((time.time() - started) * 1000),
        }
    )
    return result

