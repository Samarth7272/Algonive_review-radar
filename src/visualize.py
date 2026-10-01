"""Phase D – Insights & Visualisation. Dark, colour-coded charts + a one-page Management Summary."""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.gridspec import GridSpec

import config as C
from src import insights
from src.correlation import word_rating_correlation, words_by_star
from src.ngrams import top_ngrams

P = C.PALETTE
SENT_COLORS = {"Negative": P["neg"], "Neutral": P["neu"], "Positive": P["pos"]}
STAR_COLORS = {1: P["neg"], 2: "#FF8A7A", 3: P["neu"], 4: "#7BE8B8", 5: P["pos"]}


def apply_theme() -> None:
    plt.rcParams.update({
        "figure.facecolor": P["bg"], "savefig.facecolor": P["bg"], "axes.facecolor": P["panel"],
        "axes.edgecolor": P["grid"], "axes.labelcolor": P["muted"], "axes.titlecolor": P["text"],
        "axes.titleweight": "bold", "axes.titlesize": 13, "axes.titlelocation": "left", "axes.titlepad": 12,
        "axes.spines.top": False, "axes.spines.right": False, "axes.grid": False,
        "grid.color": P["grid"], "grid.alpha": 0.5, "xtick.color": P["muted"], "ytick.color": P["muted"],
        "text.color": P["text"], "font.size": 10, "legend.frameon": False, "legend.labelcolor": P["muted"],
    })


apply_theme()


