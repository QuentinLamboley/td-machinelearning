"""TD - Introduction au Machine Learning · Master ESMIHA.

Run: python -m streamlit run streamlit_app.py
No external API, secrets, network resources, shared writable upload folders or runtime pip.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

# Évite la multiplication des threads pour les séances multi-utilisateurs.
for _thread_var in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_thread_var] = "1"

import numpy as np
import pandas as pd
import streamlit as st

from vampire_lab.config import (DESCRIPTIONS, KEYS, LABELS, MODEL_NAMES,
                                MODEL_SHORT, UNITS, VARIABLES, glossary, initial_parameters)
from vampire_lab.exports import export_zip
from vampire_lab.ml import (cv_evaluate, compare_results, feature_importances,
                            has_xgboost, make_split, pdp_ice, threshold_metrics,
                            train_evaluate)
from vampire_lab.simulation import (copy_parameters, fingerprint, label_classes,
                                    simulate_person, simulate_population, parameters_with_proximity)
from vampire_lab import viz, ui
from vampire_lab.algorithm_visuals import algorithm_map, cv_folds_chart
from vampire_lab.neural_visuals import (ARCHITECTURES, network_chart, activation_chart,
                                        loss_chart, neuron_count)
from vampire_lab.pedagogy import QUESTIONS, BY_CODE, VISIBLE_NUMBERS, completed_count
from vampire_lab.correction_pdf import make_correction_pdf
from vampire_lab.student_pdf import make_student_pdf
from vampire_lab.runtime_limits import computation_slot
from vampire_lab.student_work import clean_name, student_id, load_work, save_work

st.set_page_config(page_title="TD - Introduction au Machine learning. | ESMIHA",
                   page_icon="🦇", layout="wide", initial_sidebar_state="collapsed",
                   menu_items={"About": "TD - Introduction au Machine Learning · Quentin Lamboley · Master ESMIHA."})
ui.inject_style()

ROOT = Path(__file__).resolve().parent
PAGES = ["01 · Présentation", "02 · Jeu de données", "03 · Exploration",
         "04 · Validation non croisée", "05 · Validation croisée",
         "06 · Comparer et évaluer", "07 · Interpréter", "08 · Prédire",
         "09 · Carnet et corrigé", "+ · Réseaux de neurones (complément)"]


def init_state():
    defaults = {
        "parameters": initial_parameters(), "sample_n": 1000,
        "sample_prevalence": .5, "sample_prevalence_pct": 50, "sample_seed": 123,
        "sample_proximity": 0, "student_identity": None,
        "data": None, "data_spec": None,
        "split": None, "cv_folds": 10, "model_results": {},
        "quiz_person": None, "quiz_reveal": False,
        "quiz_history": [], "notes": "", "instruction_pdf": None,
        "editor_rev": 0, "dataset_source": "Données d’exemple",
        "nav": PAGES[0], "student_name": "", "personal_pdf": None,
        "sample_experiment": None,
        "td_answers": {}, "td_pdf_session": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def navigate_to(page: str):
    st.session_state["nav"] = page
    persist_answers()

def persist_answers():
    # Récupère aussi le champ actuellement saisi, avant tout changement de page.
    for q in QUESTIONS:
        widget = f"answer_{q.code}"
        if widget in st.session_state:
            st.session_state["td_answers"][q.code] = str(st.session_state[widget])[:8000]
    identity = st.session_state.get("student_identity")
    if identity:
        try:
            save_work(identity, st.session_state["student_name"],
                      st.session_state["td_answers"], st.session_state.get("notes", ""),
                      etape=st.session_state.get("nav", PAGES[0]))
        except OSError:
            st.session_state["save_unavailable"] = True

def update_notes():
    persist_answers()

def identity_gate():
    if st.session_state.get("student_identity"):
        return
    ui.hero()
    st.markdown("### Retrouver ton travail")
    st.write("Avant de commencer, renseigne ton prénom et ton nom, puis choisis un code "
             "personnel d’au moins six caractères. Garde ce code : avec les mêmes informations, "
             "tu pourras retrouver les réponses enregistrées pendant la séance.")
    with st.form("student_access_form"):
        name = st.text_input("Prénom et nom", max_chars=120, placeholder="Camille Martin")
        code = st.text_input("Mon code personnel", type="password", max_chars=80,
                             help="Ne réutilise pas le mot de passe d’un autre service. Ce code permet d’éviter qu’un autre étudiant ayant le même nom puisse ouvrir tes réponses.")
        start = st.form_submit_button("Commencer ou reprendre mon TD →",type="primary",use_container_width=True)
    if start:
        try:
            name = clean_name(name)
            identity = student_id(name,code)
            prior = load_work(identity)
            st.session_state["student_identity"] = identity
            st.session_state["student_name"] = name
            st.session_state["td_answers"] = {q.code:str(prior.get("reponses",{}).get(q.code,""))[:8000] for q in QUESTIONS}
            st.session_state["notes"] = str(prior.get("notes", ""))[:30000]
            # Toujours présenter les objectifs du TD après connexion, sans effacer le travail.
            st.session_state["nav"] = PAGES[0]
            for q in QUESTIONS:
                st.session_state.pop(f"answer_{q.code}",None)
            persist_answers()
            st.rerun()
        except ValueError as exc:
            st.warning(str(exc))
    st.info("Pour conserver ton travail même si le serveur est redémarré, télécharge également ta sauvegarde JSON dans le TD. Tu pourras la réimporter chez toi.")
    st.stop()

def restore_backup(payload: dict):
    vals = payload.get("reponses")
    if not isinstance(vals,dict):
        raise ValueError("Structure de réponses non reconnue.")
    accepted = {q.code:str(vals.get(q.code,""))[:8000] for q in QUESTIONS}
    st.session_state["td_answers"] = accepted
    for key,txt in accepted.items():
        st.session_state[f"answer_{key}"] = txt
    st.session_state["notes"] = str(payload.get("notes", ""))[:30000]
    previous_stage = payload.get("etape")
    if previous_stage in PAGES:
        st.session_state["nav"] = previous_stage
    persist_answers()


def clear_explanations():
    for key in list(st.session_state.keys()):
        if key.startswith("importance_"):
            del st.session_state[key]


def current_data():
    return st.session_state["data"]


def results():
    return st.session_state["model_results"]


def require_data():
    if current_data() is not None:
        return True
    st.info("Charge ou régénère le jeu de données dans **02 · Jeu de données**.")
    st.button("Aller au jeu de données →", key="to_sim",
              on_click=navigate_to, args=(PAGES[1],))
    return False


def require_split():
    if not require_data():
        return False
    if st.session_state["split"] is not None:
        return True
    st.info("Commence par réserver un jeu de test dans **04 · Validation non croisée**.")
    return False


def ensure_sample():
    effective = parameters_with_proximity(st.session_state["parameters"], st.session_state["sample_proximity"])
    df = simulate_population(effective,
                             int(st.session_state["sample_n"]),
                             float(st.session_state["sample_prevalence"]),
                             int(st.session_state["sample_seed"]))
    st.session_state["data"] = df
    st.session_state["data_spec"] = {
        "parameters": copy_parameters(effective),
        "proximity": int(st.session_state["sample_proximity"]),
        "n": int(st.session_state["sample_n"]),
        "prevalence": float(st.session_state["sample_prevalence"]),
        "seed": int(st.session_state["sample_seed"]),
        "fingerprint": fingerprint(df),
    }
    st.session_state["split"] = None
    clear_explanations()
    st.session_state["model_results"] = {}
    st.session_state["quiz_person"] = None
    st.session_state["quiz_reveal"] = False
    st.session_state["td_pdf_session"] = None
    st.session_state["sample_experiment"] = None
    st.session_state["dataset_source"] = "Données d’exemple"
    return df


def save_answer(code: str):
    st.session_state["td_answers"][code] = st.session_state[f"answer_{code}"]
    persist_answers()


def explain(label: str, content: str):
    """Accessible ? button, next to the notion it explains."""
    a, b = st.columns([13, 1], vertical_alignment="center")
    a.markdown(f"**{label}**")
    with b:
        with st.popover("❔"):
            st.markdown(content)


def question(code: str):
    item = BY_CODE[code]
    with st.container(border=True):
        col, help_col = st.columns([12, 1], vertical_alignment="center")
        with col:
            st.markdown(f"<div class='exercise-tag'>QUESTION {VISIBLE_NUMBERS[code]} · {item.section.upper()}</div>",
                        unsafe_allow_html=True)
            st.markdown(f"**{item.enonce}**")
        with help_col:
            with st.popover("❔"):
                st.markdown("**Un indice pour avancer**")
                st.write(item.indice)
        widget=f"answer_{code}"
        if widget not in st.session_state:
            st.session_state[widget] = st.session_state["td_answers"].get(code, "")
        st.text_area("Ta réponse (tu peux la compléter plus tard)", key=widget,
                     height=95, placeholder="Explique ici ce que tu observes et pourquoi...",
                     on_change=save_answer, args=(code,))
        if st.checkbox("Comparer avec les éléments de correction", key=f"reveal_{code}"):
            st.markdown(f"<div class='answer-label'>ÉLÉMENTS DE CORRECTION</div>", unsafe_allow_html=True)
            st.markdown("**L’explication**")
            st.write(item.correction)
            st.markdown("**Un exemple concret**")
            st.info(item.exemple)
            st.markdown(f"**À retenir :** {item.retenir}")



def navigation_header():
    index = PAGES.index(st.session_state.get("nav", PAGES[0]))
    required = [q for q in QUESTIONS if q.section != "Réseaux de neurones : complément"]
    done = sum(bool(str(st.session_state["td_answers"].get(q.code, "")).strip()) for q in required)
    stage = "INTRODUCTION" if index == 0 else ("BONUS RÉSEAUX DE NEURONES" if index == len(PAGES)-1 else f"ÉTAPE {index:02d}/08")
    st.markdown(f"<div class='progress-intro'>ESMIHA · TD MACHINE LEARNING &nbsp; | &nbsp; "
                f"{stage} &nbsp; | &nbsp; {done}/{len(required)} réponses renseignées</div>",
                unsafe_allow_html=True)
    st.progress((index+1)/len(PAGES))
    if index > 0:
        st.button("⌂ Revoir la présentation du TD", key="return_intro",
                  on_click=navigate_to, args=(PAGES[0],))
    head_a, head_b = st.columns([3,1.5],vertical_alignment="center")
    head_a.caption(f"Travail de {st.session_state['student_name']} · réponses enregistrées à chaque modification")
    backup = {"version":7,"etudiant":st.session_state["student_name"],
              "etape":st.session_state["nav"], "etape_numero":index,
              "reponses":st.session_state["td_answers"],"notes":st.session_state["notes"]}
    head_b.download_button("↓ Sauvegarder mon travail (.json)",
             json.dumps(backup,ensure_ascii=False,indent=2).encode("utf-8"),
             file_name="Mon_TD_ESMIHA_sauvegarde.json",mime="application/json",use_container_width=True)
    if st.session_state.get("save_unavailable"):
        st.warning("La sauvegarde sur le serveur est indisponible. Télécharge ta sauvegarde JSON pour conserver tes réponses.")


def jump_to_page_top():
    """Replacer la lecture en haut uniquement lors d'un changement d'étape.

    Les interactions avec les widgets provoquent des reruns Streamlit, mais
    elles ne doivent pas déplacer le lecteur dans la page en cours.
    """
    current_page = st.session_state["nav"]
    previous_page = st.session_state.get("_last_rendered_page")
    st.session_state["_last_rendered_page"] = current_page
    if previous_page is None or previous_page == current_page:
        return

    import streamlit.components.v1 as components
    components.html(r"""
      <script>
      (() => {
        function toTop() {
          try {
            const win = window.parent;
            const doc = win.document;
            const anchor = doc.getElementById('esmiha-page-top');
            if (anchor) anchor.scrollIntoView({block:'start', behavior:'instant'});
            const selectors = [
              '[data-testid="stMain"]',
              '[data-testid="stAppViewContainer"]',
              'section.main', '.main', 'main'
            ];
            const elements = [doc.documentElement, doc.body,
                              doc.scrollingElement,
                              ...selectors.map(s => doc.querySelector(s))];
            for (const el of elements) {
              if (el && typeof el.scrollTo === 'function') {
                el.scrollTo({top:0,left:0,behavior:'instant'});
              }
            }
            win.scrollTo(0,0);
          } catch (_err) { /* Certains navigateurs limitent l'accès à la fenêtre parente. */ }
        }
        toTop();
        requestAnimationFrame(toTop);
      })();
      </script>
    """, height=0)


def navigation_footer():
    current = PAGES.index(st.session_state["nav"])
    st.divider()
    left, spacer, right = st.columns([2.8,3,3.7], vertical_alignment="center")
    if current > 0:
        left.button("← Étape précédente", on_click=navigate_to,
                    args=(PAGES[current-1],), use_container_width=True)
    with right:
        if current < len(PAGES)-1:
            label = "Étape suivante →" if current < len(PAGES)-2 else "Voir le complément →"
            st.button(label, type="primary", on_click=navigate_to,
                      args=(PAGES[current+1],), use_container_width=True)
        else:
            st.button("Retour à l'accueil ↺", type="primary",
                      on_click=navigate_to,args=(PAGES[0],), use_container_width=True)


def home():
    ui.hero()
    st.markdown("## Ce que tu vas apprendre")
    ui.hint("Dans ce TD, tu vas apprendre à entraîner, comparer et comprendre plusieurs modèles de classification à partir d'une enquête fictive sur une population d'humains et de vampires. Ce décor sert simplement de support pour travailler une vraie démarche de machine learning : observer les données, distinguer ce qui sert à l'apprentissage de ce qui permet la vérification, puis comparer **Random Forest, XGBoost, Ridge, Lasso** et **Elastic Net** dans les mêmes conditions avant de tester leurs prédictions sur un nouvel individu. Le complément final sur les réseaux de neurones te permettra d'explorer une autre famille de modèles. Concrètement, tu manipules les données et les méthodes, tu rédiges tes réponses, puis tu peux consulter les éléments de correction ; le bouton <b>❔</b> donne un indice sans livrer directement la réponse. Tes réponses sont conservées pendant la séance, tu peux aussi sauvegarder ton travail en JSON, télécharger ton TD rempli en PDF et ouvrir le corrigé intégral.")
    with st.expander("Petit lexique pour démarrer"):
        st.markdown("""| Terme | En clair |
