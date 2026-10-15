"""Contrôles supplémentaires : simulation, sauvegardes, plis et fiches de code."""
import json
from pathlib import Path

import numpy as np
import pytest

from vampire_lab.config import KEYS, initial_parameters
from vampire_lab.simulation import parameters_with_proximity, simulate_population
from vampire_lab.student_work import clean_name, student_id, load_work, save_work
from vampire_lab.algorithm_visuals import cv_folds_chart
from vampire_lab.code_resources import available_guides
from vampire_lab.pedagogy import QUESTIONS, VISIBLE_NUMBERS


def test_proximity_zero_identical_to_original():
    params=initial_parameters()
    assert parameters_with_proximity(params,0)==params
    assert len(simulate_population(params,200,0.5,123)) == 200


def test_proximity_100_gives_same_parameterization_for_both_classes():
    params=parameters_with_proximity(initial_parameters(),100)
    for var in KEYS:
        assert params[var]['Humain']==params[var]['Vampire']
    df=simulate_population(params,1000,0.5,123)
    assert df.isna().sum().sum()==0
    assert len(df)==1000


def test_proximity_monotonically_reduces_mean_gaps():
    base=initial_parameters()
    for key in KEYS:
        gaps=[]
        for prox in (0,25,50,75,100):
            values=parameters_with_proximity(base,prox)[key]
            gaps.append(abs(values['Humain']['mean']-values['Vampire']['mean']))
        assert all(x>=y-1e-9 for x,y in zip(gaps,gaps[1:]))


def test_bad_proximity_rejected():
    for value in (-5,101):
        with pytest.raises(ValueError):
            parameters_with_proximity(initial_parameters(),value)


def test_students_save_json_separately(tmp_path,monkeypatch):
    import vampire_lab.student_work as sw
    monkeypatch.setattr(sw,'ROOT',tmp_path)
    left=student_id('Alice Martin','m0nc0de-a')
    right=student_id('Thomas Martin','m0nc0de-b')
    assert left!=right
    save_work(left,'Alice Martin',{'01':'ma réponse','31':'ma preuve'},'mon carnet')
    save_work(right,'Thomas Martin',{'01':'autre réponse'},'')
    assert load_work(left)['reponses']['01']=='ma réponse'
    assert load_work(right)['reponses']['01']=='autre réponse'
    assert len(list(tmp_path.glob('*.json')))==2
    assert not list(tmp_path.glob('*.tmp'))
    assert 'm0nc0de' not in (tmp_path/f'{left}.json').read_text()


def test_student_authentication_requires_name_and_code():
    with pytest.raises(ValueError):student_id('Alice','m0nc0de-a')
    with pytest.raises(ValueError):student_id('Alice Martin','abc')
    assert student_id(' Alice  MARTIN ','123456')==student_id('alice martin','123456')


def test_all_fold_counts_work():
    for k in range(2,11):
        fig=cv_folds_chart(k)
        matrix=np.asarray(fig.data[0].z)
        assert matrix.shape==(k,k)
        assert int(matrix.sum())==k
    with pytest.raises(ValueError):cv_folds_chart(1)


def test_all_seven_markdown_guides_have_both_languages():
    guides=available_guides()
    assert len(guides)==7
    assert len({filename for _,filename,_ in guides})==7
    for title,filename,body in guides:
        assert filename.endswith('.md')
        assert '```python' in body and '```r' in body
        assert 'Data_vampi.csv' in body
        assert 'Vampirisme' in body


def test_58_questions_keep_the_order():
    assert len(QUESTIONS)==58
    assert [VISIBLE_NUMBERS[q.code] for q in QUESTIONS]==[f'{i:02d}' for i in range(1,59)]


def test_ten_student_save_files_concurrently(tmp_path,monkeypatch):
    import vampire_lab.student_work as sw
    from concurrent.futures import ThreadPoolExecutor
    monkeypatch.setattr(sw,'ROOT',tmp_path)
    def worker(i):
        name=f"Camille {chr(65+i)} Martin"
        identity=student_id(name,"mot-secret-de-test")
        save_work(identity,name,{"01":f"Réponse {i}"},f"Notes {i}")
        return identity,i
    with ThreadPoolExecutor(max_workers=10) as pool:
        written=list(pool.map(worker,range(10)))
    for identity,i in written:
        assert load_work(identity)["reponses"]["01"]==f"Réponse {i}"
