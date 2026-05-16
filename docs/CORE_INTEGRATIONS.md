# Core Integrations

PanClaw P0 integrations are:

1. OpenClaw
2. Hermes Agent
3. Personal WeChat via Tencent `openclaw-weixin`
4. WeCom
5. Feishu
6. Lark
7. DingTalk

These are not optional catalog examples. They are first-class integration targets exposed through:

```text
GET /integrations/core
GET /integrations/openclaw/manifest
GET /integrations/hermes/manifest
GET /plugins
```

CLI export:

```bash
env PYTHONPATH=src python3 -m panclaw export-core
env PYTHONPATH=src python3 -m panclaw export-openclaw
env PYTHONPATH=src python3 -m panclaw export-hermes
env PYTHONPATH=src python3 -m panclaw export-plugins
```

## Personal WeChat

Personal WeChat uses Tencent's official OpenClaw Weixin plugin:

```text
https://github.com/Tencent/openclaw-weixin
@tencent-weixin/openclaw-weixin
@tencent-weixin/openclaw-weixin-cli
```

Core skills:

```text
messaging.wechat.personal.openclaw_weixin.info
messaging.wechat.personal.openclaw_weixin.quick_install
messaging.wechat.personal.openclaw_weixin.manual_install
messaging.wechat.personal.openclaw_weixin.login
messaging.wechat.personal.openclaw_weixin.status
```

## Enterprise Messaging

Core skills:

```text
messaging.wecom.webhook.send
messaging.feishu.webhook.send
messaging.lark.webhook.send
messaging.dingtalk.webhook.send
```

Feishu, Lark and DingTalk event endpoints:

```text
POST /channels/feishu/events
POST /channels/lark/events
POST /channels/dingtalk/events
```

Real sending and plugin mutation require explicit approval and environment gates.

