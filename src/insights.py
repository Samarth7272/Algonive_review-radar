"""Phase D helpers – KPIs, complaint themes, release markers, before/after comparison."""
from __future__ import annotations

import re

import pandas as pd

import config as C

# "Actionable complaint" themes. Add your own keyword patterns (regex on the cleaned text).
THEMES = {
    "Bugs & crashes": r"\b(?:crash\w*|bug\w*|glitch\w*|freez\w*|froze\w*|error\w*|broken|fix)\b",
    "Login & account": r"\b(?:login|log in|sign in|signin|password|verification|otp|account|logged out)\b",
    "Pricing & billing": r"\b(?:expensive|overpriced|price\w*|subscription|charge\w*|refund\w*|paywall|billing|cost\w*|pay)\b",
    "UI & usability": r"\b(?:confus\w*|interface|design|layout|menu|navigate|navigation|cluttered|ui|ux|button\w*)\b",
    "Speed & battery": r"\b(?:slow|lag\w*|loading|load|battery|drain\w*|heat\w*|forever)\b",
    "Ads": r"\b(?:ad|ads|advert\w*|popup\w*|intrusive)\b",
    "Customer support": r"\b(?:support|reply|replies|response|respond\w*|customer service|helpdesk)\b",
}


def theme_flags(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({name: df["clean_text"].str.contains(rx, regex=True) for name, rx in THEMES.items()})


def theme_counts(df: pd.DataFrame, negative_only: bool = True) -> pd.DataFrame:
    """How many negative reviews mention each complaint theme."""
    sub = df[df["sentiment"].eq("Negative") | df["rating"].le(2)] if negative_only else df
    if sub.empty:
        return pd.DataFrame(columns=["theme", "reviews", "share"])
    counts = theme_flags(sub).sum().sort_values(ascending=False)
    out = counts.rename_axis("theme").reset_index(name="reviews")
    out["share"] = out["reviews"] / len(sub)
    return out


def kpis(df: pd.DataFrame) -> dict:
    themes = theme_counts(df)
    return {
        "reviews": len(df),
        "avg_rating": float(df["rating"].mean()) if len(df) else 0.0,
        "pct_negative": float((df["sentiment"] == "Negative").mean() * 100) if len(df) else 0.0,
        "pct_positive": float((df["sentiment"] == "Positive").mean() * 100) if len(df) else 0.0,
        "top_theme": themes.iloc[0]["theme"] if len(themes) and themes.iloc[0]["reviews"] else "–",
    }


def sentiment_trend(df: pd.DataFrame, freq: str = "W") -> pd.DataFrame:
    """Share of Negative/Neutral/Positive reviews per period (D, W or M)."""
    g = df.set_index("date").groupby([pd.Grouper(freq="MS" if freq == "M" else freq), "sentiment"]).size().unstack(fill_value=0)
    for col in ("Negative", "Neutral", "Positive"):
        if col not in g:
            g[col] = 0
    total = g[["Negative", "Neutral", "Positive"]].sum(axis=1)
    out = g[["Negative", "Neutral", "Positive"]].div(total.where(total > 0), axis=0) * 100
    out["reviews"] = total
    return out.dropna().reset_index()


def release_markers(df: pd.DataFrame, max_markers: int = 6) -> list[tuple[pd.Timestamp, str]]:
    """Update dates: manual (config.UPDATE_DATES) or the first day each app_version appears."""
    if C.UPDATE_DATES:
        return [(pd.Timestamp(d), "update") for d in C.UPDATE_DATES]
    if "app_version" not in df or df["app_version"].isna().all():
        return []
    first = df.dropna(subset=["app_version"]).groupby("app_version")["date"].min().sort_values()
    counts = df["app_version"].value_counts()
    first = first[[counts.get(v, 0) >= max(10, len(df) * 0.02) for v in first.index]]  # ignore tiny versions
    return [(d.normalize(), f"v{str(v).lstrip('v')}") for v, d in first.tail(max_markers).items()][1:] if len(first) > 1 else []


def before_after(df: pd.DataFrame, date) -> dict:
    """Negative-review share before vs after a given date (e.g. an update)."""
    date = pd.Timestamp(date)
    b, a = df[df["date"] < date], df[df["date"] >= date]
    pb = float((b["sentiment"] == "Negative").mean() * 100) if len(b) else float("nan")
    pa = float((a["sentiment"] == "Negative").mean() * 100) if len(a) else float("nan")
    return {"before": pb, "after": pa, "change": pa - pb, "n_before": len(b), "n_after": len(a)}


def worst_release(df: pd.DataFrame):
    """Release marker with the largest jump in negative share (None if no markers)."""
    best = None
    for d, v in release_markers(df):
        ba = before_after(df, d)
        if ba["n_before"] >= 20 and ba["n_after"] >= 20 and (best is None or ba["change"] > best[2]["change"]):
            best = (d, v, ba)
    return best


def example_reviews(df: pd.DataFrame, theme: str, k: int = 3) -> pd.DataFrame:
    neg = df[df["sentiment"].eq("Negative") | df["rating"].le(2)]
    hit = neg[neg["clean_text"].str.contains(THEMES[theme], regex=True)]
    sort_col = "thumbs_up" if "thumbs_up" in hit else "rating"
    return hit.sort_values(sort_col, ascending=False).head(k)[["date", "rating", "review_text"]]
