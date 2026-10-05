"""Audience Analytics: covers the PS2 syllabus modules 1-6 on the project's own data."""
import numpy as np
import pandas as pd
import streamlit as st
from scipy import stats
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import r2_score, accuracy_score
from utils.data_loader import load_raw_movies, load_movies, load_creators, minmax
from utils.ui import setup, fig_ax, show, source_note, PALETTE

setup("Audience Analytics", "📊")
st.write("Statistics and charts that explain the data behind every recommendation.")

movies, creators, raw = load_movies(), load_creators(), load_raw_movies()

tabs = st.tabs(["1 Descriptive statistics", "2 Visualisation", "3 Probability and tests",
                "4 Cleaning and preprocessing", "5 EDA", "6 Correlation and regression"])

# ---------------- Module 2: descriptive statistics ----------------
with tabs[0]:
    st.markdown("Measures of central tendency and spread (mean, median, mode, variance, standard deviation).")
    ds = st.selectbox("Dataset", ["Movie gross (USD million)", "Movie rating", "Creator followers (millions)"])
    series = {"Movie gross (USD million)": movies["gross_usd_m"], "Movie rating": movies["rating_used"],
              "Creator followers (millions)": creators["followers_m_approx"]}[ds]
    mode_val = series.round(1).mode().iloc[0]
    out = pd.DataFrame({"Value": [series.count(), series.mean(), series.median(), mode_val, series.var(), series.std(),
                                  series.min(), series.max(), series.skew()]},
                       index=["Count", "Mean", "Median", "Mode", "Variance", "Standard deviation", "Min", "Max", "Skewness"])
    st.dataframe(out.round(2), use_container_width=True)
    if series.mean() > series.median():
        st.write("The mean is higher than the median, so a few very large values pull the average up (right-skewed). "
                 "The median is the fairer 'typical' value here.")
    by = movies.groupby("industry")["gross_usd_m"].agg(["count", "mean", "median", "std"]).round(1)
    st.markdown("**Gross by industry (USD million)**")
    st.dataframe(by, use_container_width=True)

# ---------------- Module 2: visualisation ----------------
with tabs[1]:
    c1, c2 = st.columns(2)
    with c1:
        fig, ax = fig_ax(5, 3.5)
        ax.hist(movies["gross_usd_m"], bins=12, color=PALETTE["main"], edgecolor="white")
        ax.set_title("Histogram: movie gross"); ax.set_xlabel("USD million"); ax.set_ylabel("Films")
        show(fig)
    with c2:
        fig, ax = fig_ax(5, 3.5)
        names = sorted(movies["industry"].unique())
        groups = [movies[movies["industry"] == n]["gross_usd_m"].values for n in names]
        bp = ax.boxplot(groups, patch_artist=True, showfliers=False,
                        whiskerprops=dict(color="white", linewidth=1.5),
                        capprops=dict(color="white", linewidth=1.5),
                        medianprops=dict(color="white", linewidth=2.5))
        ax.set_xticklabels(names)
        for patch, n in zip(bp["boxes"], names):
            patch.set_facecolor(PALETTE[n])
            patch.set_edgecolor("white")
        ax.set_title("Box plot: gross by industry"); ax.set_ylabel("USD million")
        show(fig)
    c3, c4 = st.columns(2)
    with c3:
        fig, ax = fig_ax(5, 3.5)
        cnt = movies["genre"].value_counts()
        ax.bar(cnt.index, cnt.values, color=PALETTE["accent"])
        ax.set_title("Bar chart: films per genre"); ax.tick_params(axis="x", rotation=70)
        show(fig)
    with c4:
        fig, ax = fig_ax(5, 3.5)
        pc = creators["platform"].str.split("/").str[0].value_counts()
        ax.pie(pc.values, labels=pc.index, autopct="%1.0f%%")
        ax.set_title("Pie chart: creators by main platform")
        show(fig)
    fig, ax = fig_ax(7, 4)
    ax.scatter(movies["rating_used"], movies["gross_usd_m"], c=movies["year"], cmap="viridis", s=50)
    ax.set_xlabel("Rating"); ax.set_ylabel("Gross (USD million)"); ax.set_title("Scatter plot: rating vs gross (colour = year)")
    show(fig)

