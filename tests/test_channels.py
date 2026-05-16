from __future__ import annotations

import unittest

from panclaw.channels import (
    add_dingtalk_signature_to_url,
    add_feishu_lark_signature,
    build_wechat_passive_text_reply,
    parse_feishu_lark_event,
    parse_wechat_official_xml,
    verify_wechat_official_signature,
    wechat_official_signature,
)
from panclaw.integrations import hermes_manifest, openclaw_manifest, plugin_manifest
from panclaw.registry import get_skill
from panclaw.router import run_skill


class ChannelTests(unittest.TestCase):
    def test_wechat_official_signature(self) -> None:
        signature = wechat_official_signature("token", "123", "nonce")
        self.assertTrue(verify_wechat_official_signature("token", signature, "123", "nonce"))
        self.assertFalse(verify_wechat_official_signature("token", "bad", "123", "nonce"))

    def test_wechat_xml_parse_and_reply(self) -> None:
        xml = b"""
        <xml>
          <ToUserName><![CDATA[gh_test]]></ToUserName>
          <FromUserName><![CDATA[user_openid]]></FromUserName>
          <MsgType><![CDATA[text]]></MsgType>
          <Content><![CDATA[hello]]></Content>
        </xml>
        """
        event = parse_wechat_official_xml(xml)
        self.assertEqual(event.channel, "wechat_official")
        self.assertEqual(event.text, "hello")
        reply = build_wechat_passive_text_reply("user_openid", "gh_test", "ok")
        self.assertIn(b"<Content>ok</Content>", reply)

    def test_feishu_lark_signature_fields(self) -> None:
        body = add_feishu_lark_signature({"msg_type": "text"}, "secret", timestamp=123)
        self.assertEqual(body["timestamp"], "123")
        self.assertIn("sign", body)

    def test_dingtalk_signature_url(self) -> None:
        url = add_dingtalk_signature_to_url("https://oapi.dingtalk.com/robot/send?access_token=x", "secret", timestamp=123)
        self.assertIn("timestamp=123", url)
        self.assertIn("sign=", url)

    def test_feishu_challenge(self) -> None:
        parsed = parse_feishu_lark_event({"type": "url_verification", "challenge": "abc", "token": "t"}, expected_token="t")
        self.assertEqual(parsed["status"], "challenge")
        self.assertEqual(parsed["challenge"], "abc")

    def test_lark_skill_registered(self) -> None:
        self.assertIsNotNone(get_skill("messaging.lark.webhook.send"))
        result = run_skill("messaging.lark.webhook.send", {"dry_run": True, "text": "hello"})
        self.assertEqual(result.status, "dry_run")

    def test_manifests_include_plugins(self) -> None:
        self.assertGreater(len(openclaw_manifest()["skills"]), 1)
        hermes = hermes_manifest()
        self.assertEqual(hermes["toolsets"][0]["name"], "panclaw")
        plugins = plugin_manifest()
        channels = {item["id"] for item in plugins["channels"]}
        self.assertIn("wechat_official", channels)
        self.assertIn("lark", channels)


if __name__ == "__main__":
    unittest.main()
