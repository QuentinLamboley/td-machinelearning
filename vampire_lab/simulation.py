"""Simulate a completely fictional population for teaching supervised ML."""
from __future__ import annotations

import copy
import hashlib
import json

import numpy as np
import pandas as pd
from scipy.stats import truncnorm

from .config import KEYS


def validate_parameters(params: dict) -> None:
    for var in KEYS:
        if var not in params:
            raise ValueError(f"Variable manquante : {var}")
        for cls in ("Humain", "Vampire"):
            p = params[var][cls]
            values = [float(p[k]) for k in ("mean", "sd", "min", "max")]
            if not all(np.isfinite(values)):
                raise ValueError(f"{var} / {cls} : paramètres non finis.")
            if p["sd"] < 0:
                raise ValueError(f"{var} / {cls} : l'écart-type doit être positif ou nul.")
            if p["min"] >= p["max"]:
                raise ValueError(f"{var} / {cls} : la borne minimale doit être inférieure à la maximale.")



def parameters_with_proximity(params: dict, proximity: int | float) -> dict:
    """Rapproche les distributions des deux classes sans changer les variables.

    0 % : groupes distincts ; 100 % : distributions exactement identiques.
    Moyennes, écarts-types ET limites sont rapprochés de façon continue,
    ce qui empêche les bornes de révéler encore la classe au maximum.
    """
    similarity = float(proximity) / 100.0
    if not 0.0 <= similarity <= 1.0:
        raise ValueError("La proximité doit être comprise entre 0 et 100 %.")
    adjusted = copy.deepcopy(params)
    for variable in KEYS:
        human, vampire = params[variable]["Humain"], params[variable]["Vampire"]
        for key in ("mean", "sd", "min", "max"):
            shared = (float(human[key]) + float(vampire[key])) / 2.0
            for cls, original in (("Humain", human), ("Vampire", vampire)):
                adjusted[variable][cls][key] = (1.0 - similarity) * float(original[key]) + similarity * shared
    validate_parameters(adjusted)
    return adjusted

def simulate_population(params: dict, n: int = 1000, prevalence: float = .5, seed: int = 123) -> pd.DataFrame:
    if not 50 <= n <= 30000:
        raise ValueError("Le nombre d'individus doit être compris entre 50 et 30 000.")
    if not 0 < prevalence < 1:
        raise ValueError("La prévalence doit appartenir à ]0, 1[.")
    validate_parameters(params)
    rng = np.random.default_rng(int(seed))
    y = rng.binomial(1, prevalence, size=n)
    data: dict[str, np.ndarray] = {"Vampirisme": y.astype(int)}
    for var in KEYS:
        col = np.empty(n, dtype=float)
        for cls, value in (("Humain", 0), ("Vampire", 1)):
            selector = y == value
            count = int(selector.sum())
            if not count:
                continue
            p = params[var][cls]
            mu, sd, lo, hi = (float(p[k]) for k in ("mean", "sd", "min", "max"))
            if sd == 0:
                samples = np.full(count, np.clip(mu, lo, hi), dtype=float)
            else:
                samples = truncnorm.rvs((lo - mu) / sd, (hi - mu) / sd,
                                         loc=mu, scale=sd, size=count, random_state=rng)
            col[selector] = samples
        data[var] = col
    return pd.DataFrame(data, columns=["Vampirisme"] + KEYS)


def simulate_person(params: dict, prevalence: float, rng: np.random.Generator | None = None) -> dict:
    """An individual *outside* any training/test sample."""
    validate_parameters(params)
    rng = rng if rng is not None else np.random.default_rng()
    cls = "Vampire" if rng.random() < prevalence else "Humain"
    row: dict = {"Vampirisme": int(cls == "Vampire")}
    for var in KEYS:
        p = params[var][cls]
        mu, sd, lo, hi = (float(p[k]) for k in ("mean", "sd", "min", "max"))
        row[var] = float(np.clip(mu, lo, hi)) if sd == 0 else float(
            truncnorm.rvs((lo-mu)/sd, (hi-mu)/sd, loc=mu, scale=sd, random_state=rng))
    return row


def label_classes(data: pd.DataFrame) -> pd.DataFrame:
    view = data.copy()
    view.insert(1, "Profil", view["Vampirisme"].map({0: "Humain", 1: "Vampire"}))
    return view


def fingerprint(data: pd.DataFrame) -> str:
    arr = pd.util.hash_pandas_object(data, index=True).values.tobytes()
    return hashlib.sha256(arr).hexdigest()[:16]


def copy_parameters(params: dict) -> dict:
    return copy.deepcopy(params)


def parameter_json(params: dict, n: int, prevalence: float, seed: int) -> str:
    return json.dumps({"parametres": params, "effectif": n, "prevalence": prevalence, "graine": seed,
                       "univers": "Fictif ; pas un outil diagnostique"}, indent=2, ensure_ascii=False)
