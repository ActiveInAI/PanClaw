# PanClaw

PanClaw merges an OpenClaw-style local control plane with Hermes-style long-running agent traces, memory and tool orchestration.

It is a standard API and Python skill registry for office files, media, browser automation, cloud tools, finance data, health/learning knowledge, AEC/GIS, culture/calendar tools and enterprise messaging. The first implementation is intentionally dependency-light: the core API uses only Python standard library, while heavy or license-sensitive tools stay behind optional adapters.

## Current Scope

- `Skill Registry`: 30+ skills with domain, permissions, risk level, upstream projects and license boundary.
- `ToolRouter`: dry-run by default, approval token for mutating/high-risk calls, audit events for every run.
- `API`: `GET /health`, `GET /skills`, `GET /skills/{id}`, `POST /skills/{id}/run`.
- `Integrations`: OpenClaw manifest, Hermes Agent tool manifest and official channel plugin manifest.
- `CLI`: list, show, run, serve, export OpenClaw, export Hermes and export channel plugin metadata.
- `Messaging`: Tencent official personal WeChat OpenClaw plugin, WeChat Official Account, WeCom, Feishu, Lark and DingTalk official adapters.

## Quick Start

```bash
cd /home/insome/dev/PanClaw
env PYTHONPATH=src python3 -m panclaw list
env PYTHONPATH=src python3 -m panclaw show office.pdf.extract
env PYTHONPATH=src python3 -m panclaw run observability.local.snapshot --payload '{"dry_run": true}'
env PYTHONPATH=src python3 -m panclaw export-openclaw
env PYTHONPATH=src python3 -m panclaw export-hermes
env PYTHONPATH=src python3 -m panclaw export-plugins
env PYTHONPATH=src python3 -m panclaw export-core
env PYTHONPATH=src python3 -m panclaw run messaging.wechat.personal.openclaw_weixin.quick_install
env PYTHONPATH=src python3 -m panclaw serve --host 127.0.0.1 --port 8787
```

After packaging/installing, the shorter `panclaw ...` or `python3 -m panclaw ...` commands work without `PYTHONPATH`.

Example API call:

```bash
curl http://127.0.0.1:8787/skills
curl -X POST http://127.0.0.1:8787/skills/finance.akshare.query/run \
  -H 'content-type: application/json' \
  -d '{"dry_run": true, "dataset": "stock_zh_a_spot_em"}'
```

Integration endpoints:

```text
GET /integrations/openclaw/manifest
GET /integrations/hermes/manifest
GET /integrations/core
GET /plugins
GET /channels/health
GET/POST /channels/wechat/official/callback
POST /channels/feishu/events
POST /channels/lark/events
POST /channels/dingtalk/events
```

## Execution Policy

PanClaw will not silently perform destructive or regulated actions. These always require explicit approval and adapter-specific environment flags:

- Send messages to real users or groups.
- Control desktop keyboard/mouse.
- Log in to websites, compare carts, place orders or query personal accounts.
- Create cloud resources.
- Execute Ansible, Terraform, FFmpeg, Blender, browser automation or shell-backed tools.
- Produce medical, legal, financial, engineering, military or safety-sensitive outputs.

Official channel setup is documented in `docs/OFFICIAL_CHANNELS.md`.
Packaging and installer targets are documented in `docs/PACKAGING.md`.

## Upstream Boundary

PanClaw references OpenClaw and Hermes Agent as integration targets, not vendored dependencies. Upstream code remains upstream. PanClaw exports a skill catalog and exposes a local API that can be registered from those runtimes.

## Project Status

`v0.6.0` adds simulated usage smoke tests for desktop, mobile and architecture-specific release artifacts.