# ---------------- Module 3: probability ----------------
with tabs[2]:
    st.markdown("#### Normal distribution")
    lg = movies["log_gross"]
    mu, sd = lg.mean(), lg.std()
    fig, ax = fig_ax(6, 3.5)
    ax.hist(lg, bins=10, density=True, color="#475569", edgecolor="white")
    xs = np.linspace(lg.min(), lg.max(), 200)
    ax.plot(xs, stats.norm.pdf(xs, mu, sd), color=PALETTE["main"], lw=2)
    ax.set_xlabel("log10(gross in USD million)"); ax.set_title("Gross on log scale with fitted Normal curve")
    show(fig)
    st.write(f"Mean = {mu:.2f}, standard deviation = {sd:.2f}. About 68% of films fall between "
             f"{10**(mu-sd):,.0f} and {10**(mu+sd):,.0f} million USD.")
    sh = stats.shapiro(lg)
    st.caption(f"Shapiro-Wilk normality test p-value = {sh.pvalue:.3f} ({'looks normal' if sh.pvalue > 0.05 else 'not perfectly normal'}).")

    st.markdown("#### Bernoulli and Binomial")
    p_hit = float((movies["rating_used"] >= 7.5).mean())
    st.write(f"A film is a 'critical hit' if its rating is 7.5 or more. In this dataset p = {p_hit:.2f}. "
             f"If a studio releases 5 films, the chance that at least 2 are critical hits is "
             f"{1 - stats.binom.cdf(1, 5, p_hit):.2f} (Binomial, built from Bernoulli trials).")

    st.markdown("#### Poisson")
    per_year = movies[movies["trend_level"].isin(["High", "Very High"])].groupby("year")["title"].count().reindex(range(2022, 2027), fill_value=0)
    lam = per_year.mean()
    st.write(f"Average number of High/Very High trending films per year (2022-2026 in our list) is lambda = {lam:.1f}. "
             f"Probability of exactly {int(round(lam))} such films in a year = {stats.poisson.pmf(int(round(lam)), lam):.2f}.")
    fig, ax = fig_ax(5, 3)
    ks = np.arange(0, int(lam * 2) + 3)
    ax.bar(ks, stats.poisson.pmf(ks, lam), color=PALETTE["South"])
    ax.set_title("Poisson distribution"); ax.set_xlabel("Number of trending films in a year")
    show(fig)
    st.caption("Our list is a curated sample, not every film released, so this is a classroom illustration of Poisson, not a forecast.")

    st.markdown("#### Exponential")
    f_m = creators["followers_m_approx"]
    scale = f_m.mean()
    st.write(f"Creator followers are strongly right-skewed. Treating followers as Exponential with mean {scale:.1f} million, "
             f"the chance a creator has more than 50 million followers is {np.exp(-50 / scale):.3f}. "
             f"In our list, {(f_m > 50).mean():.3f} actually do.")

    st.markdown("#### Hypothesis test: do Indian films gross differently from Hollywood films?")
    st.write("H0: mean log-gross is the same for Hollywood and Indian (Bollywood + South) films. H1: it is different. Significance level 0.05.")
    a = movies[movies["industry"] == "Hollywood"]["log_gross"]
    b = movies[movies["industry"] != "Hollywood"]["log_gross"]
    t, p = stats.ttest_ind(a, b, equal_var=False)
    st.write(f"t = {t:.2f}, p-value = {p:.4f}. " + ("We reject H0: the difference is statistically significant." if p < 0.05
                                                  else "We fail to reject H0: no significant difference."))
    st.caption("Indian earnings are converted at 1 USD = Rs 85. Samples are curated blockbusters, so treat this as indicative.")

# ---------------- Module 4: preprocessing ----------------
with tabs[3]:
    st.markdown("#### Missing values")
    miss = raw.isna().sum()
    st.dataframe(miss[miss > 0].rename("Missing values").to_frame().T if miss.sum() else pd.DataFrame({"Missing values": [0]}), use_container_width=True)
    st.write("IMDb ratings that could not be confirmed are left blank in the CSV. We fill them with the **median rating of that industry** "
             "and mark them, so they never look like confirmed data.")
    cmp = pd.DataFrame({"Before (mean)": [raw["imdb_rating"].mean()], "After filling (mean)": [movies["rating_used"].mean()],
                        "Values filled": [int(movies["rating_missing"].sum())]})
    st.dataframe(cmp.round(2), use_container_width=True, hide_index=True)

    st.markdown("#### Duplicate records")
    st.write(f"Duplicate titles in raw data: **{int(raw.duplicated(subset=['title']).sum())}**. Duplicates are dropped with `drop_duplicates`.")

    st.markdown("#### Data types")
    st.dataframe(raw.dtypes.astype(str).rename("Type").to_frame().T, use_container_width=True)

    st.markdown("#### Normalisation (min-max)")
    norm = pd.DataFrame({"gross_usd_m": movies["gross_usd_m"], "normalised": minmax(movies["gross_usd_m"])}).head(6)
    st.dataframe(norm.round(3), use_container_width=True)
    st.caption("Formula: (x - min) / (max - min). Gross is also log-transformed because a few films earn far more than the rest.")

    st.markdown("#### Outlier detection (IQR rule)")
    q1, q3 = movies["gross_usd_m"].quantile([0.25, 0.75]); iqr = q3 - q1
    hi = q3 + 1.5 * iqr
    out = movies[movies["gross_usd_m"] > hi][["title", "industry", "gross_usd_m"]]
    st.write(f"Upper fence = {hi:,.0f} USD million. Films above it:")
    st.dataframe(out.round(1), use_container_width=True, hide_index=True)

