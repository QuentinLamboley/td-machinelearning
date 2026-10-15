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
    total = max(humans + vampires, 1)
    html = f"""
    <div id="vampire-scene" style="height:430px;position:relative;overflow:hidden;border-radius:24px;border:1px solid rgba(255,255,255,.08);background:radial-gradient(circle at 20% 18%, rgba(143,113,255,.18), transparent 28%),linear-gradient(180deg,#141a2e 0%,#101625 52%,#0a0e1a 100%);box-shadow:0 25px 60px rgba(0,0,0,.28);">
      <style>
        #vampire-scene * {{ box-sizing:border-box; }}
        #vampire-scene .moon {{ position:absolute; right:28px; top:26px; width:84px; height:84px; border-radius:50%; background:radial-gradient(circle at 35% 30%, #fff 0%, #efeaff 38%, #b8a6ff 72%, #7d66ff 100%); box-shadow:0 0 40px rgba(185,166,255,.32); }}
        #vampire-scene .mist {{ position:absolute; inset:auto 0 0 0; height:150px; background:linear-gradient(180deg, rgba(143,113,255,0), rgba(143,113,255,.03) 24%, rgba(255,255,255,.08) 100%); filter:blur(10px); }}
        #vampire-scene .caption {{ position:absolute; left:24px; top:22px; color:#f5f2ff; z-index:4; }}
        #vampire-scene .caption .over {{ font-size:11px; letter-spacing:.18em; font-weight:800; color:#ff97ba; margin-bottom:8px; }}
        #vampire-scene .caption .title {{ font-size:1.15rem; font-weight:800; line-height:1.2; max-width:220px; }}
        #vampire-scene .caption .sub {{ margin-top:7px; font-size:.84rem; color:#c9c3dc; max-width:245px; line-height:1.5; }}
        #vampire-scene .bat {{ position:absolute; width:34px; height:16px; border-top:3px solid rgba(255,255,255,.7); border-radius:60% 60% 0 0; opacity:.55; }}
        #vampire-scene .bat:before, #vampire-scene .bat:after {{ content:''; position:absolute; top:-3px; width:17px; height:16px; border-top:3px solid rgba(255,255,255,.7); border-radius:60% 60% 0 0; }}
        #vampire-scene .bat:before {{ left:-11px; transform:rotate(-18deg); }}
        #vampire-scene .bat:after {{ right:-11px; transform:rotate(18deg); }}
        #vampire-scene .scene-floor {{ position:absolute; left:0; right:0; bottom:0; height:82px; background:linear-gradient(180deg, rgba(14,18,33,0), rgba(7,9,18,.98)); }}
        #vampire-scene .vampire-wrap {{ position:absolute; left:50%; top:52%; width:230px; height:285px; transform:translate(-50%,-50%); perspective:900px; z-index:3; }}
        #vampire-scene .vampire {{ position:absolute; inset:0; transform-style:preserve-3d; transition:transform .16s ease-out; }}
        #vampire-scene .cape-back {{ position:absolute; left:22px; top:80px; width:190px; height:184px; border-radius:54% 54% 24% 24%; background:linear-gradient(180deg,#3b1833 0%, #2a1026 38%, #120712 100%); box-shadow:inset 0 0 0 1px rgba(255,255,255,.03); }}
        #vampire-scene .cape-back:before {{ content:''; position:absolute; inset:10px 20px 16px; border-radius:50% 50% 28% 28%; background:linear-gradient(180deg, rgba(255,133,173,.26), rgba(255,133,173,0) 38%); }}
        #vampire-scene .head {{ position:absolute; left:66px; top:30px; width:98px; height:116px; border-radius:48% 48% 46% 46%; background:linear-gradient(180deg,#fbf4ff 0%,#eddcf7 62%,#d6c1ea 100%); box-shadow:0 15px 24px rgba(0,0,0,.18); }}
        #vampire-scene .hair {{ position:absolute; left:57px; top:17px; width:117px; height:104px; border-radius:54% 54% 42% 42%; background:linear-gradient(180deg,#10131d 0%,#191d2a 100%); }}
        #vampire-scene .hair:before, #vampire-scene .hair:after {{ content:''; position:absolute; top:8px; width:0; height:0; border-left:16px solid transparent; border-right:16px solid transparent; border-bottom:28px solid #121621; }}
        #vampire-scene .hair:before {{ left:6px; transform:rotate(-20deg); }}
        #vampire-scene .hair:after {{ right:6px; transform:rotate(20deg); }}
        #vampire-scene .hairline {{ position:absolute; left:77px; top:38px; width:76px; height:46px; background:#131722; clip-path:polygon(0 0,100% 0,78% 52%,50% 100%,22% 52%); }}
        #vampire-scene .ear {{ position:absolute; top:68px; width:18px; height:28px; background:#ead5f2; }}
        #vampire-scene .ear.left {{ left:56px; clip-path:polygon(100% 0,0 50%,100% 100%); }}
        #vampire-scene .ear.right {{ left:156px; clip-path:polygon(0 0,100% 50%,0 100%); }}
        #vampire-scene .brow {{ position:absolute; top:74px; width:20px; height:4px; background:#1a1d2a; border-radius:999px; }}
        #vampire-scene .brow.left {{ left:85px; transform:rotate(-10deg); }}
        #vampire-scene .brow.right {{ left:125px; transform:rotate(10deg); }}
        #vampire-scene .eye {{ position:absolute; top:80px; width:22px; height:15px; background:#fff; border-radius:999px; overflow:hidden; box-shadow:0 0 0 1px rgba(23,27,41,.14) inset; }}
        #vampire-scene .eye.left {{ left:82px; }}
        #vampire-scene .eye.right {{ left:126px; }}
        #vampire-scene .pupil {{ position:absolute; left:7px; top:3px; width:8px; height:8px; border-radius:50%; background:radial-gradient(circle at 35% 35%, #ffadc6 0%, #cf456e 38%, #2b1a29 100%); transition:transform .06s linear; }}
        #vampire-scene .nose {{ position:absolute; left:109px; top:89px; width:11px; height:24px; border-left:2px solid rgba(120,88,136,.45); border-bottom:2px solid rgba(120,88,136,.28); border-radius:0 0 0 8px; }}
        #vampire-scene .mouth {{ position:absolute; left:92px; top:112px; width:44px; height:18px; border-bottom:3px solid #7f314d; border-radius:0 0 50px 50px; }}
        #vampire-scene .fang {{ position:absolute; top:127px; width:5px; height:16px; background:linear-gradient(180deg,#fff 0%,#f1ebf8 100%); clip-path:polygon(0 0,100% 0,50% 100%); }}
        #vampire-scene .fang.left {{ left:102px; }}
        #vampire-scene .fang.right {{ left:122px; }}
        #vampire-scene .neck {{ position:absolute; left:101px; top:136px; width:28px; height:24px; background:linear-gradient(180deg,#e7d4f0 0%,#d9c4ea 100%); border-radius:0 0 10px 10px; }}
        #vampire-scene .body {{ position:absolute; left:61px; top:146px; width:108px; height:112px; border-radius:36px 36px 28px 28px; background:linear-gradient(180deg,#202636 0%,#111624 100%); box-shadow:0 18px 26px rgba(0,0,0,.18); overflow:hidden; }}
        #vampire-scene .shirt {{ position:absolute; left:25px; top:18px; width:58px; height:78px; background:linear-gradient(180deg,#fbf8ff 0%,#e9e1f3 100%); clip-path:polygon(50% 0,100% 24%,82% 100%,18% 100%,0 24%); }}
        #vampire-scene .medallion {{ position:absolute; left:45px; top:26px; width:18px; height:18px; border-radius:50%; background:radial-gradient(circle at 35% 30%, #ffe5a0 0%, #f0bf58 55%, #8d6521 100%); box-shadow:0 0 10px rgba(240,191,88,.28); }}
        #vampire-scene .lapel {{ position:absolute; top:10px; width:34px; height:50px; background:linear-gradient(180deg,#65162d 0%,#320b18 100%); }}
        #vampire-scene .lapel.left {{ left:12px; clip-path:polygon(0 0,100% 0,76% 100%,0 70%); }}
        #vampire-scene .lapel.right {{ right:12px; clip-path:polygon(0 0,100% 0,100% 70%,24% 100%); }}
        #vampire-scene .stats {{ position:absolute; left:24px; right:24px; bottom:18px; display:grid; grid-template-columns:repeat(3,1fr); gap:10px; z-index:4; }}
        #vampire-scene .pill {{ background:rgba(255,255,255,.06); border:1px solid rgba(255,255,255,.08); border-radius:16px; padding:11px 12px; backdrop-filter:blur(6px); }}
        #vampire-scene .pill b {{ display:block; color:#fff; font-size:1.03rem; }}
        #vampire-scene .pill span {{ display:block; margin-top:4px; color:#bdb7cf; font-size:.76rem; line-height:1.35; }}
      </style>
      <div class="moon"></div>
      <div class="bat" style="left:236px;top:46px;transform:scale(.8)"></div>
      <div class="bat" style="left:274px;top:88px;transform:scale(.56)"></div>
      <div class="caption">
        <div class="over">JEU DE DONNÉES</div>
        <div class="title">Population d'humains et de vampires</div>
        <div class="sub">Un simple décor pour une vraie démarche d'analyse : observer, entraîner, comparer, puis interpréter.</div>
      </div>
      <div class="vampire-wrap">
        <div class="vampire" id="vampire-card">
          <div class="cape-back"></div>
          <div class="ear left"></div><div class="ear right"></div>
          <div class="hair"></div>
          <div class="head"></div>
          <div class="hairline"></div>
          <div class="brow left"></div><div class="brow right"></div>
          <div class="eye left"><div class="pupil"></div></div>
          <div class="eye right"><div class="pupil"></div></div>
          <div class="nose"></div><div class="mouth"></div>
          <div class="fang left"></div><div class="fang right"></div>
          <div class="neck"></div>
          <div class="body">
            <div class="shirt"></div>
            <div class="lapel left"></div><div class="lapel right"></div>
            <div class="medallion"></div>
          </div>
        </div>
      </div>
      <div class="mist"></div>
      <div class="scene-floor"></div>
      <div class="stats">
        <div class="pill"><b>{humans:,}</b><span>Humains</span></div>
        <div class="pill"><b>{vampires:,}</b><span>Vampires</span></div>
        <div class="pill"><b>{proximity}%</b><span>Proximité des profils</span></div>
      </div>
    </div>
    <script>
      (function() {{
        const root = document.getElementById('vampire-scene');
        if (!root) return;
        const card = root.querySelector('#vampire-card');
        const pupils = root.querySelectorAll('.pupil');
        const move = (event) => {{
          const rect = root.getBoundingClientRect();
          const x = (event.clientX - rect.left) / rect.width;
          const y = (event.clientY - rect.top) / rect.height;
          const rx = (0.5 - y) * 10;
          const ry = (x - 0.5) * 16;
          card.style.transform = `rotateX(${rx}deg) rotateY(${ry}deg)`;
          const px = Math.max(-4, Math.min(4, (x - 0.5) * 10));
          const py = Math.max(-3, Math.min(3, (y - 0.5) * 8));
          pupils.forEach((p) => p.style.transform = `translate(${px}px, ${py}px)`);
        }};
        const reset = () => {{
          card.style.transform = 'rotateX(0deg) rotateY(0deg)';
          pupils.forEach((p) => p.style.transform = 'translate(0px,0px)');
        }};
        root.addEventListener('mousemove', move);
        root.addEventListener('mouseleave', reset);
      }})();
    </script>
    """
    components.html(html, height=430)

def hint(content: str, warning: bool = False):
    css = "teaching warn" if warning else "teaching"
    st.markdown(f"<div class='{css}'>{content}</div>", unsafe_allow_html=True)


def card(number: str, title: str, text: str):
    st.markdown(f"<div class='glass'><div class='n'>{number}</div><h3>{title}</h3><p>{text}</p></div>",
                unsafe_allow_html=True)
