from __future__ import annotations

import shutil
import subprocess
from typing import Any

from .base import blocked, dry_run, not_configured, require_enabled


PLUGIN_PACKAGE = "@tencent-weixin/openclaw-weixin"
CLI_PACKAGE = "@tencent-weixin/openclaw-weixin-cli"
CHANNEL_ID = "openclaw-weixin"


def _command_preview(payload: dict[str, Any], message: str, commands: list[list[str]]) -> dict[str, Any]:
    preview = dry_run(payload, message, commands=[" ".join(command) for command in commands])
    if preview:
        return preview
    return {}


def _require_openclaw() -> str | None:
    return shutil.which("openclaw")


def _run(command: list[str]) -> dict[str, Any]:
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    return {
        "returncode": completed.returncode,
        "stdout": completed.stdout[-4000:],
        "stderr": completed.stderr[-4000:],
    }


def official_plugin_info(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "ok",
        "message": "Tencent official openclaw-weixin plugin is the supported personal WeChat boundary.",
        "plugin_package": PLUGIN_PACKAGE,
        "cli_package": CLI_PACKAGE,
        "channel_id": CHANNEL_ID,
        "source": "https://github.com/Tencent/openclaw-weixin",
        "dry_run": payload.get("dry_run", True),
    }


def quick_install(payload: dict[str, Any]) -> dict[str, Any]:
    command = ["npx", "-y", f"{CLI_PACKAGE}@latest", "install"]
    preview = _command_preview(payload, "Tencent openclaw-weixin quick install dry-run.", [command])
    if preview:
        return preview
    if not require_enabled("PANCLAW_ENABLE_OPENCLAW_PLUGIN_MUTATION"):
        return blocked("PANCLAW_ENABLE_OPENCLAW_PLUGIN_MUTATION=1 is required.")
    if not shutil.which("npx"):
        return not_configured("npx is not installed.")
    result = _run(command)
    return {"status": "ok" if result["returncode"] == 0 else "failed", "message": "Quick install finished.", **result}


def manual_install(payload: dict[str, Any]) -> dict[str, Any]:
    commands = [
        ["openclaw", "plugins", "install", PLUGIN_PACKAGE],
        ["openclaw", "config", "set", f"plugins.entries.{CHANNEL_ID}.enabled", "true"],
        ["openclaw", "config", "set", "session.dmScope", "per-account-channel-peer"],
    ]
    if payload.get("restart_gateway", True):
        commands.append(["openclaw", "gateway", "restart"])
    preview = _command_preview(payload, "Tencent openclaw-weixin manual install dry-run.", commands)
    if preview:
        return preview
    if not require_enabled("PANCLAW_ENABLE_OPENCLAW_PLUGIN_MUTATION"):
        return blocked("PANCLAW_ENABLE_OPENCLAW_PLUGIN_MUTATION=1 is required.")
    if not _require_openclaw():
        return not_configured("openclaw CLI is not installed.")
    results = [_run(command) for command in commands]
    ok = all(item["returncode"] == 0 for item in results)
    return {"status": "ok" if ok else "failed", "message": "Manual install commands finished.", "results": results}


def login(payload: dict[str, Any]) -> dict[str, Any]:
    command = ["openclaw", "channels", "login", "--channel", CHANNEL_ID]
    preview = _command_preview(payload, "Tencent openclaw-weixin QR login dry-run.", [command])
    if preview:
        return preview
    if not require_enabled("PANCLAW_ENABLE_OPENCLAW_PLUGIN_MUTATION"):
        return blocked("PANCLAW_ENABLE_OPENCLAW_PLUGIN_MUTATION=1 is required.")
    if not _require_openclaw():
        return not_configured("openclaw CLI is not installed.")
    result = _run(command)
    return {"status": "ok" if result["returncode"] == 0 else "failed", "message": "QR login command finished.", **result}


def status(payload: dict[str, Any]) -> dict[str, Any]:
    commands = [
        ["openclaw", "--version"],
        ["openclaw", "plugins", "list"],
        ["openclaw", "channels", "list"],
    ]
    preview = _command_preview(payload, "Tencent openclaw-weixin status dry-run.", commands)
    if preview:
        return preview
    if not _require_openclaw():
        return not_configured("openclaw CLI is not installed.")
    results = [_run(command) for command in commands]
    return {"status": "ok", "message": "OpenClaw Weixin status commands finished.", "results": results}

