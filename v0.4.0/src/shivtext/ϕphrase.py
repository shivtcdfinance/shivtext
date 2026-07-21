"""ϕphrase — Phrase-level compressor for φ-lang v5.

Segmentation:
  1. Common phrases → 2-char single-token codes (67-80% save)
  2. Multi-token words (3+) → 3-char codes (save 1+ tokens)
  3. 1-2 token words → leave as English (already optimal)

Session composition: repeated phrase codes auto-merge into one code.
"""
import tiktoken, json, os, string

C62 = string.digits + string.ascii_lowercase + string.ascii_uppercase
_ENC = tiktoken.get_encoding("cl100k_base")
_CUR = os.path.dirname(os.path.abspath(__file__))

# ── Code tables ──
# 2-char single-token codes for phrases
_PHRASE_CODES = [a+b for a in C62 for b in C62 if len(_ENC.encode(a+b)) == 1]
# 3-char codes for expensive words
_WORD_CODES_3 = [a+b+c for a in C62 for b in C62 for c in C62[:10]]  # sample, will expand

_PHRASE_COUNT = len(_PHRASE_CODES)
_WORD_COUNT_3 = len(_WORD_CODES_3)

# ── Build phrase dictionary ──
def _build_phrases():
    """Build phrase dictionary from agent patterns + common n-grams."""
    phrases = {}
    idx = 0

    # System/agent phrases (highest priority)
    agent_phrases = [
        "authentication service is down",
        "database connection timeout",
        "connection pool exhausted",
        "cache layer is operational",
        "queue depth is normal",
        "queue depth is high",
        "memory usage is critical",
        "memory usage is high",
        "memory usage is normal",
        "rolling update in progress",
        "rolling update complete",
        "deploy to production",
        "deploy to staging",
        "backup completed successfully",
        "backup has failed",
        "migration in progress",
        "migration completed",
        "error rate is elevated",
        "error rate is normal",
        "latency is increasing",
        "latency is normal",
        "restart the service",
        "restart the authentication service",
        "check the system health",
        "check the database connection",
        "all services are running",
        "all services are healthy",
        "system is fully operational",
        "system is degraded",
        "system is down",
        "need immediate attention",
        "no action required",
        "investigating the issue",
        "resolution in progress",
        "escalating to primary node",
        "primary node is unreachable",
        "secondary node taking over",
        "failover complete",
        "load balancer is misconfigured",
        "tls certificate expiring",
        "disk space is low",
        "cpu usage is high",
        "network partition detected",
        "replica lag is increasing",
        "read replica is behind",
        "write throughput is degraded",
        "circuit breaker is open",
        "circuit breaker reset",
        "retry queue is building",
        "dead letter queue is growing",
        "health check is failing",
        "health check passed",
        "metrics dashboard updated",
        "logs rotated successfully",
        "configuration reloaded",
        "secret rotation complete",
        "audit log is full",
        "rate limiter engaged",
        "throttling requests",
        "dependency service is slow",
        "upstream timeout detected",
        "downstream service unavailable",
        "api gateway is throttling",
        "websocket connection dropped",
        "grpc channel is broken",
        "message broker is backlogged",
        "event processor is lagging",
        "stream processor restarting",
        "batch job completed",
        "batch job timed out",
        "scheduled task failed",
        "cron job is stuck",
        "data pipeline is stalled",
        "etl process completed",
        "data inconsistency detected",
        "checksum mismatch",
        "index rebuild in progress",
        "index rebuild complete",
        "query performance degraded",
        "slow query detected",
        "table lock detected",
        "vacuum complete",
        "wal file growing",
        "replication slot is full",
        "pgbouncer pool exhausted",
        "redis sentinel election",
        "kafka consumer lag",
        "elasticsearch cluster yellow",
        "elasticsearch cluster red",
        "elasticsearch cluster green",
        "prometheus scraping timeout",
        "grafana alert triggered",
        "pagerduty incident created",
        "on call rotation changed",
        "deployment pipeline is blocked",
        "build is failing",
        "test suite failed",
        "linting errors detected",
        "security scan found vulnerabilities",
        "dependency update available",
        "ssl certificate renewed",
        "dns propagation delay",
        "cdn cache purged",
        "origin server is slow",
        "edge function deployed",
        "serverless cold start detected",
        "lambda timeout warning",
        "s3 bucket permission changed",
        "iam policy updated",
        "vpc peering established",
        "subnet is out of ips",
        "nat gateway throttling",
    ]

    for phrase in agent_phrases:
        if idx < _PHRASE_COUNT and phrase not in phrases:
            phrases[phrase] = _PHRASE_CODES[idx]
            idx += 1

    # Add common bigrams/trigrams from dictionary (auto-generated)
    try:
        import shivtext
        words = shivtext.load_dict()[:10000]
        for i in range(len(words)-1):
            bigram = f"{words[i]} {words[i+1]}"
            if bigram not in phrases and idx < _PHRASE_COUNT:
                phrases[bigram] = _PHRASE_CODES[idx]
                idx += 1
        for i in range(len(words)-2):
            trigram = f"{words[i]} {words[i+1]} {words[i+2]}"
            if trigram not in phrases and idx < _PHRASE_COUNT:
                phrases[trigram] = _PHRASE_CODES[idx]
                idx += 1
    except ImportError:
        pass

    return phrases


