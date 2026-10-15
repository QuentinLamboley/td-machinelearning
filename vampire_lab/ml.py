"""Supervised-learning protocol: one untouched holdout, CV only on training data."""
from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, average_precision_score, balanced_accuracy_score,
    brier_score_loss, confusion_matrix, f1_score, precision_score,
    recall_score, roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .config import KEYS, MODEL_NAMES


def has_xgboost() -> bool:
    try:
        import xgboost  # noqa: F401
        return True
    except (ImportError, OSError):
        return False


def build_estimator(model_name: str, seed: int = 42):
    if model_name not in MODEL_NAMES:
        raise ValueError(f"Algorithme inconnu : {model_name}")
    if model_name == "Forêt aléatoire":
        return RandomForestClassifier(n_estimators=160, min_samples_leaf=2,
                                      max_features="sqrt", class_weight="balanced",
                                      random_state=seed, n_jobs=1)
    if model_name == "XGBoost":
        try:
            from xgboost import XGBClassifier
        except (ImportError, OSError) as exc:
            raise RuntimeError("XGBoost n'est pas installé. Installer requirements-xgboost.txt.") from exc
        return XGBClassifier(n_estimators=160, max_depth=3, learning_rate=.08,
                             subsample=.9, colsample_bytree=.9, reg_lambda=1.,
                             objective="binary:logistic", eval_metric="logloss",
                             tree_method="hist", random_state=seed, n_jobs=1)
    if model_name in {"Réseau de neurones", "Réseau profond"}:
        from .neural_visuals import ARCHITECTURES
        architecture = ARCHITECTURES[model_name]
        return Pipeline([("standardisation", StandardScaler()),
                         ("modele", MLPClassifier(hidden_layer_sizes=architecture,
                                                  max_iter=280, early_stopping=False, alpha=.005,
                                                  learning_rate_init=.002, n_iter_no_change=22,
                                                  random_state=seed))])
    kwargs = {"random_state": seed, "max_iter": 2800, "C": 1., "class_weight": "balanced"}
    # sklearn 1.8 deprecated `penalty` in favor of `l1_ratio`;
    # retain the old argument on earlier releases for Python portability.
    import sklearn
    version_parts = sklearn.__version__.split(".")[:2]
    newer_api = int(version_parts[0]) > 1 or (int(version_parts[0]) == 1 and int(version_parts[1]) >= 8)
    if newer_api:
        if model_name == "Régression logistique · Ridge":
            model = LogisticRegression(solver="lbfgs", l1_ratio=0., **kwargs)
        elif model_name == "Régression logistique · Lasso":
            model = LogisticRegression(solver="saga", l1_ratio=1., **kwargs)
        else:
            model = LogisticRegression(solver="saga", l1_ratio=.5, **kwargs)
    elif model_name == "Régression logistique · Ridge":
        model = LogisticRegression(solver="lbfgs", penalty="l2", **kwargs)
    elif model_name == "Régression logistique · Lasso":
        model = LogisticRegression(solver="liblinear", penalty="l1", **kwargs)
    else:
        model = LogisticRegression(solver="saga", penalty="elasticnet", l1_ratio=.5, **kwargs)
    return Pipeline([("standardisation", StandardScaler()), ("modele", model)])


@dataclass
class Split:
    X_train: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_test: pd.Series
    seed: int
    test_ratio: float


def make_split(data: pd.DataFrame, test_ratio: float = .2, seed: int = 42) -> Split:
    if "Vampirisme" not in data.columns:
        raise ValueError("Colonne cible Vampirisme manquante")
    y = data["Vampirisme"].astype(int)
    if set(y.unique()) != {0, 1}:
        raise ValueError("Deux classes (0 et 1) sont nécessaires à l'évaluation.")
    if y.value_counts().min() < 4:
        raise ValueError("Il faut au moins 4 individus dans chaque classe. Augmentez N ou ajustez la prévalence.")
    if not 0.1 <= test_ratio <= .4:
        raise ValueError("La part réservée au test doit être comprise entre 10 % et 40 %.")
    X = data.drop(columns="Vampirisme")[KEYS].copy()
    xtr, xte, ytr, yte = train_test_split(X, y, test_size=test_ratio, random_state=int(seed), stratify=y)
    return Split(xtr, xte, ytr, yte, int(seed), float(test_ratio))


