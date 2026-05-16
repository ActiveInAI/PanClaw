from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import urlopen

from .base import blocked, dry_run, not_configured, optional_import, require_enabled, require_env


def pyautogui_control(payload: dict[str, Any]) -> dict[str, Any]:
    preview = dry_run(payload, "PyAutoGUI desktop control dry-run.", actions=payload.get("actions", []))
    if preview:
        return preview
    if not require_enabled("PANCLAW_ENABLE_DESKTOP_AUTOMATION"):
        return blocked("PANCLAW_ENABLE_DESKTOP_AUTOMATION=1 is required.")
    pyautogui, error = optional_import("pyautogui", "PyAutoGUI")
    if error:
        return error
    for action in payload.get("actions", []):
        kind = action.get("type")
        if kind == "click":
            pyautogui.click(action["x"], action["y"])
        elif kind == "write":
            pyautogui.write(action["text"])
        elif kind == "hotkey":
            pyautogui.hotkey(*action["keys"])
        else:
            return blocked(f"Unsupported desktop action: {kind}")
    return {"status": "ok", "message": "Desktop actions executed."}


def ansible_playbook(payload: dict[str, Any]) -> dict[str, Any]:
    preview = dry_run(payload, "Ansible playbook dry-run.", playbook=payload["playbook"])
    if preview:
        return preview
    if not shutil.which("ansible-playbook"):
        return not_configured("ansible-playbook is not installed.")
    command = ["ansible-playbook", payload["playbook"], "--check"]
    if payload.get("inventory"):
        command.extend(["-i", payload["inventory"]])
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    return {"status": "ok" if completed.returncode == 0 else "failed", "message": "Ansible check run finished.", "returncode": completed.returncode}


def local_snapshot(payload: dict[str, Any]) -> dict[str, Any]:
    psutil, _ = optional_import("psutil", "psutil")
    disk = shutil.disk_usage(Path.cwd())
    data: dict[str, Any] = {
        "cpu_count": os.cpu_count(),
        "disk_total": disk.total,
        "disk_used": disk.used,
        "disk_free": disk.free,
        "psutil_available": psutil is not None,
    }
    if psutil:
        data.update(
            {
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory": dict(psutil.virtual_memory()._asdict()),
            }
        )
    return {"status": "ok", "message": "Local snapshot collected.", "snapshot": data, "dry_run": payload.get("dry_run", True)}


def prometheus_query(payload: dict[str, Any]) -> dict[str, Any]:
    preview = dry_run(payload, "Prometheus query dry-run.", query=payload["query"])
    if preview:
        return preview
    base_url = require_env("PROMETHEUS_URL")
    if not base_url:
        return not_configured("PROMETHEUS_URL is not configured.")
    url = f"{base_url.rstrip('/')}/api/v1/query?{urlencode({'query': payload['query']})}"
    with urlopen(url, timeout=15) as response:  # noqa: S310 - operator-configured metrics endpoint.
        data = json.loads(response.read().decode("utf-8"))
    return {"status": "ok", "message": "Prometheus query completed.", "result": data}