|---|---|
| **Apprentissage** | Le modèle découvre des régularités dans les exemples dont on connaît déjà la classe. |
| **Prédiction** | Il propose ensuite une classe pour un individu qu'il n'a jamais vu. |
| **Algorithme** | La méthode qui lui permet de construire ses règles de décision. |
| **Train / test** | Les données utilisées pour apprendre / celles gardées de côté pour vérifier. |
| **Validation croisée** | On recommence l'évaluation sur plusieurs petits groupes du train pour éviter de dépendre d'un seul découpage. |
| **Score** | Un nombre qui résume une facette de la qualité des prédictions. Aucun score ne dit tout. |""")
        st.caption("Ces mots reviendront pendant les manipulations. Les boutons ❔ permettent de retrouver leur sens au bon moment.")
    with st.expander("Les dix variables du jeu de données"):
        st.markdown("""- **Fer sanguin** : la quantité de fer présente dans le sang.
- **Pâleur cutanée** : un indice fictif qui traduit à quel point la peau paraît pâle.
- **Sensibilité au soleil** : un score fictif qui représente la gêne ressentie au soleil.
- **Température corporelle** : la température de l'individu, en degrés Celsius.
- **Âge** : l'âge de l'individu, en années. Oui, certains vampires peuvent être très âgés.
- **Fréquence cardiaque** : le nombre de battements du cœur par minute.
- **Régénération** : un indice fictif qui résume la capacité de récupération.
- **Longueur des canines** : la taille des canines, exprimée en millimètres.
- **Force** : un indice fictif de force physique.
- **Vitesse** : un indice fictif de vitesse de déplacement.

Toutes ces variables sont simulées pour l'exercice. Elles servent à construire un jeu de données cohérent pour apprendre à comparer des modèles, pas à décrire une situation réelle.""")
    st.info("Quand tu es prêt, utilise **Étape suivante →** en bas à droite.")

