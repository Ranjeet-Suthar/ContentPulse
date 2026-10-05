import pandas as pd
import streamlit as st
from utils.data_loader import load_movies, load_movie_genres
from utils.ui import setup, fig_ax, show, source_note, PALETTE, level_badge

setup("Movie Intelligence", "🎬")
st.write("Collections, ratings and genre trends for Hollywood, Bollywood and South Indian films.")

df = load_movies()
c1, c2 = st.columns([2, 1])
inds = c1.multiselect("Industry", ["Hollywood", "Bollywood", "South"], default=["Hollywood", "Bollywood", "South"])
ymin, ymax = int(df.year.min()), int(df.year.max())
yrs = c2.slider("Release year", ymin, ymax, (2022, ymax))
f = df[df.industry.isin(inds) & df.year.between(*yrs)]
if f.empty:
    st.warning("No films match these filters.")
    st.stop()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Films shown", len(f))
k2.metric("Biggest gross", f.loc[f.gross_usd_m.idxmax(), "title"], f"Rs {f.gross_cr_inr.max():,.0f} Cr")
k3.metric("Average rating", f"{f.rating_used.mean():.1f}/10")
k4.metric("Top trending", f.iloc[0]["title"])

tab1, tab2, tab3, tab4 = st.tabs(["Top trending films", "Industry comparison", "Genre trends", "Rating vs earnings"])

with tab1:
    st.markdown("**Trend score** = 40% earnings (log scale) + 25% rating + 35% how recent the film is. 0 to 100.")
    show_df = f[["title", "industry", "language", "year", "genre", "gross_cr_inr", "imdb_rating", "trend_score", "trend_level"]].copy()
    show_df["imdb_rating"] = show_df["imdb_rating"].apply(lambda x: "n/a" if pd.isna(x) else f"{x:.1f}")
    show_df["trend_level"] = show_df["trend_level"].apply(level_badge)
    show_df.columns = ["Film", "Industry", "Language", "Year", "Genre", "Worldwide gross (Rs Cr)", "IMDb (approx)", "Trend score", "Trend level"]
    st.dataframe(show_df.round(1), use_container_width=True, hide_index=True)

    top = f.head(12).iloc[::-1]
    fig, ax = fig_ax(8, 5)
    ax.barh(top["title"], top["trend_score"], color=[PALETTE[i] for i in top["industry"]])
    ax.set_xlabel("Trend score (0-100)")
    ax.set_title("Top trending films in the selected range")
    show(fig)
    st.caption("Blue = Hollywood, Orange = Bollywood, Green = South.")

with tab2:
    g = f.groupby("industry").agg(Films=("title", "count"), Avg_gross_Cr=("gross_cr_inr", "mean"),
                                  Median_gross_Cr=("gross_cr_inr", "median"), Avg_rating=("rating_used", "mean"),
                                  Total_gross_Cr=("gross_cr_inr", "sum")).round(1)
    st.dataframe(g, use_container_width=True)
    fig, ax = fig_ax(6, 3.5)
    ax.bar(g.index, g["Median_gross_Cr"], color=[PALETTE[i] for i in g.index])
    ax.set_ylabel("Median worldwide gross (Rs Cr)")
    ax.set_title("Typical earnings by industry")
    show(fig)

with tab3:
    gg = load_movie_genres().sort_values("trend", ascending=True)
    fig, ax = fig_ax(8, 5.5)
    colors = ["#34D399" if t >= 7 else "#FBBF24" if t >= 4 else "#F87171" for t in gg["trend"]]
    ax.barh(gg["genre"], gg["trend"], color=colors)
    ax.set_xlabel("Genre trend (1-10)")
    ax.set_title("Which genres are trending (all films in dataset)")
    show(fig)
    st.caption("Green = strong, orange = medium, red = low. Trend is the average film trend score of that genre, scaled 1 to 10.")
    t = gg.sort_values("trend", ascending=False)[["genre", "films", "avg_gross", "avg_rating", "trend", "growth"]].copy()
    t["avg_gross"] = t["avg_gross"] * 8.5
    t.columns = ["Genre", "Films", "Avg gross (Rs Cr)", "Avg rating", "Trend (1-10)", "Growth (1-10)"]
    st.dataframe(t.round(1), use_container_width=True, hide_index=True)
    st.caption("Genres with only 1-3 films are less reliable; add more films to data/movies.csv to improve this.")

with tab4:
    fig, ax = fig_ax(7, 4.5)
    for ind, d in f.groupby("industry"):
        ax.scatter(d["rating_used"], d["gross_cr_inr"], label=ind, color=PALETTE[ind], s=60, alpha=0.8)
    ax.set_yscale("log")
    ax.set_xlabel("IMDb rating (approx; missing values filled with industry median)")
    ax.set_ylabel("Worldwide gross (Rs Cr, log scale)")
    ax.legend()
    ax.set_title("Do higher-rated films earn more?")
    show(fig)
    st.write("Rating and earnings are only loosely related: mass-appeal films earn a lot even with mid ratings, "
             "while highly rated small films (like 12th Fail) earn less. The Audience Analytics page measures this with a correlation.")

source_note("Box Office Mojo / The Numbers (Hollywood), Bollywood Hungama, Sacnilk, Koimoi, FilmiBeat (Indian films), IMDb (ratings, approximate). "
            "2026 films are snapshots from their release run and may still be earning. Indian earnings converted at 1 USD = Rs 85.")
