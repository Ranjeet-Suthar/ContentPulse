"""Shared look and feel (dark theme): CSS, banners, cards and chart styling."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from cycler import cycler
import streamlit as st

PALETTE = {"Hollywood": "#60A5FA", "Bollywood": "#FBBF24", "South": "#2DD4BF",
           "main": "#8B5CF6", "accent": "#F472B6", "grey": "#94A3B8"}
LEVEL_COLORS = {"Very High": "#34D399", "High": "#A3E635", "Medium": "#FBBF24", "Low": "#F87171"}
SEQ = ["#8B5CF6", "#F472B6", "#FBBF24", "#2DD4BF", "#60A5FA", "#F87171", "#A3E635", "#22D3EE"]

# Charts: transparent background, light text, neon colours
plt.rcParams.update({
    "figure.facecolor": "none", "axes.facecolor": "none", "savefig.facecolor": "none", "savefig.transparent": True,
    "text.color": "#E5E7EB", "axes.labelcolor": "#E5E7EB", "axes.edgecolor": "#4B5563", "axes.titlecolor": "#FFFFFF",
    "xtick.color": "#CBD5E1", "ytick.color": "#CBD5E1", "grid.color": "#2A2A3A",
    "legend.facecolor": "#11111A", "legend.edgecolor": "#2A2A3A", "axes.titleweight": "bold",
    "axes.prop_cycle": cycler(color=SEQ),
})

CSS = """
<style>
.block-container {padding-top: 1.4rem; max-width: 1250px;}
footer {visibility: hidden;}
[data-testid="stSidebar"] {background: #07070C; border-right: 1px solid #1F1F2E;}
.hero {background: linear-gradient(120deg, #7C3AED 0%, #DB2777 55%, #F59E0B 100%);
       padding: 1.4rem 2rem; border-radius: 18px; margin-bottom: 1.2rem;
       box-shadow: 0 0 32px rgba(139,92,246,.35);}
.hero-big {padding: 2.6rem 2.4rem;}
.hero-title {font-size: 2rem; font-weight: 800; color: #fff; line-height: 1.2;}
.hero-big .hero-title {font-size: 3rem;}
.hero-sub {font-size: 1.05rem; color: #fff; opacity: .95; margin-top: .4rem;}
.card {background: #11111A; border: 1px solid #2A2A3A; border-radius: 16px; padding: 1.1rem 1.3rem;
       height: 100%; transition: border-color .2s, box-shadow .2s;}
.card:hover {border-color: #8B5CF6; box-shadow: 0 0 18px rgba(139,92,246,.25);}
.card h4 {margin: 0 0 .4rem 0; color: #C4B5FD; font-size: 1.1rem;}
.card p {margin: 0; color: #D1D5DB; font-size: .95rem;}
.pick {background: linear-gradient(135deg, #1B1033, #2A0F25); border: 1px solid #6D28D9;
       border-radius: 18px; padding: 1.3rem 1.6rem; margin: .5rem 0 1rem 0; box-shadow: 0 0 24px rgba(139,92,246,.3);}
.pick-label {font-size: .8rem; letter-spacing: .1em; color: #A78BFA; font-weight: 700;}
.pick-name {font-size: 2rem; font-weight: 800; color: #FFFFFF;}
.pick-score {font-size: 1.1rem; color: #F472B6; font-weight: 700;}
.step {display: inline-block; width: 28px; height: 28px; line-height: 28px; text-align: center; border-radius: 50%;
       background: linear-gradient(135deg, #8B5CF6, #F472B6); color: #fff; font-weight: 700; margin-right: 8px;}
[data-testid="stMetric"] {background: #11111A; border: 1px solid #2A2A3A; border-radius: 14px; padding: .8rem 1rem;}
[data-testid="stMetricLabel"] {color: #9CA3AF;}
[data-testid="stMetricValue"] {color: #FFFFFF;}
[data-testid="stVerticalBlockBorderWrapper"] {border-radius: 14px;}
.stTabs [data-baseweb="tab-list"] {gap: 6px;}
.stTabs [data-baseweb="tab"] {background: #11111A; border-radius: 10px 10px 0 0; padding: 8px 16px; color: #CBD5E1;}
.stTabs [aria-selected="true"] {background: linear-gradient(120deg, #7C3AED, #DB2777); color: #fff !important;}
.stButton > button[kind="primary"] {background: linear-gradient(120deg, #7C3AED, #DB2777); border: none; color: #fff;
       font-weight: 700; border-radius: 12px;}
h2, h3 {border-left: 5px solid #8B5CF6; padding-left: .6rem;}
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def sidebar_brand():
    st.sidebar.markdown("### 📈 ContentPulse")
    st.sidebar.caption("Content Trend & Audience Intelligence")


def hero(title: str, subtitle: str = "", big: bool = False):
    cls = "hero hero-big" if big else "hero"
    sub = f'<div class="hero-sub">{subtitle}</div>' if subtitle else ""
    st.markdown(f'<div class="{cls}"><div class="hero-title">{title}</div>{sub}</div>', unsafe_allow_html=True)


def card(title: str, body: str):
    st.markdown(f'<div class="card"><h4>{title}</h4><p>{body}</p></div>', unsafe_allow_html=True)


def step(n: int, text: str):
    st.markdown(f'<span class="step">{n}</span> **{text}**', unsafe_allow_html=True)


def setup(title: str, icon: str):
    st.set_page_config(page_title=f"ContentPulse | {title}", page_icon=icon, layout="wide")
    inject_css()
    sidebar_brand()
    hero(f"{icon} {title}")


def source_note(text: str):
    st.caption("Sources: " + text)


def fig_ax(w=7, h=4):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.spines[["top", "right"]].set_visible(False)
    return fig, ax


def show(fig):
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def level_badge(level: str) -> str:
    return {"Very High": "🟢 Very High", "High": "🟡 High", "Medium": "🟠 Medium", "Low": "🔴 Low"}.get(level, level)
