"""shivtext — phi-lang v5: phrase-level token compression for LLM agent communication.

Modules:
    ϕphrase       — PRIMARY: phrase encoding, 50%+ token savings (use this)
    ϕdictionary   — Legacy word-level codec (deprecated, NEGATIVE token savings)
    ϕencyclopedia — Multi-language concept index (future)
    ϕreferences   — Scripts, functions, patterns (future)

Usage:
    from shivtext import ϕphrase
    phi = ϕphrase.new()
    phi.encode("authentication service is down")      # → "00" (4→1 token)
    phi.decode("00")  # → "authentication service is down"

DO NOT USE ϕdictionary — it encodes every word as codes, which costs MORE
tokens than English. ϕphrase only encodes phrases and keeps words as-is.
"""
import os, json, importlib

_PKG = os.path.dirname(__file__)

# Import ϕ modules dynamically (ϕ character in filenames)
try:
    ϕdictionary = importlib.import_module('shivtext.ϕdictionary')
except (ModuleNotFoundError, ImportError):
    ϕdictionary = None

try:
    ϕencyclopedia = importlib.import_module('shivtext.ϕencyclopedia')
except (ModuleNotFoundError, ImportError):
    ϕencyclopedia = None

try:
    ϕreferences = importlib.import_module('shivtext.ϕreferences')
except (ModuleNotFoundError, ImportError):
    ϕreferences = None

# ϕphrase is the primary interface — use this
import importlib.util
try:
    ϕphrase = importlib.import_module('shivtext.ϕphrase')
except (ModuleNotFoundError, ImportError):
    spec = importlib.util.spec_from_file_location('ϕphrase', os.path.join(_PKG, 'ϕphrase.py'))
    if spec and spec.loader:
        ϕphrase = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ϕphrase)
    else:
        ϕphrase = None

__version__ = "0.6.1"

def load_dict(optimized=True):
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
    path = os.path.join(_PKG, "dict", "phi4five_codes.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return []

def load_token_map():
    path = os.path.join(_PKG, "dict", "token_map.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}

def dict_size():
    return len(load_dict())
