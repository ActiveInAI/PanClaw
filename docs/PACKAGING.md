# Packaging

PanClaw release targets:

| Target | Artifacts | Status |
|---|---|---|
| Windows x64 | `.zip`, `.exe` | GitHub Actions |
| Windows arm64 | `.zip` | GitHub Actions |
| macOS x64 | `.tar.gz`, app zip | GitHub Actions |
| macOS arm64 | `.tar.gz`, app zip | GitHub Actions |
| Linux x64 | `.tar.gz`, `.deb` target | GitHub Actions |
| Linux arm64 | `.tar.gz`, `.deb` target | GitHub Actions |
| Android arm64 | `.apk`, `.aab` | GitHub Actions debug shell |
| iOS arm64 | `.xcarchive`, `.ipa` | unsigned shell, signing gated |

## Local Build

```bash
python3 -m unittest discover -s tests
python3 scripts/build_artifacts.py --target linux-x64 --skip-binary
```

Artifacts are written to `dist/`.

## Universal Runtime Artifact

Every build creates:

```text
panclaw-<version>.pyz
```

Run it with:

```bash
python3 panclaw-<version>.pyz list
python3 panclaw-<version>.pyz serve --host 127.0.0.1 --port 8787
```

## Platform Installers

Developer installers:

```bash
sh packaging/installers/install.sh
powershell -ExecutionPolicy Bypass -File packaging/installers/install.ps1
```

## Release CI

The workflow `.github/workflows/release-packages.yml` builds desktop/server packages on release tags.

Android debug APK/AAB packages are built by CI. iOS unsigned shell artifacts are built by CI; App Store/TestFlight/device installation still requires Apple signing credentials.

The release matrix is enforced by:

```bash
python3 scripts/check_release_matrix.py
```
