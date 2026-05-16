from __future__ import annotations

import json
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any
from urllib.request import urlopen

from .base import blocked, dry_run, not_configured, optional_import


def sports_scrapy_collect(payload: dict[str, Any]) -> dict[str, Any]:
    preview = dry_run(payload, "Sports Scrapy collection dry-run.", source=payload["source"])
    if preview:
        return preview
    return blocked("Scrapy spiders must be registered per source before execution.")


def military_rss_brief(payload: dict[str, Any]) -> dict[str, Any]:
    preview = dry_run(payload, "Military public RSS brief dry-run.", feeds=payload["feeds"])
    if preview:
        return preview
    items: list[dict[str, str]] = []
    for feed in payload["feeds"]:
        with urlopen(feed, timeout=20) as response:  # noqa: S310 - public RSS URL supplied by operator.
            root = ET.fromstring(response.read())
        for item in root.findall(".//item")[: int(payload.get("per_feed", 5))]:
            title = item.findtext("title") or ""
            link = item.findtext("link") or ""
            items.append({"title": title, "link": link})
    return {"status": "ok", "message": "Public RSS items collected; no operational guidance.", "items": items}


def freecad_script(payload: dict[str, Any]) -> dict[str, Any]:
    preview = dry_run(payload, "FreeCAD script dry-run.", script_path=payload["script_path"])
    if preview:
        return preview
    freecad = shutil.which("FreeCADCmd") or shutil.which("freecadcmd")
    if not freecad:
        return not_configured("FreeCADCmd/freecadcmd is not installed.")
    completed = subprocess.run([freecad, payload["script_path"]], check=False, capture_output=True, text=True)
    return {"status": "ok" if completed.returncode == 0 else "failed", "message": "FreeCAD command finished.", "returncode": completed.returncode}


def gdal_inspect(payload: dict[str, Any]) -> dict[str, Any]:
    preview = dry_run(payload, "GDAL inspect dry-run.", path=payload["path"])
    if preview:
        return preview
    gdalinfo = shutil.which("gdalinfo")
    if gdalinfo:
        completed = subprocess.run([gdalinfo, "-json", payload["path"]], check=False, capture_output=True, text=True)
        data = json.loads(completed.stdout) if completed.returncode == 0 and completed.stdout else {}
        return {"status": "ok" if completed.returncode == 0 else "failed", "message": "GDAL inspect finished.", "metadata": data}
    osgeo, error = optional_import("osgeo.gdal", "GDAL")
    if error:
        return error
    dataset = osgeo.Open(payload["path"])
    if dataset is None:
        return blocked("GDAL could not open the dataset.")
    return {"status": "ok", "message": "GDAL dataset opened.", "raster_x_size": dataset.RasterXSize, "raster_y_size": dataset.RasterYSize}


def lunar_compute(payload: dict[str, Any]) -> dict[str, Any]:
    preview = dry_run(payload, "Lunar/traditional-culture computation dry-run.", date=payload["date"], mode=payload.get("mode", "lunar"))
    if preview:
        return preview
    lunar_python, error = optional_import("lunar_python", "lunar-python")
    if error:
        return error
    from datetime import datetime

    solar = lunar_python.Solar.fromDate(datetime.fromisoformat(payload["date"]))
    lunar = solar.getLunar()
    return {
        "status": "ok",
        "message": "Lunar data computed. Informational only.",
        "lunar": {
            "year": lunar.getYearInChinese(),
            "month": lunar.getMonthInChinese(),
            "day": lunar.getDayInChinese(),
        },
    }

