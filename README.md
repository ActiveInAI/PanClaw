# PanClaw

PanClaw merges an OpenClaw-style local control plane with Hermes-style long-running agent traces, memory and tool orchestration.

It is a standard API and Python skill registry for office files, media, browser automation, cloud tools, finance data, health/learning knowledge, AEC/GIS, culture/calendar tools and enterprise messaging. The first implementation is intentionally dependency-light: the core API uses only Python standard library, while heavy or license-sensitive tools stay behind optional adapters.

## Current Scope

- `Skill Registry`: 30+ skills with domain, permissions, risk level, upstream projects and license boundary.
- `ToolRouter`: dry-run by default, approval token for mutating/high-risk calls, audit events for every run.
- `API`: `GET /health`, `GET /skills`, `GET /skills/{id}`, `POST /skills/{id}/run`.
- `CLI`: list, show, run and export OpenClaw-compatible skill metadata.
- `Messaging`: WeCom, Feishu and DingTalk webhook adapters; personal WeChat is blocked until a compliant official API path is configured.

## Quick Start

```bash
cd /home/insome/dev/PanClaw
env PYTHONPATH=src python3 -m panclaw list
env PYTHONPATH=src python3 -m panclaw show office.pdf.extract
env PYTHONPATH=src python3 -m panclaw run observability.local.snapshot --payload '{"dry_run": true}'
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

## Execution Policy

PanClaw will not silently perform destructive or regulated actions. These always require explicit approval and adapter-specific environment flags:

- Send messages to real users or groups.
- Control desktop keyboard/mouse.
- Log in to websites, compare carts, place orders or query personal accounts.
- Create cloud resources.
- Execute Ansible, Terraform, FFmpeg, Blender, browser automation or shell-backed tools.
- Produce medical, legal, financial, engineering, military or safety-sensitive outputs.

## Upstream Boundary

PanClaw references OpenClaw and Hermes Agent as integration targets, not vendored dependencies. Upstream code remains upstream. PanClaw exports a skill catalog and exposes a local API that can be registered from those runtimes.

## Project Status

`v0.1.0` is an auditable adapter skeleton. It is ready for local registry/API validation and follow-up work on real adapters, tests, packaging and CI.
