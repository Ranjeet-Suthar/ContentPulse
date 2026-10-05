import streamlit as st
from utils.data_loader import load_movies, load_creators, load_music_songs, load_ideas, load_music_genres
from utils.ui import inject_css, sidebar_brand, hero, card

st.set_page_config(page_title="ContentPulse", page_icon="📈", layout="wide")
inject_css()
sidebar_brand()

hero("📈 ContentPulse", "Content Trend & Audience Intelligence Platform", big=True)
st.write("Know what your audience wants **before** you spend your time and money creating it.")

st.markdown("### What is ContentPulse?")
st.write(
    "ContentPulse collects real, public numbers on movies, creators and music, turns them into simple "
    "charts and trend scores, and then suggests what you should create next, with reasons."
)

c1, c2, c3 = st.columns(3)
with c1:
    card("📱 Short and long-form creators", "See which content types are growing, who the top creators are, and which idea suits your budget, team and place.")
with c2:
    card("🎬 Movie production houses", "Compare Hollywood, Bollywood and South cinema by earnings, ratings and genre, and see which genres are rising.")
with c3:
    card("🎵 Music industry", "See which songs, artists and music styles are trending in India and how long hits stay on the charts.")

st.markdown("### What is inside")
m, cr, s = load_movies(), load_creators(), load_music_songs()
k1, k2, k3, k4 = st.columns(4)
k1.metric("Movies analysed", len(m))
k2.metric("Creators listed", len(cr))
k3.metric("Content categories", cr["category"].nunique())
k4.metric("Chart songs", len(s))

pages = [
    ("pages/1_Movie_Intelligence.py", "Movie Intelligence", "🎬", "Collections, ratings, genre and a trend score for Hollywood, Bollywood and South films"),
    ("pages/2_Creator_Intelligence.py", "Creator Intelligence", "📱", "12 content types with 10 well-known creators each, and the best-performing categories"),
    ("pages/3_Music_Intelligence.py", "Music Intelligence", "🎵", "Spotify India chart, top artists, genre share and chart longevity"),
    ("pages/4_Audience_Analytics.py", "Audience Analytics", "📊", "Mean, median, standard deviation, histograms, box plots, correlation, regression"),
    ("pages/5_What_Should_I_Create.py", "What Should I Create?", "💡", "Pick short, long, movie or music, then get a trending idea and the reasons"),
    ("pages/6_Future_Opportunities.py", "Future Opportunities", "🔮", "Rising, high-opportunity genres and categories"),
]
for row in (pages[:3], pages[3:]):
    cols = st.columns(3)
    for col, (path, label, icon, desc) in zip(cols, row):
        with col:
            with st.container(border=True):
                st.page_link(path, label=label, icon=icon)
                st.caption(desc)

st.markdown("### How the data works")
st.info(
    "Numbers are collected from public sources (Box Office Mojo, Bollywood Hungama, Sacnilk, Spotify Charts, "
    "Billboard India, Spotify Wrapped, IMDb) and saved as CSV files in the `data` folder. They are a "
    "**snapshot**, not a live feed. Trend scores are calculated from these numbers with simple, visible "
    "formulas, and genres or categories that are not trending show **low**. "
    "Where a value could not be confirmed (for example some IMDb ratings), it is left blank and handled "
    "in the Audience Analytics page. See `DATA_SOURCES.md` for details."
)
st.caption("Built with Python, Pandas, NumPy, Matplotlib, SciPy, Scikit-learn and Streamlit. Use the sidebar to open each page.")