def population():
    ui.header("ÉTAPE 01 / DONNÉES", "Générer le jeu de données", "")
    st.write("Tu peux choisir le nombre de personnages et la part de vampires. "
             "L'application prépare ensuite un tableau que tu analyseras exactement comme un jeu de données classique. "
             "La génération n'est **pas** le sujet du TD : ce sont les résultats des algorithmes qui nous intéressent.")
    ncol, pcol, closecol = st.columns([1,1.2,1.35], vertical_alignment="bottom")
    ncol.number_input("Nombre d'individus", min_value=200, max_value=5000, step=100,
                     key="sample_n", help="Un effectif plus élevé donne davantage d'exemples à l'algorithme, mais prend aussi plus de temps à analyser.")
    pcol.slider("Proportion de vampires (%)", min_value=10,max_value=90,step=5,
                key="sample_prevalence_pct",
                help="Choisis le pourcentage de vampires ; les humains représentent le reste de la population.")
    closecol.slider("Proximité humain/vampire (%)",min_value=0,max_value=100,step=5,
                    key="sample_proximity",help="0 : groupes nettement distincts. 100 : caractéristiques générées selon les mêmes distributions pour les deux groupes. Plus les groupes se ressemblent, plus la classification risque d'être difficile.")
    st.session_state["sample_prevalence"] = st.session_state["sample_prevalence_pct"] / 100.0
    st.caption("Proximité : 0 % = groupes bien distincts ; 100 % = profils indiscernables à partir de ces variables. À 100 %, le modèle ne dispose plus de caractéristiques utiles pour retrouver la classe.")
    if st.button("🎲 Générer",type="primary",use_container_width=True):
        ensure_sample()
        st.rerun()
    st.caption("La proportion choisie est une valeur de départ : la proportion obtenue varie légèrement "
               "d'un échantillon à l'autre. Chaque nouveau jeu de données remet à zéro les entraînements précédents : "
               "il faut réapprendre les modèles pour pouvoir comparer les résultats.")
    df=current_data()
    if df is None:
        df=ensure_sample()
    if st.session_state['data_spec']:
        spec=st.session_state['data_spec']
        if st.session_state.get('dataset_source') != 'CSV importé' and (
            spec.get('n')!=st.session_state['sample_n'] or
            spec.get('proximity',0)!=st.session_state['sample_proximity'] or
            abs(float(spec.get('prevalence',.5))-float(st.session_state['sample_prevalence']))>.001):
            st.warning("Les réglages ont changé, mais le tableau affiché correspond encore au dernier jeu généré. Clique sur « Générer » pour appliquer les nouveaux réglages.")
    a,c=st.columns(2)
    a.metric("Individus",f"{len(df):,}")
    c.metric("Classe Vampire",f"{df['Vampirisme'].mean():.1%}")
    t1,t2=st.columns([1,1.3],gap="large")
    with t1:
        ui.vampire_avatar(int((df['Vampirisme']==0).sum()), int((df['Vampirisme']==1).sum()), int(st.session_state['sample_proximity']))
    with t2:
        st.markdown("### Quelques lignes du tableau")
        st.dataframe(label_classes(df).head(12),use_container_width=True,hide_index=True)
        st.download_button("↓ Télécharger Data_vampi.csv",df.to_csv(index=False).encode("utf-8-sig"),
                           file_name="Data_vampi.csv",mime="text/csv",use_container_width=True)
    explain("Variable cible et prédicteurs", "**Cible** : la classe connue dans le jeu d'entraînement, ici `Vampirisme`. **Prédicteurs** : dix caractéristiques disponibles pour établir la prédiction. Le modèle ne peut pas utiliser la vraie classe lorsqu'on lui demande de la prédire.")
    question("01")
    question("02")
    with st.expander("Dictionnaire des variables"):
        for v in VARIABLES:
            st.markdown(f"**{v.label}** (`{v.key}`) : {v.description}")
    st.divider()
    st.divider()
    st.markdown("### Mini-expérience : que se passe-t-il quand la population change ?")
    for code in ('31','32','33'):
        question(code)

def exploration():
    ui.header("ÉTAPE 02 / EXPLORATION", "Explorer les relations utiles à la classification",
              "Avant de demander au modèle de prédire, regardons ce que racontent les variables. "
              "Nous allons repérer des différences entre les groupes, mais aussi les situations où les profils se ressemblent.")
    ui.hint("<b>Comment faire :</b> sélectionne une caractéristique, déplace la souris sur les graphiques "
            "pour voir les valeurs, puis compare les formes et les recouvrements. "
            "Les questions qui suivent t'aident à formuler ce que tu observes.")
    if not require_data(): return
    df = current_data()
    st.markdown("### Distributions conditionnelles")
    a, b = st.columns([2, 1])
    with a:
        var = st.selectbox("Variable étudiée", KEYS, format_func=lambda x: f"{LABELS[x]} · {UNITS[x]}")
    with b:
        chart_mode = st.radio("Représentation", ["Densités", "Violons", "Boîtes à moustaches"], horizontal=True)
    st.plotly_chart(viz.distribution_chart(df, var, chart_mode), use_container_width=True, config={"displaylogo": False})
    st.caption(DESCRIPTIONS[var])
    explain("Lire une distribution", "Le pic indique où se concentrent les observations. La largeur décrit leur dispersion. Deux courbes superposées montrent qu'un même résultat est compatible avec les deux classes.")
    question("03")
    means = df.groupby("Vampirisme")[var].agg(["mean", "std", "median", "count"]).round(2)
    means.index = means.index.map({0: "Humain", 1: "Vampire"})
    st.dataframe(means.rename(columns={"mean": "Moyenne", "std": "Écart-type", "median": "Médiane", "count": "Effectif"}),
                 use_container_width=True)
    
    ui.hint("<b>Observation :</b> les distributions peuvent se chevaucher fortement. Même une caractéristique dont la moyenne est très différente entre les classes ne garantit pas, à elle seule, une classification parfaite.")
    st.divider()
    st.markdown("### Relations entre variables")
    tabs = st.tabs(["Nuage de points", "Matrice de corrélation", "Table de données"])
    with tabs[0]:
        xcol, ycol = st.columns(2)
        x = xcol.selectbox("Axe horizontal", KEYS, index=4, format_func=lambda k: LABELS[k])
        opts = [v for v in KEYS if v != x]
        y = ycol.selectbox("Axe vertical", opts, index=min(6, len(opts)-1), format_func=lambda k: LABELS[k])
        st.plotly_chart(viz.scatter_chart(df, x, y), use_container_width=True, config={"displaylogo": False})
        st.caption("Pour conserver une interface fluide, le graphique affiche au maximum 3 000 individus, tirés de façon reproductible.")
        question("04")
    with tabs[1]:
        include_target = st.checkbox("Inclure la variable cible (0/1) dans les corrélations", value=False)
        corr_cols = (["Vampirisme"] if include_target else []) + KEYS
        if include_target:
            # The target label is not in the normal variable dictionary.
            import plotly.graph_objects as go
            mat = df[corr_cols].corr()
            pretty = ["Classe (0/1)" if v == "Vampirisme" else LABELS[v] for v in corr_cols]
            fig = go.Figure(go.Heatmap(z=mat.to_numpy(), x=pretty, y=pretty, zmin=-1, zmax=1,
                   colorscale=[[0, "#2c6c91"], [.5, "#24263c"], [1, "#ff6589"]],
                   text=np.round(mat.to_numpy(), 2), texttemplate="%{text:.2f}"))
            fig.update_yaxes(autorange="reversed")
            fig = viz.style(fig, 545)
        else:
            fig = viz.correlation_chart(df, KEYS)
        st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
        st.info("Une corrélation n'est pas une causalité. La cible binaire peut être associée à plusieurs variables sans que ces variables se causent mutuellement.")
    with tabs[2]:
        st.dataframe(label_classes(df), height=430, hide_index=True, use_container_width=True)
        st.caption("Toutes les valeurs sont simulées. Aucune donnée personnelle n'est utilisée.")
    question("05")
    question("34")
    question("35")
    question("36")


MODEL_MAIN = ["Forêt aléatoire", "XGBoost", "Régression logistique · Ridge",
              "Régression logistique · Lasso", "Régression logistique · Elastic Net"]

