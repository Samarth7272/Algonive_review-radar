"""Central settings for Review Radar. Edit this file to point the project at your own app."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
FIG_DIR = ROOT / "reports" / "figures"

# ---- Phase A: data collection ---------------------------------------------
APP_ID = "com.spotify.music"   # Google Play package name (any app with 1,000+ reviews)
REVIEW_COUNT = 3000            # how many reviews to fetch
LANG, COUNTRY = "en", "us"

# Optional: mark known release dates on the trend chart, e.g. ["2026-08-15"].
# If empty, release dates are detected automatically from the app_version column.
UPDATE_DATES: list[str] = []

# ---- Phase B: pre-processing ----------------------------------------------
EXTRA_STOPWORDS: set[str] = set()   # add words you never want in the analysis

# ---- Phase C: sentiment ---------------------------------------------------
POS_THRESHOLD = 0.05
NEG_THRESHOLD = -0.05

# ---- Look & feel ----------------------------------------------------------
PALETTE = {
    "bg": "#0B1020",
    "panel": "#141B34",
    "panel_alt": "#1C2545",
    "grid": "#2A3358",
    "text": "#E8ECF7",
    "muted": "#8B95B8",
    "violet": "#7C5CFF",
    "cyan": "#35C8FF",
    "pos": "#2EE6A6",
    "neu": "#FFB547",
    "neg": "#FF5D73",
}
