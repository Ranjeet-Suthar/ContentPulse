"""Optional: pull real Google Trends interest (India, last 12 months) for each content category.

Usage:  pip install pytrends   then   python refresh_trends.py
Writes data/google_trends.csv. When that file exists, the app blends it 50/50 with the
analyst scores for trend and growth.
"""
import numpy as np
import pandas as pd
from pytrends.request import TrendReq

KEYWORDS = {
    "Vlogging & Travel": "vlog", "Gaming": "gaming", "Education": "online classes",
    "Comedy Skits": "comedy videos", "Stand-up Comedy": "stand up comedy",
    "Roast, Reaction & Reviews": "movie review", "Prank & Challenges": "prank",
    "Tech & AI": "AI tools", "Fitness": "home workout", "Food": "recipe",
    "Short Films & Storytelling": "short film", "Podcasts & Interviews": "podcast",
}
ANCHOR = "YouTube"          # same word in every request so batches can be compared

pt = TrendReq(hl="en-IN", tz=330)
rows = []
cats = list(KEYWORDS)
for i in range(0, len(cats), 4):
    batch = cats[i:i + 4]
    terms = [KEYWORDS[c] for c in batch] + [ANCHOR]
    pt.build_payload(terms, geo="IN", timeframe="today 12-m")
    df = pt.interest_over_time()
    for c in batch:
        s = df[KEYWORDS[c]] / df[ANCHOR].replace(0, np.nan)
        s = s.dropna()
        level = s.mean()
        slope = np.polyfit(np.arange(len(s)), s.values, 1)[0] if len(s) > 3 else 0
        rows.append({"category": c, "level": level, "slope": slope})

out = pd.DataFrame(rows)
out["trend_interest"] = 1 + 9 * (out["level"] - out["level"].min()) / (out["level"].max() - out["level"].min())
rel = out["slope"] / out["level"].replace(0, np.nan)
out["growth_interest"] = 1 + 9 * (rel - rel.min()) / (rel.max() - rel.min())
out[["category", "trend_interest", "growth_interest"]].round(2).to_csv("data/google_trends.csv", index=False)
print(out.round(2))
