from __future__ import annotations

import argparse
import plistlib
import shutil
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


def write_app(app_dir: Path, version: str) -> None:
    if app_dir.exists():
        shutil.rmtree(app_dir)
    app_dir.mkdir(parents=True)
    info = {
        "CFBundleDisplayName": "PanClaw",
        "CFBundleExecutable": "PanClaw",
        "CFBundleIdentifier": "ai.active.panclaw",
        "CFBundleName": "PanClaw",
        "CFBundlePackageType": "APPL",
        "CFBundleShortVersionString": version,
        "CFBundleVersion": version,
        "MinimumOSVersion": "15.0",
        "UIDeviceFamily": [1, 2],
    }
    with (app_dir / "Info.plist").open("wb") as handle:
        plistlib.dump(info, handle)
    executable = app_dir / "PanClaw"
    executable.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    executable.chmod(0o755)
    (app_dir / "README.txt").write_text(
        "Unsigned PanClaw iOS shell. Replace with signed Xcode build when Apple signing assets are configured.\n",
        encoding="utf-8",
    )


def zip_dir(root: Path, target: Path) -> None:
    if target.exists():
        target.unlink()
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in root.rglob("*"):
            zf.write(path, path.relative_to(root.parent))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default="0.4.0")
    args = parser.parse_args()
    DIST.mkdir(exist_ok=True)
    build_root = ROOT / "build" / "ios-unsigned"
    if build_root.exists():
        shutil.rmtree(build_root)
    payload = build_root / "Payload"
    app = payload / "PanClaw.app"
    write_app(app, args.version)
    zip_dir(payload, DIST / f"PanClaw-{args.version}-ios-arm64-unsigned.ipa")

    archive = build_root / "PanClaw.xcarchive"
    app_archive = archive / "Products" / "Applications" / "PanClaw.app"
    write_app(app_archive, args.version)
    zip_dir(archive, DIST / f"PanClaw-{args.version}-ios-arm64.xcarchive.zip")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
