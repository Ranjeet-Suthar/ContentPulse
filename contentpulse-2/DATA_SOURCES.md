# Data sources and honesty notes

All files are in `data/`. They are a **snapshot compiled in October 2026**, not a live feed.
Before your viva or presentation, open the source links below and re-check any number you plan to quote.

| File | What it holds | Where the numbers come from | How firm are they? |
|---|---|---|---|
| `movies.csv` | 56 films: Hollywood, Bollywood, South | Box Office Mojo / The Numbers (Hollywood); Bollywood Hungama, Sacnilk, Koimoi, FilmiBeat (India); IMDb (ratings) | Gross figures are rounded worldwide totals. 2026 films are snapshots of a run in progress. Indian grosses are converted at 1 USD = Rs 85. IMDb ratings are approximate, and blank when not confirmed. |
| `creators.csv` | 120 creators in 12 categories | Public YouTube and Instagram channel pages | Follower counts are rounded and change every day. Run `refresh_creators.py` to update YouTube numbers. |
| `music_songs.csv` | 17 songs, weekly streams | Spotify Charts India, week of 18 Jun 2026 (via Soundcharts) | Taken from the published chart. |
| `music_artists.csv` | 19 artists | Spotify Wrapped India 2025 (ranks 1-9), Billboard India Songs 2026, Spotify India chart | Ranks 1-9 are from Wrapped; others are listed because their songs charted. |
| `music_genres.csv` | 15 music styles | Trend is measured from the chart; growth, competition, cost are marked `chart + Wrapped` or `editorial` | `editorial` means an estimate, not a measured number. |
| `movie_genres.csv` | 15 film genres | Competition, cost and team size are estimates; trend and growth are measured from `movies.csv` | Budgets and team sizes are rough guides for planning. |
| `content_ideas.csv` | 24 content ideas (12 short, 12 long) | Trend, growth, competition, earning potential are 1-10 analyst scores; cost and team are rough guides | Estimates. Blend with Google Trends using `refresh_trends.py`. |

## Sources to cite in your report
* Box Office Mojo, The Numbers, Bollywood Hungama, Sacnilk, Koimoi, FilmiBeat
* IMDb
* Spotify Charts (India), Soundcharts
* Billboard India Songs (Luminate)
* Spotify Wrapped India 2025
* YouTube Music Charts
* Google Trends
* YouTube and Instagram channel pages

## Known limits (say these honestly in your viva)
* The film list is curated (big hits plus a few well-rated smaller films), not every release, so averages are for "notable films".
* Genres with 1-3 films have weak statistics.
* Creator category scores are judgement-based unless you refresh them from Google Trends.
* The regression and probability pages are teaching demonstrations on a small dataset, not forecasts.
