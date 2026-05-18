from __future__ import annotations

from .catalog import SKILLS
from .contracts import SkillSpec

_REGISTRY: dict[str, SkillSpec] = {skill.id: skill for skill in SKILLS}


def list_skills(domain: str | None = None) -> list[SkillSpec]:
    skills = list(_REGISTRY.values())
    if domain:
        skills = [skill for skill in skills if skill.domain == domain]
    return sorted(skills, key=lambda skill: (skill.domain, skill.id))


def get_skill(skill_id: str) -> SkillSpec | None:
    return _REGISTRY.get(skill_id)


def require_skill(skill_id: str) -> SkillSpec:
    skill = get_skill(skill_id)
    if skill is None:
        raise KeyError(f"Unknown skill: {skill_id}")
    return skill


def as_openclaw_manifest() -> dict[str, object]:
    return {
        "name": "panclaw",
        "version": "0.4.1",
        "skills": [
            {
                "id": skill.id,
                "name": skill.name_en,
                "description": skill.summary,
                "domain": skill.domain,
                "risk_level": skill.risk_level.value,
                "approval_required": skill.approval_required,
                "input_schema": skill.input_schema,
                "permissions": list(skill.permissions),
                "endpoint": f"/skills/{skill.id}/run",
            }
            for skill in list_skills()
        ],
    }
