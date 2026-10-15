**Commencer ou reprendre :** renseigne ton prénom, ton nom et le code personnel choisi au début. Tes réponses sont enregistrées automatiquement pendant la séance. Pense à télécharger régulièrement ta sauvegarde JSON : elle permet de retrouver ton travail même après un redémarrage de l’application.

**Proximité des profils :** à 0 %, les populations restent bien distinctes ; à 100 %, les deux classes ont des distributions identiques pour les dix variables. Essaie plusieurs valeurs et observe comment évoluent les performances.

# TD : Introduction au Machine Learning

**Master ESMIHA · Quentin Lamboley**

## Objectif du TD

À partir d’un jeu fictif humains/vampires, entraîner, comparer, évaluer et interpréter des modèles de classification supervisée. La création des données est un outil de départ, **pas le sujet scientifique du TD**.

## Déroulement

1. Choisir le nombre d’individus (200 à 5 000) et la proportion de vampires (10 à 90 %), puis générer le jeu de données.
2. Explorer les caractéristiques et leur chevauchement entre les deux classes.
3. Réserver le jeu de test, puis entraîner les cinq méthodes historiques.
4. Réaliser une validation croisée stratifiée de 2 à 10 plis **sur l’apprentissage uniquement**.
5. Comparer les erreurs, courbes ROC/précision-rappel et seuils.
6. Interpréter les variables et classer un individu inédit.
7. Télécharger ton **TD rempli au format PDF** ou ton JSON, puis consulter le corrigé.
8. Réaliser le complément facultatif sur les réseaux de neurones.

Réglages conseillés pour commencer : 1 000 observations, 50 % de vampires, train/test 80/20 et validation croisée de 2 à 10 plis. Changer un paramètre à la fois aide à comprendre les résultats.

## Questions

**49 questions principales et 9 questions facultatives**. Les indices et les corrections sont directement accessibles sous les manipulations dans l’application. Les questions 01-49 correspondent au parcours principal ; les questions 50-58 sont consacrées au bonus réseaux de neurones.

### Données

**Question 01.** Quelle variable le modèle doit-il prédire ? Quelles informations utilisera-t-il pour le faire ?

*Réponse :* ______________________________________________________________


**Question 02.** Pourquoi faut-il regarder la proportion des deux classes avant de choisir un indicateur de performance ?

*Réponse :* ______________________________________________________________


**Question 03.** D’après vous, après avoir modifié le nombre d’individus, la proportion de vampires ou la proximité entre les deux groupes, les performances d’un même algorithme sont-elles identiques ? Comment expliquer les différences ?

*Réponse :* ______________________________________________________________


**Question 04.** Si les vampires deviennent très rares, pourquoi faut-il examiner la précision des prédictions « Vampire » ?

*Réponse :* ______________________________________________________________


**Question 05.** En quoi un petit jeu de test rend-il l’estimation des performances moins stable ?

*Réponse :* ______________________________________________________________


### Exploration

**Question 06.** Une variable dont les deux distributions se chevauchent peut-elle suffire à classer parfaitement les individus ?

*Réponse :* ______________________________________________________________


**Question 07.** Qu’apporte un nuage de points coloré par classe par rapport à l’examen séparé de deux histogrammes ?

*Réponse :* ______________________________________________________________


**Question 08.** Pourquoi faut-il examiner les corrélations avant d’interpréter l’importance des variables ?

*Réponse :* ______________________________________________________________


**Question 09.** Si une caractéristique distingue assez bien les groupes, pourquoi conserver malgré tout plusieurs prédicteurs ?

*Réponse :* ______________________________________________________________


**Question 10.** Que signifie un graphique où les deux classes se mélangent fortement ?

*Réponse :* ______________________________________________________________


**Question 11.** Pourquoi faut-il éviter d’interpréter une corrélation comme une preuve de causalité ?

*Réponse :* ______________________________________________________________


### Validation simple

