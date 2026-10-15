"""Scientific defaults and instructional metadata (fictional scenario)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Variable:
    key: str
    label: str
    unit: str
    description: str
    human_mean: float
    human_sd: float
    human_min: float
    human_max: float
    vampire_mean: float
    vampire_sd: float
    vampire_min: float
    vampire_max: float


VARIABLES = [
    Variable("Fer", "Fer sanguin", "µg/dL", "Concentration de fer dans le sang, exprimée en microgrammes par décilitre (µg/dL). Les valeurs sont simulées pour l’exercice : elles ne correspondent pas à une mesure clinique validée.", 95, 30, 25, 220, 90, 28, 25, 220),
    Variable("Blancheur", "Pâleur cutanée", "/100", "Indice fictif de pâleur de la peau, noté de 0 à 100. Une valeur proche de 0 correspond à un teint moins pâle ; une valeur proche de 100, à une pâleur plus marquée. Ce n’est pas une mesure médicale.", 68, 15, 5, 98, 74, 14, 25, 100),
    Variable("Sensibilite_soleil", "Sensibilité au soleil", "/10", "Indice fictif de gêne liée au soleil, noté de 0 à 10. À 0, l’individu ne présente pas de gêne dans le scénario ; à 10, la gêne est maximale.", 4.8, 2.5, 0, 10, 6.8, 2.2, 4.5, 10),
    Variable("Temperature_corporelle", "Température corporelle", "°C", "Température corporelle exprimée en degrés Celsius (°C). Les valeurs ont été définies pour le jeu fictif et n’ont pas de valeur diagnostique.", 36.5, .5, 35.2, 38.2, 36.2, .45, 34.5, 36.8),
    Variable("Age", "Âge", "ans", "Âge de l’individu, exprimé en années. Le scénario autorise des âges fantastiques pour les vampires, jusqu’à 600 ans.", 45, 20, 16, 98, 110, 90, 40, 600),
    Variable("Pulsation_cardiaque", "Fréquence cardiaque", "bpm", "Fréquence du pouls, exprimée en battements cardiaques par minute (bpm). Plus la valeur est élevée, plus le cœur bat rapidement dans le scénario.", 66, 14, 38, 115, 60, 12, 32, 92),
    Variable("Regeneration", "Régénération", "/10", "Indice fictif de régénération, noté de 0 à 10. À 0, la récupération est très faible ; à 10, elle est maximale dans l’univers du TD.", 4.8, 2.2, 0, 10, 6.2, 1.9, 4.5, 10),
    Variable("Longueur_canines", "Longueur des canines", "mm", "Longueur des canines, exprimée en millimètres (mm). Il s’agit d’une longueur simulée et non d’un critère de diagnostic.", 9.5, 2.8, 3, 17, 11.5, 3.2, 8, 24),
    Variable("Force", "Force", "/10", "Indice fictif de force physique, noté de 0 à 10. Une valeur proche de 0 traduit une force très faible ; une valeur proche de 10, une force élevée.", 5.8, 1.2, 0, 10, 6.2, 1.3, 0, 10),
    Variable("Vitesse", "Vitesse", "/10", "Indice fictif de vitesse de déplacement, noté de 0 à 10. Une valeur proche de 0 correspond à une faible vitesse ; une valeur proche de 10, à une vitesse très élevée. Ce n’est pas une mesure en km/h.", 5.6, 1.1, 0, 10, 5.9, 1.2, 0, 10),
]
KEYS = [v.key for v in VARIABLES]
LABELS = {v.key: v.label for v in VARIABLES}
UNITS = {v.key: v.unit for v in VARIABLES}
DESCRIPTIONS = {v.key: v.description for v in VARIABLES}
MODEL_NAMES = ["Forêt aléatoire", "XGBoost", "Régression logistique · Ridge", "Régression logistique · Lasso", "Régression logistique · Elastic Net", "Réseau de neurones", "Réseau profond"]
MODEL_SHORT = {
    "Forêt aléatoire": "Random Forest",
    "XGBoost": "XGBoost",
    "Régression logistique · Ridge": "Ridge / L2",
    "Régression logistique · Lasso": "Lasso / L1",
    "Régression logistique · Elastic Net": "Elastic Net",
    "Réseau de neurones": "MLP compact",
    "Réseau profond": "MLP profond",
}


def initial_parameters() -> dict:
    """Independent, class-specific bounds: never intersect those bounds."""
    result = {}
    for v in VARIABLES:
        result[v.key] = {
            "Humain": {"mean": v.human_mean, "sd": v.human_sd, "min": v.human_min, "max": v.human_max},
            "Vampire": {"mean": v.vampire_mean, "sd": v.vampire_sd, "min": v.vampire_min, "max": v.vampire_max},
        }
    return result


def glossary() -> list[tuple[str, str]]:
    return [
        ("Population", "Ensemble théorique des individus que l'on souhaite étudier."),
        ("Échantillon", "Individus tirés dans cette population, avec fluctuations aléatoires."),
        ("Prévalence", "Proportion d'individus de la classe positive dans la population simulée."),
        ("Train / test", "Le train sert à apprendre ; le test reste de côté pour évaluer une fois l'entraînement effectué."),
        ("Validation croisée", "On réentraîne successivement sur différents sous-ensembles du train ; elle n'utilise jamais le test."),
        ("Accuracy", "Part totale des prédictions correctes. Potentiellement trompeuse en cas de déséquilibre."),
        ("Sensibilité", "Parmi les vampires, part correctement reconnue par le modèle."),
        ("Spécificité", "Parmi les humains, part correctement reconnue par le modèle."),
        ("F1", "Moyenne harmonique de la précision et du rappel."),
        ("AUC-ROC", "Capacité à classer un vampire au-dessus d'un humain, évaluée sur plusieurs seuils."),
        ("Calibration", "Accord entre probabilités annoncées et fréquences observées."),
        ("Perceptron multicouche (MLP)", "Réseau de neurones composé de couches de neurones artificiels, entraîné par optimisation des poids."),
        ("Surapprentissage", "Lorsque le modèle mémorise trop les particularités du train et prédit moins bien sur de nouvelles données."),
        ("Dépendance partielle (PDP)", "Effet moyen simulé d'une variable en faisant varier celle-ci pour de nombreux individus ; pas un effet causal."),
    ]
