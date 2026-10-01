"""Review Radar – interactive dashboard.   Run:  streamlit run app.py"""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import config as C
from src import insights, pipeline
from src.correlation import tfidf_terms, word_rating_correlation, words_by_star
from src.ngrams import top_ngrams
from src.sample_data import generate_demo_reviews
from src.sentiment import available_methods
from src.visualize import pain_cloud

P = C.PALETTE
SENT = {"Positive": P["pos"], "Neutral": P["neu"], "Negative": P["neg"]}

st.set_page_config(page_title="Review Radar", page_icon="📡", layout="wide")
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@500;700;800&family=DM+Sans:wght@400;500;700&display=swap');
html, body, [class*="css"] {{ font-family: 'DM Sans', sans-serif; }}
h1, h2, h3 {{ font-family: 'Sora', sans-serif !important; letter-spacing: -0.02em; }}
.stApp {{ background: radial-gradient(1200px 500px at 85% -10%, #2a1f6b55, transparent), {P['bg']}; }}
.hero {{ padding: 6px 0 18px; }}
.hero h1 {{ font-size: 2.6rem; margin: 0; background: linear-gradient(90deg, {P['cyan']}, {P['violet']} 55%, {P['neg']});
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
.hero p {{ color: {P['muted']}; margin: 4px 0 0; font-size: 1.02rem; }}
.kpi {{ background: {P['panel']}; border: 1px solid {P['grid']}; border-radius: 16px; padding: 16px 18px; }}
.kpi b {{ display:block; font-family:'Sora'; font-size: 1.7rem; }}
.kpi span {{ color: {P['muted']}; font-size: .85rem; }}
.alert {{ background: {P['neg']}18; border: 1px solid {P['neg']}66; color: {P['text']}; border-radius: 14px; padding: 14px 18px; margin: 14px 0; }}
.stTabs [data-baseweb="tab"] {{ font-family: 'Sora'; }}
</style>""", unsafe_allow_html=True)


def style(fig, h=380):
    fig.update_layout(template="plotly_dark", height=h, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      margin=dict(l=10, r=10, t=40, b=10), font=dict(family="DM Sans", color=P["text"]),
                      legend=dict(orientation="h", y=1.12, x=0))
    fig.update_xaxes(gridcolor=P["grid"]); fig.update_yaxes(gridcolor=P["grid"])
    return fig


def kpi(col, label, value, color):
    col.markdown(f"<div class='kpi'><b style='color:{color}'>{value}</b><span>{label}</span></div>", unsafe_allow_html=True)


@st.cache_data(show_spinner="Analysing reviews…")
def analyse(raw: pd.DataFrame, method: str) -> pd.DataFrame:
    return pipeline.run(raw, method)


# ---- sidebar: data source + filters ------------------------------------------------------------
st.sidebar.markdown("## 📡 Review Radar")
source = st.sidebar.radio("Data source", ["Demo data", "Saved CSV (data/raw)", "Upload CSV"])
method = st.sidebar.selectbox("Sentiment engine", ["auto"] + available_methods())
raw = None
if source == "Demo data":
    raw = generate_demo_reviews()
elif source == "Saved CSV (data/raw)":
    files = sorted(C.DATA_RAW.glob("*.csv"))
    if files:
        raw = pipeline.load_csv(st.sidebar.selectbox("File", files, format_func=lambda p: p.name))
    else:
        st.sidebar.info("No CSV in data/raw yet. Run `python main.py --scrape` first.")
else:
    up = st.sidebar.file_uploader("CSV with review text, rating, date", type="csv")
    if up:
        try:
            raw = pipeline.standardize_columns(pd.read_csv(up))
        except ValueError as e:
            st.sidebar.error(str(e))

st.markdown("<div class='hero'><h1>Review Radar</h1><p>Find out <i>why</i> users are frustrated – without reading thousands of reviews.</p></div>",
            unsafe_allow_html=True)
if raw is None:
    st.info("Pick a data source in the sidebar to begin.")
    st.stop()

df_all = analyse(raw, method)
d0, d1 = df_all["date"].min().date(), df_all["date"].max().date()
rng = st.sidebar.date_input("Date range", (d0, d1), min_value=d0, max_value=d1)
stars = st.sidebar.multiselect("Star ratings", [1, 2, 3, 4, 5], default=[1, 2, 3, 4, 5])
df = df_all[df_all["rating"].isin(stars)]
if isinstance(rng, tuple) and len(rng) == 2:
    df = df[(df["date"].dt.date >= rng[0]) & (df["date"].dt.date <= rng[1])]
if df.empty:
    st.warning("No reviews match these filters."); st.stop()

k = insights.kpis(df)
c = st.columns(4)
kpi(c[0], "Reviews analysed", f"{k['reviews']:,}", P["cyan"])
kpi(c[1], "Average rating", f"{k['avg_rating']:.2f} ★", P["neu"])
kpi(c[2], "Negative reviews", f"{k['pct_negative']:.0f}%", P["neg"])
kpi(c[3], "Top complaint", k["top_theme"], P["violet"])
worst = insights.worst_release(df)
if worst and worst[2]["change"] > 5:
    d, v, ba = worst
    st.markdown(f"<div class='alert'>⚠️ <b>Release {v}</b> ({d:%d %b %Y}): negative reviews went from "
                f"<b>{ba['before']:.0f}%</b> to <b>{ba['after']:.0f}%</b>. Start with the complaint phrases in the Pain points tab.</div>",
                unsafe_allow_html=True)

t1, t2, t3, t4, t5 = st.tabs(["Overview", "Trend", "Pain points", "Rating words", "Explorer"])

with t1:
    a, b = st.columns(2)
    cnt = df["sentiment"].value_counts().reindex(["Positive", "Neutral", "Negative"]).fillna(0).reset_index()
    cnt.columns = ["sentiment", "reviews"]
    fig = px.pie(cnt, names="sentiment", values="reviews", hole=0.62, color="sentiment", color_discrete_map=SENT,
                 title="Satisfied vs unsatisfied users")
    fig.update_traces(textinfo="percent", marker=dict(line=dict(color=P["bg"], width=3)))
    a.plotly_chart(style(fig), use_container_width=True)
    rc = df["rating"].value_counts().reindex([1, 2, 3, 4, 5]).fillna(0).reset_index()
    rc.columns = ["rating", "reviews"]
    fig = px.bar(rc, x="rating", y="reviews", title="Star-rating distribution", text="reviews",
                 color="rating", color_continuous_scale=[P["neg"], P["neu"], P["pos"]])
    fig.update_coloraxes(showscale=False)
    b.plotly_chart(style(fig), use_container_width=True)

with t2:
    freq = st.radio("Group by", ["D", "W", "M"], index=1, horizontal=True, format_func={"D": "Day", "W": "Week", "M": "Month"}.get)
    tr = insights.sentiment_trend(df, freq)
    fig = go.Figure()
    for s in ("Negative", "Neutral", "Positive"):
        fig.add_trace(go.Scatter(x=tr["date"], y=tr[s], name=s, mode="lines+markers" if s == "Negative" else "lines",
                                 line=dict(color=SENT[s], width=3 if s == "Negative" else 2),
                                 fill="tozeroy" if s == "Negative" else None,
                                 fillcolor="rgba(255,93,115,0.12)"))
    marks = insights.release_markers(df)
    for d, name in marks:
        fig.add_shape(type="line", x0=d, x1=d, y0=0, y1=1, yref="paper", line=dict(color=P["violet"], dash="dash"))
        fig.add_annotation(x=d, y=1, yref="paper", text=name, showarrow=False, font=dict(color=P["violet"]), yanchor="bottom")
    fig.update_layout(title="Sentiment trend (% of reviews)", yaxis_ticksuffix="%")
    st.plotly_chart(style(fig, 440), use_container_width=True)
    opts = {f"{n} – {d:%d %b %Y}": d for d, n in marks} or {}
    if opts:
        pick = st.selectbox("Compare before / after", list(opts))
        ba = insights.before_after(df, opts[pick])
        x, y, z = st.columns(3)
        kpi(x, f"Negative before ({ba['n_before']} reviews)", f"{ba['before']:.0f}%", P["pos"])
        kpi(y, f"Negative after ({ba['n_after']} reviews)", f"{ba['after']:.0f}%", P["neg"])
        kpi(z, "Change", f"{ba['change']:+.0f} pts", P["violet"])

with t3:
    a, b = st.columns(2)
    cloud = pain_cloud(df)
    if cloud is not None:
        a.pyplot(cloud, use_container_width=True)
    else:
        wf = pd.Series(words_by_star(df, (1, 2), 20)).sort_values().reset_index()
        wf.columns = ["word", "count"]
        a.plotly_chart(style(px.bar(wf, x="count", y="word", orientation="h", title="Top words in 1★–2★ (install `wordcloud` for the cloud)",
                                   color_discrete_sequence=[P["neg"]]), 440), use_container_width=True)
    ng = top_ngrams(df[df["rating"] <= 2]["processed_text"], 2, 12).iloc[::-1]
    b.plotly_chart(style(px.bar(ng, x="count", y="ngram", orientation="h", title="Top complaint phrases (bigrams)",
                                color_discrete_sequence=[P["neg"]]), 440), use_container_width=True)
    th = insights.theme_counts(df)
    st.plotly_chart(style(px.bar(th.iloc[::-1], x="reviews", y="theme", orientation="h", text="reviews", title="Actionable complaint themes",
                                 color="reviews", color_continuous_scale=[P["violet"], P["neg"]]), 360).update_coloraxes(showscale=False),
                    use_container_width=True)
    if len(th):
        pick = st.selectbox("See real reviews for a theme", th["theme"])
        st.dataframe(insights.example_reviews(df, pick, 5), use_container_width=True, hide_index=True)

with t4:
    w = word_rating_correlation(df, top=12)
    if w.empty:
        st.info("Not enough reviews for this view.")
    else:
        fig = px.bar(w, x="r", y="word", orientation="h", color="side", title="Correlation between a word and the star rating",
                     color_discrete_map={"Low ratings": P["neg"], "High ratings": P["pos"]})
        st.plotly_chart(style(fig, 520), use_container_width=True)
    lo, hi = st.columns(2)
    lo.markdown("**TF-IDF · 1★ reviews**"); lo.dataframe(tfidf_terms(df[df["rating"] == 1]["processed_text"]), hide_index=True, use_container_width=True)
    hi.markdown("**TF-IDF · 5★ reviews**"); hi.dataframe(tfidf_terms(df[df["rating"] == 5]["processed_text"]), hide_index=True, use_container_width=True)

with t5:
    q = st.text_input("Search review text")
    sent = st.multiselect("Sentiment", ["Negative", "Neutral", "Positive"], default=["Negative", "Neutral", "Positive"])
    view = df[df["sentiment"].isin(sent)]
    if q:
        view = view[view["review_text"].str.contains(q, case=False, na=False)]
    cols = [c for c in ["date", "rating", "sentiment", "sentiment_score", "app_version", "review_text", "processed_text"] if c in view]
    st.caption(f"{len(view):,} reviews")
    st.dataframe(view[cols], use_container_width=True, hide_index=True)
    st.download_button("Download filtered CSV", view[cols].to_csv(index=False).encode(), "reviews_filtered.csv", "text/csv")
