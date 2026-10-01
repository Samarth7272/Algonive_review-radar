"""Synthetic demo reviews so the whole project runs offline (and for testing)."""
from __future__ import annotations

import numpy as np
import pandas as pd

POS = ["Love this app, works perfectly 😍", "Super smooth and easy to use", "Great update, everything feels fast!",
       "Best app in its category, totally worth it", "Clean interface, very intuitive 👍",
       "Does exactly what I need, highly recommend", "Excellent support team solved my problem quickly",
       "Beautiful design and reliable. Five stars ⭐⭐⭐⭐⭐"]
NEU = ["It's okay, does the job.", "Average app, nothing special.", "Decent but could use more features.",
       "Works fine most days, some features are missing.", "Not bad, not great either."]
NEG = {
    "login": ["Login fail every time I open the app", "Can't login after the update, says invalid password",
              "Login failed again, had to reset my password 3 times", "Stuck on the sign in screen, verification code never arrives"],
    "crash": ["App keeps crashing on startup", "Crashes every time I open settings, please fix this bug",
              "Constant freezing and crashes since the last update", "Full of bugs and glitches after the new version"],
    "pricing": ["Subscription is way too expensive for what you get", "Charged twice for my subscription, want a refund!",
                "Paywall everywhere, overpriced premium plan", "Price increase is ridiculous, cancelling my subscription"],
    "ui": ["Confusing interface, can't find anything", "New design is cluttered and hard to navigate",
           "Terrible UI, buttons are too small", "Why did you move the menu? Very confusing layout"],
    "performance": ["So slow and laggy, takes forever to load", "Drains my battery and heats up my phone",
                    "Loading screen takes ages, very slow", "Laggy scrolling, unusable on my phone"],
    "ads": ["Too many ads, constant popups $$$", "Ads every 30 seconds, so annoying", "Intrusive ads ruined the experience"],
    "support": ["Customer support never replies to my emails", "No response from support for two weeks",
                "Support is useless, just copy paste answers"],
}
SUFFIX = ["", "", "", " Please fix!!", " #disappointed", " @support", " https://example.com/help"]
VERSIONS = [("4.1.0", 0), ("4.2.0", 55), ("4.3.0", 105), ("4.4.0", 140)]  # (version, day offset); 4.4.0 is the bad release


def generate_demo_reviews(n: int = 1800, seed: int = 42, end: str = "2026-09-28") -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    end_ts = pd.Timestamp(end)
    days = rng.integers(0, 180, n)
    rows = []
    themes = list(NEG)
    for i, d in enumerate(days):
        date = end_ts - pd.Timedelta(days=int(179 - d)) + pd.Timedelta(seconds=int(rng.integers(0, 86400)))
        version = [v for v, off in VERSIONS if d >= off][-1]
        bad = d >= 140
        p_neg = 0.55 if bad else 0.22
        r = rng.random()
        if r < p_neg:
            w = np.array([.34, .30, .08, .08, .08, .06, .06]) if bad else np.array([.06, .08, .28, .18, .16, .14, .10])
            theme = rng.choice(themes, p=w / w.sum())
            text = rng.choice(NEG[theme]) + rng.choice(SUFFIX)
            rating = int(rng.choice([1, 1, 1, 2]))
        elif r < p_neg + 0.12:
            text, rating = rng.choice(NEU), 3
        else:
            text, rating = rng.choice(POS), int(rng.choice([5, 5, 5, 4]))
        rows.append((f"demo-{i:05d}", text, rating, date, int(rng.integers(0, 40)), version))
    return pd.DataFrame(rows, columns=["review_id", "review_text", "rating", "date", "thumbs_up", "app_version"])
