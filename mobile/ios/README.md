# PanClaw iOS Package

iOS packaging is a first-class release target, but it cannot produce a distributable IPA without Apple signing assets.

Target artifacts:

- `PanClaw.xcarchive`
- `PanClaw.ipa`

Required release secrets:

```text
APPLE_DEVELOPER_TEAM_ID
IOS_SIGNING_CERTIFICATE_BASE64
IOS_SIGNING_CERTIFICATE_PASSWORD
IOS_PROVISIONING_PROFILE_BASE64
```

The iOS app should run PanClaw as a local HTTP service and expose:

```text
http://127.0.0.1:<port>/health
http://127.0.0.1:<port>/integrations/core
```

Implementation options:

- BeeWare Briefcase iOS backend for Python-native packaging.
- Swift shell that embeds Python and starts `panclaw.server`.

The CI workflow keeps iOS as a gated target until bundle ID, signing certificates, provisioning profiles and app metadata are configured.

