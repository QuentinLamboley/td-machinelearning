# Lasso (L1) · TD Machine Learning ESMIHA

Lasso peut rendre certains coefficients nuls et ainsi sélectionner les variables.

Ces codes utilisent le jeu `data/Data_vampi.csv`. Exécute-les à partir de la racine du dossier du TD. **La classe 1 correspond aux vampires**, la classe 0 aux humains.

Les deux langages appliquent la même démarche, mais leurs bibliothèques n'utilisent pas exactement les mêmes réglages internes. Les résultats numériques peuvent donc différer.

## Python

```python
# Depuis la racine du projet ESMIHA
import pandas as pd
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, recall_score, precision_score

data = pd.read_csv("data/Data_vampi.csv")
X = data.drop(columns=["Vampirisme"])
y = data["Vampirisme"].astype(int)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
# Les variables sont standardisées à partir du train uniquement.
import sklearn
version_sklearn = tuple(int(x) for x in sklearn.__version__.split(".")[:2])
parametres = dict(solver="saga", C=1.0, class_weight="balanced",
                  max_iter=3000, random_state=42)
if version_sklearn >= (1, 8):
    parametres["l1_ratio"] = 1.0
else:
    parametres.update(penalty="elasticnet", l1_ratio=1.0)
modele = Pipeline([("standardisation", StandardScaler()),
                   ("modele", LogisticRegression(**parametres))])

# Validation croisée sur le train uniquement. Le test reste réservé.
cv = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)
scores = cross_validate(modele, X_train, y_train, cv=cv, n_jobs=1,
                        scoring={"accuracy":"accuracy", "balanced_accuracy":"balanced_accuracy",
                                 "f1":"f1", "roc_auc":"roc_auc"})
print("Accuracy CV (moyenne) :", round(scores["test_accuracy"].mean(), 3))
modele.fit(X_train, y_train)
predictions = modele.predict(X_test)
print("Accuracy test :", round(accuracy_score(y_test, predictions), 3))
print("Balanced accuracy test :", round(balanced_accuracy_score(y_test, predictions), 3))
print("Sensibilité test :", round(recall_score(y_test, predictions), 3))
print("Précision vampire test :", round(precision_score(y_test, predictions, zero_division=0), 3))
print("F1 test :", round(f1_score(y_test, predictions, zero_division=0), 3))
```

## R (RStudio)

```r
# Depuis la racine du projet ESMIHA (RStudio)
data <- read.csv("data/Data_vampi.csv", check.names = FALSE)
data$Vampirisme <- as.integer(data$Vampirisme)
set.seed(42)
# Séparation stratifiée : 80 % de chaque classe dans l'apprentissage.
indices_train <- unlist(lapply(split(seq_len(nrow(data)), data$Vampirisme), function(indices) {
  sample(indices, size = floor(length(indices) * 0.8))
}))
train <- data[indices_train, , drop = FALSE]
test <- data[-indices_train, , drop = FALSE]
x_train <- as.matrix(train[, setdiff(names(train), "Vampirisme"), drop = FALSE])
x_test <- as.matrix(test[, setdiff(names(test), "Vampirisme"), drop = FALSE])
y_train <- train$Vampirisme
y_test <- test$Vampirisme

# Installation une seule fois : install.packages("glmnet")
stopifnot(requireNamespace("glmnet", quietly = TRUE))
# glmnet standardise les prédicteurs sur les données d'apprentissage.
# alpha=0 : Ridge ; alpha=1 : Lasso ; alpha=0.5 : Elastic Net.
modele <- glmnet::glmnet(x_train, y_train, family="binomial", alpha=1.0,
                         lambda=0.01, standardize=TRUE)
prob_test <- as.numeric(predict(modele, newx=x_test, type="response", s=0.01))

# Évaluation sur les individus réservés au test.
predit <- as.integer(prob_test >= 0.5)
vp <- sum(predit == 1 & y_test == 1)
fn <- sum(predit == 0 & y_test == 1)
vn <- sum(predit == 0 & y_test == 0)
fp <- sum(predit == 1 & y_test == 0)
cat("Accuracy test :", round(mean(predit == y_test), 3), "\n")
cat("Sensibilité :", round(vp / max(1, vp + fn), 3), "\n")
cat("Spécificité :", round(vn / max(1, vn + fp), 3), "\n")
cat("Précision vampire :", round(vp / max(1, vp + fp), 3), "\n")
cat("Balanced accuracy :", round((vp / max(1, vp+fn) + vn / max(1, vn+fp))/2, 3), "\n")
```

## À observer

- Comment évoluent l'accuracy, la sensibilité et la précision ?
- Quel type d'erreur te semble le plus gênant dans le scénario du TD ?
- Le classement des algorithmes est-il toujours le même si tu modifies le jeu de données ?

**Pour aller plus loin :** la validation croisée à dix plis se réalise sur le train uniquement, avant de consulter le jeu de test réservé. Le fichier Python montre cette étape ; sous R, la même évaluation peut être mise en œuvre avec `caret` ou `rsample` selon les outils utilisés pendant le cours.
