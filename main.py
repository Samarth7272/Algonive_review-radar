"""Review Radar command-line runner.

  python main.py --demo                      # offline demo with synthetic reviews
  python main.py --scrape --app-id com.x.y   # download reviews from Google Play, then analyse
  python main.py --input data/raw/file.csv   # analyse an existing CSV
"""
import argparse

import config as C
from src import insights, pipeline
from src.ngrams import top_ngrams
from src.sample_data import generate_demo_reviews
from src.visualize import save_all


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--demo", action="store_true", help="use synthetic demo data")
    ap.add_argument("--scrape", action="store_true", help="fetch reviews from Google Play")
    ap.add_argument("--input", help="path to a reviews CSV")
    ap.add_argument("--app-id", default=C.APP_ID)
    ap.add_argument("--count", type=int, default=C.REVIEW_COUNT)
    ap.add_argument("--method", default="auto", choices=["auto", "lexicon", "textblob", "vader"])
    a = ap.parse_args()

    if a.scrape:
        from src.scraper import fetch_reviews, save_raw
        print(f"Scraping {a.count:,} reviews of {a.app_id} …")
        raw = fetch_reviews(a.app_id, a.count)
        print("Saved raw data →", save_raw(raw, a.app_id))
    elif a.input:
        raw = pipeline.load_csv(a.input)
    else:
        print("No source given – running on demo data (use --scrape or --input for real reviews).")
        raw = generate_demo_reviews()

    df = pipeline.run(raw, a.method)
    print("Processed data →", pipeline.save_processed(df))
    k = insights.kpis(df)
    print(f"\n{k['reviews']:,} reviews | avg {k['avg_rating']:.2f}★ | {k['pct_negative']:.0f}% negative | top complaint: {k['top_theme']}")
    print("\nTop complaint bigrams (1★–2★):")
    print(top_ngrams(df[df['rating'] <= 2]['processed_text'], 2, 8).to_string(index=False))
    w = insights.worst_release(df)
    if w:
        print(f"\nBiggest negative jump: {w[1]} on {w[0]:%Y-%m-%d} ({w[2]['before']:.0f}% → {w[2]['after']:.0f}%)")
    print("\nCharts saved:"); [print("  ", p) for p in save_all(df)]


if __name__ == "__main__":
    main()
