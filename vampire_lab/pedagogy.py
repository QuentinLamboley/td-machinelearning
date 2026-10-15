"""Questions du TD de classification supervisée ; source commune application/corrigé."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Question:
    code: str
    section: str
    enonce: str
    indice: str
    correction: str
    exemple: str = ""
    retenir: str = ""

D = [
('01','Données','Quelle variable le modèle doit-il prédire ? Quelles informations utilisera-t-il pour le faire ?', 'Repère la colonne de classe et les dix autres colonnes.', 'La cible est Vampirisme (0 = humain ; 1 = vampire). Les dix autres colonnes constituent les variables explicatives. Comme la classe est connue dans les exemples d’entraînement, il s’agit d’une classification supervisée. La nature fictive des exemples ne modifie pas cette définition.'),
('02','Données','Pourquoi faut-il regarder la proportion des deux classes avant de choisir un indicateur de performance ?', 'Un modèle qui prédit toujours la classe la plus fréquente peut paraître performant.', 'Si 95 % des observations sont humaines, répondre systématiquement « humain » donne 95 % d’accuracy mais ne détecte aucun vampire. La répartition des classes doit guider le choix des métriques et l’interprétation du résultat.'),
('03','Exploration','Une variable dont les deux distributions se chevauchent peut-elle suffire à classer parfaitement les individus ?', 'Une même valeur peut appartenir à chaque groupe.', 'Non : lorsqu’une même valeur apparaît dans les deux classes, cette seule variable ne permet pas de les distinguer avec certitude. Les modèles multivariés combinent plusieurs indices, parfois faiblement informatifs lorsqu’ils sont considérés isolément.'),
('04','Exploration','Qu’apporte un nuage de points coloré par classe par rapport à l’examen séparé de deux histogrammes ?', 'Observe simultanément deux caractéristiques.', 'Il permet d’étudier des combinaisons de deux variables et d’identifier des zones de recouvrement ou de séparation que les graphiques univariés masquent. Il ne représente toutefois qu’une projection d’un problème à dix dimensions.'),
('05','Exploration','Pourquoi faut-il examiner les corrélations avant d’interpréter l’importance des variables ?', 'Deux variables peuvent apporter une information partiellement redondante.', 'Des variables corrélées peuvent se remplacer dans un modèle. Les coefficients et les importances individuelles deviennent alors plus difficiles à interpréter. Une corrélation n’établit pas, à elle seule, une relation causale.'),
('06','Validation simple','Pourquoi sépare-t-on les observations en apprentissage et en test ?', 'Un examen est moins informatif si ses réponses ont déjà été utilisées pour réviser.', 'L’apprentissage sert à ajuster les paramètres. Le jeu de test, tenu à l’écart, mesure ensuite les prédictions sur des individus non vus. La séparation stratifiée conserve approximativement la proportion de classes dans chaque ensemble.'),
('07','Validation simple','Comment une forêt aléatoire prend-elle une décision, et pourquoi ne repose-t-elle pas sur un seul arbre ?', 'Imagine plusieurs arbres qui votent.', 'La forêt entraîne plusieurs arbres de décision avec de l’aléa dans les données et les variables proposées. Chaque arbre vote pour une classe ; les votes agrégés produisent la prédiction. Cette diversité réduit généralement l’instabilité d’un arbre isolé, sans supprimer tout risque de surapprentissage.'),
('08','Validation simple','En quoi XGBoost se distingue-t-il d’une forêt aléatoire ?', 'Les arbres arrivent-ils indépendamment ou successivement ?', 'Dans une forêt aléatoire, les arbres sont construits avec une forte indépendance et leurs résultats sont agrégés. Dans le boosting, les arbres sont ajoutés successivement pour améliorer la fonction objectif, en corrigeant progressivement les limites de l’ensemble précédent. Les performances dépendent du réglage et des données.'),
('09','Validation simple','Que pénalise Ridge et pourquoi cela peut-il améliorer la généralisation ?', 'Pense à la taille des coefficients.', 'Ridge ajoute une pénalisation L2, liée à la somme des carrés des coefficients. Elle tend à réduire leur amplitude, ce qui limite les ajustements excessifs aux particularités de l’échantillon. Dans ce TD, Ridge correspond à une régression logistique régularisée.'),
('10','Validation simple','Quelle différence pratique entre Lasso et Ridge pour la sélection des variables ?', 'Un coefficient peut-il devenir exactement nul ?', 'Lasso utilise une pénalisation L1, susceptible de rendre certains coefficients exactement nuls : il réalise ainsi une forme de sélection de variables. Ridge réduit plutôt les coefficients sans en annuler habituellement beaucoup. Avec des prédicteurs corrélés, les choix de Lasso peuvent être instables.'),
('11','Validation simple','Quel est le principe d’Elastic Net ?', 'Il combine deux types de pénalisation.', 'Elastic Net associe les pénalisations L1 de Lasso et L2 de Ridge. Ce compromis peut favoriser la parcimonie tout en stabilisant certains choix de variables corrélées. Le résultat dépend notamment de la force de régularisation et de la proportion L1/L2.'),
('12','Validation simple','Pourquoi deux modèles entraînés sur les mêmes individus n’obtiennent-ils pas nécessairement les mêmes prédictions ?', 'Leurs hypothèses et leurs façons d’apprendre diffèrent.', 'Chaque algorithme représente différemment la relation entre les variables et la classe : fonction linéaire régularisée, combinaison d’arbres ou réseau de neurones. Leurs biais, leur souplesse et leur optimisation diffèrent. Les comparer suppose de conserver les mêmes données et le même protocole.'),
('13','Validation simple','Que signifie une accuracy de 0,90 sur les données de test ?', 'Exprime ce score en nombre de prédictions correctes sur cent.', 'Au seuil retenu, environ 90 % des observations du jeu de test ont reçu la bonne classe. Cela ne dit pas quelles erreurs ont été commises, ni si les classes sont équilibrées, ni si les probabilités annoncées sont fiables. Un test limité comporte aussi une incertitude d’échantillonnage.'),
('14','Validation simple','Pourquoi la performance d’apprentissage n’est-elle pas une mesure suffisante de la qualité d’un modèle ?', 'Un élève peut mémoriser les réponses sans comprendre.', 'Un modèle très flexible peut apprendre les particularités du train et obtenir un score d’apprentissage élevé sans généraliser. C’est le surapprentissage. Il faut observer ses résultats sur des observations non utilisées à l’entraînement, et recourir à une validation appropriée pour choisir les réglages.'),
('15','Validation croisée','Décris le principe d’une validation croisée stratifiée à dix blocs.', 'Chaque bloc sert une fois à valider et neuf fois aux entraînements successifs.', 'Le train est découpé en dix plis de compositions de classes proches. Dix modèles sont entraînés : à chaque itération, neuf plis servent à l’apprentissage et le dernier à la validation. Chaque pli joue une fois le rôle de validation. Les dix scores décrivent une performance de validation interne.'),
('16','Validation croisée','Quel est l’intérêt de la validation croisée par rapport à une seule séparation apprentissage/test ?', 'Une séparation particulière peut favoriser un modèle.', 'La validation croisée répète l’évaluation interne sur plusieurs sous-ensembles. Elle aide à comparer les modèles sans s’appuyer sur une seule répartition et donne une idée de la variabilité entre plis. Elle ne remplace pas une évaluation finale indépendante et n’élimine pas toutes les sources d’incertitude.'),
('17','Validation croisée','Pourquoi doit-on standardiser à l’intérieur de chaque pli de validation ?', 'Qui doit calculer les moyennes et écarts-types ?', 'Si la standardisation utilise les observations de validation avant l’apprentissage, de l’information fuite vers le modèle. Avec un Pipeline, StandardScaler est ajusté exclusivement sur les neuf plis d’apprentissage, puis appliqué au dixième pli. Le même principe s’applique au test final.'),
('18','Validation croisée','Comment interpréter la moyenne et l’écart-type des dix scores obtenus ?', 'Une moyenne élevée peut masquer une forte instabilité.', 'La moyenne résume les dix évaluations internes ; l’écart-type indique la dispersion des performances entre les plis. Un écart-type faible suggère une moindre variabilité sur ces partitions, mais ne constitue ni un intervalle de confiance, ni une preuve de robustesse sur d’autres populations.'),
('19','Comparaison','Peut-on comparer directement l’accuracy de test et l’accuracy moyenne de validation croisée comme s’il s’agissait de deux répétitions identiques ?', 'Les données sur lesquelles les scores sont calculés ne sont pas les mêmes.', 'Non. Le test fournit une estimation sur un ensemble réservé, tandis que la validation croisée est calculée exclusivement dans le train après plusieurs réentraînements. Un écart entre ces deux scores est informatif, mais ne signifie pas à lui seul qu’une méthode est erronée. Pour choisir les modèles, privilégier la validation interne et réserver le test à l’évaluation finale.'),
('20','Comparaison','Pourquoi le modèle qui a la meilleure accuracy n’est-il pas nécessairement le meilleur choix ?', 'Que se passe-t-il lorsque les classes sont déséquilibrées ou que les erreurs ont des coûts différents ?', 'L’accuracy met toutes les erreurs dans le même total et peut masquer une sensibilité insuffisante. Il faut examiner la matrice de confusion, la sensibilité, la spécificité, la précision, l’AUC-ROC et la calibration selon l’objectif, ainsi que la stabilité et l’interprétabilité du modèle.'),
('21','Comparaison','Dans la matrice de confusion, que signifient un faux positif et un faux négatif ?', 'Considère Vampire comme classe positive.', 'Un faux positif est un humain classé vampire ; un faux négatif est un vampire classé humain. La sensibilité mesure la proportion de vampires reconnus (VP / [VP + FN]) et la spécificité celle des humains correctement reconnus (VN / [VN + FP]).'),
('22','Comparaison','Que devient généralement la sensibilité lorsque l’on abaisse le seuil de 0,50 à 0,30 ?', 'Davantage de prédictions passent du côté « vampire ».', 'À probabilités fixes, abaisser le seuil ne peut pas diminuer la sensibilité : davantage de vrais vampires peuvent être détectés. En contrepartie, la spécificité ne peut pas augmenter : certains humains deviennent faux positifs. Le compromis dépend des conséquences respectives des deux erreurs.'),
('23','Comparaison','Que complètent les courbes ROC et précision-rappel par rapport à l’accuracy ?', 'On ne se limite plus au seuil 0,50.', 'La ROC décrit le compromis sensibilité/taux de faux positifs aux différents seuils ; son aire résume la discrimination. La courbe précision-rappel décrit la relation entre la proportion de positifs annoncés correctement et le rappel ; elle est particulièrement informative lorsque la classe positive est rare. Aucune de ces courbes ne démontre la calibration.'),
('24','Comparaison','Pourquoi une bonne AUC-ROC ne garantit-elle pas de bonnes probabilités ?', 'Ranger correctement les individus et annoncer la bonne fréquence sont deux objectifs différents.', 'L’AUC-ROC mesure principalement la qualité de l’ordre des scores entre les classes. Un modèle peut bien classer les individus tout en annonçant des probabilités trop extrêmes ou trop prudentes. La courbe de calibration et le score de Brier évaluent cet autre aspect.'),
('25','Interprétation','Que mesure l’importance d’une variable calculée par permutation ?', 'Que devient le score lorsque l’on mélange les valeurs de cette variable ?', 'On permute les valeurs d’un prédicteur puis on mesure la diminution de performance. Une forte dégradation montre que le modèle exploite l’information portée par cette variable. En présence de redondances, plusieurs variables peuvent se remplacer et sembler individuellement peu importantes.'),
('26','Interprétation','Que révèle une courbe de dépendance partielle et pourquoi ne faut-il pas y voir un effet causal ?', 'On fait varier artificiellement une seule variable dans le modèle.', 'La PDP décrit comment varie, en moyenne, la prédiction du modèle lorsque l’on remplace artificiellement une variable par différentes valeurs. Les courbes ICE montrent les réponses des individus. Cette manipulation numérique ne prouve pas qu’un changement réel de la variable provoquerait ce changement de classe.'),
('27','Interprétation','Pourquoi la carte de décision en deux dimensions n’est-elle qu’une vue partielle du modèle ?', 'Le modèle utilise dix variables.', 'La carte fait varier deux caractéristiques et fixe les huit autres à une valeur de référence, ici la médiane du train. Elle n’est donc qu’une coupe de la fonction de prédiction à dix dimensions, pas une représentation exhaustive de toutes ses frontières.'),
('28','Défi','Pourquoi un modèle peut-il annoncer une probabilité de 90 % et se tromper ?', 'Une probabilité n’est pas une certitude.', 'Même bien calibrée, une probabilité de 90 % correspond à une incertitude résiduelle. De plus, une prédiction peut être mal calibrée, et des profils humains et vampires peuvent se chevaucher. C’est précisément pourquoi il faut analyser les erreurs et les probabilités sur un ensemble de cas.'),
('29','Conclusion','Quel protocole retiendrais-tu pour sélectionner un algorithme sans suradapter ton choix au jeu de test ?', 'Ordre : séparation, validation interne, choix, test réservé.', 'Je commencerais par définir la cible et les métriques, puis par réserver un jeu de test stratifié. Je comparerais les modèles et, au besoin, leurs hyperparamètres par validation croisée sur le seul train, avec le prétraitement inclus dans les pipelines. Je fixerais le modèle et le seuil avant une évaluation finale sur le test réservé, puis je discuterais les biais et limites des données fictives.'),
('30','Réseaux de neurones : complément','Comment un réseau de neurones se distingue-t-il des méthodes principales du TD, et un réseau plus profond est-il forcément meilleur ?', 'Couches, poids, activations et risque de surapprentissage.', 'Un perceptron multicouche apprend des combinaisons de variables par couches de neurones reliées par des poids ajustés. Une activation non linéaire lui permet de représenter des relations souples. Davantage de couches ne garantit pas un meilleur score et peut compliquer l’optimisation ou augmenter le surapprentissage. Il se compare à la forêt et aux régressions logistiques avec le même protocole de validation.'),
]
# Un exemple concret et un repère court accompagnent chaque correction.
# Ils sont partagés entre les exercices interactifs et le corrigé PDF.
DETAILS = {
'01': (
    "Par exemple, si l'on connaît la température, l'âge et huit autres caractéristiques d'un nouvel individu, le programme doit choisir « humain » ou « vampire » sans connaître la réponse à l'avance.",
    "La cible est ce que l'on cherche à prévoir ; les prédicteurs sont les informations disponibles pour y parvenir."),
'02': (
    "Imaginons 100 individus, dont 90 humains. Un programme qui répond toujours « humain » obtient 90 bonnes réponses, soit 90 % d'accuracy, mais il manque les 10 vampires. Son score paraît bon alors qu'il est inutile pour reconnaître la classe minoritaire.",
    "Toujours comparer l'accuracy au déséquilibre des classes et à une stratégie très simple, comme prédire la classe majoritaire."),
'03': (
    "Si un humain et un vampire ont tous deux une température de 36,2 °C, la température seule ne permet pas de trancher. En revanche, le modèle peut aussi regarder la longueur des canines, la sensibilité au soleil ou le rythme cardiaque.",
    "Un indice ambigu pris isolément peut devenir utile lorsqu'il est combiné avec d'autres."),
'04': (
    "Sur les histogrammes, l'âge et la longueur des canines semblent chacun peu discriminants. Sur le nuage de points âge × canines, on peut néanmoins voir un groupe d'individus âgés avec des canines longues plus souvent associés aux vampires.",
    "Un graphique à deux variables aide à voir des combinaisons, mais ne montre pas les huit autres caractéristiques."),
'05': (
    "Si la force et la vitesse sont très liées, un modèle peut s'appuyer surtout sur la force, un autre surtout sur la vitesse, sans que leurs prédictions changent beaucoup. Une importance faible ne signifie donc pas nécessairement que la variable n'apporte aucune information.",
    "Des variables corrélées compliquent la lecture des coefficients et des importances ; corrélation ne signifie pas causalité."),
'06': (
    "Avec 1 000 individus, on peut en réserver environ 800 pour entraîner les modèles et 200 pour vérifier leurs prédictions. Les 200 individus du test restent inconnus du modèle pendant son apprentissage.",
    "Le test sert à évaluer sur des observations non vues, pas à apprendre ni à régler continuellement les modèles."),
'07': (
    "Un arbre peut classer un individu vampire, un autre humain et un troisième vampire. En regroupant les votes de nombreux arbres construits à partir de données et de variables légèrement différentes, la forêt évite de dépendre d'une seule règle fragile.",
    "Random Forest combine des arbres diversifiés ; elle ne se contente pas de fabriquer un arbre très grand."),
'08': (
    "Dans une forêt, plusieurs arbres sont entraînés de façon relativement indépendante et leur avis est agrégé. Avec XGBoost, le deuxième arbre est construit en tenant compte de ce que le premier ensemble prédit encore mal, puis un troisième poursuit l'amélioration.",
    "Forêt : diversité et agrégation. XGBoost : construction progressive d'un ensemble d'arbres."),
'09': (
    "Sans régularisation, une régression peut donner un poids excessif à une caractéristique très particulière des 800 individus d'apprentissage. Ridge pousse les coefficients à rester plus modestes, ce qui peut éviter de suivre des fluctuations propres à ce groupe.",
    "Ridge (L2) limite l'amplitude des coefficients ; il ne supprime généralement pas les variables."),
'10': (
    "Avec dix variables, un modèle Lasso peut finir par donner un coefficient nul à la force et à la vitesse s'il juge qu'elles n'aident pas suffisamment une fois les autres variables prises en compte. Ridge peut conserver les dix coefficients, tout en les réduisant.",
    "Lasso (L1) peut écarter des prédicteurs ; ce choix peut varier quand plusieurs variables sont très proches."),
'11': (
    "Lasso pourrait retenir seulement l'une de deux caractéristiques très liées, tandis que Ridge les conserverait toutes les deux avec des poids réduits. Elastic Net cherche un compromis entre ces comportements, selon les réglages choisis.",
    "Elastic Net associe L1 et L2 : sélection possible de variables et limitation de coefficients trop grands."),
'12': (
    "Pour un individu proche de la frontière, une forêt peut choisir « vampire » parce que plusieurs arbres votent en ce sens ; une régression logistique peut au contraire calculer un score de 48 % et répondre « humain » au seuil de 50 %.",
    "Il n'existe pas de modèle gagnant par principe : on compare des méthodes différentes dans des conditions identiques."),
'13': (
    "Sur un test de 200 individus, une accuracy de 0,90 correspond à 180 prédictions correctes et 20 erreurs. Mais ces 20 erreurs pourraient concerner surtout des vampires, ce que l'accuracy ne permet pas de savoir.",
    "L'accuracy décrit la proportion de bonnes réponses, pas la nature des erreurs."),
'14': (
    "Un modèle peut réussir 99 % des prédictions sur les 800 individus qu'il a vus et seulement 75 % sur les 200 inconnus. Il a probablement retenu des particularités de son entraînement qui ne se retrouvent pas ailleurs.",
    "La généralisation se juge sur de nouvelles observations ; un score d'apprentissage élevé ne suffit jamais."),
'15': (
    "Sur 800 individus d'apprentissage, dix blocs contiennent environ 80 individus chacun. On entraîne sur environ 720 individus et on valide sur 80 ; on répète dix fois en changeant le bloc de validation. Chaque bloc est utilisé une fois pour valider.",
    "Les dix plis sont créés à l'intérieur du train : les 200 individus du test n'y participent jamais."),
'16': (
    "Avec une seule séparation, les individus les plus difficiles peuvent tomber par hasard dans le test. La validation croisée répète la mesure sur dix groupes différents et permet de voir si la méthode fonctionne de façon relativement stable.",
    "Elle sert à comparer et régler les modèles sur le train ; elle ne remplace pas le test final réservé."),
'17': (
    "Pour transformer les températures, on calcule une moyenne et un écart-type. Si ces valeurs sont calculées avec les 80 individus du pli de validation, le prétraitement a déjà « regardé » les données censées être inconnues. Le pipeline évite cette fuite.",
    "Chaque transformation qui apprend des paramètres doit être ajustée sur les données d'entraînement du pli, jamais sur sa validation."),
'18': (
    "Un algorithme obtient 0,90 d'accuracy moyenne sur dix plis. S'il oscille seulement entre 0,89 et 0,91, ses scores sont assez réguliers ; s'il va de 0,65 à 0,99, la même moyenne dissimule une forte variabilité.",
    "Toujours lire ensemble le score moyen et sa dispersion ; l'écart-type des plis n'est pas un intervalle de confiance."),
'19': (
    "Une accuracy moyenne de validation croisée de 0,87 et une accuracy de test de 0,91 ne sont pas deux tirages interchangeables. La première regroupe dix évaluations internes ; la seconde concerne un groupe réservé et un modèle réentraîné sur tout le train.",
    "Les deux scores sont utiles mais ne répondent pas exactement à la même question."),
'20': (
    "Le modèle A identifie 98 % des humains mais seulement 40 % des vampires ; le modèle B reconnaît 90 % de chaque groupe. Selon l'objectif, B peut être préférable même si les deux ont une accuracy globale proche.",
    "Le meilleur choix dépend des erreurs que l'on veut éviter, de la stabilité et de la facilité d'interprétation."),
'21': (
    "Si l'on annonce « vampire » pour un humain, c'est un faux positif. Si l'on annonce « humain » pour un vampire, c'est un faux négatif. Sur 20 vrais vampires, si le modèle en retrouve 15, sa sensibilité est de 15/20 = 75 %.",
    "Lire séparément les faux positifs et les faux négatifs pour comprendre les limites du modèle."),
'22': (
    "Un individu reçoit un score vampire de 0,42. Au seuil 0,50 il est classé humain ; au seuil 0,30 il devient vampire. Le modèle n'a pas changé, seule la règle de décision a changé.",
    "Un seuil plus bas retrouve au moins autant de vrais positifs, mais produit aussi potentiellement plus de faux positifs."),
'23': (
    "Deux modèles ont 85 % d'accuracy au seuil 0,50. L'un peut pourtant mieux classer les individus lorsqu'on modifie le seuil. Les courbes ROC et précision-rappel montrent ces compromis sur une série de seuils.",
    "L'accuracy décrit un seuil choisi ; ROC et précision-rappel renseignent sur la discrimination à plusieurs seuils."),
'24': (
    "Si, parmi cent individus auxquels le modèle attribue environ 80 % de probabilité de vampirisme, seuls cinquante sont effectivement vampires, les probabilités sont trop élevées, même si l'ordre des scores entre les individus est bon.",
    "Bien classer les individus et annoncer des probabilités fiables sont deux qualités distinctes."),
'25': (
    "On mesure d'abord une accuracy équilibrée de 0,88. On mélange ensuite la longueur des canines entre les individus, sans changer les autres variables. Si le score tombe à 0,72, cette variable est utile à ce modèle pour produire ses prédictions.",
    "La permutation mesure une perte de performance du modèle, pas une preuve biologique de l'effet d'une variable."),
'26': (
    "Pour la température, on force successivement différentes valeurs et on observe le score calculé par le modèle. La PDP résume la réponse moyenne ; les courbes ICE montrent si les individus réagissent de la même manière.",
    "Une PDP décrit le comportement du modèle, pas ce qui se passerait si l'on modifiait réellement une personne."),
'27': (
    "Une carte âge × température peut placer un individu dans une zone « vampire », mais un autre individu du même âge et de la même température peut être classé humain à cause de ses huit autres caractéristiques.",
    "La carte 2D est une coupe informative de la décision, et non un résumé complet d'un modèle à dix variables."),
'28': (
    "Une probabilité de 90 % ne veut pas dire « certitude ». Même si les probabilités sont parfaitement calibrées, parmi cent cas estimés à 90 %, on s'attend en moyenne à environ dix cas négatifs.",
    "Une probabilité décrit un degré d'incertitude ; une prédiction individuelle peut donc être fausse."),
'29': (
    "Je réserve d'abord 20 % du jeu de données. Sur les 80 % restants, je teste mes cinq algorithmes et, si nécessaire, plusieurs réglages par validation croisée. Je retiens une méthode selon les indicateurs choisis avant de consulter une seule fois la performance finale sur le test.",
    "Définir la question et les métriques, réserver le test, comparer sur le train, puis conclure sans retoucher son choix sur le test."),
'30': (
    "Un réseau apprend en ajustant les poids de liaisons entre neurones. Un petit réseau peut suffire si les relations sont simples ; un réseau plus profond demande souvent davantage de réglages et peut davantage s'adapter au bruit. Seules les performances en validation permettent de trancher.",
    "La complexité d'un réseau ne garantit ni une meilleure précision ni une meilleure généralisation."),
}

QUESTIONS=[Question(f'{int(code):02d}',section,enonce,indice,correction,*DETAILS[f'{int(code):02d}']) for code,section,enonce,indice,correction in D]
from .additional_questions import ADDITIONS
QUESTIONS.extend(Question(*row) for row in ADDITIONS)
# The original IDs are kept for compatibility with students' saved answers.
# Only the visible question numbers and their presentation order change.
APPEARANCE_ORDER = (
    ('01', '02', '31', '32', '33'),
    ('03', '04', '05', '34', '35', '36'),
    ('06', '07', '08', '09', '10', '11', '12', '13', '14', '37', '38', '39', '40'),
    ('15', '16', '17', '18', '41', '42'),
    ('19', '20', '43', '44', '21', '22', '45', '23', '46', '24'),
    ('25', '47', '26', '48', '27'),
    ('28',),
    ('49',),
    ('29', '50'),
    ('51', '52', '53', '54', '55', '56', '30', '57', '58'),
)
APPEARANCE_ORDER = tuple(code for group in APPEARANCE_ORDER for code in group)
assert set(APPEARANCE_ORDER)=={q.code for q in QUESTIONS} and len(APPEARANCE_ORDER)==len(QUESTIONS)
_DISPLAY_POSITION = {code:i for i,code in enumerate(APPEARANCE_ORDER)}
QUESTIONS.sort(key=lambda q: _DISPLAY_POSITION[q.code])
VISIBLE_NUMBERS = {q.code: f'{i:02d}' for i,q in enumerate(QUESTIONS,1)}
BY_CODE={q.code:q for q in QUESTIONS}
SECTIONS=list(dict.fromkeys(q.section for q in QUESTIONS))
def completed_count(answers:dict)->int:
    return sum(bool(str(answers.get(q.code,'')).strip()) for q in QUESTIONS)
