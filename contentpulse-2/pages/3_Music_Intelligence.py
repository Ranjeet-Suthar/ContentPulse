import pandas as pd
import streamlit as st
from utils.data_loader import load_music_songs, load_music_artists, load_music_genres, level_from_score
from utils.ui import setup, fig_ax, show, source_note, PALETTE, level_badge

setup("Music Intelligence", "🎵")
st.write("What India is streaming right now, which artists lead, and which music styles are rising.")

songs, artists, genres = load_music_songs(), load_music_artists(), load_music_genres()

tab1, tab2, tab3, tab4 = st.tabs(["Chart songs", "Artists", "Genre trends", "Reach and staying power"])

with tab1:
    st.markdown("Spotify India weekly chart (week of 18 June 2026): **weekly streams in millions**.")
    d = songs.sort_values("weekly_streams_m")
    fig, ax = fig_ax(8, 6)
    pal = {"Indian Indie / I-pop": "#F472B6", "Bollywood Romantic": "#8B5CF6"}
    ax.barh(d["title"], d["weekly_streams_m"], color=[pal.get(g, "#94A3B8") for g in d["genre"]])
    ax.set_xlabel("Weekly streams (millions)")
    show(fig)
    st.caption("Pink = Indian Indie / I-pop, Purple = Bollywood Romantic, Grey = other genres.")
    t = songs[["rank", "title", "artists", "genre", "language", "weekly_streams_m"]].copy()
    t.columns = ["Rank", "Song", "Artists", "Genre", "Language", "Weekly streams (M)"]
    st.dataframe(t, use_container_width=True, hide_index=True)

with tab2:
    a = artists.copy()
    a["spotify_india_rank_2025"] = a["spotify_india_rank_2025"].apply(lambda x: "" if pd.isna(x) else int(x))
    a.columns = ["Artist", "Genre", "Spotify India rank 2025", "Why they are here"]
    st.dataframe(a, use_container_width=True, hide_index=True)
    st.caption("Ranks 1-9 are from Spotify Wrapped India 2025; other artists are listed because their songs are on the 2026 charts.")

with tab3:
    g = genres.copy()
    g["Trend level"] = (g["trend"] * 10).apply(level_from_score).apply(level_badge)
    fig, ax = fig_ax(6, 6)
    shares = g[g["chart_share_pct"] > 0].sort_values("chart_share_pct", ascending=False)
    ax.pie(shares["chart_share_pct"], labels=shares["genre"], autopct="%1.0f%%", startangle=90)
    ax.set_title("Share of top-17 weekly streams by genre")
    show(fig)
    t = g.sort_values("trend", ascending=False)[["genre", "songs_in_chart", "chart_share_pct", "trend", "growth", "Trend level", "evidence_type", "evidence"]].round(1)
    t.columns = ["Genre", "Songs in chart", "Share of streams (%)", "Trend (1-10)", "Growth (1-10)", "Trend level", "Evidence type", "Evidence"]
    st.dataframe(t, use_container_width=True, hide_index=True)
    st.caption("Trend is measured from real chart streams, so styles missing from the chart show Low. Growth is an evidence-based score: "
               "'chart' or 'Wrapped' means a source supports it, 'editorial' means it is an estimate.")

with tab4:
    st.markdown("**Billboard India Songs: how long hits stay.** Weeks on chart as of 18 July 2026.")
    longevity = pd.DataFrame({"Song": ["Mann Mera (Gajendra Verma)", "Arz Kiya Hai - Coke Studio Bharat (Anuv Jain)", "Bairan (Banjaare)", "Aarzu (Noor, Khan, Madhurxo, Asim Azhar)"],
                              "Weeks on chart": [56, 25, 18, 4], "Chart peak": [2, 1, 1, 4]})
    fig, ax = fig_ax(7, 3.5)
    ax.barh(longevity["Song"][::-1], longevity["Weeks on chart"][::-1], color=PALETTE["main"])
    ax.set_xlabel("Weeks on chart")
    show(fig)
    st.dataframe(longevity, use_container_width=True, hide_index=True)
    st.markdown("**Who was #1 on Billboard India Songs**")
    st.dataframe(pd.DataFrame({"Week": ["31 Jan 2026", "7 Mar 2026", "6, 13, 20 Jun 2026", "18 Jul 2026"],
                               "No. 1 song": ["Gehra Hua (Dhurandhar)", "Gehra Hua (Dhurandhar)", "Bairan", "Arz Kiya Hai (Coke Studio Bharat)"],
                               "Type": ["Film song", "Film song", "Indie / I-pop", "Indie / Coke Studio"]}), hide_index=True, use_container_width=True)
    st.write("Early 2026 was led by a film song. From June, independent and Coke Studio songs took over the top spot, "
             "which matches Spotify's note that I-pop keeps growing in India. Also, YouTube's global chart in Aug 2026 was led by Shakira's "
             "FIFA anthem 'Dai Dai', but it ranked only 26th in India, which shows local taste matters.")

source_note("Spotify Charts India via Soundcharts (week of 18 Jun 2026), Billboard India Songs (Luminate), Spotify Wrapped India 2025, YouTube Music Charts (Aug 2026).")
