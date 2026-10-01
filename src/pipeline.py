"""One function that runs Phases B + C on a raw reviews DataFrame."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

import config as C
from src.preprocess import preprocess_dataframe
from src.sentiment import score_sentiment

COLUMN_MAP = {"content": "review_text", "review": "review_text", "text": "review_text", "review_body": "review_text",
              "score": "rating", "stars": "rating", "star_rating": "rating", "at": "date", "review_date": "date",
              "reviewCreatedVersion": "app_version", "thumbsUpCount": "thumbs_up", "reviewId": "review_id"}


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={k: v for k, v in COLUMN_MAP.items() if k in df.columns and v not in df.columns})
    missing = {"review_text", "rating", "date"} - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing required column(s): {sorted(missing)}. "
                         "Need review text, star rating and date.")
    return df


def load_csv(path) -> pd.DataFrame:
    return standardize_columns(pd.read_csv(path))


def run(df: pd.DataFrame, method: str = "auto") -> pd.DataFrame:
    df = preprocess_dataframe(standardize_columns(df))
    return score_sentiment(df, method)


def save_processed(df: pd.DataFrame, name: str = "reviews_processed.csv") -> Path:
    C.DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    path = C.DATA_PROCESSED / name
    df.assign(tokens=df["tokens"].str.join(" ")).to_csv(path, index=False)
    return path
