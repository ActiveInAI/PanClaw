from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .integrations import core_integrations_manifest, hermes_manifest, openclaw_manifest, plugin_manifest
from .registry import get_skill, list_skills
from .router import run_skill
from .server import serve


def _load_payload(raw: str | None) -> dict[str, Any]:
    if not raw:
        return {"dry_run": True}
    if raw.startswith("@"):
        return json.loads(Path(raw[1:]).read_text(encoding="utf-8"))
    return json.loads(raw)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="panclaw")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list")
    p_list.add_argument("--domain")

    p_show = sub.add_parser("show")
    p_show.add_argument("skill_id")

    p_run = sub.add_parser("run")
    p_run.add_argument("skill_id")
    p_run.add_argument("--payload")
    p_run.add_argument("--execute", action="store_true", help="Set dry_run=false. Approval may still be required.")
    p_run.add_argument("--approval-token")

    p_export = sub.add_parser("export-openclaw")
    p_export.add_argument("--output")
    p_export.add_argument("--base-url", default="http://127.0.0.1:8787")

    p_hermes = sub.add_parser("export-hermes")
    p_hermes.add_argument("--output")
    p_hermes.add_argument("--base-url", default="http://127.0.0.1:8787")

    p_plugins = sub.add_parser("export-plugins")
    p_plugins.add_argument("--output")
    p_plugins.add_argument("--base-url", default="http://127.0.0.1:8787")

    p_core = sub.add_parser("export-core")
    p_core.add_argument("--output")
    p_core.add_argument("--base-url", default="http://127.0.0.1:8787")

    p_serve = sub.add_parser("serve")
    p_serve.add_argument("--host", default="127.0.0.1")
    p_serve.add_argument("--port", type=int, default=8787)

    args = parser.parse_args(argv)

    if args.cmd == "list":
        rows = [skill.to_dict() for skill in list_skills(args.domain)]
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return 0

    if args.cmd == "show":
        skill = get_skill(args.skill_id)
        if not skill:
            print(json.dumps({"error": "unknown_skill", "skill_id": args.skill_id}, ensure_ascii=False))
            return 2
        print(json.dumps(skill.to_dict(), ensure_ascii=False, indent=2))
        return 0

    if args.cmd == "run":
        payload = _load_payload(args.payload)
        if args.execute:
            payload["dry_run"] = False
        result = run_skill(args.skill_id, payload, approval_token=args.approval_token)
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return 0 if result.status in {"ok", "dry_run", "not_configured", "blocked"} else 1

    if args.cmd == "export-openclaw":
        manifest = openclaw_manifest(args.base_url)
        text = json.dumps(manifest, ensure_ascii=False, indent=2)
        if args.output:
            Path(args.output).write_text(text + "\n", encoding="utf-8")
        else:
            print(text)
        return 0

    if args.cmd == "export-hermes":
        text = json.dumps(hermes_manifest(args.base_url), ensure_ascii=False, indent=2)
        if args.output:
            Path(args.output).write_text(text + "\n", encoding="utf-8")
        else:
            print(text)
        return 0

    if args.cmd == "export-plugins":
        text = json.dumps(plugin_manifest(args.base_url), ensure_ascii=False, indent=2)
        if args.output:
            Path(args.output).write_text(text + "\n", encoding="utf-8")
        else:
            print(text)
        return 0

    if args.cmd == "export-core":
        text = json.dumps(core_integrations_manifest(args.base_url), ensure_ascii=False, indent=2)
        if args.output:
            Path(args.output).write_text(text + "\n", encoding="utf-8")
        else:
            print(text)
        return 0

    if args.cmd == "serve":
        serve(args.host, args.port)
        return 0

    return 2
