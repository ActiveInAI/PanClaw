from __future__ import annotations

from pathlib import Path
from typing import Any

from .base import dry_run, optional_import


def pdf_extract(payload: dict[str, Any]) -> dict[str, Any]:
    path = Path(payload["path"])
    preview = dry_run(payload, "PDF extraction dry-run.", path=str(path))
    if preview:
        return preview
    fitz, error = optional_import("fitz", "PyMuPDF")
    if error:
        return error
    doc = fitz.open(path)
    pages = [page.get_text("text") for page in doc]
    return {"status": "ok", "message": "PDF extracted.", "page_count": len(pages), "text": "\n".join(pages)}


def docx_generate(payload: dict[str, Any]) -> dict[str, Any]:
    output_path = Path(payload["output_path"])
    preview = dry_run(payload, "DOCX generation dry-run.", output_path=str(output_path))
    if preview:
        return preview
    docx, error = optional_import("docx", "python-docx")
    if error:
        return error
    document = docx.Document()
    if payload.get("title"):
        document.add_heading(str(payload["title"]), level=1)
    for paragraph in payload.get("paragraphs", []):
        document.add_paragraph(str(paragraph))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    document.save(output_path)
    return {"status": "ok", "message": "DOCX generated.", "output_path": str(output_path)}


def xlsx_generate(payload: dict[str, Any]) -> dict[str, Any]:
    output_path = Path(payload["output_path"])
    preview = dry_run(payload, "XLSX generation dry-run.", output_path=str(output_path), rows=len(payload.get("rows", [])))
    if preview:
        return preview
    openpyxl, error = optional_import("openpyxl", "openpyxl")
    if error:
        return error
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    for row in payload.get("rows", []):
        sheet.append(row)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(output_path)
    return {"status": "ok", "message": "XLSX generated.", "output_path": str(output_path)}

