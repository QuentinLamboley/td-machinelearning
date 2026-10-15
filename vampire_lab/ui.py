"""Local, self-contained Streamlit styling components."""
import base64
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

CSS = """
<style>
:root { --ink:#f6f3fa; --sub:#a3a2b6; --hot:#ff527d; --ice:#65dee6; --violet:#987dff; }
html, body, [class*="css"], [data-testid="stApp"] { font-family: 'Inter', 'Aptos', 'Segoe UI', sans-serif; }
[data-testid="stAppViewContainer"] {
 background: radial-gradient(ellipse 65% 34% at 77% 2%, rgba(113,39,111,.23), transparent 77%),
             radial-gradient(ellipse 60% 50% at 13% 66%, rgba(23,76,105,.16), transparent 78%),
             #0c0f1b;
 color:#f1f2f8;
}
[data-testid="stHeader"] { background:rgba(11,13,24,.12); }
[data-testid="stMainBlockContainer"] { max-width:1360px; padding-top:2rem; padding-bottom:4rem; }
[data-testid="stSidebar"] { background: linear-gradient(160deg,#131728,#10111e 75%,#1c1527); border-right:1px solid rgba(255,255,255,.06); }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color:#c1bbd2; }
[data-testid="stSidebar"] [data-testid="stRadio"] label { background:rgba(255,255,255,.016); border-radius:12px; }
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover { background:rgba(255,82,125,.085); }
[data-testid="stSidebarNav"] { border-bottom:1px solid rgba(255,255,255,.06); }
header[data-testid="stHeader"] { height:2.2rem; }
[data-testid="stToolbar"] { right:1.4rem; }
h1, h2, h3 { letter-spacing:-.035em; color:#f8f5fc; }
h1 { font-size:clamp(2.15rem,4vw,3.45rem) !important; font-weight:800 !important; }
h2 { font-size:1.65rem !important; }
h3 { font-size:1.2rem !important; }
p { line-height:1.64; }
small, .stCaption { color:#9699b0 !important; }
hr { border-color:rgba(200,190,224,.09) !important; }
[data-testid="stMetric"] { background:linear-gradient(156deg, rgba(255,255,255,.058),rgba(255,255,255,.018));
 border:1px solid rgba(236,223,255,.075); border-radius:18px; padding:17px 20px; }
[data-testid="stMetricLabel"] { color:#a7aabd; }
[data-testid="stMetricValue"] { font-weight:800; letter-spacing:-.05em; }
[data-testid="stVerticalBlockBorderWrapper"] > div { border-color:rgba(234,222,255,.11) !important; border-radius:20px !important;
 background:linear-gradient(165deg,rgba(255,255,255,.037),rgba(255,255,255,.011)); }
button[kind="primary"], [data-testid="stFormSubmitButton"] button[kind="primary"] { background:linear-gradient(103deg,#ee396c,#ad3e8b) !important;
 color:#fff !important; border:none !important; box-shadow:0 9px 28px rgba(234,48,100,.16); font-weight:700; }
button { border-radius:12px !important; transition:transform .13s ease, filter .13s ease; }
button:hover { transform:translateY(-1px); filter:brightness(1.08); }
[data-testid="stTabs"] [role="tablist"] { gap:15px; }
[data-testid="stTabs"] button[role="tab"] { background:rgba(255,255,255,.03); border-radius:11px 11px 0 0!important; }
[data-testid="stDataFrame"] { border:1px solid rgba(255,255,255,.08); border-radius:13px; overflow:hidden; }
[data-testid="stExpander"] { background:rgba(255,255,255,.019); border-radius:14px; border:1px solid rgba(255,255,255,.064); }
[data-testid="stNotification"] { border-radius:14px; }
[data-testid="stProgressBar"] > div > div { background:linear-gradient(90deg,#ff527d,#9c79ff); }
.hero { position:relative; overflow:hidden; border-radius:26px; min-height:280px; padding:45px 49px; margin:7px 0 28px;
 background:radial-gradient(ellipse at 92% 32%,rgba(240,66,116,.31),transparent 35%),
 linear-gradient(115deg,#27162e 1%,#201b36 39%,#17263b 100%); border:1px solid rgba(241,191,234,.17);
 box-shadow:0 25px 70px rgba(0,0,0,.20); }
.hero:before { content:""; pointer-events:none; position:absolute; width:420px;height:420px;right:-65px;top:-70px;border:1px solid rgba(239,131,169,.24);border-radius:100%;box-shadow:0 0 0 47px rgba(221,103,140,.035),0 0 0 97px rgba(221,103,140,.025),0 0 0 149px rgba(221,103,140,.015); }
.hero:after { content:"✦";position:absolute;right:155px;top:50px;color:rgba(255,136,162,.49);font-size:54px;text-shadow:0 0 70px #ff456f; }
.hero-art {position:absolute;width:49%;max-width:610px;right:-6%;top:-25%;height:150%;object-fit:contain;opacity:.83;pointer-events:none;filter:drop-shadow(0 0 25px rgba(237,72,112,.1))}
.hero .eyebrow {font-size:11px;letter-spacing:.23em;font-weight:800;color:#ff9cbb;margin-bottom:17px;}
.hero h1{position:relative;z-index:1;max-width:850px;font-size:clamp(2.5rem,4.8vw,4.5rem)!important;line-height:1.07;margin:0 0 19px;letter-spacing:-.057em;color:#fff;}
.hero p{position:relative;z-index:1;color:#d8d0e6;max-width:720px;font-size:1.06rem;margin:0;line-height:1.7;}
.hero .hero-meta{position:relative;z-index:1;margin-top:28px;font-weight:600;font-size:12px;letter-spacing:.04em;color:#ecc6d9;}
.kicker {font-weight:800;letter-spacing:.17em;color:#fe8eae;text-transform:uppercase;font-size:11px;margin:12px 0 9px;}
.section-intro {color:#aeb2c8;font-size:1rem;margin-bottom:27px;max-width:850px;}
.glass { border-radius:18px;padding:24px 26px;border:1px solid rgba(229,219,255,.095);
 background:linear-gradient(160deg,rgba(255,255,255,.053),rgba(255,255,255,.017));margin:0 0 18px; }
.glass .n {color:#ff7697;font-size:11px;font-weight:900;letter-spacing:.15em;margin:0 0 10px;}
.glass h3{font-size:1.19rem;margin:0 0 8px;}
.glass p{color:#afb0c3;font-size:.91rem;margin:0;}
.teaching {margin:15px 0 27px;border:1px solid rgba(105,209,227,.22);border-left:3px solid #5dd2e2;border-radius:13px;
 padding:14px 20px;background:rgba(74,165,186,.068); color:#cfebef; font-size:.92rem;line-height:1.65;}
.warn {border-left-color:#ffad71;border-color:rgba(255,173,113,.24);background:rgba(231,146,90,.065);color:#f5ddc8;}
.micro {color:#9ea4bd;font-size:.81rem;line-height:1.6;}
.brand {margin:9px 0 13px;color:#fff;font-size:28px;font-weight:950;letter-spacing:-.06em;}
.brand b{color:#ff668e;}.brand-sub{letter-spacing:.19em;color:#8e90af;font-size:10px;font-weight:850;margin-bottom:26px;}
.status-dots {display:inline-block;width:7px;height:7px;border-radius:50%;background:#70d3b4;box-shadow:0 0 12px #70d3b4;margin-right:8px;}
.tagline {color:#9999b4;font-size:11px;line-height:1.7;}
.codechip {font-family:ui-monospace,monospace;color:#94d6e7;background:rgba(76,184,202,.08);border-radius:8px;padding:3px 7px;}
@media(max-width:700px){.hero{padding:27px 23px;min-height:240px}.hero:before{right:-240px}.hero:after{display:none}.hero-art{width:78%;right:-42%;opacity:.32}}
.exercise-tag {font-size:.73rem;font-weight:900;letter-spacing:.13em;color:#f98baa;margin-bottom:9px}
.answer-label {letter-spacing:.10em;font-size:.70rem;color:#66dce3;font-weight:900;margin-top:10px}
[data-testid="stPopover"] button {min-width:32px !important;width:37px !important;height:34px !important;
 padding:0!important;border:1px solid rgba(128,222,239,.3)!important;background:rgba(84,190,213,.07)!important;
 color:#8edee9!important;border-radius:50%!important;}
[data-testid="stTextArea"] textarea {background:rgba(12,17,32,.56);border-color:rgba(207,192,236,.12);
 border-radius:13px;font-size:.94rem;line-height:1.65;}
[data-testid="stTextArea"] textarea:focus {border-color:#9d83ff;box-shadow:0 0 0 1px rgba(157,131,255,.12)}
[data-testid="stPopoverBody"] {background:#191c2e!important;}
@media (prefers-reduced-motion: no-preference) {.hero {animation:hero-arrive .45s ease-out both;}
  @keyframes hero-arrive {from{opacity:.6;transform:translateY(7px)}to{opacity:1;transform:translateY(0)}}}

/* Parcours guidé : aucune barre de navigation latérale. */
[data-testid="stSidebar"], [data-testid="collapsedControl"], [data-testid="stSidebarCollapsedControl"] {display:none !important;}
[data-testid="stMainBlockContainer"]{max-width:1260px;padding-top:1.3rem;}
.hero-picture{height:auto;min-height:345px;background-size:cover;background-position:center center;display:flex;flex-direction:column;justify-content:center;padding:38px 49px;}
.hero-picture:before,.hero-picture:after{display:none;}
.hero-picture h1{font-size:clamp(2rem,4.5vw,3.35rem)!important;max-width:720px;line-height:1.16;}
.hero-picture p{max-width:650px;font-size:1.03rem;line-height:1.62;}
.lesson{padding:17px 21px;border-left:3px solid #ad9aff;border-radius:12px;margin:14px 0 19px;background:rgba(135,113,204,.07);color:#e0dcf1;line-height:1.7;}
.progress-intro{font-size:.79rem;letter-spacing:.07em;color:#b8b4c9;margin-bottom:6px;font-weight:700;}
@media(max-width:720px){.hero-picture{min-height:340px;padding:26px 24px;background-position:52% center;}.hero-picture h1{font-size:2.1rem!important;}.hero-picture p{font-size:.91rem;}}
</style>
"""


