"""Schémas interactifs des familles d'algorithmes et des plis de validation."""
import plotly.graph_objects as go
import numpy as np

PINK='#ff789e'
CYAN='#67d9e5'
VIOLET='#b39bff'
SUB='#c2cce2'

def algorithm_map(name:str):
    fig=go.Figure()
    nodes=[]; lines=[]
    if name=='Forêt aléatoire':
        desc='Arbres construits avec de la diversité  →  votes agrégés'
        nodes=[(-2.5,1.2,'Arbre 1',CYAN),(-2.5,0,'Arbre 2',CYAN),(-2.5,-1.2,'Arbre 3',CYAN),
               (0.4,0,'Vote des arbres',VIOLET),(3.0,0,'Prédiction',PINK)]
        lines=[(-1.7,1.2,-.6,0),(-1.7,0,-.6,0),(-1.7,-1.2,-.6,0),(1.3,0,2.0,0)]
    elif name=='XGBoost':
        desc='Ensemble amélioré progressivement par ajouts successifs'
        nodes=[(-2.8,0,'Arbre 1',CYAN),(-.5,0,'Arbre 2',VIOLET),(1.8,0,'Arbre 3…',PINK)]
        lines=[(-1.9,0,-1.4,0),(.45,0,.85,0)]
    else:
        penalty= 'L2 · coefficients réduits' if 'Ridge' in name else ('L1 · certains coefficients nuls' if 'Lasso' in name else 'L1 + L2 · compromis')
        desc='Régression logistique régularisée  ·  '+penalty
        nodes=[(-2.9,0,'10 variables',CYAN),(-.35,0,'Coefficients',VIOLET),(2.55,0,'P(Vampire)',PINK)]
        lines=[(-1.9,0,-1.45,0),(.62,0,1.5,0)]
    for x1,y1,x2,y2 in lines:
        fig.add_trace(go.Scatter(x=[x1,x2],y=[y1,y2],mode='lines',line=dict(color='#77859c',width=3),
                                 hoverinfo='skip',showlegend=False))
    for x,y,text,color in nodes:
        fig.add_trace(go.Scatter(x=[x],y=[y],mode='markers+text',
            marker=dict(size=58,color=color,symbol='circle',line=dict(color='#171e37',width=2)),
            text=[text],textposition='bottom center',textfont=dict(color=SUB,size=12),
            hovertemplate=text+'<extra></extra>',showlegend=False))
    fig.update_layout(title=desc,template='plotly_dark',height=250,margin=dict(l=8,r=8,t=57,b=32),
          xaxis=dict(range=[-4.0,4.0],visible=False),yaxis=dict(range=[-2.05,2.1],visible=False,scaleanchor='x'),
          paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)')
    return fig

def cv_folds_chart(k:int):
    if not isinstance(k,int) or not 2 <= k <= 10:raise ValueError('Choisis entre 2 et 10 plis.')
    grid=np.zeros((k,k))
    np.fill_diagonal(grid,1)
    fig=go.Figure(go.Heatmap(z=grid,colorscale=[[0,'#266780'],[0.4999,'#266780'],[.5,'#f0719a'],[1,'#f0719a']],
                     showscale=False,text=np.where(grid==1,'VALIDATION','TRAIN'),texttemplate='%{text}',
                     textfont=dict(size=9,color='white'),xgap=4,ygap=4,hovertemplate='Tour %{y}<br>Bloc %{x}: %{text}<extra></extra>'))
    fig.update_layout(template='plotly_dark',height=max(260, 35*k+80),
           xaxis=dict(title='Blocs du jeu d’apprentissage',tickmode='array',tickvals=list(range(k)),ticktext=list(range(1,k+1)),side='top'),
           yaxis=dict(title='Entraînements successifs',tickmode='array',tickvals=list(range(k)),ticktext=list(range(1,k+1)),autorange='reversed'),
           margin=dict(l=35,r=30,t=70,b=40),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)')
    return fig
