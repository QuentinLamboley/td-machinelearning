# Guide enseignant : TD : Introduction au Machine Learning

**Master ESMIHA · Quentin Lamboley · Version 7.0**

## Intention pédagogique

Le scénario fictif humains/vampires est un support pour expérimenter les méthodes de classification supervisée. Il ne vise **pas** à enseigner la simulation statistique ni à produire des conclusions biomédicales. Les étudiants comparent cinq algorithmes : Random Forest, XGBoost, régression logistique Ridge, Lasso et Elastic Net. Deux réseaux de neurones sont proposés **en bonus** après la synthèse.

## Déroulement conseillé

Le parcours est guidé par « Étape suivante » en bas à droite et « Étape précédente » en bas à gauche ; aucune navigation latérale n'est nécessaire. Les étudiants peuvent travailler à leur rythme et s'aider des boutons `❔`.

| Séquence | Durée indicative | Activité |
|---|---:|---|
| Jeu de données | 15-20 min | Choix de l'effectif (200 à 5 000), proportion de vampires (10 à 90 %) et proximité des profils (0 à 100 %), cible, prédicteurs. Mini-expérience comparant Ridge sur deux populations. |
| Exploration | 20 min | Distributions, recouvrement, nuages de points et corrélations. |
| Validation non croisée | 35-45 min | Train/test stratifié, compréhension de cinq algorithmes et première évaluation. |
| Validation croisée | 25-35 min | 2 à 10 plis sur le train (10 plis par défaut), dispersion et fuite d'information. |
| Évaluation | 25-35 min | Matrice de confusion, accuracy, balanced accuracy, sensibilité, précision, courbes ROC/PR, seuil et calibration. |
| Interprétation | 20-25 min | Permutation, PDP/ICE et surface conditionnelle. |
| Défi, conclusion et rendu | 15-20 min | Nouvel individu, PDF personnel et corrigé détaillé. |
| Réseaux de neurones | Bonus / domicile | Architecture, poids, biais, activation, standardisation, perte, rétropropagation et comparaison. |

Le TD comprend **49 questions principales et 9 questions de bonus**, avec indices, zones de réponse et corrigés explicatifs. Les questions sont réparties sous les manipulations, non présentées en bloc au début.

## Points scientifiques essentiels

- Réserver le test avant d'apprendre ; les plis de validation croisée proviennent exclusivement de l'apprentissage.
- La standardisation est ajustée *dans* chaque pli par un Pipeline.
- Ridge (L2), Lasso (L1) et Elastic Net sont ici des **régressions logistiques régularisées**, pas des régressions linéaires de la classe.
- Random Forest combine des arbres variés ; XGBoost construit une séquence d'arbres visant à réduire une fonction objectif.
- Les proportions de classes influencent l'interprétation de l'accuracy et de la précision positive ; un score global élevé peut masquer des vampires manqués.
- Un seuil, la calibration et une frontière 2D sont trois notions distinctes.
- Importance prédictive et dépendance partielle ne prouvent pas la causalité.
- Le réseau de neurones n'est pas intrinsèquement supérieur aux autres méthodes.

## Travaux individuels et sauvegardes

Dès l’ouverture, l’étudiant indique son prénom, son nom et un code personnel d’au moins six caractères. Ses réponses et ses notes sont enregistrées automatiquement, dans un fichier JSON propre à cette identité sur le serveur, à chaque modification. Chaque session conserve ses données et ses modèles indépendamment des autres.

La sauvegarde serveur est **temporaire** : les fichiers locaux peuvent disparaître quand Streamlit Community Cloud redémarre ou reconstruit l’application. L’étudiant doit télécharger sa sauvegarde JSON disponible en haut de chaque page pour être certain de conserver son travail, puis pourra la réimporter dans « Carnet et corrigé ». Éviter de réutiliser un mot de passe existant comme code personnel.

Le compte rendu PDF personnel reprend les 58 questions, les seules réponses de l’étudiant et ses résultats éventuels, sans le corrigé. Le corrigé de référence reste disponible séparément.

## Séance simultanée à dix étudiants

L'application limite les jeux générés à **5 000 observations** dans l'interface, configure une seule unité de calcul par bibliothèque numérique lorsque c'est possible et ne lance pas plus de **deux calculs d'entraînement coûteux à la fois** dans le processus serveur. Le reste des demandes est mis en attente. La validation croisée des réseaux de neurones est désactivée par défaut ; l'étudiant peut l'activer.

Ces protections ne constituent **pas** une garantie de capacité pour dix personnes sur l'offre gratuite de Streamlit Community Cloud : cette capacité dépend de la mémoire et du CPU réellement alloués, du type de calcul exécuté et des limites du service.

**Test de charge conseillé avant le cours** : ouvrir dix sessions de navigateur distinctes (ou les faire ouvrir par dix personnes), générer chacune 1 000 lignes, vérifier l'indépendance des réponses, puis répartir les lancements des modèles en deux ou trois vagues. Contrôler les journaux et la mémoire dans le tableau de bord Streamlit Cloud. Pour une séance longue, demander aux étudiants de sauvegarder leur JSON à mi-parcours. Si les ralentissements sont importants, passer à un hébergement plus puissant ou utiliser des installations locales.

## Publication

GitHub : `QuentinLamboley/ESMIHA-2026` ; branche `main` ; entrée Streamlit `streamlit_app.py`. Uploader le **contenu décompressé** du ZIP à la racine du dépôt, puis relancer l'application Streamlit. Le fichier `.github/workflows/controle.yml` exécute les tests au push. Ne pas confondre les fichiers de référence PDF du dépôt avec les PDFs personnels générés à la demande.
