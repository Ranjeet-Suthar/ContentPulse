import pandas as pd
import streamlit as st
from utils.recommender import get_options
from utils.ui import setup, fig_ax, show, source_note

setup("Future Opportunities", "🔮")
st.write("Which genres and content types have the best room to grow. High growth and low competition is the sweet spot.")

st.markdown("**Opportunity score** = 35% growth + 25% trend + 20% earning potential + 20% low competition (0-100).")


def add_score(d: pd.DataFrame) -> pd.DataFrame:
    d = d.copy()
    d["opportunity"] = 10 * (0.35 * d["growth"] + 0.25 * d["trend"] + 0.20 * d["monetization"] + 0.20 * (11 - d["competition"]))
    d["outlook"] = pd.cut(d["growth"], [0, 4.99, 6.99, 11], labels=["Slowing", "Steady", "Rising"])
    return d.sort_values("opportunity", ascending=False)


def block(name: str):
    d = add_score(get_options(name))
    st.markdown("**Top opportunities**")
    t = d[["option", "opportunity", "trend", "growth", "competition", "outlook"]].round(1)
    t.columns = ["Option", "Opportunity", "Trend", "Growth", "Competition", "Outlook"]
    st.dataframe(t, use_container_width=True, hide_index=True)

    c1, c2 = st.columns(2)
    with c1:
        top = d.head(8).iloc[::-1]
        fig, ax = fig_ax(5, 4)
        ax.barh(top["option"], top["opportunity"], color="#8B5CF6")
        ax.set_xlabel("Opportunity score"); ax.set_title("Top 8")
        show(fig)
    with c2:
        fig, ax = fig_ax(5, 4)
        ax.scatter(d["competition"], d["growth"], s=60, color="#F472B6")
        for _, r in d.iterrows():
            ax.annotate(r["option"], (r["competition"], r["growth"]), fontsize=6, xytext=(3, 3), textcoords="offset points")
        ax.axhline(6.5, color="grey", ls="--", lw=0.8); ax.axvline(6.5, color="grey", ls="--", lw=0.8)
        ax.set_xlabel("Competition (higher = harder)"); ax.set_ylabel("Growth")
        ax.set_title("Top-left = high growth, low competition")
        show(fig)
    best = d.iloc[0]
    st.success(f"Biggest opportunity: **{best['option']}** (score {best['opportunity']:.0f}, growth {best['growth']:.1f}/10, competition {best['competition']:.0f}/10).")
    low = d.tail(3)["option"].tolist()
    st.caption("Lowest opportunity right now: " + ", ".join(low) + ".")


tabs = st.tabs(["Short-form", "Long-form", "Movie genres", "Music styles"])
for tab, name in zip(tabs, ["Short-form content", "Long-form content", "Movie", "Music"]):
    with tab:
        block(name)

source_note("Movie and music trend and growth are measured from box office and chart data; creator category scores are analyst scores "
            "that can be blended with Google Trends (refresh_trends.py). This is guidance, not a guarantee.")
