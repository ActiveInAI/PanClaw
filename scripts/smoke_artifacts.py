from __future__ import annotations

import argparse
import hashlib
import json
import platform
import plistlib
import shutil
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


class SmokeFailure(AssertionError):
    pass


def load_version() -> str:
    for line in (ROOT / "pyproject.toml").read_text(encoding="utf-8").splitlines():
        if line.startswith("version = "):
            return line.split("=", 1)[1].strip().strip('"')
    raise SmokeFailure("pyproject.toml version not found")


def require_path(path: Path) -> Path:
    if not path.exists():
        raise SmokeFailure(f"Missing artifact: {path}")
    if path.is_file() and path.stat().st_size <= 0:
        raise SmokeFailure(f"Empty artifact: {path}")
    return path


def verify_checksums(dist: Path) -> None:
    checksum_path = require_path(dist / "SHA256SUMS")
    rows = [line.strip().split("  ", 1) for line in checksum_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not rows:
        raise SmokeFailure("SHA256SUMS is empty")
    for digest, name in rows:
        path = require_path(dist / name)
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != digest:
            raise SmokeFailure(f"Checksum mismatch for {name}")


def run_command(command: list[str]) -> str:
    result = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30, check=False)
    if result.returncode != 0:
        raise SmokeFailure(f"Command failed: {' '.join(command)}\nstdout={result.stdout}\nstderr={result.stderr}")
    return result.stdout


def assert_json_contains_health(text: str) -> None:
    data = json.loads(text)
    raw = json.dumps(data, ensure_ascii=False)
    if "messaging.channels.health" not in raw and "channels/health" not in raw:
        raise SmokeFailure("Packaged CLI output does not expose channel health integration")


def smoke_pyz(dist: Path, version: str) -> None:
    pyz = require_path(dist / f"panclaw-{version}.pyz")
    assert_json_contains_health(run_command([sys.executable, str(pyz), "export-core"]))


def smoke_desktop(args: argparse.Namespace) -> None:
    version = args.version or load_version()
    dist = Path(args.dist)
    target = args.target
    verify_checksums(dist)
    smoke_pyz(dist, version)
    manifest = json.loads(require_path(dist / f"panclaw-{version}-{target}-manifest.json").read_text(encoding="utf-8"))
    if manifest["version"] != version or manifest["target"] != target:
        raise SmokeFailure(f"Bad manifest metadata: {manifest}")

    if target.startswith("windows-"):
        smoke_windows_zip(dist, version, target)
    elif target.startswith(("linux-", "macos-")):
        smoke_posix_tar(dist, version, target)
    else:
        raise SmokeFailure(f"Unknown desktop target: {target}")

    if target.startswith("linux-"):
        smoke_deb(dist, version, target)
    if target.startswith("macos-"):
        smoke_macos_app_zip(dist, version, target)
    smoke_native_onefile_if_present(dist, version, target)
    print(f"Desktop smoke OK: {target}")


def smoke_windows_zip(dist: Path, version: str, target: str) -> None:
    archive = require_path(dist / f"panclaw-{version}-{target}.zip")
    with zipfile.ZipFile(archive) as zf:
        names = set(zf.namelist())
    root = f"panclaw-{version}-{target}"
    expected = {
        f"{root}/bin/panclaw.cmd",
        f"{root}/lib/panclaw/cli.py",
        f"{root}/lib/panclaw/adapters/messaging.py",
    }
    missing = expected - names
    if missing:
        raise SmokeFailure(f"Windows zip missing files: {sorted(missing)}")


def smoke_posix_tar(dist: Path, version: str, target: str) -> None:
    archive = require_path(dist / f"panclaw-{version}-{target}.tar.gz")
    with tarfile.open(archive, "r:gz") as tf:
        names = set(tf.getnames())
    root = f"panclaw-{version}-{target}"
    expected = {
        f"{root}/bin/panclaw",
        f"{root}/lib/panclaw/cli.py",
        f"{root}/lib/panclaw/adapters/messaging.py",
    }
    missing = expected - names
    if missing:
        raise SmokeFailure(f"POSIX archive missing files: {sorted(missing)}")


