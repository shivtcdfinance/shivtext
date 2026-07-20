"""φ-lang v4-five — Token-optimized dictionary codec. Delta-only transmission.

Core model:
  Pre-loads ALL 82,834 token-optimized English words from shivtcdfinance.
  First 3,644 words get 2-char direct codes (no delta ever).
  Remaining ~78K words are dictionary-resident — only new/domain words need delta.
  Both sides have identical dictionaries via pip install.
  Composition: repeated phrases promoted to single codes.
  Delta → 0 after vocabulary saturation.

pip install shivtcdfinance    (github.com/raman-cerie/shivtcdfinance)
  OR: works standalone with empty dict.
"""
import os, json

# ── Code table ──
_CODES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dict", "phi4five_codes.json")
with open(_CODES_PATH) as f:
    CODES = json.load(f)
CODE_COUNT = len(CODES)
C2I = {c: i for i, c in enumerate(CODES)}

def _e(n):
    if n < CODE_COUNT:
        return CODES[n]
    return '??'

def _d(c):
    return C2I.get(c, -1)

# ── Load dictionary from shivtcdfinance ──

_DICT_WORDS = []       # all words from the dictionary
_DICT_W2I = {}         # word → dict index (for lookup)

def _load_dict():
    """Load ALL words from shivtcdfinance token-optimized dictionary."""
    words = []
    w2i = {}
    try:
        import shivtext as sf
        for i, word in enumerate(sf.load_dict()):
            words.append(word)
            w2i[word] = i
    except ImportError:
        pass
    return words, w2i

_DICT_WORDS, _DICT_W2I = _load_dict()
PRELOAD_COUNT = min(len(_DICT_WORDS), CODE_COUNT - 200)  # reserve 200 for session
SESSION_RESERVE = 200


class philangdict:
    """
    Token-optimized dictionary codec.

    Pre-loads all 82K words from shivtcdfinance.
    First PRELOAD_COUNT words get 2-char codes (instant, zero delta).
    Remaining dict words are known but get session codes on first use.
    Domain/new words always get session codes.
    Both sides build identical state from delta.
    """

    CACHE = os.path.expanduser("~/.hermes/phi4five_state.json")

    def __init__(self, load_cache=False):
        self.series = []        # sn → value (str word or list composition)
        self.v2s = {}           # value → sn (reverse lookup)
        self.delta = []         # pending delta: [value, ...]
        self.freq = {}          # composition signature → count
        self.threshold = 3      # promote phrase after 3 occurrences
        self._preloaded = 0

        # Pre-load top words with direct codes
        for i, word in enumerate(_DICT_WORDS[:PRELOAD_COUNT]):
            sn = len(self.series)
            self.series.append(word)
            self.v2s[str(word)] = sn
        self._preloaded = len(self.series)

        if load_cache:
            self.load()

    # ── Value encoding ──

    def _vkey(self, value):
        if isinstance(value, list):
            return 'C:' + ','.join(str(x) for x in value)
        return str(value)

    def _resolve(self, value):
        if isinstance(value, str):
            return value
        elif isinstance(value, list):
            parts = []
            for sn in value:
                if sn < len(self.series) and self.series[sn] is not None:
                    parts.append(self._resolve(self.series[sn]))
            return ' '.join(parts)
        return '?'

    def _assign(self, value):
        key = self._vkey(value)
        if key in self.v2s:
            return self.v2s[key]
        sn = len(self.series)
        self.series.append(value)
        self.v2s[key] = sn
        self.delta.append(value)
        return sn

    # ── Composition learning ──

    def _learn(self, token_seq):
        n = len(token_seq)
        for length in [4, 3, 2]:
            for i in range(n - length + 1):
                comp = token_seq[i:i + length]
                key = self._vkey(comp)
                self.freq[key] = self.freq.get(key, 0) + 1
                if self.freq[key] >= self.threshold:
                    self._assign(comp)

    # ── Core encode/decode ──

    def encode(self, text):
        if not text or not text.strip():
            return ''

        words = text.strip().split()
        tokens = []
        for w in words:
            sn = self._assign(w)
            tokens.append(sn)

        self._learn(tokens)

        out = []
        i = 0
        while i < len(tokens):
            best_sn, best_len = None, 0
            for comp_key, freq in self.freq.items():
                if freq < self.threshold or not comp_key.startswith('C:'):
                    continue
                try:
                    comp_tokens = [int(x) for x in comp_key[2:].split(',')]
                except ValueError:
                    continue
                clen = len(comp_tokens)
                if i + clen <= len(tokens) and tokens[i:i + clen] == comp_tokens:
                    cvkey = self._vkey(comp_tokens)
                    if cvkey in self.v2s and clen > best_len:
                        best_sn = self.v2s[cvkey]
                        best_len = clen

            if best_sn is not None and best_len >= 2:
                out.append(_e(best_sn))
                i += best_len
            else:
                out.append(_e(tokens[i]))
                i += 1

        return ''.join(out)

    def decode(self, stream):
        if not stream:
            return ''

        out = []
        i = 0
        while i < len(stream) - 1:
            code = stream[i:i + 2]
            sn = _d(code)
            if sn >= 0 and sn < len(self.series) and self.series[sn] is not None:
                out.append(self._resolve(self.series[sn]))
            else:
                out.append('?')
            i += 2
        return ' '.join(out)

    # ── Delta sync ──

    def get_delta(self):
        d = self.delta[:]
        self.delta = []
        return d

    def apply_delta(self, values):
        for v in values:
            self._assign(v)

    # ── Persistence ──

    def save(self, path=None):
        p = path or self.CACHE
        os.makedirs(os.path.dirname(p), exist_ok=True)
        data = {
            'series': self.series[self._preloaded:],
            'freq': {k: v for k, v in self.freq.items() if v >= self.threshold},
        }
        with open(p, 'w') as f:
            json.dump(data, f)
        return p

    def load(self, path=None):
        p = path or self.CACHE
        if not os.path.exists(p):
            return
        with open(p) as f:
            data = json.load(f)
        for v in data.get('series', []):
            self._assign(v)
        self.freq = data.get('freq', {})

    # ── Introspection ──

    def stats(self):
        entries = sum(1 for v in self.series if v is not None)
        compositions = sum(1 for v in self.series if isinstance(v, list))
        dict_size = len(_DICT_WORDS)
        return {
            'dict_words': dict_size,
            'preloaded': self._preloaded,
            'entries': entries,
            'compositions': compositions,
            'delta_pending': len(self.delta),
            'code_space': f"{self._preloaded}/{CODE_COUNT} pre, {entries - self._preloaded} session",
        }
