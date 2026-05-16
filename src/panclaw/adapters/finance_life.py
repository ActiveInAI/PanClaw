from __future__ import annotations

import os
from typing import Any

from .base import blocked, dry_run, not_configured, optional_import, require_enabled


def akshare_query(payload: dict[str, Any]) -> dict[str, Any]:
    preview = dry_run(payload, "AkShare query dry-run.", dataset=payload["dataset"], disclaimer="market_data_only")
    if preview:
        return preview
    akshare, error = optional_import("akshare", "akshare")
    if error:
        return error
    func = getattr(akshare, payload["dataset"], None)
    if not callable(func):
        return blocked(f"AkShare dataset function not found: {payload['dataset']}")
    frame = func(**payload.get("params", {}))
    rows = frame.head(int(payload.get("limit", 20))).to_dict(orient="records")
    return {"status": "ok", "message": "AkShare data fetched. Not investment advice.", "rows": rows}


def tushare_query(payload: dict[str, Any]) -> dict[str, Any]:
    preview = dry_run(payload, "TuShare query dry-run.", api=payload["api"], disclaimer="market_data_only")
    if preview:
        return preview
    token = os.environ.get("TUSHARE_TOKEN")
    if not token:
        return not_configured("TUSHARE_TOKEN is not configured.")
    tushare, error = optional_import("tushare", "tushare")
    if error:
        return error
    pro = tushare.pro_api(token)
    func = getattr(pro, payload["api"], None)
    if not callable(func):
        return blocked(f"TuShare API not found: {payload['api']}")
    frame = func(**payload.get("params", {}))
    rows = frame.head(int(payload.get("limit", 20))).to_dict(orient="records")
    return {"status": "ok", "message": "TuShare data fetched. Not investment advice.", "rows": rows}


def browser_price_compare(payload: dict[str, Any]) -> dict[str, Any]:
    preview = dry_run(payload, "Browser price comparison dry-run.", query=payload["query"], sites=payload.get("sites", []))
    if preview:
        return preview
    if not require_enabled("PANCLAW_ENABLE_BROWSER_AUTOMATION"):
        return blocked("PANCLAW_ENABLE_BROWSER_AUTOMATION=1 is required.")
    return blocked("Real browser price comparison is not implemented in v0.1; checkout will remain disabled.")


def browser_tracking(payload: dict[str, Any]) -> dict[str, Any]:
    preview = dry_run(payload, "Browser logistics tracking dry-run.", carrier=payload.get("carrier"), tracking_number=payload["tracking_number"])
    if preview:
        return preview
    if not require_enabled("PANCLAW_ENABLE_BROWSER_AUTOMATION"):
        return blocked("PANCLAW_ENABLE_BROWSER_AUTOMATION=1 is required.")
    return blocked("Real browser tracking is not implemented in v0.1; use official carrier APIs where available.")


def food_delivery_draft(payload: dict[str, Any]) -> dict[str, Any]:
    preview = dry_run(payload, "Food delivery draft dry-run.", restaurant=payload["restaurant"], items=payload["items"])
    if preview:
        return preview
    return blocked("Final order submission and payment are not exposed. Draft-only workflow requires a browser adapter implementation.")