**Question 12.** Pourquoi sépare-t-on les observations en apprentissage et en test ?

*Réponse :* ______________________________________________________________


**Question 13.** Comment une forêt aléatoire prend-elle une décision, et pourquoi ne repose-t-elle pas sur un seul arbre ?

*Réponse :* ______________________________________________________________


**Question 14.** En quoi XGBoost se distingue-t-il d’une forêt aléatoire ?

*Réponse :* ______________________________________________________________


**Question 15.** Que pénalise Ridge et pourquoi cela peut-il améliorer la généralisation ?

*Réponse :* ______________________________________________________________


**Question 16.** Quelle différence pratique entre Lasso et Ridge pour la sélection des variables ?

*Réponse :* ______________________________________________________________


**Question 17.** Quel est le principe d’Elastic Net ?

*Réponse :* ______________________________________________________________


**Question 18.** Pourquoi deux modèles entraînés sur les mêmes individus n’obtiennent-ils pas nécessairement les mêmes prédictions ?

*Réponse :* ______________________________________________________________


**Question 19.** Que signifie une accuracy de 0,90 sur les données de test ?

*Réponse :* ______________________________________________________________


**Question 20.** Pourquoi la performance d’apprentissage n’est-elle pas une mesure suffisante de la qualité d’un modèle ?

*Réponse :* ______________________________________________________________


**Question 21.** Pourquoi est-il indispensable de faire apprendre tous les algorithmes sur exactement le même train ?

*Réponse :* ______________________________________________________________


**Question 22.** Comment reconnaître une situation de surapprentissage ?

*Réponse :* ______________________________________________________________


**Question 23.** Que signifie une probabilité prédite de 0,70 pour un individu ?

*Réponse :* ______________________________________________________________


**Question 24.** Pourquoi un algorithme plus complexe n’est-il pas automatiquement plus performant ?

*Réponse :* ______________________________________________________________


### Validation croisée

**Question 25.** Décris le principe d’une validation croisée stratifiée à dix blocs.

*Réponse :* ______________________________________________________________


**Question 26.** Quel est l’intérêt de la validation croisée par rapport à une seule séparation apprentissage/test ?

*Réponse :* ______________________________________________________________


**Question 27.** Pourquoi doit-on standardiser à l’intérieur de chaque pli de validation ?

*Réponse :* ______________________________________________________________


**Question 28.** Comment interpréter la moyenne et l’écart-type des dix scores obtenus ?

*Réponse :* ______________________________________________________________


**Question 29.** Pourquoi ne faut-il pas regarder le test final pour choisir le meilleur algorithme ?

*Réponse :* ______________________________________________________________


**Question 30.** Pourquoi un résultat moyen en validation croisée peut-il masquer un problème ?

*Réponse :* ______________________________________________________________


### Comparaison

**Question 31.** Peut-on comparer directement l’accuracy de test et l’accuracy moyenne de validation croisée comme s’il s’agissait de deux répétitions identiques ?

*Réponse :* ______________________________________________________________


**Question 32.** Pourquoi le modèle qui a la meilleure accuracy n’est-il pas nécessairement le meilleur choix ?

*Réponse :* ______________________________________________________________


**Question 33.** Quelle différence entre sensibilité et précision positive ?

*Réponse :* ______________________________________________________________


**Question 34.** Pourquoi l’accuracy peut-elle augmenter alors que le modèle devient moins utile ?

*Réponse :* ______________________________________________________________


**Question 35.** Dans la matrice de confusion, que signifient un faux positif et un faux négatif ?

*Réponse :* ______________________________________________________________


**Question 36.** Que devient généralement la sensibilité lorsque l’on abaisse le seuil de 0,50 à 0,30 ?

*Réponse :* ______________________________________________________________


**Question 37.** Quel est l’effet de l’augmentation du seuil de décision ?

*Réponse :* ______________________________________________________________


**Question 38.** Que complètent les courbes ROC et précision-rappel par rapport à l’accuracy ?

