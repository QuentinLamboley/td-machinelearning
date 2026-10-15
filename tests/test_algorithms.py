import warnings
import pytest
from vampire_lab.config import MODEL_NAMES, initial_parameters
from vampire_lab.simulation import simulate_population
from vampire_lab.ml import has_xgboost, make_split, train_evaluate


@pytest.mark.parametrize("name", MODEL_NAMES)
def test_every_algorithm_trains_and_predicts(name):
    if name == "XGBoost" and not has_xgboost():
        pytest.skip("XGBoost facultatif non installé")
    sp = make_split(simulate_population(initial_parameters(), 260, .5, 19), .2, 42)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        res = train_evaluate(name, sp, folds=3, do_cv=False)
    assert res["name"] == name
    assert len(res["probability"]) == len(sp.X_test)
    assert all(0 <= p <= 1 for p in res["probability"])
    assert 0 <= res["metrics"]["accuracy"] <= 1