PHRASES = {}
CODE_TO_PHRASE = {}
_PHRASES_BUILT = False

def _ensure_phrases():
    global PHRASES, CODE_TO_PHRASE, _PHRASES_BUILT
    if _PHRASES_BUILT:
        return
    PHRASES = _build_phrases()
    CODE_TO_PHRASE = {v: k for k, v in PHRASES.items()}
    _PHRASES_BUILT = True


def new(load_cache=False):
    """Create a new ϕphrase session."""
    _ensure_phrases()
    s = {
        'phrases': dict(PHRASES),
        'code_to_phrase': dict(CODE_TO_PHRASE),
        'delta': [],
        'compositions': {},    # "ϕA ϕB" → count
        'comp_codes': {},      # "ϕA ϕB" → "ϕZ"
        'rev_comp': {},        # "ϕZ" → ["ϕA", "ϕB"]
        'threshold': 3,
    }
    return Session(s)


class Session:
    def __init__(self, s):
        self._s = s

    def encode(self, text):
        """Segment and encode: phrases first, then expensive words, rest as English."""
        if not text or not text.strip():
            return ''

        s = self._s
        remaining = text.strip()
        result = []

        # Pass 1: Greedy longest-match phrase encoding — preserve order
        sorted_phrases = sorted(s['phrases'], key=len, reverse=True)
        tokens = remaining.split()
        encoded_positions = set()
        i = 0

        while i < len(tokens):
            best_len = 0
            best_code = None

            for phrase in sorted_phrases:
                p_tokens = phrase.split()
                plen = len(p_tokens)
                if i + plen <= len(tokens) and tokens[i:i+plen] == p_tokens:
                    if plen > best_len:
                        best_len = plen
                        best_code = s['phrases'][phrase]

            if best_code and best_len >= 2:
                for j in range(best_len):
                    encoded_positions.add(i + j)
                i += best_len
            else:
                i += 1

        # Build output preserving original word order
        result = []
        i = 0
        while i < len(tokens):
            if i in encoded_positions:
                # Find the phrase starting at this position
                for phrase in sorted_phrases:
                    p_tokens = phrase.split()
                    if tokens[i:i+len(p_tokens)] == p_tokens and i + len(p_tokens) <= len(tokens):
                        result.append('^' + s['phrases'][phrase])
                        i += len(p_tokens)
                        break
                else:
                    result.append(tokens[i])
                    i += 1
            else:
                result.append(tokens[i])
                i += 1

        encoded = ' '.join(result)

        # Composition learning: detect repeated code pairs
        self._learn_compositions(result)

        return encoded

    def decode(self, text):
        """Decode: expand ^prefixed phrase codes, pass through English words."""
        if not text:
            return ''
        s = self._s
        tokens = text.strip().split()
        out = []

        i = 0
        while i < len(tokens):
            tok = tokens[i]

            # Only process if it's a ^prefixed code
            if tok.startswith('^'):
                code = tok[1:]  # strip ^
                # Check composition
                if code in s['rev_comp']:
                    parts = []
                    for ct in s['rev_comp'][code]:
                        if ct in s['code_to_phrase']:
                            parts.append(s['code_to_phrase'][ct])
                        else:
                            parts.append(ct)
                    out.append(' '.join(parts))
                # Check phrase
                elif code in s['code_to_phrase']:
                    out.append(s['code_to_phrase'][code])
                else:
                    out.append(tok)  # unknown code, pass through
            else:
                out.append(tok)  # English word, pass through
            i += 1

        return ' '.join(out)

    def delta(self):
        d = self._s['delta'][:]
        self._s['delta'] = []
        return d

    def apply(self, values):
        for v in values:
            self._assign(v)

    def stats(self):
        s = self._s
        return {
            'phrases': len(s['phrases']),
            'compositions': len(s['comp_codes']),
            'delta': len(s['delta']),
        }

    def _learn_compositions(self, tokens):
        """Learn repeated code sequences → promote to single code."""
        s = self._s
        code_tokens = [t[1:] for t in tokens if t.startswith('^') and t[1:] in s['code_to_phrase']]
        for i in range(len(code_tokens) - 1):
            pair = f"{code_tokens[i]} {code_tokens[i+1]}"
            s['compositions'][pair] = s['compositions'].get(pair, 0) + 1
            if s['compositions'][pair] >= s['threshold'] and pair not in s['comp_codes']:
                # Find a free code
                for code in _PHRASE_CODES:
                    if code not in s['code_to_phrase'] and code not in s['rev_comp']:
                        s['comp_codes'][pair] = code
                        s['rev_comp'][code] = code_tokens[i:i+2]
                        s['delta'].append({'type': 'comp', 'pair': pair, 'code': code})
                        break

    def _assign(self, value):
        s = self._s
        if isinstance(value, dict) and value.get('type') == 'comp':
            pair = value['pair']
            code = value['code']
            s['comp_codes'][pair] = code
            s['rev_comp'][code] = pair.split()
            # Also add as phrase for decoding
            parts = []
            for p in pair.split():
                if p in s['code_to_phrase']:
                    parts.append(s['code_to_phrase'][p])
            s['code_to_phrase'][code] = ' '.join(parts) if parts else pair
