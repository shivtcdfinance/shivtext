"""ϕv4 — φ-lang v4 decoder. 3-char base-36 codes, 19,802 words.

Read-only fallback for v4-encoded content (skill paths, legacy files).
v4 uses 3-char codes (36³ = 46,656 capacity) vs v5's 2-char codes.

This is for READING old φ-lang v4 content — not the primary encoder.
Use ϕphrase for new encoding.
"""
import os

_CUR = os.path.dirname(os.path.abspath(__file__))
_DICT_PATH = os.path.join(_CUR, "dict", "v4.dict")

# Load: 3-char code → word
CODE2WORD = {}
WORD2CODE = {}

def _load():
    global CODE2WORD, WORD2CODE
    if CODE2WORD:
        return
    try:
        with open(_DICT_PATH) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    code, word = line.split("=", 1)
                    code = code.strip()
                    word = word.strip()
                    CODE2WORD[code] = word
                    WORD2CODE[word] = code
    except FileNotFoundError:
        pass

def decode_v4(text):
    """Decode v4-encoded 3-char codes back to English words."""
    _load()
    if not text:
        return ""
    tokens = text.strip().split()
    out = []
    for token in tokens:
        word = CODE2WORD.get(token)
        out.append(word if word else token)
    return " ".join(out)

def encode_v4(text):
    """Encode English words to v4 3-char codes. Unknown words pass through."""
    _load()
    if not text:
        return ""
    words = text.strip().split()
    out = []
    for w in words:
        code = WORD2CODE.get(w)
        if code:
            out.append(code)
        else:
            out.append(w)
    return " ".join(out)

def is_v4(text):
    """Check if text looks like v4-encoded content (3-char codes)."""
    if not text:
        return False
    tokens = text.strip().split()
    if not tokens:
        return False
    v4_count = sum(1 for t in tokens if len(t) == 3 and t in CODE2WORD)
    return v4_count > 0 and v4_count / len(tokens) > 0.5

_load()
