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

As of 2026-05-16, PanClaw treats `Tencent/openclaw-weixin` as the official personal WeChat plugin boundary for OpenClaw.

Source:

```text
https://github.com/Tencent/openclaw-weixin
```

Official package names:

```text
@tencent-weixin/openclaw-weixin
@tencent-weixin/openclaw-weixin-cli
```

PanClaw still does not use reverse-engineered personal WeChat protocols, desktop click automation or QR session hijacking. It delegates personal WeChat connectivity to Tencent's official OpenClaw Weixin plugin.

Quick install dry-run:

```bash
env PYTHONPATH=src python3 -m panclaw run messaging.wechat.personal.openclaw_weixin.quick_install
```

Manual install dry-run:

```bash
env PYTHONPATH=src python3 -m panclaw run messaging.wechat.personal.openclaw_weixin.manual_install
```

QR login dry-run:

```bash
env PYTHONPATH=src python3 -m panclaw run messaging.wechat.personal.openclaw_weixin.login
```

Real execution requires:

```bash
PANCLAW_ENABLE_OPENCLAW_PLUGIN_MUTATION=1
PANCLAW_APPROVAL_TOKEN=...
```

Then pass `--execute --approval-token <token>`.

The official manual flow is:

```bash
npx -y @tencent-weixin/openclaw-weixin-cli install

openclaw plugins install "@tencent-weixin/openclaw-weixin"
openclaw config set plugins.entries.openclaw-weixin.enabled true
openclaw channels login --channel openclaw-weixin
openclaw gateway restart
```

For multiple WeChat accounts, use:

```bash
openclaw channels login --channel openclaw-weixin
openclaw config set session.dmScope per-account-channel-peer
```

## WeChat Official Account

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

Official Account callback URL:

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
