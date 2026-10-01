"""Phase B – Text Pre-processing: lowercase, noise removal, stop-words, tokenisation, lemmas."""
from __future__ import annotations

import re

import pandas as pd

import config as C

# Negations are KEPT on purpose so bigrams like "not working" / "cant login" survive.
NEGATIONS = {"not", "no", "never", "cant", "cannot", "dont", "doesnt", "didnt", "wont",
             "isnt", "wasnt", "couldnt", "wouldnt", "without", "barely"}

_BASE_STOP = set("""a about above after again all am an and any are arent as at be because been before being below between
both but by can could did do does doing down during each few for from further had has have having he her here hers herself
him himself his how i if in into is it its itself just me more most my myself nor of off on once only or other our ours
ourselves out over own same she should so some such than that the their theirs them themselves then there these they this
those through to too under until up very was we were what when where which while who whom why will with you your yours
yourself yourselves im ive id ill youre youve thats theres hes shes theyre weve isnt arent wasnt werent hasnt havent hadnt
doesnt dont didnt wont wouldnt shouldnt couldnt cant""".split())
_DOMAIN_STOP = {"app", "apps", "application", "please", "pls", "plz", "really", "get", "got", "would", "one",
                "also", "even", "like", "https", "http", "www", "com", "thing", "lot"}
STOPWORDS = (_BASE_STOP | _DOMAIN_STOP | set(C.EXTRA_STOPWORDS)) - NEGATIONS

_URL = re.compile(r"https?://\S+|www\.\S+")
_ED_EXC = {"speed", "need", "feed", "seed", "indeed", "proceed", "exceed", "succeed", "embed", "hundred"}
_ING_EXC = {"thing", "something", "nothing", "anything", "everything", "during", "morning", "evening",
            "string", "spring", "setting", "king", "bring", "ring", "sing"}
_E_ENDINGS = ("at", "iz", "ov", "ak", "ir", "ur", "ut", "ez", "rg", "as", "us", "iv", "ud", "ag", "lv")


def clean_text(text) -> str:
    """Lowercase + strip URLs, emojis, digits and special characters (@ # $ …)."""
    text = str(text).lower().replace("’", "'").replace("‘", "'")
    text = _URL.sub(" ", text)
    text = text.replace("'", "")                # can't -> cant, don't -> dont
    text = re.sub(r"[^a-z\s]", " ", text)       # emojis, punctuation, numbers, @ # $
    return re.sub(r"\s+", " ", text).strip()


def tokenize(text: str) -> list[str]:
    return text.split()


def remove_stopwords(tokens: list[str]) -> list[str]:
    return [t for t in tokens if t not in STOPWORDS and len(t) > 1]


def _restore(stem: str) -> str:
    if len(stem) > 2 and stem[-1] == stem[-2] and stem[-1] in "bdgmnprt":
        return stem[:-1]                         # logg -> log
    return stem + "e" if stem.endswith(_E_ENDINGS) else stem   # updat -> update


def lemmatize_word(w: str) -> str:
    """Light rule-based lemmatiser (no downloads). Swap in NLTK/spaCy for higher accuracy."""
    if len(w) <= 3 or w.endswith(("ss", "us", "is")):
        return w
    if w.endswith("ies") and len(w) > 4:
        return w[:-3] + "y"
    if w.endswith("es") and w[:-2].endswith(("s", "x", "z", "ch", "sh")):
        w = w[:-2]
    elif w.endswith("s"):
        w = w[:-1]
    if w.endswith("ing") and len(w) > 5 and w not in _ING_EXC:
        return _restore(w[:-3])
    if w.endswith("ed") and len(w) > 4 and w not in _ED_EXC:
        return _restore(w[:-2])
    return w


def lemmatize(tokens: list[str]) -> list[str]:
    return [lemmatize_word(t) for t in tokens]


def preprocess_text(text) -> dict:
    clean = clean_text(text)
    tokens = lemmatize(remove_stopwords(tokenize(clean)))
    return {"clean_text": clean, "tokens": tokens, "processed_text": " ".join(tokens)}


def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.dropna(subset=["review_text", "rating"])
    df["review_text"] = df["review_text"].astype(str)
    df["rating"] = df["rating"].astype(int)
    df["date"] = pd.to_datetime(df["date"])
    subset = ["review_id"] if "review_id" in df.columns else ["review_text", "date"]
    df = df.drop_duplicates(subset=subset).reset_index(drop=True)
    parts = df["review_text"].map(preprocess_text).apply(pd.Series)
    df = pd.concat([df, parts], axis=1)
    df["word_count"] = df["tokens"].str.len()
    return df
