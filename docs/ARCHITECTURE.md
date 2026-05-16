# PanClaw Architecture

## Positioning

PanClaw = OpenClaw-style channel/control plane + Hermes-style long-running agent traces + audited Skills.

It is not a fork of OpenClaw or Hermes Agent. It is an adapter layer that can be called by either system, or by any model runtime through HTTP/CLI.

## Layers

1. `ChannelGateway`: WeCom, Feishu, DingTalk, official WeChat-compatible channels and future OpenClaw channels.
2. `AgentOrchestrator`: planner/generator/evaluator separation and long-running job state.
3. `SkillRegistry`: data-driven catalog of capabilities, permissions, schemas, risk and upstreams.
4. `ToolRouter`: one entry point for every skill call.
5. `Approver`: human or token-gated approval for mutating actions.
6. `AuditLog`: append-only local JSONL evidence for invocations.
7. `AdapterBoundary`: optional libraries, CLIs, SaaS APIs and GPL/heavy runtimes stay outside the core package.

## Runtime Chain

```text
Request
  -> Planner
  -> ToolRouter
  -> Skill input validation
  -> Risk and permission check
  -> Approval gate
  -> Adapter call
  -> Evaluator summary
  -> Audit event
  -> Structured response
```

## Data Contracts

Each skill records:

- stable `id`
- domain and tags
- upstream project references
- input/output JSON-schema-like dictionaries
- permissions
- risk level
- approval requirement
- sandbox mode
- license boundary

The catalog in `src/panclaw/catalog.py` is the source of truth.

