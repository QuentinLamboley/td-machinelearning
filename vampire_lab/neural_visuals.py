"""Schémas interactifs du perceptron multicouche et de l'optimisation."""
from __future__ import annotations
import numpy as np
import plotly.graph_objects as go
from .viz import style, CYAN, RED, VIOLET, MUTED

ARCHITECTURES = {
    "Réseau de neurones": (24, 12),
    "Réseau profond": (48, 24, 12),
}


def neuron_count(architecture: tuple[int, ...], inputs: int = 10) -> int:
    sizes = (inputs,) + tuple(architecture) + (1,)
    return sum((a + 1) * b for a, b in zip(sizes[:-1], sizes[1:]))


def network_chart(architecture: tuple[int, ...]) -> go.Figure:
    """A limited set of illustrative nodes; labels contain actual layer sizes."""
    sizes = [10, *architecture, 1]
    fig = go.Figure()
    axes = []
    for layer, n in enumerate(sizes):
        shown = min(n, 7)
        yy = np.linspace(-2.8, 2.8, shown) if shown > 1 else np.array([0.])
        axes.append([(layer * 2.3, float(y)) for y in yy])
    for layer in range(len(axes) - 1):
        xs, ys = [], []
        for x0, y0 in axes[layer]:
            for x1, y1 in axes[layer + 1]:
                xs.extend([x0, x1, None]); ys.extend([y0, y1, None])
        fig.add_trace(go.Scatter(x=xs, y=ys, mode='lines', line=dict(color='rgba(151,155,207,.12)', width=.8), hoverinfo='skip', showlegend=False))
    for i, coords in enumerate(axes):
        xs, ys = zip(*coords)
        color = CYAN if i == 0 else (RED if i == len(axes) - 1 else VIOLET)
        txt = ('Données<br>10 variables' if i == 0 else
               ('Sortie<br>P(vampire)' if i == len(axes)-1 else f'Couche {i}<br>{sizes[i]} neurones'))
        fig.add_trace(go.Scatter(x=xs, y=ys, mode='markers', showlegend=False,
                                 marker=dict(size=23 if len(coords) > 1 else 30, color=color,
                                             line=dict(color='#ffffff', width=1), opacity=.9),
                                 hovertemplate=txt+'<extra></extra>'))
        fig.add_annotation(x=xs[0], y=3.45, text=txt, showarrow=False,
                           font=dict(size=12, color='#e8e9f6'), align='center')
        if sizes[i] > len(coords):
            fig.add_annotation(x=xs[0], y=-3.55, text=f'+ {sizes[i] - len(coords)} autres',
                               showarrow=False, font=dict(size=10, color=MUTED))
    fig.update_xaxes(visible=False, range=[-1, (len(sizes)-1)*2.3+1])
    fig.update_yaxes(visible=False, range=[-4, 4])
    fig.update_layout(hovermode='closest')
    return style(fig, 355)


def activation_chart() -> go.Figure:
    x = np.linspace(-4, 4, 220)
    fig = go.Figure()
    for name, vals, col in [('ReLU', np.maximum(x, 0), RED),
                            ('Sigmoïde', 1/(1+np.exp(-x)), CYAN),
                            ('Tanh', np.tanh(x), VIOLET)]:
        fig.add_trace(go.Scatter(x=x, y=vals, name=name, mode='lines', line=dict(width=3, color=col)))
    fig.update_xaxes(title='Somme pondérée reçue par un neurone')
    fig.update_yaxes(title='Valeur transmise')
    return style(fig, 340)


def loss_chart(estimator) -> go.Figure | None:
    net = getattr(estimator, 'named_steps', {}).get('modele', estimator)
    loss = getattr(net, 'loss_curve_', None)
    if loss is None or len(loss) == 0:
        return None
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=np.arange(1,len(loss)+1), y=loss, mode='lines',
                             line=dict(color=RED, width=3), name='Perte sur le train',
                             fill='tozeroy', fillcolor='rgba(255,83,125,.10)'))
    fig.update_xaxes(title='Itérations d’optimisation')
    fig.update_yaxes(title='Fonction de perte (train)', rangemode='tozero')
    return style(fig, 345)
