# ContentPulse - Content Trend & Audience Intelligence Platform

A Python + Streamlit web app (PS2 mini project) that studies movies, creators and music, then suggests
**what to create next, and why**.

## Pages
| Page | What it does |
|---|---|
| Home (`app.py`) | Name, idea, who it helps, what is inside |
| 1 Movie Intelligence | Hollywood, Bollywood and South films: gross, rating, genre, trend score |
| 2 Creator Intelligence | 12 content types, 10 creators each, top-performing categories, short vs long |
| 3 Music Intelligence | Spotify India chart, artists, genre share, chart longevity |
| 4 Audience Analytics | Mean/median/mode/std, histogram, bar, pie, box, scatter, probability, t-test, cleaning, EDA, correlation, regression |
| 5 What Should I Create? | Choose short / long / movie / music, interests, budget, team, place, get a recommendation with reasons |
| 6 Future Opportunities | Rising, high-opportunity genres and categories |

## Syllabus map
| Module | Where it is used |
|---|---|
| 1 Python, NumPy, Pandas, CSV import | `utils/data_loader.py`, all pages |
| 2 Descriptive statistics and visualisation | Page 4 tabs 1-2, pages 1-3 charts |
| 3 Probability distributions, hypothesis testing | Page 4 tab 3 (Normal, Bernoulli/Binomial, Poisson, Exponential, t-test) |
| 4 Preprocessing and cleaning | Page 4 tab 4 (missing values, duplicates, data types, min-max, IQR outliers) |
| 5 Exploratory data analysis | Page 4 tab 5 (univariate and bivariate) |
| 6 Correlation and regression | Page 4 tab 6 (Pearson, linear and logistic regression) |

## Run on your computer
```bash
python -m venv .venv
.venv\Scripts\activate          # Windows   (Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt
streamlit run app.py
```

## Put it on GitHub and Streamlit
1. Create a new empty repository on github.com (for example `contentpulse`).
2. In this folder run:
```bash
git init
git add .
git commit -m "ContentPulse v1"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/contentpulse.git
git push -u origin main
```
3. Go to https://share.streamlit.io, sign in with GitHub, click **New app**, choose your repository,
   branch `main`, main file `app.py`, then **Deploy**.

## How the scores work (no random numbers)
* **Movie trend score (0-100)** = 40% earnings (log scale) + 25% rating + 35% recency. Films that are old or small show lower.
* **Movie genre trend/growth** are measured from `data/movies.csv`.
* **Music genre trend** is measured from real Spotify India chart streams. Genres not on the chart score 1/10 (low).
* **Creator category scores** (trend, growth, competition, earning potential) are 1-10 analyst scores in `data/content_ideas.csv`.
  Run `refresh_trends.py` to blend in live Google Trends numbers.
* **Recommendation score** = 50% market (trend, growth, earnings, low competition) + 35% fit (budget, team, place) + 15% your interests.

## Updating the data
* Edit the CSV files in `data/` (add more films, creators or songs and every chart updates).
* `python refresh_trends.py` - pulls Google Trends interest for each category (needs internet and `pip install pytrends`).
* `python refresh_creators.py` - updates subscriber counts through the YouTube Data API (needs a free API key in `YOUTUBE_API_KEY`).

See `DATA_SOURCES.md` for where each number comes from and what is approximate.

## Look and feel
* Black theme and colours are set in `.streamlit/config.toml`; banners, cards and chart styling are in `utils/ui.py`.
