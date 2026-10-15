# TD : Introduction au Machine Learning · ESMIHA 2026

**Quentin Lamboley · Master ESMIHA · Version 7.1**

Application Streamlit de classification supervisée utilisant une population fictive d'humains et de vampires. L'objectif est **l'apprentissage et l'évaluation du machine learning**, pas la théorie de la génération des données.

## Ce qui est inclus

- **Jeu de données paramétrable** : de 200 à 5 000 individus, 10 à 90 % de vampires et proximité des profils entre 0 et 100 % ; comparaison de deux populations avec un même algorithme.
- **Cinq méthodes principales** : Random Forest, XGBoost, régression logistique Ridge (L2), Lasso (L1) et Elastic Net (L1 + L2).
- **Évaluation complète** : train/test stratifié, validation croisée de 2 à 10 plis sur le train, matrice de confusion, sensibilité, spécificité, accuracy, balanced accuracy, F1, ROC, précision-rappel, calibration.
- **Interprétation** : permutation, PDP/ICE, surface de décision conditionnelle.
- **Défi humain/vampire** avec révélation après le pronostic.
- **58 questions pédagogiques** : 49 principales et 9 sur les réseaux de neurones (bonus), toutes accompagnées d'indices `❔` et de corrections (explication, exemple, à retenir).
- **Interface guidée** avec boutons de progression en bas, visuel local optimisé, sans menu latéral.
- **PDF individuel** reprenant le prénom, le nom, les réponses et les résultats éventuels de l'étudiant ; **PDF de correction** distinct, disponible en fin de parcours.
- **Reprise à domicile** : prénom, nom et code personnel pour retrouver les réponses de la séance tant que le serveur conserve ses fichiers ; sauvegarde JSON à télécharger pour une reprise garantie même après un redémarrage ; archive ZIP des résultats de calcul.

## Démarrage local

Prérequis : Python 3.11-3.13 recommandé, Internet au premier lancement pour installer les dépendances.

| Système | Démarrage |
|---|---|
| Windows | Double-cliquer sur `LANCER_WINDOWS.bat` |
| Linux | `sh LANCER_LINUX_MAC.sh` (installer `python3-venv` si nécessaire) |
| macOS | `sh LANCER_LINUX_MAC.sh` |

L'adresse locale est normalement `http://localhost:8501`. Ou lancement manuel :

```bash
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

## Mettre à jour le dépôt GitHub existant

Dépôt : [QuentinLamboley/ESMIHA-2026](https://github.com/QuentinLamboley/ESMIHA-2026).

1. Télécharger et **décompresser** l'archive V7.
2. Déposer le contenu des dossiers et les fichiers **à la racine du dépôt** sur GitHub (le fichier d'entrée ne doit pas être dans un sous-dossier).
3. Publier les modifications dans `main` (commit).
4. Streamlit Community Cloud est configuré avec dépôt `QuentinLamboley/ESMIHA-2026`, branche `main` et fichier `streamlit_app.py`. Le service redéploie alors cette version.
5. Vérifier en particulier la génération du PDF individuel, la comparaison de deux populations et l'absence de menu latéral.

Ne téléversez **pas le ZIP seul** sur GitHub : Streamlit a besoin des fichiers extraits.

## Travail simultané et confidentialité

Chaque connexion Streamlit dispose d’un `st.session_state` indépendant. Les réponses et les notes sont également enregistrées automatiquement dans un fichier JSON propre à chaque identité (prénom, nom et code personnel). Ce stockage local peut être supprimé lors d’un redémarrage de Streamlit Community Cloud : chaque étudiant doit télécharger sa sauvegarde JSON pour être certain de reprendre le TD chez lui. Les calculs lourds passent par un sémaphore global limitant à **deux entraînements simultanés**, et les threads BLAS sont bornés afin de limiter la consommation de ressources. La validation croisée des réseaux est facultative et décochée par défaut.

**Attention :** ces garde-fous facilitent une séance à dix étudiants mais ne garantissent pas que l'instance gratuite Streamlit Community Cloud disposera de suffisamment de CPU et de mémoire pour tous les calculs. Procéder au test de charge indiqué dans `docs/GUIDE_ENSEIGNANT.md` avant le TD. Les étudiants doivent télécharger leur sauvegarde JSON pour pouvoir reprendre leur travail après une fermeture ou une interruption de session.

## Fichiers importants

| Chemin | Usage |
|---|---|
| `streamlit_app.py` | Parcours pédagogique Streamlit |
| `vampire_lab/` | Modèles ML, interface, simulation, visualisations, questions et générateurs de PDF |
| `assets/paysage_td.webp` | Illustration d'accueil autonome, optimisée pour le web |
| `data/Data_vampi.csv` | Jeu de référence prêt à analyser |
| `docs/GUIDE_TD.md` | Consignes et toutes les questions |
| `docs/GUIDE_ENSEIGNANT.md` | Séance, objectifs et test à dix utilisateurs |
| `docs/CORRIGE_COMPLET_ESMIHA.pdf` | Corrigé détaillé des 58 questions |
| `tests/` | Tests automatisés, dont isolation des PDFs individuels |
| `.github/workflows/controle.yml` | Tests automatiques sur GitHub |
| `.streamlit/config.toml` | Configuration Streamlit |

Les résultats obtenus dépendent de l'échantillon, des modèles et du protocole. L'usage du scénario fictif ne permet aucune conclusion biomédicale.

## Scripts Python et R

Les sept fiches Markdown téléchargeables à la fin du TD se trouvent dans `docs/codes/`. Elles présentent le code de Random Forest, XGBoost, Ridge, Lasso, Elastic Net, réseau compact et réseau profond dans les deux langages.
