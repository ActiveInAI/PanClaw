from __future__ import annotations

import base64
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

from .base import blocked, dry_run, not_configured, optional_import, require_env


def pillow_process(payload: dict[str, Any]) -> dict[str, Any]:
    preview = dry_run(payload, "Pillow image processing dry-run.", input_path=payload["input_path"], output_path=payload["output_path"])
    if preview:
        return preview
    image_mod, error = optional_import("PIL.Image", "Pillow")
    if error:
        return error
    image = image_mod.open(payload["input_path"])
    if payload.get("max_size"):
        image.thumbnail(tuple(payload["max_size"]))
    output_path = Path(payload["output_path"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)
    return {"status": "ok", "message": "Image processed.", "output_path": str(output_path)}


def stable_diffusion_generate(payload: dict[str, Any]) -> dict[str, Any]:
    preview = dry_run(payload, "Stable Diffusion generation dry-run.", prompt=payload["prompt"])
    if preview:
        return preview
    base_url = require_env("STABLE_DIFFUSION_WEBUI_URL")
    if not base_url:
        return not_configured("STABLE_DIFFUSION_WEBUI_URL is not configured.")
    request = Request(
        f"{base_url.rstrip('/')}/sdapi/v1/txt2img",
        data=json.dumps({"prompt": payload["prompt"], "negative_prompt": payload.get("negative_prompt", "")}).encode("utf-8"),
        headers={"content-type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=120) as response:  # noqa: S310 - local service adapter.
        data = json.loads(response.read().decode("utf-8"))
    images = data.get("images", [])
    output_dir = Path(payload.get("output_dir", "artifacts/images"))
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[str] = []
    for idx, image_b64 in enumerate(images):
        path = output_dir / f"sd-{idx}.png"
        path.write_bytes(base64.b64decode(image_b64.split(",", 1)[-1]))
        paths.append(str(path))
    return {"status": "ok", "message": "Images generated.", "paths": paths}


def whisper_transcribe(payload: dict[str, Any]) -> dict[str, Any]:
    preview = dry_run(payload, "Whisper transcription dry-run.", audio_path=payload["audio_path"])
    if preview:
        return preview
    if not shutil.which("whisper"):
        return not_configured("whisper CLI is not installed.")
    command = ["whisper", payload["audio_path"]]
    if payload.get("language"):
        command.extend(["--language", str(payload["language"])])
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    return {
        "status": "ok" if completed.returncode == 0 else "failed",
        "message": "Whisper command finished.",
        "returncode": completed.returncode,
        "stdout": completed.stdout[-4000:],
        "stderr": completed.stderr[-4000:],
    }


def ffmpeg_convert(payload: dict[str, Any]) -> dict[str, Any]:
    preview = dry_run(payload, "FFmpeg conversion dry-run.", input_path=payload["input_path"], output_path=payload["output_path"])
    if preview:
        return preview
    if not shutil.which("ffmpeg"):
        return not_configured("ffmpeg binary is not installed.")
    args = [str(item) for item in payload.get("args", [])]
    if any(item in {";", "&&", "||", "|"} for item in args):
        return blocked("Shell control operators are not accepted in FFmpeg args.")
    command = ["ffmpeg", "-y", "-i", payload["input_path"], *args, payload["output_path"]]
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    return {"status": "ok" if completed.returncode == 0 else "failed", "message": "FFmpeg command finished.", "returncode": completed.returncode}


def blender_python(payload: dict[str, Any]) -> dict[str, Any]:
    preview = dry_run(payload, "Blender script dry-run.", script_path=payload["script_path"])
    if preview:
        return preview
    blender = shutil.which("blender")
    if not blender:
        return not_configured("blender binary is not installed.")
    completed = subprocess.run([blender, "--background", "--python", payload["script_path"]], check=False, capture_output=True, text=True)
    return {"status": "ok" if completed.returncode == 0 else "failed", "message": "Blender command finished.", "returncode": completed.returncode}

