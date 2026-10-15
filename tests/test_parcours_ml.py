"""Régression du parcours centré sur le machine learning."""
from pathlib import Path
import io
import pandas as pd
from pypdf import PdfReader
from vampire_lab.algorithm_visuals import algorithm_map, cv_folds_chart
from vampire_lab.config import KEYS, initial_parameters
from vampire_lab.ml import make_split, cv_evaluate, train_evaluate
from vampire_lab.pedagogy import QUESTIONS, BY_CODE
from vampire_lab.correction_pdf import make_correction_pdf

ROOT=Path(__file__).resolve().parent.parent

def test_fichier_de_donnees_pret_a_etre_exploite():
    df=pd.read_csv(ROOT/'data'/'Data_vampi.csv')
    assert len(df)==1000
    assert df.columns.tolist()==['Vampirisme']+KEYS
    assert set(df['Vampirisme'].unique())=={0,1}
    assert df.isna().sum().sum()==0

def test_questions_ml_pas_sur_le_generateur():
    assert len(QUESTIONS)==58
    text=' '.join(q.enonce.lower() for q in QUESTIONS)
    assert 'bernoulli' not in text
    assert 'loi normale' not in text
    assert 'graine aléatoire' not in text
    assert sum(q.section=='Réseaux de neurones : complément' for q in QUESTIONS)==9
    for word in ['ridge','lasso','elastic net','xgboost','forêt aléatoire','validation croisée']:
        assert word in text
    assert len(BY_CODE)==len(QUESTIONS)

def test_graphiques_des_cinq_algorithmes():
    for name in ['Forêt aléatoire','XGBoost','Régression logistique · Ridge',
                 'Régression logistique · Lasso','Régression logistique · Elastic Net']:
        assert len(algorithm_map(name).data)>0
    for k in [3,5,10]:
        fig=cv_folds_chart(k)
        assert len(fig.data[0].z)==k
        assert sum(fig.data[0].z[i][i] for i in range(k))==k

def test_validation_dix_plis_train_uniquement():
    df=pd.read_csv(ROOT/'data'/'Data_vampi.csv')
    sp=make_split(df,seed=42)
    a=cv_evaluate('Régression logistique · Ridge',sp,10)
    assert len(a['accuracy'])==10
    result=train_evaluate('Forêt aléatoire',sp,do_cv=False)
    assert result['cv'] is None
    assert 0<=result['metrics']['accuracy']<=1

def test_pdf_centrage_et_contenu():
    pdf=PdfReader(io.BytesIO(make_correction_pdf()))
    text=' '.join(page.extract_text() for page in pdf.pages)
    assert 'Validation non croisée' in text
    for needle in ['Random Forest','XGBoost','Ridge','Lasso','Elastic Net','10 plis']:
        assert needle in text
    assert 'Bernoulli' not in text
    assert len(pdf.pages)>=7