def _save(fig, name: str, out_dir: Path | None) -> Path:
    out_dir = Path(out_dir or C.FIG_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / name
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return path


# ---- individual charts (each draws on a given axis so they can be reused) --------------------------
def plot_sentiment_donut(df, ax):
    counts = df["sentiment"].value_counts().reindex(["Positive", "Neutral", "Negative"]).fillna(0)
    ax.pie(counts, colors=[SENT_COLORS[k] for k in counts.index], startangle=90, counterclock=False,
           wedgeprops=dict(width=0.34, edgecolor=P["panel"], linewidth=3))
    ax.text(0, 0.06, f"{counts['Positive'] / max(counts.sum(), 1):.0%}", ha="center", va="center",
            fontsize=26, fontweight="bold", color=P["pos"])
    ax.text(0, -0.2, "satisfied", ha="center", va="center", fontsize=10, color=P["muted"])
    ax.legend([f"{k}  {v / max(counts.sum(), 1):.0%}" for k, v in counts.items()], loc="lower center",
              bbox_to_anchor=(0.5, -0.12), ncol=3, fontsize=9, handlelength=1, columnspacing=1.2)
    ax.set_title("Satisfied vs unsatisfied users")


def plot_rating_bars(df, ax):
    c = df["rating"].value_counts().reindex([1, 2, 3, 4, 5]).fillna(0)
    bars = ax.bar(c.index, c.values, color=[STAR_COLORS[i] for i in c.index], width=0.66)
    for b, v in zip(bars, c.values):
        ax.text(b.get_x() + b.get_width() / 2, v, f"{int(v):,}", ha="center", va="bottom", fontsize=9, color=P["muted"])
    ax.set_xticks([1, 2, 3, 4, 5], ["1★", "2★", "3★", "4★", "5★"])
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_title("Star-rating distribution")


def plot_trend(df, ax, freq: str = "W", markers=None):
    t = insights.sentiment_trend(df, freq)
    if t.empty:
        return
    ax.fill_between(t["date"], t["Negative"], color=P["neg"], alpha=0.16)
    ax.plot(t["date"], t["Negative"], color=P["neg"], lw=2.6, marker="o", ms=4, label="Negative")
    ax.plot(t["date"], t["Positive"], color=P["pos"], lw=2, alpha=0.9, label="Positive")
    ax.set_ylim(0, max(100, t[["Negative", "Positive"]].max().max() * 1.05))
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    ax.grid(axis="y")
    markers = insights.release_markers(df) if markers is None else markers
    top = ax.get_ylim()[1]
    for d, name in markers:
        ax.axvline(d, color=P["violet"], ls="--", lw=1.4)
        ax.text(d, top * 0.97, f" {name}", color=P["violet"], fontsize=9, fontweight="bold", va="top")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.legend(loc="upper left", ncol=2, bbox_to_anchor=(0, 1.0))
    ax.set_title("Sentiment trend – did an update hurt?")


def plot_bigrams(df, ax, stars=(1, 2), top: int = 10):
    ng = top_ngrams(df[df["rating"].isin(stars)]["processed_text"], 2, top)
    if ng.empty:
        ax.text(0.5, 0.5, "not enough data", ha="center", color=P["muted"]); return
    ng = ng.iloc[::-1]
    ax.barh(ng["ngram"], ng["count"], color=P["neg"], height=0.66)
    for y, v in enumerate(ng["count"]):
        ax.text(v, y, f"  {v}", va="center", fontsize=9, color=P["muted"])
    ax.set_xticks([]); ax.spines["bottom"].set_visible(False)
    ax.set_title("Top complaint phrases (bigrams)")


def plot_themes(df, ax):
    th = insights.theme_counts(df).iloc[::-1]
    if th.empty:
        return
    cmap = LinearSegmentedColormap.from_list("pain", [P["violet"], P["neg"]])
    ax.barh(th["theme"], th["reviews"], color=[cmap(i / max(len(th) - 1, 1)) for i in range(len(th))], height=0.66)
    for y, (v, s) in enumerate(zip(th["reviews"], th["share"])):
        ax.text(v, y, f"  {v}  ({s:.0%})", va="center", fontsize=9, color=P["muted"])
    ax.set_xticks([]); ax.spines["bottom"].set_visible(False)
    ax.set_title("What users complain about")


def plot_rating_words(df, ax, top: int = 7):
    w = word_rating_correlation(df, top=top)
    if w.empty:
        ax.text(0.5, 0.5, "not enough data", ha="center", color=P["muted"]); return
    ax.barh(w["word"], w["r"], color=[P["neg"] if r < 0 else P["pos"] for r in w["r"]], height=0.66)
    ax.axvline(0, color=P["grid"], lw=1)
    ax.set_xlabel("← goes with 1★        correlation with rating        goes with 5★ →", fontsize=8)
    ax.set_title("Words that move the rating")


# ---- standalone figures -----------------------------------------------------------------------------
def pain_cloud(df, path: Path | None = None):
    """Word Cloud of Pain – only 1★ and 2★ reviews. Returns a figure (None if wordcloud isn't installed)."""
    try:
        from wordcloud import WordCloud
    except ImportError:
        return None
    freq = words_by_star(df, (1, 2), top=150)
    if not freq:
        return None
    cmap = LinearSegmentedColormap.from_list("pain", [P["violet"], P["neg"], "#FFB3A7"])
    wc = WordCloud(width=1600, height=800, background_color=P["bg"], colormap=cmap, max_words=150,
                   prefer_horizontal=0.9, relative_scaling=0.45, margin=6).generate_from_frequencies(freq)
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.imshow(wc, interpolation="bilinear"); ax.axis("off")
    ax.set_title("Word Cloud of Pain  (1★ & 2★ reviews)", fontsize=16)
    if path:
        fig.savefig(path, dpi=160, bbox_inches="tight")
    return fig


def save_all(df, out_dir: Path | None = None) -> list[Path]:
    paths = []
    for name, fn, size in (("01_sentiment_distribution.png", lambda a: plot_sentiment_donut(df, a), (5, 5)),
                           ("02_rating_distribution.png", lambda a: plot_rating_bars(df, a), (6, 4)),
                           ("03_sentiment_trend.png", lambda a: plot_trend(df, a), (11, 4.5)),
                           ("04_top_bigrams_pain.png", lambda a: plot_bigrams(df, a), (7, 5)),
                           ("05_complaint_themes.png", lambda a: plot_themes(df, a), (7, 5)),
                           ("06_rating_words.png", lambda a: plot_rating_words(df, a, 10), (7, 6))):
        fig, ax = plt.subplots(figsize=size)
        fn(ax)
        paths.append(_save(fig, name, out_dir))
    fig = pain_cloud(df)
    if fig is not None:
        paths.append(_save(fig, "07_word_cloud_of_pain.png", out_dir))
    paths.append(management_summary(df, out_dir))
    return paths


def management_summary(df, out_dir: Path | None = None, app_name: str = "") -> Path:
    """One-page dashboard for managers."""
    k = insights.kpis(df)
    fig = plt.figure(figsize=(19, 12.5))
    gs = GridSpec(3, 6, figure=fig, height_ratios=[0.5, 1.15, 1.15], hspace=0.5, wspace=0.9)
    head = fig.add_subplot(gs[0, :]); head.axis("off")
    head.text(0, 0.78, "Review Radar  ·  Management Summary" + (f"  ·  {app_name}" if app_name else ""),
              fontsize=21, fontweight="bold", color=P["text"], transform=head.transAxes)
    span = f"{df['date'].min():%d %b %Y} – {df['date'].max():%d %b %Y}"
    head.text(0, 0.36, f"{span}  |  sentiment engine: {df.attrs.get('sentiment_method', 'lexicon')}",
              fontsize=11, color=P["muted"], transform=head.transAxes)
    cards = [("Reviews analysed", f"{k['reviews']:,}", P["cyan"]), ("Average rating", f"{k['avg_rating']:.2f} ★", P["neu"]),
             ("Negative reviews", f"{k['pct_negative']:.0f}%", P["neg"]), ("Top complaint", k["top_theme"], P["violet"])]
    for i, (lab, val, col) in enumerate(cards):
        x = 0.58 + i * 0.105
        head.text(x, 0.72, val, fontsize=17 if i < 3 else 12.5, fontweight="bold", color=col, transform=head.transAxes, ha="left")
        head.text(x, 0.3, lab, fontsize=9.5, color=P["muted"], transform=head.transAxes, ha="left")
    plot_sentiment_donut(df, fig.add_subplot(gs[1, 0:2]))
    plot_trend(df, fig.add_subplot(gs[1, 2:6]))
    plot_bigrams(df, fig.add_subplot(gs[2, 0:2]))
    plot_themes(df, fig.add_subplot(gs[2, 2:4]))
    plot_rating_words(df, fig.add_subplot(gs[2, 4:6]))
    worst = insights.worst_release(df)
    if worst:
        d, v, ba = worst
        fig.text(0.125, 0.045, f"Insight: negative reviews jumped from {ba['before']:.0f}% to {ba['after']:.0f}% "
                 f"after release {v} ({d:%d %b %Y}). Check the top complaint phrases above first.",
                 fontsize=12.5, color=P["neg"], fontweight="bold")
    return _save(fig, "00_management_summary.png", out_dir)
