"""Phase C (1/3) – Sentiment scoring: Positive / Neutral / Negative."""
from __future__ import annotations

import math

import pandas as pd

import config as C
from src.preprocess import NEGATIONS, lemmatize_word

_POS = {"good": 1, "great": 1.5, "excellent": 2, "amazing": 2, "awesome": 2, "love": 1.5, "lovely": 1, "perfect": 2,
        "best": 1.5, "nice": 1, "fantastic": 2, "wonderful": 2, "smooth": 1, "fast": 1, "easy": 1, "helpful": 1,
        "useful": 1, "intuitive": 1.5, "clean": 1, "beautiful": 1.5, "reliable": 1.5, "fun": 1, "enjoy": 1,
        "happy": 1.5, "work": 0.5, "worth": 1, "recommend": 1.5, "impressive": 1.5, "superb": 2, "brilliant": 2,
        "seamless": 1.5, "simple": 0.8, "convenient": 1, "stable": 1, "star": 0.5, "solve": 1, "quickly": 0.5}
_NEG = {"bad": 1, "terrible": 2, "awful": 2, "worst": 2, "horrible": 2, "hate": 2, "useless": 2, "waste": 1.5,
        "scam": 2, "crash": 1.5, "bug": 1.2, "buggy": 1.5, "glitch": 1.2, "glitchy": 1.5, "freeze": 1.3, "frozen": 1.3,
        "slow": 1.2, "laggy": 1.3, "lag": 1.2, "broken": 1.5, "fail": 1.5, "failure": 1.5, "error": 1.2, "problem": 1,
        "issue": 1, "annoy": 1.3, "annoying": 1.3, "frustrate": 1.5, "frustrating": 1.5, "disappoint": 1.5,
        "disappointing": 1.5, "expensive": 1.2, "overpriced": 1.5, "ripoff": 2, "stuck": 1.2, "unusable": 2,
        "uninstall": 1.5, "unresponsive": 1.5, "confuse": 1.2, "confusing": 1.2, "cluttered": 1.2, "intrusive": 1.3,
        "poor": 1.2, "worse": 1.5, "garbage": 2, "trash": 2, "ridiculous": 1.5, "refund": 1, "overcharge": 1.5,
        "spam": 1.3, "drain": 1.2, "suck": 1.5, "invalid": 1, "never": 0.5, "ad": 0.6, "cancel": 0.8, "forever": 0.8}


def _lexicon(text: str) -> float:
    toks, total = text.split(), 0.0
    for i, t in enumerate(toks):
        lem = lemmatize_word(t)
        v = _POS.get(t, _POS.get(lem, 0)) - _NEG.get(t, _NEG.get(lem, 0))
        if v and any(p in NEGATIONS for p in toks[max(0, i - 3):i]):
            v = -0.8 * v
        total += v
    return math.tanh(total / 2)


def _textblob(text: str) -> float:
    from textblob import TextBlob
    return TextBlob(text).sentiment.polarity


def _vader(text: str) -> float:
    from nltk.sentiment import SentimentIntensityAnalyzer  # needs nltk.download("vader_lexicon")
    return SentimentIntensityAnalyzer().polarity_scores(text)["compound"]


def available_methods() -> list[str]:
    out = ["lexicon"]
    for name, mod in (("textblob", "textblob"), ("vader", "nltk")):
        try:
            __import__(mod)
            out.append(name)
        except ImportError:
            pass
    return out


def label(score: float) -> str:
    return "Positive" if score > C.POS_THRESHOLD else "Negative" if score < C.NEG_THRESHOLD else "Neutral"


def score_sentiment(df: pd.DataFrame, method: str = "auto") -> pd.DataFrame:
    """Adds sentiment_score, sentiment (text based) and rating_sentiment (star based)."""
    df = df.copy()
    if method == "auto":
        method = "textblob" if "textblob" in available_methods() else "lexicon"
    if method == "textblob":
        df["sentiment_score"] = df["review_text"].map(_textblob)
    elif method == "vader":
        df["sentiment_score"] = df["review_text"].map(_vader)
    else:
        df["sentiment_score"] = df["clean_text"].map(_lexicon)
    df["sentiment"] = df["sentiment_score"].map(label)
    df["rating_sentiment"] = df["rating"].map(lambda r: "Negative" if r <= 2 else "Neutral" if r == 3 else "Positive")
    df.attrs["sentiment_method"] = method
    return df