def smoke_deb(dist: Path, version: str, target: str) -> None:
    arch = "amd64" if target.endswith("x64") else "arm64"
    package = require_path(dist / f"panclaw_{version}_{arch}.deb")
    if not shutil.which("dpkg-deb"):
        return
    info = run_command(["dpkg-deb", "--info", str(package)])
    contents = run_command(["dpkg-deb", "--contents", str(package)])
    if f"Version: {version}" not in info or f"Architecture: {arch}" not in info:
        raise SmokeFailure("DEB metadata smoke failed")
    if "usr/bin/panclaw" not in contents or "usr/share/panclaw/panclaw/cli.py" not in contents:
        raise SmokeFailure("DEB contents smoke failed")


def smoke_macos_app_zip(dist: Path, version: str, target: str) -> None:
    archive = require_path(dist / f"PanClaw-{version}-{target}.app.zip")
    with zipfile.ZipFile(archive) as zf:
        names = set(zf.namelist())
        plist_name = f"PanClaw-{target}.app/Contents/Info.plist"
        if plist_name not in names:
            raise SmokeFailure("macOS app Info.plist missing")
        info = plistlib.loads(zf.read(plist_name))
    if info.get("CFBundleShortVersionString") != version:
        raise SmokeFailure("macOS app version smoke failed")
    expected = {
        f"PanClaw-{target}.app/Contents/MacOS/PanClaw",
        f"PanClaw-{target}.app/Contents/Resources/panclaw/panclaw/cli.py",
    }
    missing = expected - names
    if missing:
        raise SmokeFailure(f"macOS app zip missing files: {sorted(missing)}")


def smoke_native_onefile_if_present(dist: Path, version: str, target: str) -> None:
    suffix = ".exe" if target.startswith("windows-") else ""
    binary = dist / f"panclaw-{version}-{target}-onefile{suffix}"
    if not binary.exists() or not is_native_target(target):
        return
    assert_json_contains_health(run_command([str(binary), "export-core"]))


def is_native_target(target: str) -> bool:
    system = platform.system().lower()
    machine = platform.machine().lower().replace("amd64", "x64").replace("x86_64", "x64").replace("aarch64", "arm64")
    return target == f"{system}-{machine}"


def smoke_android(args: argparse.Namespace) -> None:
    version = args.version or load_version()
    dist = Path(args.dist)
    apk = require_path(dist / f"panclaw-{version}-android-arm64-debug.apk")
    aab = require_path(dist / f"panclaw-{version}-android-arm64-debug.aab")
    with zipfile.ZipFile(apk) as zf:
        names = set(zf.namelist())
    if "AndroidManifest.xml" not in names or "classes.dex" not in names:
        raise SmokeFailure("Android APK structure smoke failed")
    with zipfile.ZipFile(aab) as zf:
        names = set(zf.namelist())
    if "base/manifest/AndroidManifest.xml" not in names:
        raise SmokeFailure("Android AAB manifest smoke failed")
    print("Android smoke OK: android-arm64")


def smoke_ios(args: argparse.Namespace) -> None:
    version = args.version or load_version()
    dist = Path(args.dist)
    ipa = require_path(dist / f"PanClaw-{version}-ios-arm64-unsigned.ipa")
    archive = require_path(dist / f"PanClaw-{version}-ios-arm64.xcarchive.zip")
    with zipfile.ZipFile(ipa) as zf:
        names = set(zf.namelist())
        plist_name = "Payload/PanClaw.app/Info.plist"
        if plist_name not in names:
            raise SmokeFailure("iOS IPA Info.plist missing")
        info = plistlib.loads(zf.read(plist_name))
    if info.get("CFBundleShortVersionString") != version:
        raise SmokeFailure("iOS IPA version smoke failed")
    if "Payload/PanClaw.app/PanClaw" not in names:
        raise SmokeFailure("iOS IPA executable placeholder missing")
    with zipfile.ZipFile(archive) as zf:
        names = set(zf.namelist())
    if "PanClaw.xcarchive/Products/Applications/PanClaw.app/Info.plist" not in names:
        raise SmokeFailure("iOS xcarchive structure smoke failed")
    print("iOS smoke OK: ios-arm64")


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke-test PanClaw release artifacts.")
    parser.add_argument("kind", choices=["desktop", "android", "ios"])
    parser.add_argument("--target", default="")
    parser.add_argument("--dist", default=str(DIST))
    parser.add_argument("--version", default="")
    args = parser.parse_args()
    if args.kind == "desktop":
        if not args.target:
            raise SmokeFailure("--target is required for desktop smoke tests")
        smoke_desktop(args)
    elif args.kind == "android":
        smoke_android(args)
    elif args.kind == "ios":
        smoke_ios(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
