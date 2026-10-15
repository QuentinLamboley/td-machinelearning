"""Create project-local venv and launch Streamlit with the exact interpreter used for pip."""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import venv
from pathlib import Path

BASE = Path(__file__).resolve().parent
VENV = BASE / ".venv"
PYTHON = VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
STAMP = VENV / ".esmiha_requirements_sha256"


def main():
    if sys.version_info < (3, 10):
        raise SystemExit("Python 3.10 ou plus récent est nécessaire (3.11-3.13 recommandé).")
    os.chdir(BASE)
    if not PYTHON.is_file():
        print("[TD Machine Learning] Création de l'environnement Python local...", flush=True)
        try:
            venv.EnvBuilder(with_pip=True).create(VENV)
        except Exception as exc:
            raise SystemExit(f"Échec de création du venv : {exc}. Vérifiez que python3-venv / ensurepip est disponible.")
    req = BASE / "requirements.txt"
    req_hash = hashlib.sha256(req.read_bytes()).hexdigest()
    if not STAMP.exists() or STAMP.read_text().strip() != req_hash:
        print("[TD Machine Learning] Installation des dépendances nécessaires (premier lancement)...", flush=True)
        proc = subprocess.run([str(PYTHON), "-m", "pip", "install", "--disable-pip-version-check", "-r", str(req)], cwd=BASE)
        if proc.returncode:
            raise SystemExit("Impossible d'installer les dépendances. Internet est requis au premier lancement. "
                             "Sous Linux, installer python3-venv si nécessaire. Réessayez après résolution.")
        STAMP.write_text(req_hash, encoding="ascii")
    print("[TD Machine Learning] Démarrage local : http://localhost:8501", flush=True)
    os.environ.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false")
    os.execv(str(PYTHON), [str(PYTHON), "-m", "streamlit", "run", str(BASE / "streamlit_app.py")]) if os.name != "nt" else subprocess.run(
        [str(PYTHON), "-m", "streamlit", "run", str(BASE / "streamlit_app.py")], cwd=BASE, check=False)


if __name__ == "__main__":
    main()
