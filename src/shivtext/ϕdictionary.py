"""ϕdictionary — DEPRECATED. Use ϕphrase instead.

WARNING: This encodes EVERY word as 2-char codes, costing MORE LLM tokens
than English. Use ϕphrase for phrase-only encoding (50%+ savings).

Usage:
    from shivtext import ϕphrase
    phi = ϕphrase.new()
    phi.encode("hello world")
"""
import os, json

# ── Code table ──
_CODES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dict", "phi4five_codes.json")
with open(_CODES) as f:
    CODES = json.load(f)
CODE_COUNT = len(CODES)
C2I = {c: i for i, c in enumerate(CODES)}

def _e(n):
    return CODES[n] if n < CODE_COUNT else '??'

def _d(c):
    return C2I.get(c, -1)

# ── Load dictionary ──

_DICT_WORDS = None
_DICT_W2I = None

def _load():
    global _DICT_WORDS, _DICT_W2I
    if _DICT_WORDS is not None:
        return _DICT_WORDS, _DICT_W2I
    words, w2i = [], {}
    try:
        import shivtext as sf
        for i, word in enumerate(sf.load_dict()):
            words.append(word)
            w2i[word] = i
    except ImportError:
        pass
    _DICT_WORDS, _DICT_W2I = words, w2i
    return words, w2i

_DICT_WORDS, _DICT_W2I = None, None
PRELOAD = None
CACHE_PATH = os.path.expanduser("~/.hermes/ϕdictionary_state.json")


def new(load_cache=False):
    """Create a new dictionary session. Pre-loads 3,644 token-optimized words."""
    global PRELOAD, _DICT_WORDS
    if _DICT_WORDS is None:
        _load()
    if PRELOAD is None:
        PRELOAD = min(len(_DICT_WORDS), CODE_COUNT - 200)
    s = {
        'series': [],
        'v2s': {},
        'delta': [],
        'freq': {},
        'threshold': 3,
        '_preloaded': 0,
    }

    for word in _DICT_WORDS[:PRELOAD]:
        sn = len(s['series'])
        s['series'].append(word)
        s['v2s'][str(word)] = sn
    s['_preloaded'] = len(s['series'])

    if load_cache:
        _load_cache(s)

    return _Session(s)


class _Session:
    """Internal session wrapper - use φdictionary.new(), not this directly."""

    def __init__(self, s):
        self._s = s

    def encode(self, text):
        s = self._s
        if not text or not text.strip():
            return ''

        words = text.strip().split()
        tokens = [self._assign(w) for w in words]
        self._learn(tokens)

        out, i = [], 0
        while i < len(tokens):
            best_sn, best_len = None, 0
            for comp_key, freq in s['freq'].items():
                if freq < s['threshold'] or not comp_key.startswith('C:'):
                    continue
                try:
                    ct = [int(x) for x in comp_key[2:].split(',')]
                except ValueError:
                    continue
                clen = len(ct)
                if i + clen <= len(tokens) and tokens[i:i + clen] == ct:
                    cvkey = 'C:' + ','.join(str(x) for x in ct)
                    if cvkey in s['v2s'] and clen > best_len:
                        best_sn = s['v2s'][cvkey]
                        best_len = clen

            if best_sn is not None and best_len >= 2:
                out.append(_e(best_sn))
                i += best_len
            else:
                out.append(_e(tokens[i]))
                i += 1

        return ''.join(out)

    def decode(self, stream):
        s = self._s
        if not stream:
            return ''

        out, i = [], 0
        while i < len(stream) - 1:
            code = stream[i:i + 2]
            sn = _d(code)
            if sn >= 0 and sn < len(s['series']) and s['series'][sn] is not None:
                out.append(self._resolve(s['series'][sn]))
            else:
                out.append('?')
            i += 2
        return ' '.join(out)

    def delta(self):
        """Return and clear pending delta entries."""
        d = self._s['delta'][:]
        self._s['delta'] = []
        return d

    def apply(self, values):
        """Apply received delta to build matching dictionary."""
        for v in values:
            self._assign(v)

    def save(self, path=None):
        s = self._s
        p = path or CACHE_PATH
        os.makedirs(os.path.dirname(p), exist_ok=True)
        data = {
            'series': s['series'][s['_preloaded']:],
            'freq': {k: v for k, v in s['freq'].items() if v >= s['threshold']},
        }
        with open(p, 'w') as f:
            json.dump(data, f)
        return p

    def load(self, path=None):
        _load_cache(self._s, path)

    def stats(self):
        s = self._s
        entries = sum(1 for v in s['series'] if v is not None)
        comps = sum(1 for v in s['series'] if isinstance(v, list))
        return {
            'dict': len(_DICT_WORDS),
            'preloaded': s['_preloaded'],
            'entries': entries,
            'compositions': comps,
            'delta_pending': len(s['delta']),
        }

    # ── internals ──

    def _assign(self, value):
        s = self._s
        key = self._vkey(value)
        if key in s['v2s']:
            return s['v2s'][key]
        sn = len(s['series'])
        s['series'].append(value)
        s['v2s'][key] = sn
        s['delta'].append(value)
        return sn

    def _vkey(self, value):
        if isinstance(value, list):
            return 'C:' + ','.join(str(x) for x in value)
        return str(value)

    def _resolve(self, value):
        s = self._s
        if isinstance(value, str):
            return value
        elif isinstance(value, list):
            parts = []
            for sn in value:
                if sn < len(s['series']) and s['series'][sn] is not None:
                    parts.append(self._resolve(s['series'][sn]))
            return ' '.join(parts)
        return '?'

    def _learn(self, tokens):
        s = self._s
        n = len(tokens)
        for length in [4, 3, 2]:
            for i in range(n - length + 1):
                comp = tokens[i:i + length]
                key = self._vkey(comp)
                s['freq'][key] = s['freq'].get(key, 0) + 1
                if s['freq'][key] >= s['threshold']:
                    self._assign(comp)


def _load_cache(s, path=None):
    p = path or CACHE_PATH
    if not os.path.exists(p):
        return
    with open(p) as f:
        data = json.load(f)
    for v in data.get('series', []):
        key = 'C:' + ','.join(str(x) for x in v) if isinstance(v, list) else str(v)
        sn = len(s['series'])
        s['series'].append(v)
        s['v2s'][key] = sn
    s['freq'] = data.get('freq', {})