def method_info(name):
    texts={
      "Forêt aléatoire": ("Plusieurs arbres, un vote collectif", "Une forêt aléatoire entraîne des arbres légèrement différents, puis agrège leurs prédictions. Elle peut représenter des relations non linéaires et des interactions sans imposer une équation linéaire."),
      "XGBoost": ("Des arbres qui s'ajoutent les uns aux autres", "XGBoost construit progressivement une combinaison d'arbres. Chaque nouvel arbre contribue à améliorer l'objectif optimisé par l'ensemble. Ce principe est différent du vote d'arbres appris indépendamment."),
      "Régression logistique · Ridge": ("Des coefficients rendus plus prudents", "La régression logistique transforme une somme pondérée de caractéristiques en probabilité. Ridge (L2) pénalise les coefficients trop grands pour limiter la complexité."),
      "Régression logistique · Lasso": ("Réduire et sélectionner", "Lasso (L1) peut rendre certains coefficients exactement nuls. C'est une façon d'obtenir un modèle plus parcimonieux, même si la sélection est parfois instable avec des variables corrélées."),
      "Régression logistique · Elastic Net": ("Un compromis entre L1 et L2", "Elastic Net combine les pénalisations de Lasso et Ridge. Il peut à la fois réduire les coefficients et en annuler certains."),
    }
    title,txt=texts[name]
    st.markdown(f"#### {title}")
    st.write(txt)
    st.plotly_chart(algorithm_map(name),use_container_width=True,config={"displaylogo":False})
    reminders={
      "Forêt aléatoire": "À observer : les arbres donnent des avis différents et la forêt les rassemble.",
      "XGBoost": "À observer : les arbres se succèdent pour améliorer progressivement le résultat collectif.",
      "Régression logistique · Ridge": "À observer : toutes les variables peuvent conserver un poids, mais les poids trop extrêmes sont freinés.",
      "Régression logistique · Lasso": "À observer : certains poids peuvent devenir nuls. Une variable peut alors être écartée.",
      "Régression logistique · Elastic Net": "À observer : réduction des poids et sélection possible de variables sont combinées.",
    }
    st.caption(reminders[name])

def training():
    ui.header("ÉTAPE 03 / VALIDATION NON CROISÉE", "Entraîner et tester une première fois",
              "Cette étape met en place une séparation apprentissage/test, puis la comparaison de Random Forest, XGBoost, Ridge, Lasso et Elastic Net sur exactement le même jeu de données.")
    if not require_data():return
    st.markdown("### A. Réserver un jeu de test")
    ui.hint("<b>Image à retenir :</b> si tu révises un exercice avec ses réponses, tu ne peux "
            "pas ensuite utiliser le même exercice pour prouver que tu sais résoudre des cas inconnus. "
            "Le train sert à apprendre ; le test permet de découvrir comment le modèle se comporte "
            "sur de nouvelles observations.")
    st.write("Le modèle apprend sur 80 % des individus. Les 20 % restants permettent d'observer la qualité de ses prédictions sur des exemples qu'il n'a pas rencontrés pendant l'apprentissage.")
    ratio=st.slider("Part du jeu de test",.1,.4,.2,.05,key="ratio_input",help="20 % est le protocole proposé pour ce TD.")
    split_seed = 42
    if st.button("Créer la séparation 80/20 (ou appliquer le réglage choisi)",type="primary",use_container_width=True):
        try:
            split=make_split(current_data(),test_ratio=float(ratio),seed=int(split_seed))
            st.session_state['split']=split
            st.session_state['model_results']={}
            st.session_state['td_pdf_session']=None
            clear_explanations()
            st.success("Séparation définie. Le train et le test sont conservés pendant la séance.")
        except ValueError as exc:st.error(str(exc))
    if st.session_state['split'] is None:
        question("06")
        return
    split=st.session_state['split']
    if float(ratio)!=split.test_ratio or int(split_seed)!=split.seed:
        st.warning("Les réglages affichés ne correspondent pas à la séparation active. Relance la création pour les appliquer.")
    m1,m2=st.columns(2)
    m1.metric("Apprentissage",len(split.X_train))
    m2.metric("Test réservé",len(split.X_test))
    question("06")
    st.divider()
    st.markdown("### B. Comprendre les différentes familles d'algorithmes")
    family=st.selectbox("Choisir une méthode à examiner",MODEL_MAIN,format_func=lambda k:MODEL_SHORT[k])
    method_info(family)
    explain("Pourquoi parle-t-on de régularisation ?","Les modèles peuvent apprendre des fluctuations propres à l'échantillon. **Ridge (L2)** réduit les coefficients ; **Lasso (L1)** peut en annuler ; **Elastic Net** combine les deux. Ici, toutes ces variantes sont des **régressions logistiques**, et non des régressions linéaires de la classe 0/1.")
    for code in ["07","08","09","10","11"]:
        # Une question par méthode, juste sous le tableau explicatif et la figure de la méthode correspondante.
        if {"07":"Forêt aléatoire","08":"XGBoost","09":"Régression logistique · Ridge","10":"Régression logistique · Lasso","11":"Régression logistique · Elastic Net"}[code]==family:
            question(code)
    st.divider()
    st.markdown("### C. Entraîner les cinq méthodes sur exactement les mêmes données")
    if not has_xgboost():
        st.info("XGBoost n’est pas disponible dans cet environnement. Installe-le avec `python -m pip install -r requirements-xgboost.txt`, puis relance l’application. Les autres méthodes restent accessibles.")
    available=[k for k in MODEL_MAIN if k!='XGBoost' or has_xgboost()]
    selected=st.multiselect("Choisir les méthodes à comparer",available,
                            default=[k for k in MODEL_MAIN if k in available],
                            format_func=lambda k:MODEL_SHORT[k],key='select_simple')
    if st.button("▶ Entraîner et évaluer sans validation croisée",type="primary",disabled=not selected,use_container_width=True):
        progress=st.progress(0.,text="Entraînement...")
        for i,name in enumerate(selected):
            try:
                with st.spinner(f"Ajustement de {MODEL_SHORT[name]}..."):
                    with computation_slot():
                        st.session_state['model_results'][name]=train_evaluate(name,split,10,False)
                    st.session_state.pop(f'importance_{name}',None)
                    st.session_state['td_pdf_session']=None
            except Exception as exc:st.error(f"{name} : {exc}")
            progress.progress((i+1)/len(selected))
        st.success("Modèles ajustés. Tu peux maintenant choisir le nombre de plis pour la validation croisée.")
    if results():
        st.markdown("#### Résultats de cette première évaluation (test réservé)")
        frame=compare_results(results())
        st.dataframe(frame[["Modèle","Accuracy test","Balanced accuracy test","AUC-ROC test","F1 test"]].style.format(precision=3),
                     hide_index=True,use_container_width=True)
        st.plotly_chart(viz.comparison_chart(frame),use_container_width=True,config={"displaylogo":False})
        question("12")
        question("13")
        question("14")
        for code in ('37','38','39','40'):
            question(code)
        st.caption("Dans une vraie étude, le test n'est pas utilisé pour ajuster continuellement le choix du modèle ; ce premier tableau sert ici à comprendre la méthode dite non croisée.")

