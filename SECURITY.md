# Security Policy

PanClaw intentionally treats every external channel and every model output as untrusted.

## Defaults

- Skills run in dry-run mode unless explicitly approved.
- Mutating skills require `PANCLAW_APPROVAL_TOKEN`.
- Browser, desktop, messaging and cloud mutation adapters require separate environment flags.
- Audit events are written to `PANCLAW_AUDIT_LOG` when a skill is invoked.

## Non-goals

PanClaw does not provide unofficial personal WeChat automation, payment automation, credential scraping, medical diagnosis, investment advice, legal opinions, construction sign-off or military targeting.

## Reporting

Open an issue with a minimal reproduction and do not include secrets, tokens, cookies or personal data.

