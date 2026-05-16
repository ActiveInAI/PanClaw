# Official Channel Plugins

PanClaw integrates messaging platforms only through official boundaries.

## OpenClaw

Export a manifest:

```bash
env PYTHONPATH=src python3 -m panclaw export-openclaw --base-url http://127.0.0.1:8787
```

Runtime endpoints:

```text
GET  /integrations/openclaw/manifest
POST /skills/{skill_id}/run
```

OpenClaw should call PanClaw skills through the HTTP run endpoint and pass `dry_run=true` unless a human has approved execution.

## Hermes Agent

Export a Hermes-compatible tool manifest:

```bash
env PYTHONPATH=src python3 -m panclaw export-hermes --base-url http://127.0.0.1:8787
```

Runtime endpoint:

```text
GET /integrations/hermes/manifest
```

Hermes tools use the same PanClaw approval header:

```text
x-panclaw-approval-token: <PANCLAW_APPROVAL_TOKEN>
```

## WeChat Personal Account

PanClaw does not automate personal WeChat accounts. There is no enabled personal-account plugin that drives a user account through reverse-engineered protocols, Web hooks, desktop control or QR session hijacking.

Supported official WeChat boundary:

- WeChat Official Account callback verification.
- WeChat Official Account passive text reply.
- WeChat Official Account customer-service message API, gated by `WECHAT_OFFICIAL_ACCESS_TOKEN`.

Configuration:

```bash
WECHAT_OFFICIAL_TOKEN=...
WECHAT_OFFICIAL_ACCESS_TOKEN=...
PANCLAW_ENABLE_MESSAGE_SEND=1
```

Callback URL:

```text
GET/POST http://127.0.0.1:8787/channels/wechat/official/callback
```

Skill:

```bash
env PYTHONPATH=src python3 -m panclaw run messaging.wechat.official_account.customer_service_send \
  --payload '{"dry_run": true, "openid": "OPENID", "text": "hello"}'
```

## WeCom

Configuration:

```bash
WECOM_WEBHOOK_URL=...
PANCLAW_ENABLE_MESSAGE_SEND=1
```

Skill:

```text
messaging.wecom.webhook.send
```

## Feishu

Configuration:

```bash
FEISHU_WEBHOOK_URL=...
FEISHU_WEBHOOK_SECRET=...
FEISHU_VERIFICATION_TOKEN=...
PANCLAW_ENABLE_MESSAGE_SEND=1
```

Callback:

```text
POST /channels/feishu/events
```

Skill:

```text
messaging.feishu.webhook.send
```

## Lark

Configuration:

```bash
LARK_WEBHOOK_URL=...
LARK_WEBHOOK_SECRET=...
LARK_VERIFICATION_TOKEN=...
PANCLAW_ENABLE_MESSAGE_SEND=1
```

Callback:

```text
POST /channels/lark/events
```

Skill:

```text
messaging.lark.webhook.send
```

## DingTalk

Configuration:

```bash
DINGTALK_WEBHOOK_URL=...
DINGTALK_WEBHOOK_SECRET=...
PANCLAW_ENABLE_MESSAGE_SEND=1
```

Callback:

```text
POST /channels/dingtalk/events
```

Skill:

```text
messaging.dingtalk.webhook.send
```

## Approval

Real sending requires all of:

- `dry_run=false`
- `PANCLAW_ENABLE_MESSAGE_SEND=1`
- matching `x-panclaw-approval-token` or CLI `--approval-token`
- configured official webhook/API credential

