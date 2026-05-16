from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    REGULATED = "regulated"
    DESTRUCTIVE = "destructive"


class SkillStatus(str, Enum):
    READY = "ready"
    OPTIONAL_DEPENDENCY = "optional_dependency"
    EXTERNAL_SERVICE = "external_service"
    LICENSE_GATED = "license_gated"
    OFFICIAL_API_REQUIRED = "official_api_required"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class UpstreamProject:
    name: str
    url: str
    license: str | None = None
    boundary: str = "optional_adapter"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SkillSpec:
    id: str
    name_zh: str
    name_en: str
    domain: str
    summary: str
    entrypoint: str
    upstreams: tuple[UpstreamProject, ...] = ()
    input_schema: dict[str, Any] = field(default_factory=dict)
    output_schema: dict[str, Any] = field(default_factory=dict)
    permissions: tuple[str, ...] = ()
    risk_level: RiskLevel = RiskLevel.LOW
    status: SkillStatus = SkillStatus.READY
    approval_required: bool = False
    sandbox: str = "local_process"
    license_boundary: str = "core_safe"
    tags: tuple[str, ...] = ()
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["risk_level"] = self.risk_level.value
        data["status"] = self.status.value
        data["upstreams"] = [upstream.to_dict() for upstream in self.upstreams]
        return data


@dataclass(frozen=True)
class SkillResult:
    skill_id: str
    status: str
    message: str
    data: dict[str, Any] = field(default_factory=dict)
    audit_id: str | None = None
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

