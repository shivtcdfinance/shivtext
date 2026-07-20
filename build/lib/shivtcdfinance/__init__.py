"""shivtcdfinance — token-optimized dictionary for φ-lang v4-five.

82,834 English words ranked by LLM token efficiency.
Dictionary → instant vocabulary for phi-lang codec.
Encyclopaedia → multi-language concept index (future).
Reference → scripts, functions, patterns (future).

Usage:
    import shivtcdfinance
    words = shivtcdfinance.load_dict()  # → list of 82,834 words
"""
import os, json

__version__ = "0.1.0"
_PKG = os.path.dirname(__file__)

def load_dict(optimized=True):
    """Return all dictionary words, token-optimized order by default."""
    name = "frequency_dictionary_en_82_765_opt.txt" if optimized else "frequency_dictionary_en_82_765.txt"
    path = os.path.join(_PKG, "dict", name)
    if not os.path.exists(path):
        return []
    words = []
    with open(path) as f:
        for line in f:
            parts = line.strip().split()
            if parts:
                words.append(parts[0])
    return words

def load_codes():
    """Return token-safe 2-char code table."""
    path = os.path.join(_PKG, "dict", "phi4five_codes.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return []

def load_token_map():
    """Return word → {rank, tokens} mapping."""
    path = os.path.join(_PKG, "dict", "token_map.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}

def dict_size():
    """Number of words in the dictionary."""
    return len(load_dict())
