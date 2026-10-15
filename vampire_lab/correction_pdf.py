"""Corrigé autonome du TD, généré localement au format PDF."""
from __future__ import annotations

from io import BytesIO
from threading import Lock
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, PageBreak,
    KeepTogether, Table, TableStyle, Flowable,
)

from .pedagogy import QUESTIONS, SECTIONS, VISIBLE_NUMBERS

DARK = colors.HexColor('#171b2a')
INK = colors.HexColor('#252838')
SUB = colors.HexColor('#58617a')
PINK = colors.HexColor('#c83762')
CYAN = colors.HexColor('#187f92')
PAPER = colors.HexColor('#f7f7fb')
RULE = colors.HexColor('#e2e4ed')
FONT_OK = False
FONT_LOCK = Lock()


def fonts():
    global FONT_OK
    if FONT_OK:
        return
    with FONT_LOCK:
        if FONT_OK:
            return
        import reportlab
        folder = Path(reportlab.__file__).resolve().parent / 'fonts'
        pdfmetrics.registerFont(TTFont('ESMIHAFont', str(folder / 'Vera.ttf')))
        pdfmetrics.registerFont(TTFont('ESMIHABold', str(folder / 'VeraBd.ttf')))
        pdfmetrics.registerFontFamily('ESMIHAFont', normal='ESMIHAFont', bold='ESMIHABold')
        FONT_OK = True


class LineDiagram(Flowable):
    def __init__(self, kind='split', width=470, height=102):
        super().__init__(); self.width=width; self.height=height; self.kind=kind

    def draw(self):
        c = self.canv
        def rect(x,y,w,h,col,title,detail):
            c.setFillColor(col);c.roundRect(x,y,w,h,8,stroke=0,fill=1)
            c.setFillColor(colors.white);c.setFont('ESMIHABold',10);c.drawCentredString(x+w/2,y+h*.57,title)
            c.setFont('ESMIHAFont',7.7);c.drawCentredString(x+w/2,y+h*.26,detail)
        if self.kind=='split':
            rect(5,33,126,49,DARK,'Population','100 %')
            rect(198,58,115,43,CYAN,'Apprentissage','80 %')
            rect(198,3,115,43,PINK,'Test réservé','20 %')
            rect(360,58,102,43,DARK,'CV sur train','10 plis')
            c.setStrokeColor(SUB);c.setLineWidth(1.4)
            for xa,ya,xb,yb in [(131,58,198,78),(131,58,198,24),(313,78,360,78)]:
                c.line(xa,ya,xb,yb)
        elif self.kind=='mlflow':
            rect(0,30,110,48,CYAN,'Jeu de données','10 variables')
            rect(120,30,110,48,DARK,'5 méthodes','RF · XGB · L1/L2')
            rect(240,30,108,48,PINK,'Validation','10 plis')
            rect(358,30,108,48,CYAN,'Interpréter','Scores · courbes')
        elif self.kind=='matrix':
            rect(5,52,222,45,CYAN,'Vrai négatif','Humain prédit humain')
            rect(239,52,222,45,PINK,'Faux positif','Humain prédit vampire')
            rect(5,1,222,45,PINK,'Faux négatif','Vampire prédit humain')
            rect(239,1,222,45,CYAN,'Vrai positif','Vampire prédit vampire')
        else:
            rect(2,29,112,54,CYAN,'10 entrées','Variables')
            rect(170,29,118,54,DARK,'Couches cachées','24 puis 12')
            rect(346,29,114,54,PINK,'1 sortie','P(vampire)')
            c.setStrokeColor(SUB)
            c.line(114,55,170,55);c.line(288,55,346,55)


def styles():
    common = dict(fontName='ESMIHAFont', textColor=INK, leading=15)
    return {
        'cover_label': ParagraphStyle('cover_label', fontName='ESMIHABold', fontSize=11, leading=17, textColor=PINK, spaceAfter=20),
        'cover_title': ParagraphStyle('cover_title', fontName='ESMIHABold', fontSize=29, leading=37, textColor=DARK, spaceAfter=19),
        'subtitle': ParagraphStyle('subtitle', fontName='ESMIHAFont', fontSize=13, leading=20, textColor=SUB),
        'h1': ParagraphStyle('h1', fontName='ESMIHABold', fontSize=16, leading=23, textColor=DARK, spaceBefore=18, spaceAfter=13, keepWithNext=True),
        'question': ParagraphStyle('question', fontName='ESMIHABold', fontSize=10.9, leading=16, textColor=DARK, spaceBefore=14, spaceAfter=7, keepWithNext=True),
        'body': ParagraphStyle('body', fontSize=9.6, spaceAfter=7, **common),
        'example': ParagraphStyle('example',fontName='ESMIHAFont',fontSize=9.0,leading=14.3,textColor=CYAN,leftIndent=11,spaceAfter=7),
        'key': ParagraphStyle('key',fontName='ESMIHABold',fontSize=8.8,leading=13.4,textColor=DARK,leftIndent=11,spaceAfter=11),
        'small': ParagraphStyle('small',fontSize=8.5, spaceAfter=8,**common),
        'note': ParagraphStyle('note',fontName='ESMIHAFont',fontSize=8.8,leading=13.7,textColor=SUB,spaceAfter=9),
        'table_head': ParagraphStyle('table_head',fontName='ESMIHABold',fontSize=8.8,leading=12,textColor=colors.white),
        'table': ParagraphStyle('table',fontName='ESMIHAFont',fontSize=8.6,leading=12.5,textColor=INK),
    }