def cross_validation_page():
    ui.header("ÉTAPE 04 / VALIDATION CROISÉE", "Répéter l'évaluation sur plusieurs blocs",
              "Cette étape applique une validation croisée stratifiée sur les seules données d'apprentissage. Le jeu de test ne participe à aucun pli.")
    if not require_split():return
    if not results():
        st.info("Entraîne d'abord une ou plusieurs méthodes dans « 04 · Validation non croisée ».")
        return
    st.markdown("### A. Visualiser les tours de validation")
    st.write("Une seule séparation peut donner un résultat favorable ou défavorable par hasard. "
             "La validation croisée permet de refaire plusieurs fois un exercice comparable : "
             "un groupe d'individus est mis de côté, on entraîne sur les autres, puis on change de groupe. "
             "Au bout de tous les tours, chaque individu du train a participé une fois à la validation.")
    folds=st.slider("Nombre de plis", min_value=2, max_value=10, value=10, step=1, key='folds_choice',
                    help="Choisis librement entre 2 et 10 plis. Un seul pli ne permet pas de séparer apprentissage et validation. La proposition de départ est de 10 plis.")
    st.plotly_chart(cv_folds_chart(int(folds)),use_container_width=True,config={"displaylogo":False})
    explain("Validation croisée stratifiée", "On partage le **train** en plusieurs blocs. À chaque tour, un bloc sert à valider et les autres à entraîner un nouveau modèle. Chaque bloc sert une fois à valider. **Le jeu de test reste à l'écart.** La stratification préserve approximativement les proportions de classes dans les plis.")
    question("15")
    question("16")
    st.markdown("### B. Calculer les performances internes")
    st.write("Le prétraitement est recalculé à l'intérieur de chaque pli, ce qui évite une fuite d'information lors de la validation.")
    question("17")
    chosen=st.multiselect("Modèles à valider",list(results()),default=list(results()),
                          format_func=lambda k:MODEL_SHORT[k],key='select_cv')
    if st.button("▶ Effectuer la validation croisée",type="primary",disabled=not chosen,use_container_width=True):
        # Une modification du nombre de plis invalide les anciennes CV pour éviter de mélanger les protocoles.
        if int(folds)!=st.session_state.get('cv_folds'):
            for r in results().values():r['cv']=None
        st.session_state['cv_folds']=int(folds)
        progress=st.progress(0.,text="Validation interne...")
        for i,name in enumerate(chosen):
            try:
                with st.spinner(f"Validation croisée : {MODEL_SHORT[name]}..."):
                    with computation_slot():
                        st.session_state['model_results'][name]['cv']=cv_evaluate(name,st.session_state['split'],int(folds))
                    st.session_state['td_pdf_session']=None
            except Exception as exc:st.error(f"{name} : {exc}")
            progress.progress((i+1)/len(chosen))
        st.success("Les scores des plis sont enregistrés et prêts à être comparés.")
    available_cv={k:r for k,r in results().items() if r.get('cv')}
    if available_cv:
        import plotly.graph_objects as go
        fig=go.Figure()
        for name,r in available_cv.items():
            scores=r['cv']['accuracy']
            fig.add_trace(go.Scatter(x=list(range(1,len(scores)+1)),y=scores,
                         mode='lines+markers',name=MODEL_SHORT[name],line={'width':2}))
        fig.update_layout(title='Accuracy observée à chaque pli',xaxis_title='Pli de validation',
                          yaxis_title='Accuracy',yaxis_range=[0,1],height=400,template='plotly_dark',
                          paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig,use_container_width=True,config={'displaylogo':False})
        summary=pd.DataFrame([{'Algorithme':MODEL_SHORT[n], 'Accuracy CV moyenne':np.mean(r['cv']['accuracy']),
                               'Écart-type entre plis':np.std(r['cv']['accuracy']),
                               'F1 CV moyen':np.mean(r['cv']['f1']),
                               'AUC-ROC CV moyenne':np.mean(r['cv']['roc_auc'])} for n,r in available_cv.items()])
        st.dataframe(summary.style.format(precision=3),hide_index=True,use_container_width=True)
        question("18")
        st.caption("L'écart-type entre les plis n'est pas un intervalle de confiance : il décrit la dispersion des scores sur ce découpage.")
        question('41')
        question('42')

def neural_networks():
    ui.header("COMPLÉMENT FACULTATIF", "Un autre algorithme : le réseau de neurones",
              "Cette partie est un prolongement facultatif du TD. Elle présente le perceptron multicouche comme une famille supplémentaire à comparer à Random Forest, XGBoost et aux régressions logistiques.")
    ui.hint("<b>Partie bonus :</b> tu as déjà découvert cinq méthodes de classification. "
            "Le réseau de neurones est une sixième façon de résoudre le même problème. Nous allons "
            "comprendre ses éléments un par un, puis le comparer aux modèles classiques. "
            "Aucune notion avancée de mathématiques n'est nécessaire pour cette première approche.")
    st.markdown("### Avant de commencer : la machine apprend-elle comme un cerveau ?")
    st.write("Le nom peut prêter à confusion. Un neurone artificiel ne pense pas. Il reçoit "
             "des nombres, les combine avec des coefficients appelés *poids*, puis transmet "
             "un résultat. Imagine une série de petits calculs reliés entre eux. En modifiant "
             "progressivement leurs coefficients, on obtient une règle de prédiction.")
    ui.hint("<b>Notre objectif :</b> donner dix caractéristiques d'un individu au réseau et "
            "obtenir un score entre 0 et 1. Ce score est ensuite interprété comme une "
            "probabilité prédite de la classe Vampire, à condition d'en vérifier la calibration.")
    st.markdown("### 1. Visualiser l'architecture")
    mode = st.radio("Architecture à explorer", list(ARCHITECTURES),
                    format_func=lambda name: MODEL_SHORT[name], horizontal=True,
                    help="Un perceptron multicouche (MLP) est un réseau dense : chaque neurone d'une couche est relié à ceux de la suivante.")
    architecture = ARCHITECTURES[mode]
    st.plotly_chart(network_chart(architecture), use_container_width=True,
                    config={"displaylogo": False})
    a,b,c = st.columns(3)
    a.metric("Variables entrantes", "10")
    b.metric("Couches cachées", str(len(architecture)))
    c.metric("Poids et biais", f"{neuron_count(architecture):,}")
    st.caption("Le schéma simplifie visuellement les couches les plus peuplées : les effectifs indiqués sont ceux du modèle réellement entraîné.")
    explain("Les poids et les biais", "Chaque connexion a un **poids** qui amplifie ou atténue le signal. "
            "Un **biais** permet au neurone d'ajuster son résultat indépendamment des entrées. "
            "Les poids ne sont pas écrits à la main : ils sont appris pendant l'entraînement.")
    st.write("Les dix variables entrent à gauche du schéma. Elles traversent une ou plusieurs "
             "**couches cachées**, où elles sont progressivement combinées. À droite, une sortie "
             "résume le score prédit. Le schéma représente une architecture ; "
             "il ne prétend pas représenter un raisonnement conscient.")
    for code in ('51','52'):
        question(code)

    st.divider()
    st.markdown("### 2. Comprendre les fonctions d'activation")
    st.plotly_chart(activation_chart(), use_container_width=True,
                    config={"displaylogo": False})
    ui.hint("<b>Très simplement :</b> sans activation non linéaire, empiler plusieurs couches linéaires revient à une seule transformation linéaire. La fonction ReLU permet au réseau d'apprendre des relations plus souples ; la sigmoïde sert ici à comprendre la probabilité de sortie de la classe positive.")
    explain("Standardisation", "Avant de recevoir une observation, le MLP utilise un StandardScaler "
            "calculé sur l'apprentissage. L'âge, la température et les scores sur dix sont ainsi "
            "replacés sur des échelles comparables. La validation et le test sont transformés "
            "avec les seules valeurs apprises sur l'entraînement.")
    st.write("La **fonction d'activation** permet au réseau d'aller au-delà d'une simple "
             "combinaison linéaire. Sur le graphique, ReLU transmet les valeurs positives "
             "et ramène les valeurs négatives à zéro. La sigmoïde transforme un nombre "
             "en une valeur comprise entre 0 et 1 : elle aide à comprendre la sortie probabiliste.")
    question('53')
    question('54')
    st.markdown("### Une analogie pour comprendre l'apprentissage")
    st.write("Imagine un élève qui s'entraîne sur des dossiers déjà corrigés. Il propose "
             "une réponse, regarde l'écart avec la solution connue, puis ajuste sa méthode. "
             "Le réseau fait quelque chose de comparable, mais à travers des opérations "
             "mathématiques : ses poids sont modifiés pour diminuer une **fonction de perte**. "
             "C'est la rétropropagation qui calcule comment chaque poids contribue à l'erreur.")
    question('55')


    st.divider()
    st.markdown("### 3. Faire apprendre le réseau")
    if not require_split():
        st.caption("La préparation des données se réalise dans l'étape Apprentissage, avant de venir ici.")
        return
    split = st.session_state["split"]
    st.markdown("Pour comparer les approches, l’application conserve les mêmes données et les mêmes réglages d’entraînement. L'apprentissage du réseau est réalisé sur le train ; la validation croisée utilise uniquement le train.")
    do_cv = st.checkbox("Inclure la validation croisée (plus long)", value=False,
                        key="neural_cv", help="La validation croisée répète l'entraînement de zéro sur plusieurs sous-ensembles du train.")
    if st.button(f"▶ Entraîner {MODEL_SHORT[mode]}", type="primary", use_container_width=True):
        try:
            with st.spinner("Optimisation des poids en cours..."):
                with computation_slot():
                    result = train_evaluate(mode, split, st.session_state["cv_folds"], do_cv)
            st.session_state["model_results"][mode] = result
            st.session_state["td_pdf_session"] = None
            st.session_state.pop(f"importance_{mode}", None)
            st.success("Réseau entraîné. Tu peux consulter les prédictions dans Évaluation et les analyser dans Interprétation.")
        except Exception as exc:
            st.error(f"L'entraînement n'a pas abouti : {exc}")
    if mode in results():
        r = results()[mode]
        left,right = st.columns([1.55, 1],gap="large")
        with left:
            st.markdown("#### Évolution de la perte pendant l'entraînement")
            fig = loss_chart(r["estimator"])
            if fig is not None:
                st.plotly_chart(fig,use_container_width=True,config={"displaylogo":False})
        with right:
            st.metric("Accuracy sur le test réservé",f"{r['metrics']['accuracy']:.1%}")
            st.metric("Sensibilité",f"{r['metrics']['recall']:.1%}")
            if r["cv"]:
                st.metric("Accuracy moyenne des plis",f"{np.mean(r['cv']['accuracy']):.1%}")
            st.caption("La courbe de perte décrit uniquement l'optimisation sur les données d'apprentissage. Elle ne mesure pas directement la généralisation.")
    else:
        st.info("Entraîne l'architecture choisie pour afficher sa courbe d'optimisation.")

    st.markdown("### Comment lire la courbe de perte ?")
    st.write("Une courbe descendante signifie que le réseau réduit l'erreur qu'il cherche "
             "à minimiser sur les individus utilisés pour apprendre. Elle ne suffit pas "
             "pour savoir s'il prédira correctement de nouveaux individus. "
             "Pour cela, il faut vérifier ses résultats en validation et sur le test réservé.")
    question('56')
    question("30")
    st.markdown("### 4. Comparer les deux architectures")
    compare = [key for key in ARCHITECTURES if key in results()]
    if len(compare)==2:
        st.dataframe(compare_results({k:results()[k] for k in compare}).style.format(precision=3),
                     hide_index=True,use_container_width=True)
        st.caption("Le nombre de couches ne suffit jamais, à lui seul, à départager deux réseaux. Compare leurs erreurs et la variabilité en validation croisée.")
    else:
        st.caption("Entraîne les deux réseaux successivement pour comparer leurs performances sur le même protocole.")
    question('57')
    question('58')
    ui.hint("<b>Conclusion du bonus :</b> ajouter des couches ne rend pas automatiquement un réseau meilleur. "
            "Comme pour les autres méthodes, compare les résultats, les erreurs, "
            "la stabilité et le coût de calcul avant de choisir une approche.")


