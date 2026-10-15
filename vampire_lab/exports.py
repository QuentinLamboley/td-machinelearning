"""Export reproducible study material without writing shared user workspaces."""
from __future__ import annotations

import io
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from .ml import result_jsonable
from .simulation import parameter_json


def export_zip(data: pd.DataFrame | None, params: dict, n: int, prevalence: float, seed: int,
               results: dict, notes: str = "", instruction_pdf: bytes | None = None, source: str = "Données d’exemple") -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("README.txt", "TD Machine Learning : export de séance ESMIHA\nJeu de données à usage pédagogique.\n"
                   "Aucun score n'est un résultat clinique.\nClasse cible: Vampirisme = 1 (vampire).\n"
                   "Validation croisée réalisée exclusivement sur l'échantillon d'apprentissage.\n")
        z.writestr("origine_donnees.txt", source)
        if source != "CSV importé":
            z.writestr("parametres_simulation.json", parameter_json(params, n, prevalence, seed))
        if data is not None:
            z.writestr("Data_vampi.csv", data.to_csv(index=False).encode("utf-8-sig"))
        if results:
            z.writestr("resultats_modeles.json", json.dumps(
                {name: result_jsonable(result) for name, result in results.items()},
                ensure_ascii=False, indent=2))
        z.writestr("carnet.md", notes)
        if instruction_pdf:
            z.writestr("consignes_personnelles.pdf", instruction_pdf)
    return buf.getvalue()
