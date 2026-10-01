import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.preprocess import clean_text, lemmatize_word, preprocess_text
from src.sample_data import generate_demo_reviews
from src import pipeline


def test_lowercase_and_noise_removed():
    assert clean_text("Login FAIL 😡 @support #bug $$ https://x.com") == "login fail support bug"


def test_negation_kept_stopwords_removed():
    p = preprocess_text("The app is not working and I can't login")
    assert "not" in p["tokens"] and "cant" in p["tokens"] and "the" not in p["tokens"]


def test_lemmas():
    assert lemmatize_word("crashes") == "crash" and lemmatize_word("updated") == "update"


def test_pipeline_columns():
    df = pipeline.run(generate_demo_reviews(300))
    assert {"processed_text", "sentiment", "rating_sentiment"} <= set(df.columns)
    assert set(df["sentiment"]) <= {"Positive", "Neutral", "Negative"}