*Réponse :* ______________________________________________________________


**Question 39.** Pourquoi faut-il lire à la fois les courbes ROC et précision-rappel ?

*Réponse :* ______________________________________________________________


**Question 40.** Pourquoi une bonne AUC-ROC ne garantit-elle pas de bonnes probabilités ?

*Réponse :* ______________________________________________________________


### Interprétation

**Question 41.** Que mesure l’importance d’une variable calculée par permutation ?

*Réponse :* ______________________________________________________________


**Question 42.** Si une variable ressort importante pour un modèle, faut-il en conclure qu’elle cause le vampirisme ?

*Réponse :* ______________________________________________________________


**Question 43.** Que révèle une courbe de dépendance partielle et pourquoi ne faut-il pas y voir un effet causal ?

*Réponse :* ______________________________________________________________


**Question 44.** Pourquoi les courbes ICE peuvent-elles être différentes d’un individu à l’autre ?

*Réponse :* ______________________________________________________________


**Question 45.** Pourquoi la carte de décision en deux dimensions n’est-elle qu’une vue partielle du modèle ?

*Réponse :* ______________________________________________________________


### Défi

**Question 46.** Pourquoi un modèle peut-il annoncer une probabilité de 90 % et se tromper ?

*Réponse :* ______________________________________________________________


### Prédiction

**Question 47.** Si ton pronostic et celui de la machine diffèrent, comment analyser ce désaccord ?

*Réponse :* ______________________________________________________________


### Conclusion

**Question 48.** Quel protocole retiendrais-tu pour sélectionner un algorithme sans suradapter ton choix au jeu de test ?

*Réponse :* ______________________________________________________________


**Question 49.** Quelles informations minimales faut-il donner pour que quelqu’un puisse reproduire ton analyse ?

*Réponse :* ______________________________________________________________


### Réseaux de neurones : complément

**Question 50.** Qu’appelle-t-on un neurone artificiel dans ce TD ?

*Réponse :* ______________________________________________________________


**Question 51.** À quoi servent les couches cachées entre les dix variables et la décision finale ?

*Réponse :* ______________________________________________________________


**Question 52.** Que change une fonction d’activation comme ReLU ?

*Réponse :* ______________________________________________________________


**Question 53.** Pourquoi standardise-t-on les dix variables avant d’entraîner le réseau ?

*Réponse :* ______________________________________________________________


**Question 54.** Qu’apprend réellement le réseau pendant l’entraînement ?

*Réponse :* ______________________________________________________________


**Question 55.** Une courbe de perte qui diminue signifie-t-elle que le réseau sera performant sur des personnes inconnues ?

*Réponse :* ______________________________________________________________


**Question 56.** Comment un réseau de neurones se distingue-t-il des méthodes principales du TD, et un réseau plus profond est-il forcément meilleur ?

*Réponse :* ______________________________________________________________


**Question 57.** Pourquoi un réseau profond peut-il être moins bon qu’un réseau compact ?

*Réponse :* ______________________________________________________________


**Question 58.** En quoi un réseau de neurones diffère-t-il d’une forêt aléatoire ou d’une régression logistique ?

*Réponse :* ______________________________________________________________

## Compte rendu attendu

Un tableau comparant les cinq modèles, la description du protocole train/test et CV, l’interprétation d’une matrice de confusion et d’un graphique d’importance, et une conclusion nuancée. Lorsque des effectifs ou des proportions différents sont choisis, expliquer ce que cela change dans l’interprétation des scores.

## Pour travailler chez soi

Le TD fonctionne sur le site Streamlit sans installation. Pour le lancer localement, décompresser le dossier et utiliser `LANCER_WINDOWS.bat` ou `sh LANCER_LINUX_MAC.sh` (Python et dépendances nécessaires). Les réponses sont enregistrées automatiquement durant la séance ; télécharger le fichier JSON permet de les conserver même si le serveur redémarre. Le PDF individuel doit être généré de nouveau après une modification des réponses.
