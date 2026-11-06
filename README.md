<div align="center">

# 📡 Review Radar

### Turn thousands of app-store reviews into clear, actionable user complaints

*An end-to-end NLP and data analytics pipeline with an interactive dashboard, built for Algonive Data Science Task 3.*



![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)




![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit&logoColor=white)




![NLP](https://img.shields.io/badge/NLP-TextBlob%20%7C%20TF--IDF-green)




![Tests](https://img.shields.io/badge/Tests-pytest-0A9EDC?logo=pytest&logoColor=white)



[📧 Hire Me](mailto:samarthworldwide@gmail.com) · [💼 LinkedIn](https://www.linkedin.com/in/samarth-shukla-b72003293) · [🐙 GitHub](https://github.com/Samarth7272)

</div>

---

## 🎯 The Problem

Product teams receive thousands of app-store reviews, and nobody has time to read them all. The real reasons users are frustrated stay buried.

**Review Radar** solves this. It takes raw reviews and produces:

- 🧹 Cleaned, analysis-ready text
- 😀😐😡 Positive / Neutral / Negative sentiment
- 🔎 Complaint bigrams (e.g. *"login fail"*) and complaint themes
- 📊 Words most correlated with 1★ vs 5★ ratings
- 📈 An update-impact trend line showing how each release affected ratings
- 📄 A one-page **management summary** for non-technical stakeholders

---

## ✨ Key Features

| Feature | Description |
|---|---|
| **Review scraping** | Pulls review text, star rating and date for 1,000+ reviews from Google Play |
| **Text preprocessing** | Lowercasing, noise removal, stop-word removal, tokenisation, lemmatisation |
| **Sentiment analysis** | Positive / Neutral / Negative scoring for every review |
| **Bigram analysis** | Surfaces recurring complaint phrases |
| **Rating correlation** | Compares words in 1★ vs 5★ reviews, using TF-IDF |
| **Complaint themes** | Regex-based categorisation of complaints, easy to extend |
| **Update-impact trend** | Detects app versions automatically and plots ratings around each release |
| **Word cloud of pain** | Visualises language from 1★–2★ reviews only |
| **Interactive dashboard** | Dark-themed Streamlit app with 5 tabs |
| **Management summary** | Auto-generated one-page PNG report |

---

## 🧠 How It Works

```
Reviews ─► Scrape/Load ─► Clean Text ─► Sentiment ─► N-grams & TF-IDF ─► Insights ─► Dashboard + Report
          (Phase A)       (Phase B)     (Phase C)     (Phase C)          (Phase D)    (Phase D)
```

---

## 🛠️ Tech Stack

- **Language:** Python
- **Data:** Pandas, NumPy
- **NLP:** TextBlob, NLTK, TF-IDF (scikit-learn)
- **Scraping:** google-play-scraper
- **Visualisation:** Matplotlib, WordCloud, Streamlit
- **Testing:** pytest
- **BI-ready:** Processed CSV can be imported into Tableau

---

## 🚀 Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/Samarth7272/Algonive_review-radar.git
cd Algonive_review-radar

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
python -m textblob.download_corpora   # one-time

# 4. Run the demo (offline, uses synthetic reviews)
python main.py --demo

# 5. Launch the interactive dashboard
streamlit run app.py
```

### Run on real data

```bash
# Scrape live reviews from Google Play
python main.py --scrape --app-id com.spotify.music --count 3000

# Or analyse your own CSV
python main.py --input data/raw/your_file.csv
```

Set your target app in `config.py` (`APP_ID`, `REVIEW_COUNT`, optional `UPDATE_DATES`).

---

## 📁 Project Structure

```
review-radar/
├── app.py               Streamlit dashboard (dark theme, 5 tabs)
├── main.py              CLI pipeline (scrape/load → clean → sentiment → insights)
├── config.py            App ID, thresholds, colour palette
├── src/
│   ├── scraper.py       Phase A – google-play-scraper → DataFrame
│   ├── preprocess.py    Phase B – lowercase, noise removal, stop-words, lemmatisation
│   ├── sentiment.py     Phase C – Positive / Neutral / Negative scoring
│   ├── ngrams.py        Phase C – bigram analysis
│   ├── correlation.py   Phase C – word ↔ rating correlation, TF-IDF
│   ├── insights.py      Phase D – KPIs, complaint themes, release impact
│   ├── visualize.py     Phase D – trend, word cloud, distributions
│   ├── pipeline.py      Glue: standardise columns → preprocess → analyse
│   └── sample_data.py   Synthetic demo reviews
├── data/raw · data/processed    Inputs / outputs (CSV)
├── reports/figures/     Generated PNG charts
├── notebooks/exploration.ipynb  Exploration playground
└── tests/               Unit tests
```

---

## ✅ Project Requirements Covered

| Requirement | Implementation |
|---|---|
| Review text, star rating, date from 1,000+ reviews | `src/scraper.py` |
| Lowercasing, noise removal, stop-words, tokenisation, lemmatisation | `src/preprocess.py` |
| Positive / Neutral / Negative scoring | `src/sentiment.py` |
| Bigrams (e.g. "login fail") | `src/ngrams.py` |
| Words in 1★ vs 5★ reviews, TF-IDF | `src/correlation.py` |
| Trend line around updates | `plot_trend` (auto-detects app versions) |
| Word Cloud of Pain (1★–2★) | `pain_cloud` |
| Satisfied vs unsatisfied distribution | `plot_sentiment_donut`, `plot_rating_bars` |
| Management summary | `reports/figures/00_management_summary.png` |

---

## 🔧 Customisation

- **New complaint category:** add a regex to `THEMES` in `src/insights.py`
- **Words to ignore:** edit `EXTRA_STOPWORDS` in `config.py`
- **Colours:** edit `PALETTE` in `config.py` and `.streamlit/config.toml`
- **Non-English reviews:** the cleaner keeps only a–z, so adapt `clean_text` for other scripts
- **Tableau:** import `data/processed/reviews_processed.csv`

---

## 🧪 Testing

```bash
pytest tests
```

---

## 🔮 Future Improvements

- Transformer-based sentiment (e.g. BERT / VADER comparison)
- Topic modelling with LDA or BERTopic
- Multi-language review support
- App Store (iOS) scraping
- Deploy the dashboard on Streamlit Community Cloud

---

## 👨‍💻 About the Author

**Samarth Shukla** is a B.Tech Computer Science student (2027) and Software Engineer Intern. He works with Python, AI/ML, NLP, and backend development (REST APIs, OAuth 2.0, Next.js, TypeScript, PostgreSQL).

This project shows I can take a messy real-world problem and deliver a complete solution: data collection, NLP, analysis, an interactive dashboard, testing, and a report that non-technical managers can use.

### 💼 Open to Opportunities

I'm actively looking for **Software Engineer, Data Science, AI/ML and Backend** roles (full-time and internships). If this project impressed you, I'd love to talk.

[

![Email](https://img.shields.io/badge/Email-samarthworldwide%40gmail.com-D14836?logo=gmail&logoColor=white)

](mailto:samarthworldwide@gmail.com)
[

![LinkedIn](https://img.shields.io/badge/LinkedIn-Samarth%20Shukla-0A66C2?logo=linkedin&logoColor=white)

](https://www.linkedin.com/in/samarth-shukla-b72003293)
[

![GitHub](https://img.shields.io/badge/GitHub-Samarth7272-181717?logo=github&logoColor=white)

](https://github.com/Samarth7272)

📧 **Contact:** samarthworldwide@gmail.com

---

<div align="center">

⭐ If you found this project useful, please give it a star!

*Built as part of the Algonive Data Science Internship, Task 3.*

</div>
