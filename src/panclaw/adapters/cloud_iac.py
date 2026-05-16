from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any

from .base import blocked, dry_run, not_configured, require_enabled


def terraform_plan(payload: dict[str, Any]) -> dict[str, Any]:
    workdir = Path(payload["workdir"])
    preview = dry_run(payload, "Terraform plan dry-run.", workdir=str(workdir))
    if preview:
        return preview
    terraform = shutil.which("terraform")
    if not terraform:
        return not_configured("terraform binary is not installed.")
    if not workdir.exists():
        return blocked(f"Terraform workdir does not exist: {workdir}")
    completed = subprocess.run([terraform, "plan", "-no-color"], cwd=workdir, check=False, capture_output=True, text=True)
    return {
        "status": "ok" if completed.returncode == 0 else "failed",
        "message": "Terraform plan finished.",
        "returncode": completed.returncode,
        "stdout": completed.stdout[-8000:],
        "stderr": completed.stderr[-4000:],
    }


def cloud_create_server(payload: dict[str, Any]) -> dict[str, Any]:
    preview = dry_run(
        payload,
        "Cloud server creation dry-run.",
        provider=payload.get("provider"),
        region=payload.get("region"),
        instance_type=payload.get("instance_type"),
    )
    if preview:
        return preview
    if not require_enabled("PANCLAW_ENABLE_CLOUD_MUTATION"):
        return blocked("PANCLAW_ENABLE_CLOUD_MUTATION=1 is required for cloud resource creation.")
    return blocked(
        "Provider-specific create-server adapters are intentionally not enabled in v0.1.",
        required_next_steps=[
            "Define credential scope and billing guardrails.",
            "Add provider-specific dry-run validation.",
            "Add quota, region and cost policy checks.",
        ],
    )

