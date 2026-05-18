# PanClaw Android Package

Android packaging is a first-class release target, but it requires a mobile shell and signing identity.

Target artifacts:

- `panclaw-android-arm64.apk`
- `panclaw-android-arm64.aab`

Required release secrets:

```text
ANDROID_KEYSTORE_BASE64
ANDROID_KEYSTORE_PASSWORD
ANDROID_KEY_ALIAS
ANDROID_KEY_PASSWORD
```

The mobile app should run PanClaw as a local HTTP service and expose:

```text
http://127.0.0.1:<port>/health
http://127.0.0.1:<port>/integrations/core
```

Implementation options:

- BeeWare Briefcase Android backend for Python-native packaging.
- Kotlin shell that embeds a Python runtime and starts `panclaw.server`.
- Termux-compatible package for developer installs.

The CI workflow keeps Android as a gated target until the package name, icon, signing key and mobile shell are configured.

