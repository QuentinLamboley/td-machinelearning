import numpy as np
import pandas as pd
from vampire_lab.config import initial_parameters
from vampire_lab.simulation import simulate_population
from vampire_lab.ml import (compare_results, cv_evaluate, make_split,
                            train_evaluate, threshold_metrics, pdp_ice,
                            feature_importances)
from vampire_lab import viz


def sample():
    return simulate_population(initial_parameters(), 260, .45, 12)


def test_split_stratified_disjoint():
    split = make_split(sample(), .2, 42)
    assert len(split.X_train) == 208
    assert len(split.X_test) == 52
    assert not set(split.X_train.index) & set(split.X_test.index)
    assert abs(split.y_train.mean() - split.y_test.mean()) < .03


def test_cv_does_not_use_holdout():
    a = make_split(sample(), .2, 7)
    b = make_split(sample(), .2, 7)
    # Sabotage test only: CV must remain exactly identical.
    b.X_test.loc[:, "Age"] = 99999
    b.y_test = 1 - b.y_test
    res_a = cv_evaluate("Régression logistique · Ridge", a, folds=3)
    res_b = cv_evaluate("Régression logistique · Ridge", b, folds=3)
    assert res_a == res_b


def test_models_metrics_plotting():
    sp = make_split(sample(), .2, 5)
    model = train_evaluate("Régression logistique · Ridge", sp, folds=3)
    assert 0 <= model["metrics"]["accuracy"] <= 1
    assert 0 <= model["metrics"]["roc_auc"] <= 1
    assert len(model["cv"]["accuracy"]) == 3
    assert 0 <= threshold_metrics(model, .3)["recall"] <= 1
    frame = compare_results({model["name"]: model})
    assert frame.shape == (1, 7)
    # Plotly figures should serialise in supported versions.
    assert viz.comparison_chart(frame).to_json()
    assert viz.distribution_chart(sample(), "Age").to_json()
    assert viz.correlation_chart(sample(), ["Age", "Fer"]).to_json()
    assert viz.confusion_chart(model).to_json()
    assert viz.calibration_chart(model).to_json()
    fig1, fig2 = viz.roc_pr_charts(model)
    assert fig1.to_json() and fig2.to_json()


def test_pdp_and_importance():
    sp = make_split(sample(), .2, 5)
    res = train_evaluate("Forêt aléatoire", sp, do_cv=False)
    pdp = pdp_ice(res["estimator"], sp.X_train, "Age", grid_size=11, individuals=12)
    assert pdp["ice"].shape == (12, 11)
    assert len(pdp["pdp"]) == 11
    assert (pdp["ice"] >= 0).all() and (pdp["ice"] <= 1).all()
    importance = feature_importances(res["estimator"], sp.X_train, sp.y_train)
    assert len(importance) == 10
    assert viz.pdp_chart(pdp, "Age").to_json()
    assert viz.importance_chart(importance).to_json()
    assert viz.decision_surface(res["estimator"], sp.X_train, "Age", "Fer").to_json()
