from __future__ import annotations

from typing import Any

from .registry import list_skills


DEFAULT_BASE_URL = "http://127.0.0.1:8787"


def core_integrations_manifest(base_url: str = DEFAULT_BASE_URL) -> dict[str, Any]:
    return {
        "name": "PanClaw Core Integrations",
        "version": "0.4.2",
        "base_url": base_url,
        "priority": "p0",
        "integrations": [
            {
                "id": "openclaw",
                "name": "OpenClaw",
                "type": "agent_runtime",
                "manifest": f"{base_url}/integrations/openclaw/manifest",
                "status": "integrated",
                "skills": "all_panclaw_skills",
            },
            {
                "id": "hermes_agent",
                "name": "Hermes Agent",
                "type": "agent_runtime",
                "manifest": f"{base_url}/integrations/hermes/manifest",
                "status": "integrated",
                "skills": "all_panclaw_skills_as_http_tools",
            },
            {
                "id": "wechat_personal_openclaw_weixin",
                "name": "Personal WeChat via Tencent openclaw-weixin",
                "type": "official_channel_plugin",
                "source": "https://github.com/Tencent/openclaw-weixin",
                "package": "@tencent-weixin/openclaw-weixin",
                "cli_package": "@tencent-weixin/openclaw-weixin-cli",
                "status": "integrated",
                "skills": [
                    "messaging.wechat.personal.openclaw_weixin.info",
                    "messaging.wechat.personal.openclaw_weixin.quick_install",
                    "messaging.wechat.personal.openclaw_weixin.manual_install",
                    "messaging.wechat.personal.openclaw_weixin.login",
                    "messaging.wechat.personal.openclaw_weixin.status",
                ],
            },
            {
                "id": "wecom",
                "name": "WeCom",
                "type": "official_channel_plugin",
                "status": "integrated",
                "skills": ["messaging.wecom.webhook.send"],
            },
            {
                "id": "feishu",
                "name": "Feishu",
                "type": "official_channel_plugin",
                "status": "integrated",
                "skills": ["messaging.feishu.webhook.send"],
                "events": f"{base_url}/channels/feishu/events",
            },
            {
                "id": "lark",
                "name": "Lark",
                "type": "official_channel_plugin",
                "status": "integrated",
                "skills": ["messaging.lark.webhook.send"],
                "events": f"{base_url}/channels/lark/events",
            },
            {
                "id": "dingtalk",
                "name": "DingTalk",
                "type": "official_channel_plugin",
                "status": "integrated",
                "skills": ["messaging.dingtalk.webhook.send"],
                "events": f"{base_url}/channels/dingtalk/events",
            },
        ],
    }


def openclaw_manifest(base_url: str = DEFAULT_BASE_URL) -> dict[str, Any]:
    return {
        "name": "panclaw",
        "display_name": "PanClaw",
        "version": "0.4.2",
        "description": "Audited Skills and official messaging plugins for OpenClaw-compatible agents.",
        "type": "http_skill_provider",
        "base_url": base_url,
        "skills_endpoint": f"{base_url}/skills",
        "health_endpoint": f"{base_url}/health",
        "security": {
            "default_mode": "dry_run",
            "approval_header": "x-panclaw-approval-token",
            "audit": "append_only_jsonl",
        },
        "skills": [_skill_to_openclaw(skill, base_url) for skill in list_skills()],
    }


def hermes_manifest(base_url: str = DEFAULT_BASE_URL) -> dict[str, Any]:
    return {
        "name": "panclaw",
        "version": "0.4.2",
        "description": "PanClaw HTTP tools for Hermes Agent.",
        "toolsets": [
            {
                "name": "panclaw",
                "transport": "http",
                "base_url": base_url,
                "tools": [_skill_to_hermes_tool(skill, base_url) for skill in list_skills()],
            }
        ],
        "notes": [
            "Use dry_run=true unless the operator has explicitly approved the action.",
            "High-risk tools require the x-panclaw-approval-token header.",
        ],
    }


