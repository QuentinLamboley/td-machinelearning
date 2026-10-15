"""Compte rendu individuel au format PDF ; calcul intégralement en mémoire."""
from __future__ import annotations
from datetime import date
from io import BytesIO
from xml.sax.saxutils import escape
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, KeepTogether
from .pedagogy import QUESTIONS, SECTIONS, VISIBLE_NUMBERS
from .correction_pdf import fonts, page_decor, DARK, INK, SUB, PINK, CYAN


def make_student_pdf(answers: dict, notes: str = '', student_name: str = '',
                     spec: dict | None = None, model_results: dict | None = None) -> bytes:
    """PDF isolé à partir des réponses passées en argument, jamais depuis un fichier partagé."""
    fonts()
    buf = BytesIO()
    doc = BaseDocTemplate(buf, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2.1*cm, bottomMargin=2.2*cm,
        title='TD - Introduction au Machine Learning - Mon compte rendu',
        author='Quentin Lamboley', subject='Compte rendu individuel - Master ESMIHA')
    frame = Frame(doc.leftMargin,doc.bottomMargin,doc.width,doc.height,
                  leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
    doc.addPageTemplates(PageTemplate(id='page',frames=frame,onPage=page_decor))
    heading=ParagraphStyle('student_heading',fontName='ESMIHABold',fontSize=22,leading=30,textColor=DARK,spaceAfter=12)
    section=ParagraphStyle('student_section',fontName='ESMIHABold',fontSize=13,leading=19,textColor=PINK,spaceBefore=15,spaceAfter=8,keepWithNext=True)
    question=ParagraphStyle('student_q',fontName='ESMIHABold',fontSize=10,leading=15,textColor=DARK,spaceBefore=9,spaceAfter=4,keepWithNext=True)
    answer=ParagraphStyle('student_a',fontName='ESMIHAFont',fontSize=9.4,leading=15,textColor=INK,spaceAfter=11,leftIndent=10)
    small=ParagraphStyle('student_small',fontName='ESMIHAFont',fontSize=9,leading=14,textColor=SUB,spaceAfter=11)
    def p(text,style):
        return Paragraph(escape(str(text)).replace('\n','<br/>'),style)
    rows=[Spacer(1,.5*cm),p('TD - Introduction au Machine Learning',heading),
        p('Master ESMIHA · Quentin Lamboley · Compte rendu individuel',small),
        p('Étudiant(e) : '+(student_name.strip()[:140] or 'Non renseigné'),small),
        p('Date : '+date.today().strftime('%d/%m/%Y'),small)]
    n_answered=sum(bool(str(answers.get(q.code,'')).strip()) for q in QUESTIONS)
    rows.append(p(f'Questions renseignées : {n_answered} / {len(QUESTIONS)} (complément compris).',small))
    if spec:
        rows.append(p(f"Jeu analysé : {spec.get('n','-')} observations ; "
                      f"{float(spec.get('prevalence',.5)):.0%} de vampires (fréquence théorique ou observée).",small))
    if spec and 'proximity' in spec:
        rows.append(p(f"Proximité des profils humains/vampires : {spec['proximity']} %.",small))
    if model_results:
        rows.append(p('Résultats des modèles entraînés pendant la séance',section))
        for name, result in model_results.items():
            m=result.get('metrics',{})
            rows.append(p(f"{name} : accuracy {m.get('accuracy',0):.1%}, "
                          f"sensibilité {m.get('recall',0):.1%}, "
                          f"balanced accuracy {m.get('balanced_accuracy',0):.1%}.",small))
    for sec in SECTIONS:
        rows.append(p(sec,section))
        for q in (x for x in QUESTIONS if x.section==sec):
            response=str(answers.get(q.code,'')).strip()[:8000]
            rows.append(p(f'{VISIBLE_NUMBERS[q.code]} / {q.enonce}',question))
            if response:
                rows.append(p(response,answer))
            else:
                rows.append(p('Réponse non renseignée.',small))
    if notes.strip():
        rows.extend([p('Notes et conclusion personnelles',section),p(notes.strip()[:30000],answer)])
    rows.append(p('Les réponses ci-dessus proviennent du travail saisi pendant cette séance. Ce document ne contient pas le corrigé de référence.',small))
    doc.build(rows)
    return buf.getvalue()
