from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGETS = ROOT / "packaging" / "targets.json"

REQUIRED_TARGETS = {
    "windows-x64",
    "windows-arm64",
    "macos-x64",
    "macos-arm64",
    "linux-x64",
    "linux-arm64",
    "android-arm64",
    "ios-arm64",
}


def main() -> int:
    data = json.loads(TARGETS.read_text(encoding="utf-8"))
    found = {item["id"] for item in data["desktop"] + data["mobile"]}
    missing = sorted(REQUIRED_TARGETS - found)
    extra = sorted(found - REQUIRED_TARGETS)
    if missing:
        raise SystemExit(f"Missing required release targets: {', '.join(missing)}")
    if extra:
        print(f"Additional release targets: {', '.join(extra)}")
    print(f"Release matrix OK: {len(found)} targets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

