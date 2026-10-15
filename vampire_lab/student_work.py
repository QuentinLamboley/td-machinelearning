"""Sauvegarde des réponses d’une séance, séparée pour chaque étudiant."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import unicodedata

ROOT = Path(__file__).resolve().parents[1] / ".student_work"

def clean_name(name: str) -> str:
    name = " ".join(str(name).strip().split())
    if len(name) < 3 or len(name) > 120 or not all(c.isalpha() or c.isspace() or c in "-’'" for c in name):
        raise ValueError("Renseigne ton prénom et ton nom, sans chiffres ni caractères spéciaux.")
    if len(name.split()) < 2:
        raise ValueError("Renseigne ton prénom et ton nom.")
    return name

def student_id(name: str, access_code: str) -> str:
    normalized = unicodedata.normalize("NFKC", clean_name(name)).casefold()
    if not (6 <= len(access_code) <= 80) or not access_code.strip():
        raise ValueError("Choisis un code personnel d’au moins 6 caractères.")
    return hashlib.sha256((normalized + "\x1f" + access_code).encode("utf-8")).hexdigest()

def _safe_path(identity: str) -> Path:
    if not re.fullmatch(r"[0-9a-f]{64}", identity):
        raise ValueError("Identifiant non valide.")
    return ROOT / (identity + ".json")

def load_work(identity: str) -> dict:
    path = _safe_path(identity)
    if not path.exists():
        return {}
    try:
        if path.stat().st_size > 1_500_000:
            return {}
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError, UnicodeError):
        return {}

def save_work(identity: str, name: str, answers: dict, notes: str, etape: str | None = None) -> dict:
    """Fichier remplacé de façon atomique pour ne pas écrire de JSON partiel."""
    path = _safe_path(identity)
    safe_answers = {str(k): str(v)[:8000] for k,v in answers.items() if re.fullmatch(r"\d{2}",str(k))}
    data = {"version": 7, "etudiant": clean_name(name), "reponses": safe_answers,
            "notes": str(notes)[:30000], "enregistre_le": datetime.now(timezone.utc).isoformat()}
    if etape is not None:
        data["etape"] = str(etape)[:110]
    ROOT.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=ROOT, prefix="save-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            json.dump(data, out, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return data
