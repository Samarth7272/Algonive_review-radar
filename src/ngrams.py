"""Phase C (2/3) – N-gram analysis (bigrams by default)."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer


def top_ngrams(texts, n: int = 2, top: int = 15, min_df: int = 2) -> pd.DataFrame:
    """Most frequent n-grams in `texts` (already pre-processed). Returns columns: ngram, count."""
    texts = [t for t in texts if isinstance(t, str) and t.strip()]
    empty = pd.DataFrame(columns=["ngram", "count"])
    if not texts:
        return empty
    try:
        vec = CountVectorizer(ngram_range=(n, n), min_df=min_df if len(texts) >= 20 else 1)
        counts = np.asarray(vec.fit_transform(texts).sum(axis=0)).ravel()
    except ValueError:  # empty vocabulary
        return empty
    out = pd.DataFrame({"ngram": vec.get_feature_names_out(), "count": counts})
    return out.sort_values("count", ascending=False).head(top).reset_index(drop=True)
