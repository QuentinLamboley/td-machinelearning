"""Consistent dark, interactive Plotly figures. No external visual assets."""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.calibration import calibration_curve
from sklearn.metrics import precision_recall_curve, roc_curve

from .config import LABELS, UNITS

BG = "rgba(0,0,0,0)"
GRID = "rgba(185,200,237,.105)"
TEXT = "#e8e9f6"
MUTED = "#a0a5bd"
RED = "#ff537d"
CYAN = "#5cdbe8"
VIOLET = "#9d83ff"
CLASSES = {"Humain": CYAN, "Vampire": RED}
SERIES = [RED, CYAN, VIOLET, "#ffc87a", "#7be4a6", "#d9a4e8"]


def style(fig: go.Figure, height: int = 405, title: str | None = None) -> go.Figure:
    fig.update_layout(
        template="plotly_dark", paper_bgcolor=BG, plot_bgcolor=BG,
        font=dict(family="Inter, Segoe UI, sans-serif", color=TEXT, size=12),
        title=dict(text=title, font=dict(size=18, color=TEXT), x=.025) if title else None,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0,
                    bgcolor="rgba(0,0,0,0)", font=dict(color=MUTED)),
        margin=dict(l=40, r=24, t=65 if title else 34, b=42),
        hoverlabel=dict(bgcolor="#202138", font_color="#ffffff", bordercolor="#444564"),
        height=height,
    )
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=GRID, linecolor=GRID,
                     title_font=dict(color=MUTED), tickfont=dict(color=MUTED))
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=GRID, linecolor=GRID,
                     title_font=dict(color=MUTED), tickfont=dict(color=MUTED))
    return fig


def distribution_chart(data: pd.DataFrame, variable: str, mode: str = "Densités") -> go.Figure:
    df = data[[variable, "Vampirisme"]].copy()
    df["Profil"] = df["Vampirisme"].map({0: "Humain", 1: "Vampire"})
    if mode == "Boîtes à moustaches":
        fig = px.box(df, x="Profil", y=variable, color="Profil", points="outliers",
                     color_discrete_map=CLASSES)
        fig.update_layout(showlegend=False)
        fig.update_yaxes(title=f"{LABELS[variable]} ({UNITS[variable]})")
    elif mode == "Violons":
        fig = px.violin(df, x="Profil", y=variable, color="Profil", box=True,
                        color_discrete_map=CLASSES)
        fig.update_layout(showlegend=False)
        fig.update_yaxes(title=f"{LABELS[variable]} ({UNITS[variable]})")
    else:
        fig = px.histogram(df, x=variable, color="Profil", nbins=40,
                           histnorm="probability density", barmode="overlay",
                           opacity=.73, color_discrete_map=CLASSES)
        fig.update_yaxes(title="Densité estimée (histogramme)")
        fig.update_xaxes(title=f"{LABELS[variable]} ({UNITS[variable]})")
    return style(fig, 425)


def scatter_chart(data: pd.DataFrame, x: str, y: str) -> go.Figure:
    df = data.sample(min(3000, len(data)), random_state=42).copy()
    df["Profil"] = df["Vampirisme"].map({0: "Humain", 1: "Vampire"})
    fig = px.scatter(df, x=x, y=y, color="Profil", color_discrete_map=CLASSES,
                     opacity=.56, hover_data={"Profil": True},
                     render_mode="webgl" if len(df) > 1000 else "svg")
    fig.update_traces(marker=dict(size=7, line=dict(width=0)))
    fig.update_xaxes(title=f"{LABELS[x]} ({UNITS[x]})")
    fig.update_yaxes(title=f"{LABELS[y]} ({UNITS[y]})")
    return style(fig, 435)


def correlation_chart(df: pd.DataFrame, features: list[str]) -> go.Figure:
    m = df[features].corr()
    pretty = [LABELS[k] for k in features]
    fig = go.Figure(go.Heatmap(z=m.to_numpy(), x=pretty, y=pretty,
        zmin=-1, zmax=1, zmid=0, colorscale=[
            [0., "#2c6c91"], [.25, "#234c6b"], [.5, "#24263c"], [.75, "#923957"], [1., "#ff6589"]],
        text=np.round(m.to_numpy(), 2), texttemplate="%{text:.2f}",
        textfont=dict(size=10), hovertemplate="%{y} / %{x}<br>r = %{z:.3f}<extra></extra>"))
    fig.update_yaxes(autorange="reversed")
    return style(fig, 530)


