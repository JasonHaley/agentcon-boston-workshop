import re
from pathlib import Path

def load_stopwords(*paths: str) -> set[str]:
    words = set()
    for p in paths:
        for line in Path(p).read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if s and not s.startswith("#"):
                words.add(s.lower())
    return words

WORD_RE = re.compile(r"[A-Za-z][A-Za-z'-]*")

def clean_text(text: str, stop: set[str]) -> str:
    tokens = [t.lower() for t in WORD_RE.findall(text)]
    kept = [t for t in tokens if t not in stop]
    return " ".join(kept)