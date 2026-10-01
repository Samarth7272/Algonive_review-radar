# 📡 Review Radar
**Algonive Data Science Task 3** – find the real reasons behind user frustration without reading thousands of app-store reviews.

Reviews in → *actionable complaints* out: cleaned text, sentiment, complaint bigrams, complaint themes, rating-correlated words, an update-impact trend and a one-page management summary.

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m textblob.download_corpora                     # one-time, for TextBlob sentiment

python main.py --demo                                   # offline demo, writes charts to reports/figures/
streamlit run app.py                                    # interactive dashboard
```
Real data:
```bash
python main.py --scrape --app-id com.spotify.music --count 3000    # Phase A: Google Play
python main.py --input data/raw/your_file.csv                      # any CSV with review_text, rating, date
```
Set your app in `config.py` (`APP_ID`, `REVIEW_COUNT`, optional `UPDATE_DATES`).

## Project structure
```
review-radar/
├── app.py               Streamlit dashboard (dark theme, 5 tabs)
├── main.py              CLI pipeline (scrape/load → clean → sentiment → charts)
├── config.py            app id, thresholds, colour palette
├── src/
│   ├── scraper.py       Phase A  – google-play-scraper → DataFrame/CSV
│   ├── preprocess.py    Phase B  – lowercase, noise removal, stop-words, tokenise, lemmatise
│   ├── sentiment.py     Phase C  – Positive / Neutral / Negative (TextBlob, VADER or built-in lexicon)
│   ├── ngrams.py        Phase C  – bigram analysis
│   ├── correlation.py   Phase C  – word↔rating correlation, TF-IDF, 1★ vs 5★ words
│   ├── insights.py      Phase D  – KPIs, complaint themes, release markers, before/after
│   ├── visualize.py     Phase D  – trend, word cloud of pain, distribution, management summary
│   ├── pipeline.py      glue: standardise columns → preprocess → sentiment
│   └── sample_data.py   synthetic demo reviews
├── data/raw · data/processed          inputs / outputs (CSV)
├── reports/figures                    generated PNG charts
├── notebooks/exploration.ipynb        your playground
└── tests/                             unit tests
```

## Task checklist (from the brief)
| Brief requirement | Where |
|---|---|
| Review text, star rating, date from 1,000+ reviews | `src/scraper.py` |
| Lowercase, noise removal, stop-words, tokenisation, lemmatisation | `src/preprocess.py` |
| Positive / Neutral / Negative scoring | `src/sentiment.py` |
| Bigrams ("login fail") | `src/ngrams.py` |
| Words in 1★ vs 5★ reviews, TF-IDF | `src/correlation.py` |
| Trend line around updates | `plot_trend` (auto-detects app versions) |
| Word Cloud of Pain (1★–2★ only) | `pain_cloud` |
| Satisfied vs unsatisfied distribution | `plot_sentiment_donut`, `plot_rating_bars` |
| Management Summary | `reports/figures/00_management_summary.png` |

## Make it yours
- New complaint category → add a regex to `THEMES` in `src/insights.py`.
- Words to ignore → `EXTRA_STOPWORDS` in `config.py`.
- Colours → `PALETTE` in `config.py` (also `.streamlit/config.toml`).
- Non-English reviews: the cleaner keeps only a–z; adapt `clean_text` for other scripts.
- Tableau: import `data/processed/reviews_processed.csv`.

Run tests: `pytest tests`