# ---------------- Module 5: EDA ----------------
with tabs[4]:
    st.markdown("#### Univariate analysis")
    col = st.selectbox("Choose a column", ["gross_usd_m", "rating_used", "year", "trend_score"])
    c1, c2 = st.columns(2)
    with c1:
        fig, ax = fig_ax(4.5, 3); ax.hist(movies[col], bins=10, color=PALETTE["main"], edgecolor="white"); ax.set_title(f"{col}: histogram"); show(fig)
    with c2:
        fig, ax = fig_ax(4.5, 3)
        ax.boxplot(movies[col], vert=False, showfliers=False,
                   boxprops=dict(color="white", linewidth=1.5),
                   whiskerprops=dict(color="white", linewidth=1.5),
                   capprops=dict(color="white", linewidth=1.5),
                   medianprops=dict(color="#FB923C", linewidth=2.5))
        ax.set_title(f"{col}: box plot")
        show(fig)
    st.markdown("#### Categorical data")
    c3, c4 = st.columns(2)
    c3.dataframe(movies["genre"].value_counts().rename("Films"), use_container_width=True)
    c4.dataframe(movies["industry"].value_counts().rename("Films"), use_container_width=True)
    st.markdown("#### Bivariate analysis")
    yr = movies.groupby("year")["gross_usd_m"].median()
    fig, ax = fig_ax(7, 3.5)
    ax.plot(yr.index, yr.values, marker="o", color=PALETTE["accent"])
    ax.set_title("Trend over time: median gross by release year"); ax.set_xlabel("Year"); ax.set_ylabel("USD million")
    show(fig)
    st.write("Films from 2022-2025 dominate our list because they are the biggest recent hits; 2026 films are still earning, "
             "so their totals can still grow.")
    st.markdown("**Average gross by genre and industry (USD million)**")
    st.dataframe(movies.pivot_table(index="genre", columns="industry", values="gross_usd_m", aggfunc="mean").round(0), use_container_width=True)

# ---------------- Module 6: correlation and regression ----------------
with tabs[5]:
    num = movies[["gross_usd_m", "log_gross", "rating_used", "year", "trend_score"]]
    corr = num.corr(method="pearson")
    fig, ax = fig_ax(5.5, 4.5)
    im = ax.imshow(corr, cmap="magma", vmin=-1, vmax=1)
    ax.set_xticks(range(len(corr))); ax.set_xticklabels(corr.columns, rotation=45, ha="right")
    ax.set_yticks(range(len(corr))); ax.set_yticklabels(corr.columns)
    for i in range(len(corr)):
        for j in range(len(corr)):
            ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=8,
                    color="black" if corr.iloc[i, j] > 0.55 else "white")
    fig.colorbar(im); ax.set_title("Pearson correlation")
    show(fig)
    r, p = stats.pearsonr(movies["rating_used"], movies["log_gross"])
    st.write(f"Pearson r between rating and log-gross = **{r:.2f}** (p = {p:.3f}). "
             f"{'Weak' if abs(r) < 0.3 else 'Moderate' if abs(r) < 0.6 else 'Strong'} {'positive' if r > 0 else 'negative'} relationship.")

    st.markdown("#### Simple linear regression: predict log-gross from rating")
    X = movies[["rating_used"]].values; y = movies["log_gross"].values
    lr = LinearRegression().fit(X, y)
    pred = lr.predict(X)
    fig, ax = fig_ax(6, 3.5)
    ax.scatter(X, y, color=PALETTE["main"]); xs = np.linspace(X.min(), X.max(), 50).reshape(-1, 1)
    ax.plot(xs, lr.predict(xs), color="#F472B6"); ax.set_xlabel("Rating"); ax.set_ylabel("log10 gross")
    show(fig)
    st.write(f"Equation: log10(gross) = {lr.intercept_:.2f} + {lr.coef_[0]:.2f} x rating. R-squared = {r2_score(y, pred):.2f}. "
             "A low R-squared means rating alone cannot predict earnings.")

    st.markdown("#### Logistic regression: will a film earn 500+ million USD?")
    yb = (movies["gross_usd_m"] >= 500).astype(int)
    Xm = movies[["rating_used", "recency"]].values
    lg_m = LogisticRegression().fit(Xm, yb)
    st.write(f"Accuracy on our data = {accuracy_score(yb, lg_m.predict(Xm)):.2f}.")
    rt = st.slider("Rating", 5.0, 9.0, 7.5, 0.1)
    yr_pick = st.slider("Release year", 2018, 2026, 2026)
    prob = lg_m.predict_proba([[rt, max(0, 1 - (2026 - yr_pick) / 8)]])[0, 1]
    st.metric("Estimated chance of 500M+ USD", f"{prob*100:.0f}%")
    st.caption("A teaching model on a small, curated list. It is not a real box-office forecast.")

source_note("All numbers on this page are calculated live from the CSV files in the data folder.")
