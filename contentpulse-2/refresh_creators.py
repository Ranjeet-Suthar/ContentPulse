"""Optional: update YouTube subscriber counts with the YouTube Data API v3.

Usage:  set YOUTUBE_API_KEY (free key from Google Cloud Console), then  python refresh_creators.py
Searches each YouTube creator by name, takes the top channel result, and prints the subscriber count in millions.
Check the printed names before you overwrite data/creators.csv (set SAVE = True).
"""
import os
import requests
import pandas as pd

KEY = os.environ.get("YOUTUBE_API_KEY")
SAVE = False
if not KEY:
    raise SystemExit("Set the YOUTUBE_API_KEY environment variable first.")

df = pd.read_csv("data/creators.csv")
new = []
for _, r in df.iterrows():
    if "YouTube" not in r["platform"]:
        new.append(r["followers_m_approx"]); continue
    s = requests.get("https://www.googleapis.com/youtube/v3/search",
                     params={"part": "snippet", "q": r["name"], "type": "channel", "maxResults": 1, "key": KEY}).json()
    items = s.get("items", [])
    if not items:
        new.append(r["followers_m_approx"]); continue
    cid = items[0]["snippet"]["channelId"]; title = items[0]["snippet"]["title"]
    c = requests.get("https://www.googleapis.com/youtube/v3/channels",
                     params={"part": "statistics", "id": cid, "key": KEY}).json()
    subs = int(c["items"][0]["statistics"].get("subscriberCount", 0)) / 1e6
    print(f"{r['name']:45s} -> {title:35s} {subs:8.2f} M")
    new.append(round(subs, 2))
if SAVE:
    df["followers_m_approx"] = new
    df.to_csv("data/creators.csv", index=False)
    print("Saved.")
