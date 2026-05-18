from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

from .channels import (
    build_wechat_passive_text_reply,
    parse_dingtalk_event,
    parse_feishu_lark_event,
    parse_wechat_official_xml,
    verify_wechat_official_signature,
)
from .adapters.messaging import official_channel_health
from .integrations import core_integrations_manifest, hermes_manifest, openclaw_manifest, plugin_manifest
from .registry import get_skill, list_skills
from .router import run_skill


def _json_bytes(data: object, status: int = 200) -> tuple[int, bytes]:
    return status, json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")


class PanClawHandler(BaseHTTPRequestHandler):
    server_version = "PanClaw/0.3"

    def _send_json(self, data: object, status: int = 200) -> None:
        code, body = _json_bytes(data, status)
        self.send_response(code)
        self.send_header("content-type", "application/json; charset=utf-8")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_bytes(self, body: bytes, content_type: str = "text/plain; charset=utf-8", status: int = 200) -> None:
        self.send_response(status)
        self.send_header("content-type", content_type)
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - stdlib hook.
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        if path == "/health":
            self._send_json({"status": "ok", "service": "panclaw"})
            return
        if path == "/skills":
            self._send_json([skill.to_dict() for skill in list_skills()])
            return
        if path.startswith("/skills/"):
            skill_id = unquote(path.removeprefix("/skills/"))
            skill = get_skill(skill_id)
            if not skill:
                self._send_json({"error": "unknown_skill", "skill_id": skill_id}, 404)
                return
            self._send_json(skill.to_dict())
            return
        if path == "/integrations/openclaw/manifest":
            self._send_json(openclaw_manifest(self._base_url()))
            return
        if path == "/integrations/hermes/manifest":
            self._send_json(hermes_manifest(self._base_url()))
            return
        if path == "/plugins":
            self._send_json(plugin_manifest(self._base_url()))
            return
        if path == "/integrations/core":
            self._send_json(core_integrations_manifest(self._base_url()))
            return
        if path == "/channels/health":
            self._send_json(official_channel_health({"dry_run": True}))
            return
        if path == "/channels/wechat/official/callback":
            self._handle_wechat_official_get(parsed.query)
            return
        self._send_json({"error": "not_found"}, 404)

    def do_POST(self) -> None:  # noqa: N802 - stdlib hook.
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        if path == "/channels/wechat/official/callback":
            self._handle_wechat_official_post(parsed.query)
            return
        if path == "/channels/feishu/events":
            self._handle_json_channel_event("feishu")
            return
        if path == "/channels/lark/events":
            self._handle_json_channel_event("lark")
            return
        if path == "/channels/dingtalk/events":
            self._handle_json_channel_event("dingtalk")
            return
        if not (path.startswith("/skills/") and path.endswith("/run")):
            self._send_json({"error": "not_found"}, 404)
            return

        skill_id = unquote(path.removeprefix("/skills/").removesuffix("/run").rstrip("/"))
        length = int(self.headers.get("content-length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload: dict[str, Any] = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            self._send_json({"error": "invalid_json", "message": str(exc)}, 400)
            return

        approval_token = self.headers.get("x-panclaw-approval-token")
        result = run_skill(skill_id, payload, actor=self.client_address[0], approval_token=approval_token)
        status = 200 if result.status not in {"schema_failed", "failed"} else 400
        self._send_json(result.to_dict(), status)

    def _handle_wechat_official_get(self, query: str) -> None:
        params = {key: values[0] for key, values in parse_qs(query).items()}
        token = os.environ.get("WECHAT_OFFICIAL_TOKEN")
        if not token:
            self._send_json({"error": "not_configured", "message": "WECHAT_OFFICIAL_TOKEN is not configured."}, 503)
            return
        required = {"signature", "timestamp", "nonce", "echostr"}
        if not required.issubset(params):
            self._send_json({"error": "bad_request", "required": sorted(required)}, 400)
            return
        if not verify_wechat_official_signature(token, params["signature"], params["timestamp"], params["nonce"]):
            self._send_json({"error": "forbidden", "message": "Invalid WeChat signature."}, 403)
            return
        self._send_bytes(params["echostr"].encode("utf-8"))

    def _handle_wechat_official_post(self, query: str) -> None:
        params = {key: values[0] for key, values in parse_qs(query).items()}
        token = os.environ.get("WECHAT_OFFICIAL_TOKEN")
        if token and {"signature", "timestamp", "nonce"}.issubset(params):
            if not verify_wechat_official_signature(token, params["signature"], params["timestamp"], params["nonce"]):
                self._send_json({"error": "forbidden", "message": "Invalid WeChat signature."}, 403)
                return
        length = int(self.headers.get("content-length", "0"))
        raw = self.rfile.read(length) if length else b""
        try:
            event = parse_wechat_official_xml(raw)
        except Exception as exc:  # noqa: BLE001 - platform payloads vary.
            self._send_json({"error": "invalid_xml", "message": str(exc)}, 400)
            return
        if event.text:
            reply = build_wechat_passive_text_reply(event.sender or "", event.chat_id or "", "PanClaw 已收到。")
            self._send_bytes(reply, "application/xml; charset=utf-8")
            return
        self._send_bytes(b"success")

    def _handle_json_channel_event(self, channel: str) -> None:
        length = int(self.headers.get("content-length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload: dict[str, Any] = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            self._send_json({"error": "invalid_json", "message": str(exc)}, 400)
            return
        if channel == "dingtalk":
            self._send_json(parse_dingtalk_event(payload))
            return
        token_name = "FEISHU_VERIFICATION_TOKEN" if channel == "feishu" else "LARK_VERIFICATION_TOKEN"
        parsed = parse_feishu_lark_event(payload, expected_token=os.environ.get(token_name), channel=channel)
        if parsed.get("status") == "challenge":
            self._send_json({"challenge": parsed["challenge"]})
            return
        status = 403 if parsed.get("status") == "forbidden" else 200
        self._send_json(parsed, status)

    def _base_url(self) -> str:
        host = self.headers.get("host", "127.0.0.1:8787")
        return f"http://{host}"

    def log_message(self, fmt: str, *args: object) -> None:
        return


def serve(host: str = "127.0.0.1", port: int = 8787) -> None:
    httpd = ThreadingHTTPServer((host, port), PanClawHandler)
    print(f"PanClaw API listening on http://{host}:{port}")
    httpd.serve_forever()
