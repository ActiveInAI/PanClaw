from __future__ import annotations

import json
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
