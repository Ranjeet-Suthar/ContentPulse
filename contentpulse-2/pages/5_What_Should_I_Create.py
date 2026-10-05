import pandas as pd
import streamlit as st
from utils.data_loader import ENVIRONMENTS
from utils.recommender import (MODES, TEAM_CHOICES, MOVIE_BUDGETS, CREATOR_BUDGETS, MUSIC_BUDGETS,
                               get_options, score_options, explain)
from utils.ui import setup, fig_ax, show, source_note, step

setup("What Should I Create?", "💡")
st.write("Answer five quick questions and get a trending direction with the reasons behind it.")

step(1, "What do you want to make?")
mode = st.radio("Type", MODES, horizontal=True, label_visibility="collapsed")
opts = get_options(mode)

step(2, "Pick your interests")
label = {"Movie": "genres", "Music": "music styles"}.get(mode, "content ideas")
interests = st.multiselect(f"Choose 3 or more {label} (you can pick many)", list(opts["option"]))
if 0 < len(interests) < 3:
    st.caption("Tip: picking 3 or more gives a better match.")

step(3, "Budget")
budgets = {"Movie": MOVIE_BUDGETS, "Music": MUSIC_BUDGETS}.get(mode, CREATOR_BUDGETS)
b_label = st.selectbox("How much can you spend to start?", list(budgets))
budget = budgets[b_label]

step(4, "Team size")
team_label = st.selectbox("Who is on your team?", list(TEAM_CHOICES))
team = TEAM_CHOICES[team_label]

step(5, "Where will you create?")
envs = st.multiselect("Places you can use", ENVIRONMENTS, default=["Home"])

if st.button("Show my recommendation", type="primary"):
    scored = score_options(opts, interests, budget, team, envs)
    best = scored.iloc[0]

    st.markdown(f'<div class="pick"><div class="pick-label">BEST PICK FOR YOU</div>'
                f'<div class="pick-name">{best["option"]}</div>'
                f'<div class="pick-score">Match score {best["score"]:.0f} / 100</div></div>', unsafe_allow_html=True)
    st.markdown("**Why this works for you**")
    for line in explain(best, budget, team, envs, interests):
        st.write("- " + line)
    if best.get("examples"):
        st.write(f"**Look at for inspiration:** {best['examples']}")
    if "platforms" in best and isinstance(best.get("platforms"), str):
        st.write(f"**Where to post:** {best['platforms']}")

    st.markdown("#### Other good options")
    top = scored.head(5)
    fig, ax = fig_ax(7, 3.5)
    ax.barh(top["option"][::-1], top["score"][::-1], color=["#475569"] * 4 + ["#8B5CF6"])
    ax.set_xlabel("Match score"); show(fig)

    st.markdown("#### Best trending option right now (ignoring your limits)")
    trending = opts.assign(m=lambda d: 0.5 * d["trend"] + 0.5 * d["growth"]).sort_values("m", ascending=False).iloc[0]
    st.write(f"**{trending['option']}** has the strongest mix of trend ({trending['trend']:.1f}/10) and growth "
             f"({trending['growth']:.1f}/10) in this group. " +
             ("It is also your top match." if trending["option"] == best["option"] else
              "It is not your top match because of your budget, team or place, but it is worth working towards."))

    low = scored[scored["trend"] <= 3]
    if len(low) and any(i in list(low["option"]) for i in interests):
        st.warning("Some of your interests are currently low on trend: " +
                   ", ".join(i for i in interests if i in list(low["option"])) + ". You can still make them, but expect slower growth.")
else:
    st.info("Fill in the choices above and press the button.")

source_note("Scores are built from the CSV files: movie trend from box office and ratings, music trend from Spotify India streams, "
            "creator scores from category trend, growth, earning potential and competition.")
