"""Phase A – Data Collection. Fetch reviews from the Google Play Store."""
from __future__ import annotations

import time
from pathlib import Path

import pandas as pd

import config as C


def fetch_reviews(app_id: str = C.APP_ID, count: int = C.REVIEW_COUNT,
                  lang: str = C.LANG, country: str = C.COUNTRY) -> pd.DataFrame:
    """Download up to `count` newest reviews. Needs `pip install google-play-scraper`."""
    from google_play_scraper import Sort, reviews  # imported lazily so the rest works offline

    collected, token = [], None
    while len(collected) < count:
        batch, token = reviews(
            app_id, lang=lang, country=country, sort=Sort.NEWEST,
            count=min(200, count - len(collected)), continuation_token=token,
        )
        collected.extend(batch)
        print(f"  fetched {len(collected):,}/{count:,}")
        if not batch or token is None or getattr(token, "token", True) is None:
            break
        time.sleep(0.5)  # be polite to the store

    df = pd.DataFrame(collected)
    keep = ["reviewId", "content", "score", "at", "thumbsUpCount", "reviewCreatedVersion"]
    df = df[[c for c in keep if c in df.columns]].rename(columns={
        "reviewId": "review_id", "content": "review_text", "score": "rating",
        "at": "date", "thumbsUpCount": "thumbs_up", "reviewCreatedVersion": "app_version",
    })
    return df


def save_raw(df: pd.DataFrame, app_id: str = C.APP_ID) -> Path:
    C.DATA_RAW.mkdir(parents=True, exist_ok=True)
    path = C.DATA_RAW / f"{app_id}_reviews.csv"
    df.to_csv(path, index=False)
    return path
