import pandas as pd
import streamlit as st
from utils.data_loader import load_creators, load_ideas, minmax
from utils.ui import setup, fig_ax, show, source_note, PALETTE

setup("Creator Intelligence", "📱")
st.write("Twelve content types, ten well-known creators in each, and which categories perform best right now.")

cr = load_creators()
ideas = load_ideas()

# Category scoreboard (average of short and long ideas for that category)
cat = ideas.groupby("category").agg(trend=("trend", "mean"), growth=("growth", "mean"),
                                    monetization=("monetization", "mean"), competition=("competition", "mean")).reset_index()
cat["performance"] = (0.35 * cat["trend"] + 0.25 * cat["growth"] + 0.25 * cat["monetization"] + 0.15 * (11 - cat["competition"])) * 10
cat = cat.merge(cr.groupby("category").agg(creators=("name", "count"), median_followers_m=("followers_m_approx", "median")).reset_index(), on="category")
cat = cat.sort_values("performance", ascending=False)

tab1, tab2, tab3 = st.tabs(["Top-performing categories", "Creators by category", "Short vs long form"])

with tab1:
    st.markdown("**Performance score** = 35% trend + 25% growth + 25% earning potential + 15% low competition (0-100).")
    fig, ax = fig_ax(8, 5)
    d = cat.iloc[::-1]
    colors = ["#34D399" if p >= 65 else "#FBBF24" if p >= 50 else "#F87171" for p in d["performance"]]
    ax.barh(d["category"], d["performance"], color=colors)
    ax.set_xlabel("Performance score (0-100)")
    show(fig)
    t = cat[["category", "trend", "growth", "monetization", "competition", "performance", "creators", "median_followers_m"]].round(1)
    t.columns = ["Category", "Trend", "Growth", "Earning potential", "Competition", "Performance", "Creators listed", "Median followers (M)"]
    st.dataframe(t, use_container_width=True, hide_index=True)
    st.caption("Trend, growth, earning potential and competition are 1-10 scores (see DATA_SOURCES.md). Competition: higher means harder to stand out.")

with tab2:
    sel = st.selectbox("Choose a content type", sorted(cr["category"].unique()))
    d = cr[cr["category"] == sel].sort_values("followers_m_approx", ascending=False)
    t = d[["name", "platform", "country", "followers_m_approx"]].copy()
    t.columns = ["Creator", "Main platform", "Country", "Followers / subscribers (millions, approx)"]
    st.dataframe(t, use_container_width=True, hide_index=True)
    fig, ax = fig_ax(8, 4.5)
    dd = d.iloc[::-1]
    ax.barh(dd["name"], dd["followers_m_approx"], color=PALETTE["main"])
    ax.set_xlabel("Followers / subscribers (millions, approx)")
    ax.set_title(f"Top {sel} creators")
    show(fig)
    st.caption("Follower counts are rounded public numbers and change daily. Refresh them with refresh_creators.py (YouTube Data API).")

with tab3:
    mode_sel = ideas.groupby("mode")[["trend", "growth", "competition", "monetization"]].mean().round(2)
    st.dataframe(mode_sel, use_container_width=True)
    pv = ideas.pivot_table(index="category", columns="mode", values="trend")
    fig, ax = fig_ax(8, 5)
    pv = pv.sort_values("Short-form")
    y = range(len(pv))
    ax.barh([i - 0.2 for i in y], pv["Short-form"], height=0.4, label="Short-form", color="#F472B6")
    ax.barh([i + 0.2 for i in y], pv["Long-form"], height=0.4, label="Long-form", color="#8B5CF6")
    ax.set_yticks(list(y)); ax.set_yticklabels(pv.index)
    ax.set_xlabel("Trend (1-10)"); ax.legend()
    ax.set_title("Where short-form beats long-form")
    show(fig)
    st.write("Short-form is stronger for comedy, vlogs, food and quick tips, while long-form is stronger for education, "
             "podcasts and tech reviews because viewers stay longer.")

source_note("YouTube and Instagram channel pages (public follower counts, rounded), Spotify Wrapped India 2025 (podcast ranking). "
            "Category scores are 1-10 analyst scores that can be blended with Google Trends via refresh_trends.py.")
