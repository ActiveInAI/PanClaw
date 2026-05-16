from __future__ import annotations

import json
from typing import Any
from urllib.request import Request, urlopen

from .base import blocked, dry_run, not_configured, require_enabled, require_env


def wechat_personal_boundary(payload: dict[str, Any]) -> dict[str, Any]:
    return blocked(
        "Personal WeChat automation is disabled until a compliant official API path is configured.",
        allowed_paths=[
            "WeChat Official Account / Mini Program APIs where applicable",
            "WeCom official APIs",
            "OpenClaw channel adapter only after terms and security review",
        ],
        dry_run=payload.get("dry_run", True),
    )


def _post_json(url: str, body: dict[str, Any]) -> dict[str, Any]:
    request = Request(
        url,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"content-type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=15) as response:  # noqa: S310 - user-configured official webhook.
        raw = response.read().decode("utf-8", errors="replace")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        payload = {"raw": raw}
    return {"status": "ok", "message": "Message sent.", "provider_response": payload}


def wecom_send(payload: dict[str, Any]) -> dict[str, Any]:
    preview = dry_run(payload, "WeCom message send dry-run.", provider="wecom", text=payload.get("text", ""))
    if preview:
        return preview
    if not require_enabled("PANCLAW_ENABLE_MESSAGE_SEND"):
        return blocked("PANCLAW_ENABLE_MESSAGE_SEND=1 is required for real message sending.")
    url = require_env("WECOM_WEBHOOK_URL")
    if not url:
        return not_configured("WECOM_WEBHOOK_URL is not configured.")
    return _post_json(url, {"msgtype": "text", "text": {"content": payload["text"]}})


def feishu_send(payload: dict[str, Any]) -> dict[str, Any]:
    preview = dry_run(payload, "Feishu message send dry-run.", provider="feishu", text=payload.get("text", ""))
    if preview:
        return preview
    if not require_enabled("PANCLAW_ENABLE_MESSAGE_SEND"):
        return blocked("PANCLAW_ENABLE_MESSAGE_SEND=1 is required for real message sending.")
    url = require_env("FEISHU_WEBHOOK_URL")
    if not url:
        return not_configured("FEISHU_WEBHOOK_URL is not configured.")
    return _post_json(url, {"msg_type": "text", "content": {"text": payload["text"]}})


def dingtalk_send(payload: dict[str, Any]) -> dict[str, Any]:
    preview = dry_run(payload, "DingTalk message send dry-run.", provider="dingtalk", text=payload.get("text", ""))
    if preview:
        return preview
    if not require_enabled("PANCLAW_ENABLE_MESSAGE_SEND"):
        return blocked("PANCLAW_ENABLE_MESSAGE_SEND=1 is required for real message sending.")
    url = require_env("DINGTALK_WEBHOOK_URL")
    if not url:
        return not_configured("DINGTALK_WEBHOOK_URL is not configured.")
    return _post_json(url, {"msgtype": "text", "text": {"content": payload["text"]}})