def class_chart(data: pd.DataFrame) -> go.Figure:
    ct = data["Vampirisme"].value_counts().reindex([0, 1], fill_value=0)
    fig = go.Figure(go.Bar(x=["Humains", "Vampires"], y=ct.to_numpy(),
                           marker_color=[CYAN, RED], marker_line_width=0,
                           text=ct.to_numpy(), textposition="outside"))
    fig.update_yaxes(title="Effectif", rangemode="tozero")
    fig.update_layout(showlegend=False)
    return style(fig, 310)


def cv_chart(result: dict) -> go.Figure | None:
    cv = result.get("cv")
    if not cv:
        return None
    frame = pd.DataFrame({"Pli": list(range(1, len(cv["accuracy"]) + 1)),
                          "Accuracy": cv["accuracy"], "Balanced accuracy": cv["balanced_accuracy"]})
    fig = go.Figure()
    for label, color in (("Accuracy", RED), ("Balanced accuracy", CYAN)):
        fig.add_trace(go.Scatter(x=frame["Pli"], y=frame[label], name=label,
                                 mode="lines+markers", line=dict(width=3, color=color),
                                 marker=dict(size=9)))
    fig.update_yaxes(range=[0, 1.04], title="Score")
    fig.update_xaxes(dtick=1, title="Pli de validation")
    return style(fig, 340)


def comparison_chart(frame: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for key, label, color in (("Accuracy test", "Test réservé", RED),
                              ("Accuracy CV moyenne", "CV : apprentissage", CYAN)):
        fig.add_trace(go.Bar(name=label, x=frame["Modèle"], y=frame[key],
                             marker_color=color, opacity=.9,
                             hovertemplate="%{x}<br>%{y:.3f}<extra>" + label + "</extra>"))
    fig.update_layout(barmode="group")
    fig.update_yaxes(range=[0, 1.05], title="Accuracy")
    fig.update_xaxes(tickangle=-25)
    return style(fig, 430)


def roc_pr_charts(result: dict) -> tuple[go.Figure, go.Figure]:
    truth, probs = result["truth"], result["probability"]
    fpr, tpr, _ = roc_curve(truth, probs)
    prec, recall, _ = precision_recall_curve(truth, probs)
    roc = go.Figure()
    roc.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="Aléatoire",
                             line=dict(dash="dash", color=MUTED)))
    roc.add_trace(go.Scatter(x=fpr, y=tpr, mode="lines", name=f"AUC = {result['metrics']['roc_auc']:.3f}",
                             fill="tozeroy", fillcolor="rgba(255,83,125,.1)", line=dict(color=RED, width=3)))
    roc.update_xaxes(title="1 − spécificité", range=[0, 1])
    roc.update_yaxes(title="Sensibilité", range=[0, 1.02])
    pr = go.Figure()
    pr.add_hline(y=float(np.mean(truth)), line_dash="dash", line_color=MUTED)
    pr.add_trace(go.Scatter(x=recall, y=prec, name="Précision / rappel",
                            line=dict(color=CYAN, width=3), fill="tozeroy",
                            fillcolor="rgba(92,219,232,.11)"))
    pr.update_xaxes(title="Rappel", range=[0, 1])
    pr.update_yaxes(title="Précision", range=[0, 1.02])
    return style(roc, 345), style(pr, 345)


def confusion_chart(result: dict, threshold: float = .5) -> go.Figure:
    from sklearn.metrics import confusion_matrix
    pred = (result["probability"] >= threshold).astype(int)
    mat = confusion_matrix(result["truth"], pred, labels=[0, 1])
    fig = go.Figure(go.Heatmap(z=mat, x=["Humain", "Vampire"], y=["Humain", "Vampire"],
        colorscale=[[0, "#262943"], [1, RED]], showscale=False,
        text=mat.astype(str), texttemplate="%{text}", textfont=dict(size=25, color="#ffffff"),
        hovertemplate="Réel : %{y}<br>Prévu : %{x}<br>n = %{z}<extra></extra>"))
    fig.update_xaxes(title="Classe prédite", side="bottom")
    fig.update_yaxes(title="Classe réelle", autorange="reversed")
    return style(fig, 330)


