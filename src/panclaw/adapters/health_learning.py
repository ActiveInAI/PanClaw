from __future__ import annotations

from pathlib import Path
from typing import Any

from .base import blocked, dry_run, not_configured, optional_import


def biopython_process(payload: dict[str, Any]) -> dict[str, Any]:
    preview = dry_run(payload, "BioPython processing dry-run.", operation=payload.get("operation", "gc_content"))
    if preview:
        return preview
    bio_seq, error = optional_import("Bio.Seq", "biopython")
    if error:
        return error
    sequence = bio_seq.Seq(payload["sequence"])
    operation = payload.get("operation", "gc_content")
    if operation == "reverse_complement":
        result = str(sequence.reverse_complement())
    elif operation == "transcribe":
        result = str(sequence.transcribe())
    else:
        gc = (sequence.count("G") + sequence.count("C")) / max(len(sequence), 1)
        result = {"gc_content": gc}
    return {"status": "ok", "message": "BioPython operation completed. Not medical advice.", "result": result}


def medical_rag_search(payload: dict[str, Any]) -> dict[str, Any]:
    preview = dry_run(payload, "Medical RAG search dry-run.", query=payload["query"])
    if preview:
        return preview
    root = Path(payload.get("knowledge_base", "data/private/medical_rag"))
    if not root.exists():
        return not_configured("Local medical knowledge base is not configured.", expected_path=str(root))
    matches: list[dict[str, str]] = []
    query = payload["query"].lower()
    for path in root.rglob("*.md"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if query in text.lower():
            matches.append({"path": str(path), "excerpt": text[:500]})
        if len(matches) >= int(payload.get("limit", 5)):
            break
    return {"status": "ok", "message": "Medical references retrieved. Not diagnosis.", "matches": matches}


def sympy_solve(payload: dict[str, Any]) -> dict[str, Any]:
    preview = dry_run(payload, "SymPy solve dry-run.", expression=payload["expression"])
    if preview:
        return preview
    sympy, error = optional_import("sympy", "sympy")
    if error:
        return error
    expr = sympy.sympify(payload["expression"])
    variable = sympy.symbols(payload.get("variable", "x"))
    result = sympy.solve(expr, variable)
    return {"status": "ok", "message": "Expression solved.", "result": [str(item) for item in result]}


def kiwix_search(payload: dict[str, Any]) -> dict[str, Any]:
    preview = dry_run(payload, "Kiwix search dry-run.", query=payload["query"], archive=payload.get("archive"))
    if preview:
        return preview
    return blocked("Kiwix search requires a selected external CLI/service adapter and local ZIM archive review.")