def evaluation():
    ui.header("ÉTAPE 05 / COMPARAISON", "Ne jamais s'arrêter à un score",
              "Compare les algorithmes, examine leurs erreurs et comprends ce que mesure chaque indicateur. Tous les graphiques utilisent les prédictions du jeu de test réservé.")
    if not require_split(): return
    if not results():
        st.info("Entraîne au moins un modèle dans « 04 · Validation non croisée ».")
        return
    frame = compare_results(results())
    st.markdown("### Panorama des modèles")
    st.write("Regarde d'abord les performances globales, puis cherche les erreurs. "
             "Ne choisis pas simplement la première ligne du classement : selon la proportion "
             "de vampires, un score très élevé peut masquer une mauvaise détection de la classe rare.")
    split = st.session_state["split"]
    major = int(split.y_train.mode().iloc[0])
    baseline_acc = float(np.mean(split.y_test.to_numpy() == major))
    st.caption(f"Repère essentiel : prédire **toujours {('Vampire' if major else 'Humain')}** donne déjà "
               f"**{baseline_acc:.1%} d'accuracy** sur le test, mais ne reconnaît jamais l'autre classe. "
               "Compare aussi la balanced accuracy et la sensibilité.")
    st.plotly_chart(viz.comparison_chart(frame), use_container_width=True, config={"displaylogo": False})
    st.dataframe(frame.style.format(precision=3, na_rep="-"), use_container_width=True, hide_index=True)
    question("19")
    question("20")
    question("43")
    question("44")
    st.caption("Comparer plusieurs modèles sur le même test est utile pour l'enseignement, mais sélectionner indéfiniment celui ayant le meilleur score de test finit par entraîner un sur-ajustement au test. Pour une étude réelle, sélectionner sur CV puis tester une seule fois.")
    st.divider()
    st.markdown("### Autopsie d'un modèle")
    choice = st.selectbox("Modèle à examiner", list(results()), format_func=lambda k: MODEL_SHORT[k])
    result = results()[choice]
    metrics = result["metrics"]
    cc = st.columns(5)
    cc[0].metric("Accuracy", f"{metrics['accuracy']:.1%}")
    cc[1].metric("Balanced accuracy", f"{metrics['balanced_accuracy']:.1%}")
    cc[2].metric("Sensibilité", f"{metrics['recall']:.1%}")
    cc[3].metric("Spécificité", f"{metrics['specificity']:.1%}")
    cc[4].metric("AUC-ROC", f"{metrics['roc_auc']:.3f}")
    explain("Sensibilité / spécificité", "**Sensibilité** : parmi les vrais vampires, quelle proportion le modèle retrouve-t-il ? **Spécificité** : parmi les humains, quelle proportion est reconnue ? Ces deux indicateurs répondent à des questions différentes.")
    t1, t2, t3 = st.tabs(["Erreurs & seuil", "Discrimination", "Calibration & CV"])
    with t1:
        st.markdown("**Expérimentation du seuil de décision**")
        threshold = st.slider("Classer comme vampire si P(vampire) ≥", .05, .95, .5, .05,
                              key=f"threshold_{choice}")
        altered = threshold_metrics(result, threshold)
        a, b, c = st.columns(3)
        a.metric("F1 au seuil affiché", f"{altered['f1']:.3f}")
        b.metric("Sensibilité", f"{altered['recall']:.3f}")
        c.metric("Spécificité", f"{altered['specificity']:.3f}")
        st.plotly_chart(viz.confusion_chart(result, threshold), use_container_width=True, config={"displaylogo": False})
        st.caption("Lignes = vérité ; colonnes = prédiction. Haut droit = humain faussement classé vampire. Bas gauche = vampire manqué.")
        question("21")
        question("22")
        question("45")
    with t2:
        a, b = st.columns(2)
        roc, pr = viz.roc_pr_charts(result)
        with a:
            st.markdown("#### ROC")
            st.plotly_chart(roc, use_container_width=True, config={"displaylogo": False})
        with b:
            st.markdown("#### Précision-rappel")
            st.plotly_chart(pr, use_container_width=True, config={"displaylogo": False})
        st.plotly_chart(viz.probability_chart(result), use_container_width=True, config={"displaylogo": False})
        st.caption("Sur une population déséquilibrée, la courbe précision-rappel est souvent plus informative que l'accuracy seule.")
        question("23")
        question("46")
    with t3:
        a, b = st.columns(2)
        with a:
            st.markdown("#### Fiabilité des probabilités")
            st.plotly_chart(viz.calibration_chart(result), use_container_width=True, config={"displaylogo": False})
            st.metric("Score de Brier (plus faible = mieux)", f"{metrics['brier']:.3f}")
        with b:
            st.markdown("#### Variabilité entre plis")
            cv_fig = viz.cv_chart(result)
            if cv_fig is not None:
                st.plotly_chart(cv_fig, use_container_width=True, config={"displaylogo": False})
                st.caption(f"Accuracy CV = {np.mean(result['cv']['accuracy']):.3f} ± {np.std(result['cv']['accuracy']):.3f} (écart-type des plis, non intervalle de confiance).")
            else:
                st.info("La validation croisée n'a pas été demandée pour cet entraînement.")
        st.caption("Pour de petites classes ou des prédictions trop concentrées, les courbes de calibration peuvent être irrégulières.")
    question("24")


