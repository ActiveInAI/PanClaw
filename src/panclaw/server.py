from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import unquote, urlparse

from .registry import get_skill, list_skills
from .router import run_skill


def _json_bytes(data: object, status: int = 200) -> tuple[int, bytes]:
    return status, json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")


class PanClawHandler(BaseHTTPRequestHandler):
    server_version = "PanClaw/0.1"

    def _send_json(self, data: object, status: int = 200) -> None:
        code, body = _json_bytes(data, status)
        self.send_response(code)
        self.send_header("content-type", "application/json; charset=utf-8")
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
        self._send_json({"error": "not_found"}, 404)

    def do_POST(self) -> None:  # noqa: N802 - stdlib hook.
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
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

    def log_message(self, fmt: str, *args: object) -> None:
        return


def serve(host: str = "127.0.0.1", port: int = 8787) -> None:
    httpd = ThreadingHTTPServer((host, port), PanClawHandler)
    print(f"PanClaw API listening on http://{host}:{port}")
    httpd.serve_forever()

