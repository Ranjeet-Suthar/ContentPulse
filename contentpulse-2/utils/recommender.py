"""Rule-based, explainable recommender for the 'What Should I Create?' page.

score = weighted mix of trend, growth, monetisation, low competition and fit
(budget, team size, environment). Every number comes from the data files.
"""
import numpy as np
import pandas as pd
from utils.data_loader import (load_ideas, load_music_genres, load_movie_genres, load_creators, load_movies)

TEAM_CHOICES = {"Solo (1)": 1, "Small (2-3)": 3, "Medium (4-10)": 10, "Large (10+)": 30}
MOVIE_BUDGETS = {"Under Rs 2 crore": 2, "Rs 2-10 crore": 10, "Rs 10-50 crore": 50,
                 "Rs 50-150 crore": 150, "Rs 150 crore+": 500}
CREATOR_BUDGETS = {"Under Rs 5,000": 5000, "Rs 5,000-25,000": 25000, "Rs 25,000-1 lakh": 100000,
                   "Rs 1 lakh+": 500000}
MUSIC_BUDGETS = {"Under Rs 10,000": 10000, "Rs 10,000-50,000": 50000, "Rs 50,000-2 lakh": 200000,
                 "Rs 2 lakh+": 1000000}

MODES = ["Short-form content", "Long-form content", "Movie", "Music"]


def get_options(mode: str) -> pd.DataFrame:
    """Return a common table: option, trend, growth, competition, monetization, min_budget, min_team, envs, note."""
    if mode in ("Short-form content", "Long-form content"):
        key = "Short-form" if mode.startswith("Short") else "Long-form"
        d = load_ideas()
        d = d[d["mode"] == key].copy()
        out = pd.DataFrame({"option": d["idea"], "trend": d["trend"], "growth": d["growth"],
                            "competition": d["competition"], "monetization": d["monetization"],
                            "min_budget": d["min_budget_inr"], "min_team": d["min_team"],
                            "envs": d["envs"], "note": d["why"], "category": d["category"],
                            "platforms": d["platforms"]})
        cr = load_creators()
        out["examples"] = out["category"].apply(
            lambda c: ", ".join(cr[cr["category"] == c].sort_values("followers_m_approx", ascending=False)["name"].head(5)))
        out["unit"] = "Rs"
    elif mode == "Movie":
        d = load_movie_genres()
        m = d.copy()
        out = pd.DataFrame({"option": m["genre"], "trend": m["trend"], "growth": m["growth"],
                            "competition": m["competition"], "monetization": m["monetization"],
                            "min_budget": m["min_budget_cr"], "min_team": m["min_team"],
                            "envs": m["envs"], "note": m["note"], "films": m["films"]})
        mv = load_movies()
        out["examples"] = out["option"].apply(
            lambda g: ", ".join(mv[mv["genre"] == g].sort_values("trend_score", ascending=False)["title"].head(4)))
        out["unit"] = "Cr"
    else:
        d = load_music_genres()
        out = pd.DataFrame({"option": d["genre"], "trend": d["trend"], "growth": d["growth"],
                            "competition": d["competition"], "monetization": d["monetization"],
                            "min_budget": d["min_budget_inr"], "min_team": d["min_team"],
                            "envs": d["envs"], "note": d["evidence"], "examples": d["example_artists"],
                            "evidence_type": d["evidence_type"]})
        out["unit"] = "Rs"
    return out.reset_index(drop=True)


def score_options(opts: pd.DataFrame, interests: list, budget: float, team: int, envs: list) -> pd.DataFrame:
    o = opts.copy()
    o["budget_ok"] = o["min_budget"] <= budget
    o["team_ok"] = o["min_team"] <= team
    o["env_match"] = o["envs"].apply(lambda e: any(x in e for x in envs) if envs else True)
    # fit: 1 = fully fits. Budget and team shortfall reduce it smoothly.
    b_fit = np.minimum(1.0, budget / o["min_budget"].clip(lower=1e-9))
    t_fit = np.minimum(1.0, team / o["min_team"].clip(lower=1))
    e_fit = o["env_match"].astype(float) * 0.5 + 0.5
    o["fit"] = 0.45 * b_fit + 0.30 * t_fit + 0.25 * e_fit
    o["market"] = (0.40 * o["trend"] + 0.30 * o["growth"] + 0.15 * o["monetization"]
                   + 0.15 * (11 - o["competition"])) / 10
    o["interest_bonus"] = o["option"].isin(interests).astype(float)
    o["score"] = 100 * (0.50 * o["market"] + 0.35 * o["fit"] + 0.15 * o["interest_bonus"])
    return o.sort_values("score", ascending=False).reset_index(drop=True)


def explain(row: pd.Series, budget: float, team: int, envs: list, interests: list) -> list:
    """Plain-English reasons for the top pick."""
    r = []
    r.append(f"Trend strength is {row['trend']:.1f}/10 and growth is {row['growth']:.1f}/10, "
             f"so demand is {'rising' if row['growth'] >= 7 else 'steady' if row['growth'] >= 5 else 'slow'}.")
    if row["competition"] >= 8:
        r.append(f"Competition is high ({row['competition']:.0f}/10), so you need a clear style to stand out.")
    elif row["competition"] <= 6:
        r.append(f"Competition is moderate ({row['competition']:.0f}/10), so it is easier to get noticed.")
    unit = row["unit"]
    need = f"Rs {row['min_budget']:,.0f}" if unit == "Rs" else f"Rs {row['min_budget']:g} crore"
    have = f"Rs {budget:,.0f}" if unit == "Rs" else f"Rs {budget:g} crore"
    r.append(f"Suggested starting budget is about {need}; yours is {have} "
             f"({'enough' if row['budget_ok'] else 'a bit low, so start smaller or find a partner'}).")
    r.append(f"Suggested minimum team is {int(row['min_team'])}; yours is {team} "
             f"({'enough' if row['team_ok'] else 'smaller, so keep the scope simple'}).")
    r.append("Your chosen place suits it." if row["env_match"] else
             "Your chosen place is not ideal for it; try " + ", ".join(row["envs"][:3]) + ".")
    if row["option"] in interests:
        r.append("It also matches your interests.")
    r.append(f"Why it works: {row['note']}.")
    return r