def interpretation():
    ui.header("ÉTAPE 06 / INTERPRÉTATION", "Ouvrir la boîte noire",
              "Cherche les indices utilisés par les modèles, observe la façon dont une variable modifie les prédictions moyennes et explore une coupe bidimensionnelle de la frontière de décision.")
    if not require_split(): return
    if not results():
        st.info("Entraîne au moins un modèle dans Apprentissage.")
        return
    choice = st.selectbox("Algorithme à interpréter", list(results()), format_func=lambda k: MODEL_SHORT[k])
    result = results()[choice]
    split = st.session_state["split"]
    st.write("Entraîner un modèle ne suffit pas : il faut comprendre **sur quelles informations** "
             "il s'appuie et **comment** ses réponses changent avec les caractéristiques. "
             "Les trois graphiques présentent des angles complémentaires ; aucun ne démontre "
             "une relation de cause à effet.")
    explain("Interpréter une prédiction", "Il faut distinguer **la contribution d’une variable dans le modèle**, **la réaction moyenne du score lorsque cette variable varie**, et **une relation causale**. Les graphiques de cette page renseignent surtout les deux premières notions.")
    tab1, tab2, tab3 = st.tabs(["Importance par permutation", "Dépendance partielle & ICE", "Surface de décision 2D"])
    with tab1:
        st.markdown("On mélange une variable du **train** et on regarde si la balanced accuracy du modèle se dégrade. La comparaison est calculée sur une même échelle pour tous les modèles.")
        if st.button("Calculer les importances", key=f"imp_{choice}"):
            with st.spinner("Permutation des variables..."):
                with computation_slot():
                    st.session_state[f"importance_{choice}"] = feature_importances(
                        result["estimator"], split.X_train, split.y_train, split.seed)
        imp = st.session_state.get(f"importance_{choice}")
        if imp is not None:
            st.plotly_chart(viz.importance_chart(imp), use_container_width=True, config={"displaylogo": False})
            st.dataframe(imp.rename(columns={"variable": "Variable", "importance": "Baisse moyenne du score", "ecart_type": "Variabilité"}), hide_index=True)
        question("25")
        question("47")
        ui.hint("<b>Limite :</b> une importance faible n'établit pas qu'une variable est inutile. Des variables corrélées peuvent se substituer les unes aux autres. Les importances peuvent même être négatives par fluctuation d'échantillonnage.")
    with tab2:
        var = st.selectbox("Variable manipulée", KEYS, format_func=lambda k: LABELS[k], key="pdpvar")
        show_ice = st.toggle("Afficher les courbes individuelles (ICE)", value=True)
        st.plotly_chart(viz.pdp_chart(pdp_ice(result["estimator"], split.X_train, var,
                                             seed=split.seed), var, show_ice),
                        use_container_width=True, config={"displaylogo": False})
        question("26")
        question("48")
        ui.hint("<b>Lecture :</b> la courbe vive représente la probabilité moyenne prédite lorsque cette variable prend différentes valeurs pour plusieurs individus de l'échantillon d'apprentissage ; les traits fins montrent les réponses individuelles (ICE). La moyenne n'est <b>pas</b> un effet causal, et certaines combinaisons de caractéristiques peuvent être peu plausibles.")
    with tab3:
        l, r = st.columns(2)
        x = l.selectbox("Variable 1", KEYS, index=4, format_func=lambda k: LABELS[k], key="dec_x")
        ylist = [k for k in KEYS if k != x]
        y = r.selectbox("Variable 2", ylist, format_func=lambda k: LABELS[k], key="dec_y")
        st.plotly_chart(viz.decision_surface(result["estimator"], split.X_train, x, y),
                        use_container_width=True, config={"displaylogo": False})
        question("27")
        ui.hint("<b>Coupe conditionnelle et non frontière complète :</b> toutes les autres variables sont fixées à la médiane du train. Le paysage de probabilités dépend des valeurs retenues pour ces autres variables.", warning=True)


def challenge():
    ui.header("ÉTAPE 07 / PRÉDICTION", "Humain ou vampire ?",
              "Découvre un individu inédit, hors des données d'entraînement et de test. Fais ton pronostic avant de demander l'avis de la machine et de découvrir la vraie classe.")
    if not require_data(): return
    if not results():
        st.info("Il faut d'abord entraîner un modèle pour comparer ta prédiction à la sienne.")
        return
    explain("Probabilité prédite", "Une probabilité de 0,80 signifie que le modèle attribue 80 % à la classe Vampire pour ce profil. Elle n’est **pas** une certitude, et sa fiabilité dépend de la calibration du modèle.")
    if st.session_state.get("dataset_source")=="CSV importé":
        st.info("Le personnage du défi provient du générateur fictif intégré et non du fichier CSV importé. Il ne sert pas à évaluer les performances sur ce fichier.")
    if st.button("🎲 Générer un personnage inédit", type="primary"):
        spec = st.session_state["data_spec"]
        st.session_state["quiz_person"] = simulate_person(spec["parameters"], spec["prevalence"])
        st.session_state["quiz_reveal"] = False
        st.session_state["quiz_choice"] = "Humain"
    person = st.session_state["quiz_person"]
    if person is None:
        st.info("Génère d'abord un personnage. Sa vraie classe restera secrète jusqu'à ta réponse.")
        return
    st.markdown("### Dossier de l'individu #inconnu")
    a, b = st.columns([1.3, 1], gap="large")
    with a:
        table = pd.DataFrame([{"Caractéristique": LABELS[k], "Valeur": round(person[k], 2),
                               "Unité": UNITS[k]} for k in KEYS])
        st.dataframe(table, hide_index=True, use_container_width=True, height=390)
    with b:
        with st.container(border=True):
            st.markdown("#### Ton enquête")
            guess = st.radio("Quelle est ton hypothèse ?", ["Humain", "Vampire"],
                             horizontal=True, key="quiz_choice", disabled=st.session_state["quiz_reveal"])
            model_choice = st.selectbox("Algorithme de comparaison", list(results()),
                                         format_func=lambda k: MODEL_SHORT[k], key="quiz_model",
                                         disabled=st.session_state["quiz_reveal"])
            if st.button("🔍 Vérifier les prédictions", type="primary", use_container_width=True,
                         disabled=st.session_state["quiz_reveal"]):
                row = pd.DataFrame([{k: person[k] for k in KEYS}], columns=KEYS)
                proba = float(results()[model_choice]["estimator"].predict_proba(row)[0, 1])
                st.session_state["quiz_prediction"] = {
                    "guess": guess, "model": model_choice, "prob": proba,
                    "pred": "Vampire" if proba >= .5 else "Humain",
                    "truth": "Vampire" if person["Vampirisme"] == 1 else "Humain",
                }
                st.session_state["quiz_reveal"] = True
                st.session_state["quiz_history"].append(st.session_state["quiz_prediction"].copy())
                st.rerun()
    if st.session_state["quiz_reveal"]:
        p = st.session_state["quiz_prediction"]
        st.divider()
        st.markdown("### Révélation")
        a, b, c = st.columns(3)
        a.metric("Vérité (simulée)", p["truth"])
        b.metric("Ta réponse", p["guess"], "✓ Exact" if p["guess"] == p["truth"] else "✗ Incorrect")
        c.metric("Avis de l'algorithme", p["pred"], f"P(vampire) = {p['prob']:.1%}")
        if p["pred"] != p["truth"]:
            st.warning("Le modèle s'est trompé : dans une population qui se chevauche, certaines erreurs sont inévitables.")
        else:
            st.success("Le modèle a correctement reconnu la classe simulée.")
    if st.session_state["quiz_history"]:
        with st.expander(f"Historique des défis ({len(st.session_state['quiz_history'])})"):
            st.dataframe(pd.DataFrame(st.session_state["quiz_history"]).rename(columns={
                "guess": "Réponse", "model": "Modèle", "prob": "Probabilité vampire",
                "pred": "Prédiction ML", "truth": "Vérité"}), hide_index=True)
    question("28")
    question("49")