def calibration_chart(result: dict) -> go.Figure:
    true, pred = calibration_curve(result["truth"], result["probability"], n_bins=8, strategy="quantile")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], line=dict(color=MUTED, dash="dash"), name="Idéal"))
    fig.add_trace(go.Scatter(x=pred, y=true, name="Modèle", mode="lines+markers",
                             marker=dict(size=10), line=dict(width=3, color=VIOLET)))
    fig.update_xaxes(range=[0, 1], title="Probabilité moyenne annoncée")
    fig.update_yaxes(range=[0, 1], title="Fréquence observée")
    return style(fig, 330)


def probability_chart(result: dict) -> go.Figure:
    fig = go.Figure()
    for y, name, color in [(0, "Humains", CYAN), (1, "Vampires", RED)]:
        probs = result["probability"][result["truth"] == y]
        fig.add_trace(go.Histogram(x=probs, name=name, opacity=.75, marker_color=color,
                                   xbins=dict(start=0, end=1, size=.05)))
    fig.add_vline(x=.5, line_color="#ffdb94", line_dash="dash",
                  annotation_text="Seuil 0,50", annotation_font_color="#ffdb94")
    fig.update_layout(barmode="overlay")
    fig.update_xaxes(title="Probabilité prédite P(vampire)", range=[0, 1])
    fig.update_yaxes(title="Effectif")
    return style(fig, 340)


def importance_chart(importances: pd.DataFrame) -> go.Figure:
    frame = importances.sort_values("importance").copy()
    fig = go.Figure(go.Bar(y=frame["variable"].map(LABELS), x=frame["importance"],
                           orientation="h", marker_color=RED, error_x=dict(type="data",
                            array=frame["ecart_type"], color=MUTED),
                           hovertemplate="%{y}<br>Δ balanced accuracy = %{x:.4f}<extra></extra>"))
    fig.update_xaxes(title="Baisse de balanced accuracy après permutation")
    return style(fig, 380)


def pdp_chart(pdp: dict, variable: str, show_ice: bool = True) -> go.Figure:
    fig = go.Figure()
    if show_ice:
        for line in pdp["ice"]:
            fig.add_trace(go.Scatter(x=pdp["grid"], y=line, showlegend=False,
                                     mode="lines", hoverinfo="skip",
                                     line=dict(color="rgba(134,145,189,.19)", width=1)))
    fig.add_trace(go.Scatter(x=pdp["grid"], y=pdp["pdp"], name="Dépendance partielle",
                             mode="lines", line=dict(color=RED, width=4)))
    fig.update_yaxes(title="P(vampire) moyenne", range=[0, 1])
    fig.update_xaxes(title=f"{LABELS[variable]} ({UNITS[variable]})")
    return style(fig, 440)


def decision_surface(model, X: pd.DataFrame, x: str, y: str, seed: int = 42) -> go.Figure:
    """Conditional 2D slice, fixing all other features to the train medians."""
    if x == y:
        raise ValueError("Deux variables distinctes sont nécessaires")
    minx, maxx = X[x].quantile([.02, .98]).tolist()
    miny, maxy = X[y].quantile([.02, .98]).tolist()
    gx = np.linspace(minx, maxx, 54)
    gy = np.linspace(miny, maxy, 46)
    xx, yy = np.meshgrid(gx, gy)
    const = X.median(axis=0).to_frame().T
    grid = pd.concat([const] * xx.size, ignore_index=True)
    grid[x] = xx.ravel()
    grid[y] = yy.ravel()
    pred = model.predict_proba(grid[X.columns])[:, 1].reshape(xx.shape)
    fig = go.Figure(go.Heatmap(x=gx, y=gy, z=pred,
        colorscale=[[0, "#153f61"], [.5, "#3c2e54"], [1, "#b13d6a"]],
        zmin=0, zmax=1, colorbar=dict(title="P(V)", len=.73),
        hovertemplate=f"{LABELS[x]}: %{{x:.2f}}<br>{LABELS[y]}: %{{y:.2f}}<br>P(V): %{{z:.2f}}<extra></extra>"))
    sample = X.sample(n=min(200, len(X)), random_state=seed)
    fig.add_trace(go.Scatter(x=sample[x], y=sample[y], mode="markers", name="Individus du train",
                             marker=dict(size=4, color="rgba(255,255,255,.48)", line=dict(width=0))))
    fig.update_xaxes(title=f"{LABELS[x]} ({UNITS[x]})")
    fig.update_yaxes(title=f"{LABELS[y]} ({UNITS[y]})")
    return style(fig, 430)