def page_decor(canvas, doc):
    w,h=A4
    canvas.saveState()
    canvas.setFillColor(DARK)
    canvas.rect(0,h-13, w,13,fill=1,stroke=0)
    canvas.setFont('ESMIHABold',8.7)
    canvas.setFillColor(SUB)
    canvas.drawString(2.0*cm,1.25*cm,'ESMIHA  /  TRAVAUX DIRIGÉS  /  APPRENTISSAGE SUPERVISÉ')
    canvas.drawRightString(w-2*cm,1.25*cm,f'{doc.page:02d}')
    canvas.setStrokeColor(RULE)
    canvas.line(2*cm,1.65*cm,w-2*cm,1.65*cm)
    canvas.restoreState()


def make_correction_pdf(spec=None, results=None) -> bytes:
    """Full printable solutions; optional factual summary of the running session."""
    fonts(); sty=styles()
    buffer=BytesIO()
    doc=BaseDocTemplate(buffer, pagesize=A4, leftMargin=2*cm,rightMargin=2*cm,
                        topMargin=2.1*cm,bottomMargin=2.2*cm,
                        title='TD ESMIHA - Corrigé détaillé', author='Quentin Lamboley',
                        subject='Classification supervisée - simulation humains et vampires')
    frame=Frame(doc.leftMargin,doc.bottomMargin,doc.width,doc.height,leftPadding=0,
                bottomPadding=0,rightPadding=0,topPadding=0)
    doc.addPageTemplates(PageTemplate(id='normal',frames=frame,onPage=page_decor))
    p=lambda txt,style='body': Paragraph(escape(str(txt)),sty[style])
    story=[]
    story.extend([Spacer(1,1.2*cm),p('MASTER ESMIHA  ·  SUPPORT DE TRAVAUX DIRIGÉS','cover_label'),
        Paragraph('Machine learning :<br/>corrigé du TD',sty['cover_title']),
        p('Validation non croisée, validation croisée, comparaison des modèles et interprétation','subtitle'),
        Spacer(1,1.2*cm), LineDiagram('mlflow'),Spacer(1,.9*cm),
        p('QUENTIN LAMBOLEY  ·  MASTER ESMIHA','cover_label'),
        p('Ce corrigé suit les manipulations, de la première exploration jusqu’à la comparaison des algorithmes. Les exemples chiffrés servent à comprendre un raisonnement ; ils ne sont pas des scores à retrouver obligatoirement. La fabrication du jeu de données ne fait pas partie des questions.','body'),
        Spacer(1,.35*cm),p('Repère méthodologique','question'),
        p('L’objectif n’est pas de deviner toutes les réponses à coup sûr, mais de comprendre comment entraîner un algorithme, vérifier ses erreurs et interpréter son résultat. Les personnages sont fictifs : nous travaillons sur les méthodes, pas sur le réalisme des données.','body'),
        PageBreak()])
    story += [p('Comment utiliser ce corrigé','h1'),
        p('Pour chaque question, je propose d’abord une explication, puis un exemple concret et un point à retenir. Il faut essayer la manipulation dans l’application avant de consulter cette correction. Plusieurs formulations peuvent être justes si le raisonnement est scientifiquement argumenté.','body'),
        p('Protocole de référence : jeu de données fictif de 1 000 observations, séparation stratifiée 80/20, puis validation croisée à dix plis dans l’apprentissage. L’effectif, la proportion des classes et la proximité des profils peuvent être modifiés pour étudier leur influence sur l’évaluation. Comparer Random Forest, XGBoost, Ridge, Lasso et Elastic Net. Les réseaux de neurones sont un complément facultatif.','body'),
        Spacer(1,.3*cm),LineDiagram('split'),Spacer(1,.3*cm),
        p('La validation croisée doit avoir lieu à l’intérieur du train. Le jeu de test ne sert pas à choisir le modèle, les variables ou le seuil de décision.','note')]
    for sec in SECTIONS:
        story.append(p(sec.upper(),'h1'))
        if sec=='Comparaison':
            story.extend([LineDiagram('matrix'),Spacer(1,.25*cm)])
        elif sec=='Réseaux de neurones : complément':
            story.extend([LineDiagram('network'),Spacer(1,.25*cm)])
        for q in [x for x in QUESTIONS if x.section==sec]:
            story.append(KeepTogether([
                p(f'{VISIBLE_NUMBERS[q.code]}  /  {q.enonce}','question'),
                p(q.correction,'body'),
                Paragraph('<b>Exemple concret.</b> ' + escape(q.exemple),sty['example']),
                Paragraph('À retenir : ' + escape(q.retenir),sty['key']),
            ]))
    story.append(PageBreak())
    story.append(p('Formules et repères pour interpréter les scores','h1'))
    formulas = [
        ('Accuracy','(VP + VN) / (VP + VN + FP + FN)','Proportion totale des décisions correctes.'),
        ('Sensibilité','VP / (VP + FN)','Parmi les vampires, proportion reconnue.'),
        ('Spécificité','VN / (VN + FP)','Parmi les humains, proportion reconnue.'),
        ('Précision positive','VP / (VP + FP)','Parmi les profils annoncés vampires, proportion réellement vampire.'),
        ('Balanced accuracy','(sensibilité + spécificité) / 2','Moyenne des performances sur les deux classes.'),
        ('F1-score','2 × précision × sensibilité / (précision + sensibilité)','Équilibre précision/rappel au seuil retenu.'),
        ('Score de Brier','Moyenne de (probabilité - cible)²','Plus faible = mieux ; dépend aussi de la prévalence.'),
        ('AUC-ROC','Aire sous la courbe ROC','Capacité à classer les deux classes sur les seuils possibles.'),
    ]
    rows=[[Paragraph('Indicateur',sty['table_head']),Paragraph('Calcul',sty['table_head']),Paragraph('Interprétation',sty['table_head'])]]
    rows += [[Paragraph(escape(a),sty['table']),Paragraph(escape(b),sty['table']),Paragraph(escape(c),sty['table'])] for a,b,c in formulas]
    table=Table(rows,colWidths=[3.65*cm,5.7*cm,7.0*cm],repeatRows=1,hAlign='LEFT')
    table.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),DARK),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,PAPER]),
        ('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),9),
        ('TOPPADDING',(0,0),(-1,-1),9),('LEFTPADDING',(0,0),(-1,-1),9),
        ('RIGHTPADDING',(0,0),(-1,-1),9),('LINEBELOW',(0,-1),(-1,-1),.5,RULE),
    ]))
    story += [table,Spacer(1,.45*cm),
        p('VP : vrai positif. VN : vrai négatif. FP : faux positif. FN : faux négatif. Dans ce TD, « Vampire » est la classe positive.','note'),
        p('Pour refaire le TD à domicile','h1'),
        p('1. Décompresser le dossier du TD. 2. Installer Python 3.11 ou 3.12 si nécessaire. 3. Exécuter le lanceur Windows, Linux ou macOS. 4. Attendre la première installation des dépendances, puis ouvrir l’adresse locale indiquée. 5. Reproduire les manipulations en utilisant les boutons de progression et conserver ses réponses dans le carnet. Les lancements suivants peuvent fonctionner sans connexion une fois toutes les dépendances installées.','body'),
        p('À conserver dans le compte rendu : effectif et répartition des classes, prédicteurs utilisés, protocole train/test, algorithmes comparés, nombre de plis, scores et leurs limites, matrice de confusion, interprétation des variables et conclusions.','body')]
    if spec or results:
        story.append(p('Résultats de la séance en cours','h1'))
        if spec:
            story.append(p(f"Jeu analysé : {spec.get('n','-')} individus ; proportion de vampires : {float(spec.get('prevalence',.5)):.1%} ; référence de reproductibilité : {spec.get('seed','-')}.",'body'))
        if results:
            for name,r in results.items():
                metrics=r.get('metrics',{})
                story.append(p(f"{name} : accuracy test {metrics.get('accuracy',0):.1%} ; sensibilité {metrics.get('recall',0):.1%} ; spécificité {metrics.get('specificity',0):.1%} ; AUC-ROC {metrics.get('roc_auc',0):.3f}.",'small'))
            story.append(p('Ces résultats correspondent uniquement aux observations et aux modèles de cette séance. Ils ne sont pas des valeurs à obtenir obligatoirement : changer les données ou les réglages peut modifier les scores.','note'))
    story += [Spacer(1,.45*cm),p('Quentin Lamboley  ·  Master ESMIHA  ·  Support de travaux dirigés','note')]
    doc.build(story)
    return buffer.getvalue()
