"""shivtext — token-optimized φ-lang toolkit.

Modules:
    ϕdictionary   — 82K words, 3,844 codes, composition learning
    ϕencyclopedia — Multi-language concept index (future)
    ϕreferences   — Scripts, functions, patterns (future)

Usage:
    from shivtext import ϕdictionary
    d = ϕdictionary.new()
    d.encode("hello world")
"""
import os, json, importlib

_PKG = os.path.dirname(__file__)

# Import ϕ modules dynamically (ϕ character in filenames)
ϕdictionary = importlib.import_module('shivtext.ϕdictionary')
ϕencyclopedia = importlib.import_module('shivtext.ϕencyclopedia')
ϕreferences = importlib.import_module('shivtext.ϕreferences')
try:
    ϕphrase = importlib.import_module('shivtext.ϕphrase')
except (ModuleNotFoundError, ImportError):
    spec = importlib.util.spec_from_file_location('ϕphrase', os.path.join(_PKG, 'ϕphrase.py'))
    if spec and spec.loader:
        ϕphrase = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ϕphrase)

__version__ = "0.7.0"

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
