from __future__ import annotations

import unittest

from panclaw.registry import get_skill, list_skills
from panclaw.router import run_skill


class RegistryTests(unittest.TestCase):
    def test_skill_ids_are_unique(self) -> None:
        skills = list_skills()
        self.assertEqual(len(skills), len({skill.id for skill in skills}))

    def test_required_domains_exist(self) -> None:
        domains = {skill.domain for skill in list_skills()}
        for domain in {
            "messaging",
            "office_pdf",
            "image",
            "audio_video",
            "three_d",
            "computer_control",
            "observability",
            "cloud",
            "finance",
            "commerce_life",
            "health_medical",
            "learning",
            "sports_military",
            "aec_gis",
            "culture_fengshui",
        }:
            self.assertIn(domain, domains)

    def test_approval_gate_blocks_real_high_risk_execution(self) -> None:
        result = run_skill("messaging.wecom.webhook.send", {"dry_run": False, "text": "hello"})
        self.assertEqual(result.status, "approval_required")

    def test_low_risk_snapshot_runs(self) -> None:
        result = run_skill("observability.local.snapshot", {"dry_run": True})
        self.assertEqual(result.status, "ok")
        self.assertIn("snapshot", result.data)

    def test_lookup(self) -> None:
        self.assertIsNotNone(get_skill("office.pdf.extract"))


if __name__ == "__main__":
    unittest.main()

