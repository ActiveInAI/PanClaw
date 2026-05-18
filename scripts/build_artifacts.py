from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import zipapp
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
BUILD = ROOT / "build" / "panclaw-package"
SRC = ROOT / "src"


def run(command: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(command))
    return subprocess.run(command, cwd=ROOT, check=check, text=True)


def load_version() -> str:
    for line in (ROOT / "pyproject.toml").read_text(encoding="utf-8").splitlines():
        if line.startswith("version = "):
            return line.split("=", 1)[1].strip().strip('"')
    raise RuntimeError("pyproject.toml version not found")


def clean() -> None:
    if BUILD.exists():
        shutil.rmtree(BUILD)
    if DIST.exists():
        shutil.rmtree(DIST)
    BUILD.mkdir(parents=True)
    DIST.mkdir(parents=True)


def copy_tree() -> Path:
    app = BUILD / "app"
    shutil.copytree(SRC / "panclaw", app / "panclaw", ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"))
    shutil.copy2(ROOT / "README.md", app / "README.md")
    shutil.copy2(ROOT / "LICENSE", app / "LICENSE")
    return app


def build_zipapp(app: Path, version: str) -> Path:
    target = DIST / f"panclaw-{version}.pyz"
    zipapp.create_archive(
        app,
        target=target,
        interpreter="/usr/bin/env python3",
        main="panclaw.cli:main",
        compressed=True,
    )
    return target


def build_platform_archive(app: Path, version: str, target_id: str) -> Path:
    system = platform.system().lower()
    machine = platform.machine().lower().replace("amd64", "x64").replace("x86_64", "x64").replace("aarch64", "arm64")
    target = target_id or f"{system}-{machine}"
    stage = BUILD / f"panclaw-{version}-{target}"
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)
    lib_dir = stage / "lib"
    bin_dir = stage / "bin"
    lib_dir.mkdir()
    bin_dir.mkdir()
    shutil.copytree(app / "panclaw", lib_dir / "panclaw", ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"))
    shutil.copy2(ROOT / "README.md", stage / "README.md")
    shutil.copy2(ROOT / "LICENSE", stage / "LICENSE")
    if system == "windows":
        launcher = bin_dir / "panclaw.cmd"
        launcher.write_text("@echo off\r\nset PYTHONPATH=%~dp0..\\lib\r\npython -m panclaw %*\r\n", encoding="utf-8")
        archive = DIST / f"{stage.name}.zip"
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for path in stage.rglob("*"):
                zf.write(path, path.relative_to(stage.parent))
        return archive
    launcher = bin_dir / "panclaw"
    launcher.write_text("#!/usr/bin/env sh\nPYTHONPATH=\"$(dirname \"$0\")/../lib\" exec python3 -m panclaw \"$@\"\n", encoding="utf-8")
    launcher.chmod(0o755)
    archive = DIST / f"{stage.name}.tar.gz"
    with tarfile.open(archive, "w:gz") as tf:
        tf.add(stage, arcname=stage.name)
    return archive


def build_linux_deb(app: Path, version: str, target_id: str) -> Path | None:
    if not target_id.startswith("linux-") or shutil.which("dpkg-deb") is None:
        return None
    arch = "amd64" if target_id.endswith("x64") else "arm64"
    root = BUILD / f"deb-{target_id}"
    package_root = root / f"panclaw_{version}_{arch}"
    if root.exists():
        shutil.rmtree(root)
    control = package_root / "DEBIAN" / "control"
    app_dir = package_root / "usr" / "share" / "panclaw"
    bin_dir = package_root / "usr" / "bin"
    control.parent.mkdir(parents=True)
    app_dir.mkdir(parents=True)
    bin_dir.mkdir(parents=True)
    shutil.copytree(app / "panclaw", app_dir / "panclaw", ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"))
    (bin_dir / "panclaw").write_text("#!/usr/bin/env sh\nPYTHONPATH=/usr/share/panclaw exec python3 -m panclaw \"$@\"\n", encoding="utf-8")
    (bin_dir / "panclaw").chmod(0o755)
    control.write_text(
        "\n".join(
            [
                "Package: panclaw",
                f"Version: {version}",
                "Section: utils",
                "Priority: optional",
                f"Architecture: {arch}",
                "Depends: python3 (>= 3.11)",
                "Maintainer: ActiveInAI",
                "Description: PanClaw audited skill router and official channel integration service",
                "",
            ]
        ),
        encoding="utf-8",
    )
    target = DIST / f"panclaw_{version}_{arch}.deb"
    run(["dpkg-deb", "--build", str(package_root), str(target)])
    return target


def build_macos_app_zip(app: Path, version: str, target_id: str) -> Path | None:
    if not target_id.startswith("macos-"):
        return None
    bundle = BUILD / f"PanClaw-{target_id}.app"
    if bundle.exists():
        shutil.rmtree(bundle)
    contents = bundle / "Contents"
    macos = contents / "MacOS"
    resources = contents / "Resources" / "panclaw"
    macos.mkdir(parents=True)
    resources.mkdir(parents=True)
    shutil.copytree(app / "panclaw", resources / "panclaw", ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"))
    launcher = macos / "PanClaw"
    launcher.write_text(
        "#!/usr/bin/env sh\n"
        "APP_DIR=\"$(CDPATH= cd -- \"$(dirname -- \"$0\")/../Resources/panclaw\" && pwd)\"\n"
        "PYTHONPATH=\"$APP_DIR\" exec python3 -m panclaw serve --host 127.0.0.1 --port 8787\n",
        encoding="utf-8",
    )
    launcher.chmod(0o755)
    (contents / "Info.plist").write_text(
        f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">
<plist version=\"1.0\">
<dict>
  <key>CFBundleDisplayName</key><string>PanClaw</string>
  <key>CFBundleExecutable</key><string>PanClaw</string>
  <key>CFBundleIdentifier</key><string>ai.active.panclaw</string>
  <key>CFBundleName</key><string>PanClaw</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleShortVersionString</key><string>{version}</string>
  <key>CFBundleVersion</key><string>{version}</string>
</dict>
</plist>
""",
        encoding="utf-8",
    )
    target = DIST / f"PanClaw-{version}-{target_id}.app.zip"
    if target.exists():
        target.unlink()
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in bundle.rglob("*"):
            zf.write(path, path.relative_to(bundle.parent))
    return target


def build_wheel() -> None:
    result = subprocess.run([sys.executable, "-m", "build", "--wheel", "--sdist"], cwd=ROOT, text=True, check=False)
    if result.returncode != 0:
        print("python -m build unavailable or failed; skipping wheel/sdist in this environment")


def try_pyinstaller(version: str, target_id: str) -> Path | None:
    if shutil.which("pyinstaller") is None:
        print("pyinstaller not installed; skipping onefile binary")
        return None
    name = "panclaw.exe" if platform.system().lower() == "windows" else "panclaw"
    run(
        [
            "pyinstaller",
            "--onefile",
            "--name",
            Path(name).stem,
            "--paths",
            str(SRC),
            "--distpath",
            str(BUILD / "pyinstaller-dist"),
            "--workpath",
            str(BUILD / "pyinstaller-work"),
            "--specpath",
            str(BUILD / "pyinstaller-spec"),
            str(ROOT / "scripts" / "pyinstaller_entry.py"),
        ]
    )
    built = BUILD / "pyinstaller-dist" / name
    if not built.exists():
        built = BUILD / "pyinstaller-dist" / Path(name).stem
    if not built.exists():
        return None
    suffix = ".exe" if platform.system().lower() == "windows" else ""
    target = DIST / f"panclaw-{version}-{target_id or platform.system().lower()}-onefile{suffix}"
    shutil.copy2(built, target)
    return target


def write_checksums() -> Path:
    checksum_path = DIST / "SHA256SUMS"
    rows: list[str] = []
    for path in sorted(DIST.iterdir()):
        if path.is_file() and path.name != "SHA256SUMS":
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            rows.append(f"{digest}  {path.name}")
    checksum_path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return checksum_path


def write_release_manifest(version: str, target_id: str, artifacts: list[Path]) -> Path:
    manifest = {
        "name": "PanClaw",
        "version": version,
        "target": target_id or "local",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "artifacts": [path.name for path in artifacts if path],
    }
    path = DIST / f"panclaw-{version}-{manifest['target']}-manifest.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default="")
    parser.add_argument("--skip-binary", action="store_true")
    args = parser.parse_args()

    version = load_version()
    clean()
    app = copy_tree()
    artifacts = [build_zipapp(app, version), build_platform_archive(app, version, args.target)]
    for optional in (build_linux_deb(app, version, args.target), build_macos_app_zip(app, version, args.target)):
        if optional:
            artifacts.append(optional)
    build_wheel()
    if not args.skip_binary:
        binary = try_pyinstaller(version, args.target)
        if binary:
            artifacts.append(binary)
    artifacts.append(write_release_manifest(version, args.target, artifacts))
    write_checksums()
    print(f"Built {len(artifacts)} artifacts in {DIST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