def inject_style():
    st.markdown(CSS, unsafe_allow_html=True)


def hero():
    """Illustration locale légère : aucun chargement d'image externe."""
    image_bytes = (Path(__file__).resolve().parent.parent / "assets" / "paysage_td.webp").read_bytes()
    art = base64.b64encode(image_bytes).decode("ascii")
    st.markdown("""<div class='hero hero-picture' style="background-image:
      linear-gradient(90deg,rgba(10,15,29,.94) 0%,rgba(10,15,29,.77) 37%,rgba(10,15,29,.06) 90%),
      url('data:image/webp;base64,""" + art + """');">
      <div class='eyebrow'>MASTER ESMIHA · TRAVAUX DIRIGÉS</div>
      <h1>TD - Introduction au<br><span style='color:#ff95b3'>Machine learning.</span></h1>
      <p>Une enquête fictive pour apprendre à entraîner des modèles, à évaluer leurs erreurs et à comprendre leurs prédictions. Tu pourras tester plusieurs méthodes, répondre aux questions et garder ton travail.</p>
      <div class='hero-meta'>CLASSIFICATION SUPERVISÉE &nbsp;·&nbsp; QUENTIN LAMBOLEY</div>
    </div>""", unsafe_allow_html=True)


def header(phase: str, title: str, introduction: str):
    st.markdown(f"<div class='kicker'>{phase}</div>", unsafe_allow_html=True)
    st.title(title)
    st.markdown(f"<div class='section-intro'>{introduction}</div>", unsafe_allow_html=True)



def vampire_avatar(humans: int, vampires: int, proximity: int):
    """Affiche le portrait cinématographique et le suivi du regard dans un composant autonome."""
    assets = Path(__file__).resolve().parent.parent / "assets"
    template = (assets / "vampire_scene.html").read_text(encoding="utf-8")
    portrait_data = base64.b64encode((assets / "vampire_cinematic.webp").read_bytes()).decode("ascii")
    html = (template.replace("__PORTRAIT_DATA__", portrait_data)
                    .replace("__HUMANS__", str(max(int(humans), 0)))
                    .replace("__VAMPIRES__", str(max(int(vampires), 0)))
                    .replace("__PROXIMITY__", str(max(0, min(100, int(proximity))))))
    components.html(html, height=460, scrolling=False)


def hint(content: str, warning: bool = False):
    css = "teaching warn" if warning else "teaching"
    st.markdown(f"<div class='{css}'>{content}</div>", unsafe_allow_html=True)


def card(number: str, title: str, text: str):
    st.markdown(f"<div class='glass'><div class='n'>{number}</div><h3>{title}</h3><p>{text}</p></div>",
                unsafe_allow_html=True)