def notebook():
    ui.header("ÉTAPE 08 / RESTITUTION", "Mon carnet et mes résultats",
              "Conserve tes observations, retrouve tes réponses et télécharge ton compte rendu personnel. Ton travail est enregistré pendant la séance ; garde aussi une sauvegarde JSON pour le refaire chez toi.")
    with st.expander("↥ Retrouver mes réponses à partir d’une sauvegarde JSON"):
        st.caption("En cas de changement d’ordinateur ou de redémarrage du serveur, importe ici ta sauvegarde personnelle.")
        saved = st.file_uploader("Choisir mon fichier de sauvegarde (.json)",type=["json"],key="answers_import")
        if saved is not None and st.button("Restaurer mes réponses",use_container_width=True):
            try:
                if saved.size > 1_000_000:
                    raise ValueError("Le fichier dépasse 1 Mo.")
                restore_backup(json.loads(saved.getvalue().decode("utf-8")))
                st.success("Tes réponses et tes notes ont été restaurées.")
                st.rerun()
            except (ValueError,TypeError,UnicodeDecodeError,json.JSONDecodeError) as exc:
                st.error(f"Impossible de lire cette sauvegarde : {exc}")

    a, b = st.columns([1.3, 1], gap="large")
    with a:
        st.markdown("### Mon carnet de laboratoire")
        st.text_area("Observations et conclusions", key="notes", height=310, on_change=update_notes,
                     placeholder="Hypothèses, graphiques remarquables, erreurs observées, interprétation...\n")
        st.download_button("↓ Télécharger mes notes Markdown",
                           st.session_state["notes"].encode("utf-8"), file_name="carnet_td.md",
                           mime="text/markdown", use_container_width=True)
    with b:
        st.markdown("### Mes réponses sont-elles conservées ?")
        st.write("Tes réponses sont enregistrées automatiquement pour ton prénom, ton nom et ton code personnel, à chaque modification. Pour pouvoir les retrouver même si l’hébergement est redémarré, télécharge aussi le fichier JSON proposé en haut de chaque page.")
    st.divider()
    st.markdown("### Télécharger les résultats de la séance")
    spec = st.session_state["data_spec"]
    if spec is None:
        params = st.session_state["parameters"]
        n, prev, seed = int(st.session_state["sample_n"]), float(st.session_state["sample_prevalence"]), int(st.session_state["sample_seed"])
    else:
        params, n, prev, seed = spec["parameters"], spec["n"], spec["prevalence"], spec["seed"]
    data_archive = export_zip(current_data(), params, n, prev, seed, results(),
                              st.session_state["notes"], st.session_state["instruction_pdf"],
                              source=st.session_state["dataset_source"])
    st.download_button("📦 Télécharger le dossier complet de l'expérience (.zip)",
                       data_archive, file_name="TD_Machine_Learning_Experience_ESMIHA.zip", type="primary",
                       mime="application/zip", use_container_width=True)
    st.markdown("### Ma conclusion")
    question("29")
    question("50")
    st.markdown("### Ressources pédagogiques")
    path = ROOT / "docs" / "GUIDE_TD.md"
    st.download_button("↓ Guide du TD", path.read_bytes(),
                       file_name=path.name, mime="text/markdown", use_container_width=True)
    with st.expander("Glossaire du module"):
        for term, definition in glossary():
            st.markdown(f"**{term}** : {definition}")
    st.divider()
    st.markdown("### Mon compte rendu individuel (PDF)")
    st.write("Retrouve les questions **avec tes propres réponses**, dans l'ordre du TD. "
             "Ce fichier est destiné à être conservé ou remis à l'enseignant. Il ne contient "
             "pas les éléments de correction. Seules les réponses de ta session sont utilisées.")
    st.caption(f"Compte rendu au nom de : **{st.session_state['student_name']}**")
    if st.button("📝 Préparer mon compte rendu PDF",type="primary",use_container_width=True):
        with st.spinner("Mise en page de tes réponses..."):
            latest_answers = {q.code: st.session_state.get(f"answer_{q.code}",
                              st.session_state['td_answers'].get(q.code, "")) for q in QUESTIONS}
            st.session_state['td_answers'].update(latest_answers)
            st.session_state['personal_pdf'] = make_student_pdf(
                latest_answers,st.session_state['notes'],
                st.session_state['student_name'],st.session_state['data_spec'],results())
    if st.session_state.get('personal_pdf'):
        st.download_button("↓ Télécharger mon TD rempli (PDF)",
                           st.session_state['personal_pdf'],
                           file_name="Mon_TD_Machine_Learning_ESMIHA.pdf",
                           mime="application/pdf",use_container_width=True)
    st.caption("Après avoir modifié une réponse, clique à nouveau sur « Préparer mon compte rendu PDF » pour actualiser ton document.")
    st.divider()
    st.markdown("### Corrigé complet du TD, au format PDF")
    ui.hint("<b>Pour réviser à ton rythme :</b> les 58 questions sont reprises dans l'ordre, accompagnées de réponses expliquées, de schémas, des définitions et des formules utiles. Le PDF est fourni avec l'application et reste disponible sans connexion Internet.")
    if st.button("Créer un corrigé avec les résultats de cette séance",use_container_width=True):
        with st.spinner("Mise en page du corrigé..."):
            st.session_state["td_pdf_session"] = make_correction_pdf(st.session_state["data_spec"], results())
    if st.session_state["td_pdf_session"] is not None:
        st.download_button("↓ Télécharger mon corrigé contextualisé (PDF)",
                           st.session_state["td_pdf_session"],
                           file_name="Corrige_ESMIHA_ma_seance.pdf", mime="application/pdf",use_container_width=True)
    st.markdown("### Sauvegarder mes réponses pour les reprendre chez moi")
    st.caption("Tu peux enregistrer ton avancement, fermer le navigateur et réimporter ce fichier depuis le même espace lors de ta prochaine séance.")
    answer_record = {"version": 7, "etudiant": st.session_state["student_name"],
                     "etape": st.session_state["nav"],
                     "etape_numero": PAGES.index(st.session_state["nav"]),
                     "reponses": st.session_state["td_answers"], "notes": st.session_state["notes"]}
    st.download_button("↓ Enregistrer mes réponses et mon carnet (.json)",
                       json.dumps(answer_record,ensure_ascii=False,indent=2).encode('utf-8'),
                       file_name="Mes_reponses_TD_ESMIHA.json",mime="application/json",use_container_width=True)



init_state()
identity_gate()
if current_data() is None:
    starter = ROOT / "data" / "Data_vampi.csv"
    if starter.is_file():
        # Fichier fourni avec le TD : les étudiants arrivent directement sur les données.
        df = pd.read_csv(starter)
        st.session_state["data"] = df
        st.session_state["data_spec"] = {
            "parameters": copy_parameters(st.session_state["parameters"]),
            "n": len(df), "prevalence": 0.5,
            "seed": 123, "fingerprint": fingerprint(df),
        }
    else:
        ensure_sample()  # Fallback si le fichier de démonstration est absent.
st.markdown('<div id="esmiha-page-top"></div>', unsafe_allow_html=True)
navigation_header()
page=st.session_state["nav"]
if page==PAGES[0]:home()
elif page==PAGES[1]:population()
elif page==PAGES[2]:exploration()
elif page==PAGES[3]:training()
elif page==PAGES[4]:cross_validation_page()
elif page==PAGES[5]:evaluation()
elif page==PAGES[6]:interpretation()
elif page==PAGES[7]:challenge()
elif page==PAGES[8]:notebook()
else:
    neural_networks()
    from vampire_lab.code_resources import available_guides
    st.divider()
    st.markdown("## Refaire les analyses en Python et en R")
    st.write("Retrouve ici le code des sept méthodes étudiées, en Python et en R (RStudio). Ces fiches permettent de refaire les analyses sur ton ordinateur à partir du fichier Data_vampi.csv.")
    for title, filename, content in available_guides():
        st.download_button(f"↓ {title} (Markdown)",content.encode("utf-8"),
                           file_name=filename,mime="text/markdown",use_container_width=True)

navigation_footer()
jump_to_page_top()
st.markdown("<div style='text-align:center;color:#8c90a7;font-size:11px;letter-spacing:.13em;padding:15px 0'>MASTER ESMIHA  ·  TD MACHINE LEARNING  ·  QUENTIN LAMBOLEY</div>",unsafe_allow_html=True)
