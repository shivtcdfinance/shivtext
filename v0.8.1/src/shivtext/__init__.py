"""shivtext — phrase-level token compression for agent communication.

Modules:
    ϕphrase       — Phrase encoder. Maps common phrases to short codes.
    ϕdictionary   — Word-level codec (82K words, composition learning).
    ϕencyclopedia — Multi-language concept index (future).
    ϕreferences   — Scripts, functions, patterns (future).

Usage:
    from shivtext import ϕphrase
    phi = ϕphrase.new()
    phi.encode("authentication service is down")  # -> "00"
    phi.decode("00")  # -> "authentication service is down"
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

# Import ϕ modules
import importlib
try:
    ϕphrase = importlib.import_module('shivtext.ϕphrase')
except (ModuleNotFoundError, ImportError):
    ϕphrase = None

__version__ = "0.8.1"

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