def cv_evaluate(name: str, split: Split, folds: int = 5) -> dict:
    if folds < 2:
        raise ValueError("Il faut au minimum deux plis.")
    if int(split.y_train.value_counts().min()) < folds:
        raise ValueError(f"Il faut au moins {folds} individus de chaque classe dans l'apprentissage.")
    estimator = build_estimator(name, split.seed)
    cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=split.seed)
    scores = cross_validate(estimator, split.X_train, split.y_train, cv=cv, n_jobs=1,
                            scoring={"accuracy": "accuracy", "balanced_accuracy": "balanced_accuracy",
                                     "roc_auc": "roc_auc", "f1": "f1"}, error_score="raise")
    return {k.replace("test_", ""): [float(x) for x in v] for k, v in scores.items() if k.startswith("test_")}


def _compute_metrics(y_true, pred, prob):
    cm = confusion_matrix(y_true, pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()
    return {
        "accuracy": float(accuracy_score(y_true, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, pred)),
        "precision": float(precision_score(y_true, pred, zero_division=0)),
        "recall": float(recall_score(y_true, pred, zero_division=0)),
        "specificity": float(tn / (tn + fp)) if tn + fp else float("nan"),
        "f1": float(f1_score(y_true, pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, prob)),
        "average_precision": float(average_precision_score(y_true, prob)),
        "brier": float(brier_score_loss(y_true, prob)),
    }


def train_evaluate(name: str, split: Split, folds: int = 5, do_cv: bool = True) -> dict:
    cv = cv_evaluate(name, split, folds) if do_cv else None
    clf = build_estimator(name, split.seed)
    clf.fit(split.X_train, split.y_train)
    prob = np.asarray(clf.predict_proba(split.X_test)[:, 1], dtype=float)
    pred = (prob >= .5).astype(int)
    result = {
        "name": name, "estimator": clf,
        "metrics": _compute_metrics(split.y_test, pred, prob),
        "cv": cv,
        "prediction": pred,
        "probability": prob,
        "truth": split.y_test.to_numpy().astype(int),
        "threshold": .5,
    }
    return result


def threshold_metrics(result: dict, threshold: float) -> dict:
    pred = (result["probability"] >= threshold).astype(int)
    return _compute_metrics(result["truth"], pred, result["probability"])


def feature_importances(model, X: pd.DataFrame, y: pd.Series, seed: int = 42) -> pd.DataFrame:
    """Comparably-scaled, test-free permutation importance on train only."""
    from sklearn.inspection import permutation_importance
    sample = X.sample(n=min(400, len(X)), random_state=seed)
    labels = y.loc[sample.index]
    p = permutation_importance(model, sample, labels, scoring="balanced_accuracy",
                               n_repeats=4, random_state=seed, n_jobs=1)
    return pd.DataFrame({"variable": X.columns, "importance": p.importances_mean,
                         "ecart_type": p.importances_std}).sort_values("importance", ascending=False)


def pdp_ice(model, X: pd.DataFrame, feature: str, seed: int = 42,
            grid_size: int = 35, individuals: int = 36) -> dict:
    """Brute-force PDP: average predictions across observed people, with ICE traces."""
    if feature not in X.columns:
        raise KeyError(feature)
    sample = X.sample(n=min(individuals, len(X)), random_state=seed).copy()
    lower = float(X[feature].quantile(.02))
    upper = float(X[feature].quantile(.98))
    if lower == upper:
        lower, upper = float(X[feature].min()), float(X[feature].max())
    if lower == upper:
        lower, upper = lower - .5, upper + .5
    grid = np.linspace(lower, upper, grid_size)
    curves = []
    for value in grid:
        modified = sample.copy()
        modified.loc[:, feature] = value
        curves.append(np.asarray(model.predict_proba(modified)[:, 1], dtype=float))
    ice = np.array(curves).T
    return {"grid": grid, "ice": ice, "pdp": ice.mean(axis=0)}


def compare_results(results: dict[str, dict]) -> pd.DataFrame:
    rows = []
    for name, result in results.items():
        met = result["metrics"]
        folds = result.get("cv")
        rows.append({"Modèle": name, "Accuracy test": met["accuracy"],
                     "Balanced accuracy test": met["balanced_accuracy"],
                     "AUC-ROC test": met["roc_auc"], "F1 test": met["f1"],
                     "Accuracy CV moyenne": (float(np.mean(folds["accuracy"])) if folds else float("nan")),
                     "Écart-type CV": (float(np.std(folds["accuracy"])) if folds else float("nan"))})
    return pd.DataFrame(rows)


def result_jsonable(result: dict) -> dict:
    """Excludes live model instances and individual-level output."""
    return {"modele": result["name"], "metriques_test": result["metrics"],
            "validation_croisee": result["cv"], "seuil": result["threshold"]}
