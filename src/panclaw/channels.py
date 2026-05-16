from __future__ import annotations

import base64
import hashlib
import hmac
import time
import urllib.parse
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ChannelEvent:
    channel: str
    event_type: str
    sender: str | None = None
    chat_id: str | None = None
    text: str | None = None
    raw: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "channel": self.channel,
            "event_type": self.event_type,
            "sender": self.sender,
            "chat_id": self.chat_id,
            "text": self.text,
            "raw": self.raw or {},
        }


def wechat_official_signature(token: str, timestamp: str, nonce: str) -> str:
    value = "".join(sorted([token, timestamp, nonce]))
    return hashlib.sha1(value.encode("utf-8")).hexdigest()


def verify_wechat_official_signature(token: str, signature: str, timestamp: str, nonce: str) -> bool:
    expected = wechat_official_signature(token, timestamp, nonce)
    return hmac.compare_digest(expected, signature)


def parse_wechat_official_xml(body: bytes | str) -> ChannelEvent:
    raw_body = body.encode("utf-8") if isinstance(body, str) else body
    root = ET.fromstring(raw_body)
    data = {child.tag: child.text or "" for child in root}
    msg_type = data.get("MsgType", "unknown")
    event_type = data.get("Event") if msg_type == "event" else msg_type
    return ChannelEvent(
        channel="wechat_official",
        event_type=event_type or "unknown",
        sender=data.get("FromUserName"),
        chat_id=data.get("ToUserName"),
        text=data.get("Content"),
        raw=data,
    )


def build_wechat_passive_text_reply(to_user: str, from_user: str, content: str) -> bytes:
    root = ET.Element("xml")
    values = {
        "ToUserName": to_user,
        "FromUserName": from_user,
        "CreateTime": str(int(time.time())),
        "MsgType": "text",
        "Content": content,
    }
    for key, value in values.items():
        child = ET.SubElement(root, key)
        child.text = value
    return ET.tostring(root, encoding="utf-8", xml_declaration=False)


def feishu_lark_webhook_sign(secret: str, timestamp: int | str) -> str:
    key = f"{timestamp}\n{secret}".encode("utf-8")
    digest = hmac.new(key, b"", hashlib.sha256).digest()
    return base64.b64encode(digest).decode("utf-8")


def add_feishu_lark_signature(body: dict[str, Any], secret: str, timestamp: int | None = None) -> dict[str, Any]:
    ts = timestamp or int(time.time())
    signed = dict(body)
    signed["timestamp"] = str(ts)
    signed["sign"] = feishu_lark_webhook_sign(secret, ts)
    return signed


def dingtalk_robot_sign(secret: str, timestamp: int | str) -> str:
    string_to_sign = f"{timestamp}\n{secret}".encode("utf-8")
    digest = hmac.new(secret.encode("utf-8"), string_to_sign, hashlib.sha256).digest()
    return urllib.parse.quote_plus(base64.b64encode(digest).decode("utf-8"))


def add_dingtalk_signature_to_url(webhook_url: str, secret: str, timestamp: int | None = None) -> str:
    ts = timestamp or int(time.time() * 1000)
    sign = dingtalk_robot_sign(secret, ts)
    sep = "&" if "?" in webhook_url else "?"
    return f"{webhook_url}{sep}timestamp={ts}&sign={sign}"


def parse_feishu_lark_event(payload: dict[str, Any], *, expected_token: str | None = None, channel: str = "feishu") -> dict[str, Any]:
    if expected_token and payload.get("token") and not hmac.compare_digest(str(payload["token"]), expected_token):
        return {"status": "forbidden", "message": "Invalid verification token."}
    if payload.get("type") == "url_verification" and payload.get("challenge"):
        return {"status": "challenge", "challenge": payload["challenge"]}
    event = payload.get("event", payload)
    message = event.get("message", {}) if isinstance(event, dict) else {}
    sender = event.get("sender", {}) if isinstance(event, dict) else {}
    return {
        "status": "ok",
        "event": ChannelEvent(
            channel=channel,
            event_type=str(event.get("type", payload.get("header", {}).get("event_type", "message"))),
            sender=str(sender.get("sender_id", {}).get("open_id", "")) or None,
            chat_id=str(message.get("chat_id", "")) or None,
            text=_extract_feishu_lark_text(message),
            raw=payload,
        ).to_dict(),
    }


def _extract_feishu_lark_text(message: dict[str, Any]) -> str | None:
    content = message.get("content")
    if not content:
        return None
    if isinstance(content, str):
        try:
            import json

            parsed = json.loads(content)
        except Exception:  # noqa: BLE001 - platform payloads vary.
            return content
        return parsed.get("text") if isinstance(parsed, dict) else content
    if isinstance(content, dict):
        return str(content.get("text", "")) or None
    return str(content)


def parse_dingtalk_event(payload: dict[str, Any]) -> dict[str, Any]:
    text = payload.get("text", {})
    content = text.get("content") if isinstance(text, dict) else None
    return {
        "status": "ok",
        "event": ChannelEvent(
            channel="dingtalk",
            event_type=str(payload.get("msgtype", "message")),
            sender=str(payload.get("senderStaffId", payload.get("senderId", ""))) or None,
            chat_id=str(payload.get("conversationId", "")) or None,
            text=content,
            raw=payload,
        ).to_dict(),
    }

