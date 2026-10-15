# Révision du support : V4

## Fil conducteur restauré

Le support étudié (`streamlit_app.py`, dépôt `CoursML_ESMIHA`) reposait sur des données fictives, une validation non croisée, une validation croisée à dix blocs, la comparaison des modèles, des courbes de réponse et un défi de classification.

La V3 consacrait trop de place au simulateur et aux réseaux de neurones. La V4 rétablit la place centrale des cinq méthodes historiques : Random Forest, XGBoost, Ridge, Lasso et Elastic Net. Les réseaux de neurones sont accessibles dans un complément facultatif.

## Corrections méthodologiques

- Données directement exploitables à l’ouverture ; outils de génération relégués à un panneau facultatif, sans question dédiée.
- Validation non croisée identifiée distinctement de la validation croisée stratifiée à dix plis, avec visualisation des plis.
- CV calculée exclusivement sur le jeu d’apprentissage ; prétraitements dans les pipelines ; affichage de la moyenne et de l’écart-type entre plis.
- Comparaison des modèles enrichie (accuracy, balanced accuracy, F1, sensibilité, spécificité, AUC-ROC, PR, Brier).
- Trente questions réellement centrées sur le machine learning ; indice `?`, espace de réponse et correction intégrale en PDF.
- Visualisations des principes RF, XGBoost, Ridge, Lasso et Elastic Net ; explications des limites des PDP/ICE et des importances.
- Lancement local Windows/Linux/macOS ; sauvegarde JSON des réponses, données et résultats ZIP, corrigé PDF inclus.

## Limites

L’ensemble repose sur des données fictives et ne constitue pas une validation scientifique réelle. Les performances de test sont affichées dans un cadre d’enseignement : sélectionner en pratique sur CV puis tester une seule fois. L’application n’ajuste pas les hyperparamètres des différents algorithmes et ne réalise pas de validation externe.

## Version 5.0 - consolidation pédagogique et publication

- Maintien du protocole, des cinq algorithmes principaux et des trente questions de la V4.
- Développement de chacun des trente éléments de correction : un exemple concret, puis une idée à retenir. La source `vampire_lab/pedagogy.py` est commune à l'application et au PDF.
- Ajout d'un petit lexique de départ, d'explications de lecture sous les schémas d'algorithmes et amélioration des textes d'accueil.
- Nouveau corrigé PDF de douze pages, vérifié visuellement.
- Préparation d'un dépôt GitHub publiable à sa racine, d'un outil de publication assistée, d'un fichier `packages.txt` pour Linux Cloud et d'un workflow GitHub Actions.

## Version 7.0 : paramétrage et restitution

- Ajout d’une proximité des profils comprise entre 0 et 100 %, appliquée aux dix variables du simulateur. À 100 %, les deux classes partagent exactement les mêmes distributions.
- Dictionnaire enrichi avec les unités, les échelles et le sens des indicateurs.
- Suppression des réglages techniques de reproductibilité visibles, du panneau facultatif d’import du CSV et des consignes PDF personnelles.
- Validation croisée stratifiée réglable de 2 à 10 plis ; un pli unique n’est pas défini. Adaptation du schéma de validation à chaque valeur.
- Identification par prénom, nom et code personnel ; sauvegarde JSON automatique indépendante par identité sur le serveur et export personnel téléchargeable en secours. Les fichiers sur Streamlit Community Cloud ne sont pas conservés après tous les redémarrages.
- Tentative de retour automatique en haut de page après une navigation.
- Sept fiches Markdown de code Python et R (RStudio) : cinq algorithmes principaux et deux réseaux de neurones.
- Maintien des 58 questions et du corrigé PDF détaillé ; actualisation de la question sur les paramètres de population.
