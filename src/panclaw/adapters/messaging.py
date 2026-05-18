from __future__ import annotations

import json
import shutil
from typing import Any
from urllib.request import Request, urlopen

from panclaw.channels import add_dingtalk_signature_to_url, add_feishu_lark_signature

from .base import blocked, dry_run, not_configured, require_enabled, require_env


def wechat_personal_boundary(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "ok",
        "message": "Personal WeChat is supported through Tencent's official openclaw-weixin plugin boundary.",
        "plugin_package": "@tencent-weixin/openclaw-weixin",
        "cli_package": "@tencent-weixin/openclaw-weixin-cli",
        "source": "https://github.com/Tencent/openclaw-weixin",
        "dry_run": payload.get("dry_run", True),
    }


def official_channel_health(payload: dict[str, Any]) -> dict[str, Any]:
    del payload
    openclaw_path = shutil.which("openclaw")
    send_enabled = require_enabled("PANCLAW_ENABLE_MESSAGE_SEND")
    channels = [
        {
            "id": "wechat_personal_openclaw_weixin",
            "name": "Personal WeChat via Tencent openclaw-weixin",
            "configured": bool(openclaw_path),
            "send_enabled": bool(openclaw_path),
            "receive_enabled": bool(openclaw_path),
            "checks": {
                "openclaw_cli": bool(openclaw_path),
                "plugin_package": "@tencent-weixin/openclaw-weixin",
                "channel_id": "openclaw-weixin",
            },
        },
        {
            "id": "wechat_official",
            "name": "WeChat Official Account",
            "configured": bool(require_env("WECHAT_OFFICIAL_TOKEN") or require_env("WECHAT_OFFICIAL_ACCESS_TOKEN")),
            "send_enabled": send_enabled and bool(require_env("WECHAT_OFFICIAL_ACCESS_TOKEN")),
            "receive_enabled": bool(require_env("WECHAT_OFFICIAL_TOKEN")),
            "checks": {
                "WECHAT_OFFICIAL_TOKEN": bool(require_env("WECHAT_OFFICIAL_TOKEN")),
                "WECHAT_OFFICIAL_ACCESS_TOKEN": bool(require_env("WECHAT_OFFICIAL_ACCESS_TOKEN")),
            },
        },
        _webhook_channel("wecom", "WeCom", "WECOM_WEBHOOK_URL", None, send_enabled),
        _webhook_channel("feishu", "Feishu", "FEISHU_WEBHOOK_URL", "FEISHU_WEBHOOK_SECRET", send_enabled),
        _webhook_channel("lark", "Lark", "LARK_WEBHOOK_URL", "LARK_WEBHOOK_SECRET", send_enabled),
        _webhook_channel("dingtalk", "DingTalk", "DINGTALK_WEBHOOK_URL", "DINGTALK_WEBHOOK_SECRET", send_enabled),
    ]
    configured = sum(1 for channel in channels if channel["configured"])
    return {
        "status": "ok",
        "message": "Official channel health snapshot.",
        "send_gate_enabled": send_enabled,
        "configured_channels": configured,
        "total_channels": len(channels),
        "channels": channels,
    }


def _webhook_channel(channel_id: str, name: str, url_env: str, secret_env: str | None, send_enabled: bool) -> dict[str, Any]:
    url_configured = bool(require_env(url_env))
    checks: dict[str, Any] = {url_env: url_configured}
    if secret_env:
        checks[secret_env] = bool(require_env(secret_env))
    return {
        "id": channel_id,
        "name": name,
        "configured": url_configured,
        "send_enabled": send_enabled and url_configured,
        "receive_enabled": False,
        "checks": checks,
    }


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
    body = {"msg_type": "text", "content": {"text": payload["text"]}}
    secret = require_env("FEISHU_WEBHOOK_SECRET")
    if secret:
        body = add_feishu_lark_signature(body, secret)
    return _post_json(url, body)


def lark_send(payload: dict[str, Any]) -> dict[str, Any]:
    preview = dry_run(payload, "Lark message send dry-run.", provider="lark", text=payload.get("text", ""))
    if preview:
        return preview
    if not require_enabled("PANCLAW_ENABLE_MESSAGE_SEND"):
        return blocked("PANCLAW_ENABLE_MESSAGE_SEND=1 is required for real message sending.")
    url = require_env("LARK_WEBHOOK_URL")
    if not url:
        return not_configured("LARK_WEBHOOK_URL is not configured.")
    body = {"msg_type": "text", "content": {"text": payload["text"]}}
    secret = require_env("LARK_WEBHOOK_SECRET")
    if secret:
        body = add_feishu_lark_signature(body, secret)
    return _post_json(url, body)


def dingtalk_send(payload: dict[str, Any]) -> dict[str, Any]:
    preview = dry_run(payload, "DingTalk message send dry-run.", provider="dingtalk", text=payload.get("text", ""))
    if preview:
        return preview
    if not require_enabled("PANCLAW_ENABLE_MESSAGE_SEND"):
        return blocked("PANCLAW_ENABLE_MESSAGE_SEND=1 is required for real message sending.")
    url = require_env("DINGTALK_WEBHOOK_URL")
    if not url:
        return not_configured("DINGTALK_WEBHOOK_URL is not configured.")
    secret = require_env("DINGTALK_WEBHOOK_SECRET")
    if secret:
        url = add_dingtalk_signature_to_url(url, secret)
    return _post_json(url, {"msgtype": "text", "text": {"content": payload["text"]}})


def wechat_official_customer_service_send(payload: dict[str, Any]) -> dict[str, Any]:
    preview = dry_run(payload, "WeChat Official Account customer-service send dry-run.", openid=payload.get("openid"), text=payload.get("text", ""))
    if preview:
        return preview
    if not require_enabled("PANCLAW_ENABLE_MESSAGE_SEND"):
        return blocked("PANCLAW_ENABLE_MESSAGE_SEND=1 is required for real message sending.")
    access_token = require_env("WECHAT_OFFICIAL_ACCESS_TOKEN")
    if not access_token:
        return not_configured("WECHAT_OFFICIAL_ACCESS_TOKEN is not configured.")
    url = f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={access_token}"
    body = {
        "touser": payload["openid"],
        "msgtype": "text",
        "text": {"content": payload["text"]},
    }
    return _post_json(url, body)
