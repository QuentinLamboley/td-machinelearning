"""Vérifie que le même contenu pédagogique est disponible à l'écran et dans le PDF."""
from io import BytesIO
from pathlib import Path
from pypdf import PdfReader
from vampire_lab.pedagogy import QUESTIONS, BY_CODE
from vampire_lab.correction_pdf import make_correction_pdf

ROOT = Path(__file__).resolve().parent.parent


def test_toutes_les_corrections_contiennent_un_exemple_et_un_repere():
    assert len(QUESTIONS) == 58
    assert sum(q.section.startswith('Réseaux') for q in QUESTIONS) == 9
    assert set(BY_CODE) == {f'{i:02d}' for i in range(1, 59)}
    for q in QUESTIONS:
        assert len(q.correction) > 120, q.code
        assert len(q.exemple) > 65, q.code
        assert len(q.retenir) > 50, q.code
        assert 'Bernoulli' not in q.enonce


def test_corrige_pdf_reprend_les_exemples_et_repères():
    reader = PdfReader(BytesIO(make_correction_pdf()))
    all_text = '\n'.join(page.extract_text() for page in reader.pages)
    assert 15 <= len(reader.pages) <= 35
    assert all_text.count('Exemple concret.') == 58
    assert all_text.count('À retenir :') == 58
    assert 'Un bon score indique que le modèle retrouve correctement les régularités' not in all_text
    for q in QUESTIONS:
        assert q.enonce[:30] in all_text or f'{q.code} /' in all_text


def test_fichiers_github_et_local():
    for name in ('README.md', 'requirements.txt', 'packages.txt',
                 'streamlit_app.py', 'data/Data_vampi.csv',
                 'docs/CORRIGE_COMPLET_ESMIHA.pdf', '.github/workflows/controle.yml',
                 'PUBLIER_GITHUB.py', 'PUBLIER_GITHUB_WINDOWS.bat',
                 'PUBLIER_GITHUB_LINUX_MAC.sh'):
        assert (ROOT / name).is_file(), name
    assert 'xgboost' in (ROOT / 'requirements.txt').read_text().lower()
