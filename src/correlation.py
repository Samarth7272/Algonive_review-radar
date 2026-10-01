"""Phase C (3/3) – Rating correlation & TF-IDF: which words live in 1-star vs 5-star reviews?"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from src.preprocess import NEGATIONS


def word_rating_correlation(df: pd.DataFrame, min_df: int = 5, top: int = 12) -> pd.DataFrame:
    """Correlation between 'word appears in review' and star rating.
    Negative r  -> word goes with low ratings (pain word); positive r -> goes with high ratings."""
    docs = df["processed_text"].fillna("")
    if docs.str.strip().eq("").all() or len(df) < 10:
        return pd.DataFrame(columns=["word", "r", "side"])
    vec = CountVectorizer(binary=True, min_df=min(min_df, max(1, len(df) // 50)))
    X = vec.fit_transform(docs)
    y = df["rating"].to_numpy(dtype=float)
    n = len(y)
    mx = np.asarray(X.mean(axis=0)).ravel()
    cov = np.asarray(X.T @ y).ravel() / n - mx * y.mean()
    sd = np.sqrt(np.maximum(mx * (1 - mx), 1e-12)) * y.std()
    out = pd.DataFrame({"word": vec.get_feature_names_out(), "r": cov / np.maximum(sd, 1e-12)})
    out = out[~out["word"].isin(NEGATIONS)]
    pick = pd.concat([out.nsmallest(top, "r"), out.nlargest(top, "r")]).drop_duplicates("word")
    pick["side"] = np.where(pick["r"] < 0, "Low ratings", "High ratings")
    return pick.sort_values("r").reset_index(drop=True)


def tfidf_terms(texts, top: int = 15) -> pd.DataFrame:
    """Top TF-IDF terms (mean weight) for a group of reviews."""
    texts = [t for t in texts if isinstance(t, str) and t.strip()]
    if len(texts) < 2:
        return pd.DataFrame(columns=["term", "tfidf"])
    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2 if len(texts) > 20 else 1)
    try:
        X = vec.fit_transform(texts)
    except ValueError:
        return pd.DataFrame(columns=["term", "tfidf"])
    out = pd.DataFrame({"term": vec.get_feature_names_out(), "tfidf": np.asarray(X.mean(axis=0)).ravel()})
    return out.sort_values("tfidf", ascending=False).head(top).reset_index(drop=True)


def words_by_star(df: pd.DataFrame, stars, top: int = 100) -> dict[str, int]:
    """Word frequencies for the given star ratings (used for the Word Cloud of Pain)."""
    sub = df[df["rating"].isin(stars)]
    freq: dict[str, int] = {}
    for toks in sub["tokens"]:
        for t in toks:
            if t not in NEGATIONS:
                freq[t] = freq.get(t, 0) + 1
    return dict(sorted(freq.items(), key=lambda kv: -kv[1])[:top])
