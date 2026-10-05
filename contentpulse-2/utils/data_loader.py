"""Loads and prepares all ContentPulse data.

Syllabus link: Module 1 (Pandas, CSV import) and Module 4 (missing values,
duplicates, normalisation).
"""
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st

DATA = Path(__file__).resolve().parent.parent / "data"
CURRENT_YEAR = 2026
USD_TO_INR = 85.0          # used only for display: 1 USD = 85 INR
ENVIRONMENTS = ["Studio / Set", "Home", "Private room", "Public place", "Mall", "Metro", "Bus",
                "Railway station", "Airport", "Cafe / Restaurant", "Outdoor / Nature", "College campus"]


def minmax(s: pd.Series) -> pd.Series:
    """Min-max normalisation to the 0-1 range."""
    s = s.astype(float)
    if s.max() == s.min():
        return s * 0.0
    return (s - s.min()) / (s.max() - s.min())


def level_from_score(score: float) -> str:
    if score >= 75:
        return "Very High"
    if score >= 55:
        return "High"
    if score >= 35:
        return "Medium"
    return "Low"


@st.cache_data
def load_raw_movies() -> pd.DataFrame:
    return pd.read_csv(DATA / "movies.csv")


@st.cache_data
def load_movies() -> pd.DataFrame:
    """Clean movies, fill missing ratings, build a transparent trend score."""
    df = load_raw_movies().drop_duplicates(subset=["title"]).copy()
    df["rating_missing"] = df["imdb_rating"].isna()
    industry_median = df.groupby("industry")["imdb_rating"].transform("median")
    df["rating_used"] = df["imdb_rating"].fillna(industry_median).fillna(df["imdb_rating"].median())
    df["gross_cr_inr"] = df["gross_usd_m"] * USD_TO_INR / 10          # 1 crore = 10 million
    df["log_gross"] = np.log10(df["gross_usd_m"])
    df["recency"] = (1 - (CURRENT_YEAR - df["year"]) / 8).clip(0, 1)  # 2026 -> 1.0, 2018 or older -> 0
    df["trend_score"] = 100 * (0.40 * minmax(df["log_gross"]) + 0.25 * minmax(df["rating_used"])
                               + 0.35 * df["recency"])
    df["trend_level"] = df["trend_score"].apply(level_from_score)
    return df.sort_values("trend_score", ascending=False).reset_index(drop=True)


@st.cache_data
def load_creators() -> pd.DataFrame:
    df = pd.read_csv(DATA / "creators.csv").drop_duplicates(subset=["name"]).copy()
    df["log_followers"] = np.log10(df["followers_m_approx"])
    return df


@st.cache_data
def load_ideas() -> pd.DataFrame:
    df = pd.read_csv(DATA / "content_ideas.csv")
    df["envs"] = df["envs"].str.split(";")
    # Optional: blend in live Google Trends scores if refresh_trends.py has been run
    gt = DATA / "google_trends.csv"
    if gt.exists():
        t = pd.read_csv(gt).set_index("category")
        for col, src in (("trend", "trend_interest"), ("growth", "growth_interest")):
            if src in t.columns:
                live = df["category"].map(t[src])
                df[col] = np.where(live.notna(), 0.5 * df[col] + 0.5 * live, df[col])
    return df


@st.cache_data
def load_music_songs() -> pd.DataFrame:
    return pd.read_csv(DATA / "music_songs.csv")


@st.cache_data
def load_music_artists() -> pd.DataFrame:
    return pd.read_csv(DATA / "music_artists.csv")


@st.cache_data
def load_music_genres() -> pd.DataFrame:
    """Genre table; 'trend' comes from real chart streams, so genres not on the chart score low."""
    g = pd.read_csv(DATA / "music_genres.csv")
    g["envs"] = g["envs"].str.split(";")
    songs = load_music_songs()
    streams = songs.groupby("genre")["weekly_streams_m"].sum()
    songs_n = songs.groupby("genre")["title"].count()
    g["chart_streams_m"] = g["genre"].map(streams).fillna(0.0)
    g["songs_in_chart"] = g["genre"].map(songs_n).fillna(0).astype(int)
    g["chart_share_pct"] = 100 * g["chart_streams_m"] / streams.sum()
    g["trend"] = 1 + 9 * minmax(g["chart_streams_m"])
    return g


@st.cache_data
def load_movie_genres() -> pd.DataFrame:
    """Genre table; trend and growth are measured from movies.csv."""
    meta = pd.read_csv(DATA / "movie_genres.csv")
    meta["envs"] = meta["envs"].str.split(";")
    m = load_movies()
    agg = m.groupby("genre").agg(films=("title", "count"), avg_trend=("trend_score", "mean"),
                                 total_gross=("gross_usd_m", "sum"), avg_gross=("gross_usd_m", "mean"),
                                 avg_rating=("rating_used", "mean"))
    recent_gross = m[m["year"] >= 2025].groupby("genre")["gross_usd_m"].sum()
    recent_count = m[m["year"] >= 2025].groupby("genre")["title"].count()
    # recent share = half from money share, half from how many of the genre's films are from 2025-26
    agg["recent_share"] = (0.5 * (recent_gross / agg["total_gross"]).reindex(agg.index).fillna(0.0)
                           + 0.5 * (recent_count / agg["films"]).reindex(agg.index).fillna(0.0))
    g = meta.merge(agg.reset_index(), on="genre", how="left").fillna({"films": 0, "avg_trend": 0.0,
                                                                      "recent_share": 0.0, "avg_gross": 0.0})
    g["trend"] = 1 + 9 * minmax(g["avg_trend"])
    g["growth"] = 1 + 9 * g["recent_share"]
    g["monetization"] = 1 + 9 * minmax(np.log10(g["avg_gross"].clip(lower=1)))
    return g
