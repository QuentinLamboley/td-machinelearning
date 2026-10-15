"""Contrôles V6 : paramètres du TD, présentation et rendus indépendants."""
from io import BytesIO
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from pypdf import PdfReader
from vampire_lab.pedagogy import QUESTIONS, BY_CODE, VISIBLE_NUMBERS
from vampire_lab.student_pdf import make_student_pdf
from vampire_lab.correction_pdf import make_correction_pdf
from vampire_lab.config import initial_parameters
from vampire_lab.simulation import simulate_population
from vampire_lab.runtime_limits import computation_slot
from vampire_lab.ml import make_split, train_evaluate

ROOT = Path(__file__).resolve().parents[1]


def test_58_questions_et_nouvelles_notions():
    assert len(QUESTIONS) == 58
    assert len([q for q in QUESTIONS if q.section.startswith('Réseaux')]) == 9
    assert 'une erreur' in BY_CODE['33'].correction.lower()
    for key in ('31','32','33','37','43','47','51','56','58'):
        assert len(BY_CODE[key].correction)>130
        assert BY_CODE[key].indice
        assert BY_CODE[key].exemple
        assert BY_CODE[key].retenir


def test_personal_pdf_isolation_ten_students():
    def student(i):
        name = f'Etudiant numero {i}'
        unique = f'ReponsePersonnelleUnique{i:02d}'
        pdf = make_student_pdf({'01': unique}, notes='Carnet individuel', student_name=name)
        text = '\n'.join(page.extract_text() for page in PdfReader(BytesIO(pdf)).pages)
        return name,unique,text
    with ThreadPoolExecutor(max_workers=10) as pool:
        reports = list(pool.map(student,range(10)))
    for i,(name,unique,body) in enumerate(reports):
        assert name in body
        assert unique in body
        for j in range(10):
            if i != j:
                assert f'ReponsePersonnelleUnique{j:02d}' not in body
        assert 'ÉLÉMENTS DE CORRECTION' not in body


def test_pdf_student_remplit_toutes_les_sections():
    pdf=make_student_pdf({'01':'Cible : vampirisme.', '56':'La perte du train ne suffit pas.'},
                         'Analyse personnelle.','Camille Martin',{'n':800,'prevalence':.3})
    body=' '.join(p.extract_text() for p in PdfReader(BytesIO(pdf)).pages)
    assert 'Camille Martin' in body
    assert '800 observations' in body
    assert 'La perte du train' in body
    assert 'Réseaux de neurones' in body
    assert 'Réponse non renseignée' in body


def test_jeu_de_donnees_variation_effectif_et_proportion():
    param=initial_parameters()
    a=simulate_population(param,500,.5,123)
    b=simulate_population(param,1500,.15,123)
    assert len(a)==500 and len(b)==1500
    assert abs(float(a.Vampirisme.mean())-.5)<.08
    assert abs(float(b.Vampirisme.mean())-.15)<.05
    with computation_slot():
        a_r=train_evaluate('Régression logistique · Ridge',make_split(a),do_cv=False)
        b_r=train_evaluate('Régression logistique · Ridge',make_split(b),do_cv=False)
    assert 0 <= a_r['metrics']['balanced_accuracy'] <=1
    assert 0 <= b_r['metrics']['balanced_accuracy'] <=1


def test_source_sans_branding_et_navigation_sans_sidebar():
    main=(ROOT/'streamlit_app.py').read_text()
    ui=(ROOT/'vampire_lab/ui.py').read_text()
    assert 'def navigation_footer():' in main
    assert 'page=sidebar()' not in main
    assert 'def sidebar():' not in main
    assert 'VAMP' + '/LAB' not in main+ui
    assert 'Machine learning' in main+ui
    assert (ROOT/'assets/paysage_td.webp').stat().st_size < 160000
    assert 'make_student_pdf' in main
    assert (ROOT/'docs/CORRIGE_COMPLET_ESMIHA.pdf').exists()


def test_pdf_reference_contient_toutes_les_questions():
    b=make_correction_pdf()
    text=' '.join(p.extract_text() for p in PdfReader(BytesIO(b)).pages)
    for q in QUESTIONS:
        assert f'{VISIBLE_NUMBERS[q.code]} /' in text
    assert 'VAMP' + '/LAB' not in text