def plugin_manifest(base_url: str = DEFAULT_BASE_URL) -> dict[str, Any]:
    return {
        "name": "PanClaw Official Channel Plugins",
        "version": "0.4.2",
        "base_url": base_url,
        "channels": [
            {
                "id": "wechat_personal_openclaw_weixin",
                "name": "Personal WeChat via Tencent openclaw-weixin",
                "plugin_package": "@tencent-weixin/openclaw-weixin",
                "cli_package": "@tencent-weixin/openclaw-weixin-cli",
                "source": "https://github.com/Tencent/openclaw-weixin",
                "channel_id": "openclaw-weixin",
                "capabilities": ["qr_login", "receive_message", "send_message", "media_message", "multi_account"],
                "official_boundary": True,
                "skills": [
                    "messaging.wechat.personal.openclaw_weixin.quick_install",
                    "messaging.wechat.personal.openclaw_weixin.manual_install",
                    "messaging.wechat.personal.openclaw_weixin.login",
                    "messaging.wechat.personal.openclaw_weixin.status",
                ],
            },
            {
                "id": "wechat_official",
                "name": "WeChat Official Account",
                "callback": f"{base_url}/channels/wechat/official/callback",
                "env": ["WECHAT_OFFICIAL_TOKEN", "WECHAT_OFFICIAL_ACCESS_TOKEN"],
                "capabilities": ["verify_callback", "receive_message", "passive_reply", "customer_service_send"],
                "official_boundary": True,
            },
            {
                "id": "wecom",
                "name": "WeCom",
                "webhook_env": "WECOM_WEBHOOK_URL",
                "capabilities": ["send_text"],
                "official_boundary": True,
            },
            {
                "id": "feishu",
                "name": "Feishu",
                "webhook_env": "FEISHU_WEBHOOK_URL",
                "secret_env": "FEISHU_WEBHOOK_SECRET",
                "callback": f"{base_url}/channels/feishu/events",
                "capabilities": ["send_text", "receive_event", "url_verification"],
                "official_boundary": True,
            },
            {
                "id": "lark",
                "name": "Lark",
                "webhook_env": "LARK_WEBHOOK_URL",
                "secret_env": "LARK_WEBHOOK_SECRET",
                "callback": f"{base_url}/channels/lark/events",
                "capabilities": ["send_text", "receive_event", "url_verification"],
                "official_boundary": True,
            },
            {
                "id": "dingtalk",
                "name": "DingTalk",
                "webhook_env": "DINGTALK_WEBHOOK_URL",
                "secret_env": "DINGTALK_WEBHOOK_SECRET",
                "callback": f"{base_url}/channels/dingtalk/events",
                "capabilities": ["send_text", "receive_event"],
                "official_boundary": True,
            },
        ],
    }


def _skill_to_openclaw(skill: Any, base_url: str) -> dict[str, Any]:
    return {
        "id": skill.id,
        "name": skill.name_en,
        "description": skill.summary,
        "domain": skill.domain,
        "permissions": list(skill.permissions),
        "risk_level": skill.risk_level.value,
        "approval_required": skill.approval_required,
        "input_schema": skill.input_schema,
        "run": {
            "method": "POST",
            "url": f"{base_url}/skills/{skill.id}/run",
        },
    }


def _skill_to_hermes_tool(skill: Any, base_url: str) -> dict[str, Any]:
    return {
        "name": skill.id.replace(".", "_"),
        "title": skill.name_en,
        "description": skill.summary,
        "input_schema": skill.input_schema or {"type": "object", "properties": {}},
        "http": {
            "method": "POST",
            "url": f"{base_url}/skills/{skill.id}/run",
            "headers": {
                "content-type": "application/json",
            },
        },
        "panclaw": {
            "skill_id": skill.id,
            "risk_level": skill.risk_level.value,
            "approval_required": skill.approval_required,
        },
    }
