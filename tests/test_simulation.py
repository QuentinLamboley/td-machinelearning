import numpy as np
import pandas as pd
import pytest
from vampire_lab.config import KEYS, initial_parameters
from vampire_lab.simulation import (simulate_population, simulate_person,
                                    fingerprint, validate_parameters)


def test_reproducibility():
    params = initial_parameters()
    a = simulate_population(params, 1000, .5, 123)
    b = simulate_population(params, 1000, .5, 123)
    c = simulate_population(params, 1000, .5, 124)
    pd.testing.assert_frame_equal(a, b)
    assert not a.equals(c)
    assert fingerprint(a) != fingerprint(c)
    assert list(a.columns) == ["Vampirisme"] + KEYS


def test_bounds_are_class_specific_and_vampires_can_be_older_than_98():
    p = initial_parameters()
    df = simulate_population(p, 2500, .5, 3)
    for var in KEYS:
        for cls, target in (("Humain", 0), ("Vampire", 1)):
            chunk = df.loc[df.Vampirisme == target, var]
            assert chunk.between(p[var][cls]["min"], p[var][cls]["max"]).all()
    assert df.loc[df.Vampirisme == 1, "Age"].max() > 98
    assert df.loc[df.Vampirisme == 0, "Age"].min() < 40


def test_zero_variance():
    p = initial_parameters()
    p["Fer"]["Humain"].update(mean=110, sd=0)
    df = simulate_population(p, 300, .5, 2)
    assert (df.loc[df.Vampirisme == 0, "Fer"] == 110).all()


def test_invalid_bounds():
    p = initial_parameters()
    p["Fer"]["Vampire"]["min"] = 230
    with pytest.raises(ValueError):
        validate_parameters(p)


def test_person_shape():
    p = initial_parameters()
    row = simulate_person(p, .5, np.random.default_rng(10))
    assert set(row) == {"Vampirisme", *KEYS}
    assert row["Vampirisme"] in (0, 1)
