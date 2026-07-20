"""ϕphrase — Phrase-level compressor for φ-lang v5.

Zero-ambiguity design:
  Codes that collide with English words ("hi", "go", "be") are never assigned.
  2-char token in 82K dict → English word. Not in dict → φ code.
  No ^ prefix needed. 1,527 safe single-token codes.
"""
import tiktoken, json, os, string

C62 = string.digits + string.ascii_lowercase + string.ascii_uppercase
_ENC = tiktoken.get_encoding("cl100k_base")
_CUR = os.path.dirname(os.path.abspath(__file__))

# ── Code tables ──
# Ordered: safe 1-token codes first, then unsafe 1-token, then 2-token (fallback)
_ALL_2CHAR = [a+b for a in C62 for b in C62]
_SAFE_1TOK = []
_UNSAFE_1TOK = []
_MULTI_TOK = []
_ENGLISH_WORDS = None

def _init_code_tables():
    global _SAFE_1TOK, _UNSAFE_1TOK, _MULTI_TOK, _ENGLISH_WORDS
    if _SAFE_1TOK:
        return
    try:
        import shivtext
        _ENGLISH_WORDS = set(shivtext.load_dict())
    except ImportError:
        _ENGLISH_WORDS = set()
    # Add common 2-char English words not in frequency dict
    _ENGLISH_WORDS.update(["yo","ok","ha","ah","oh","er","um","eh","mm","sh","hm",
                            "ow","aw","ew","ay","ya","ye","na","da","ta","ma","pa",
                            "fa","lo","ho","ey","oy"])
    for c in _ALL_2CHAR:
        nt = len(_ENC.encode(c))
        if nt == 1:
            if c in _ENGLISH_WORDS:
                _UNSAFE_1TOK.append(c)
            else:
                _SAFE_1TOK.append(c)
        else:
            _MULTI_TOK.append(c)

# ── Phrase dictionary ──
PHRASES = {}
CODE_TO_PHRASE = {}
_PHRASES_BUILT = False

def _ensure_phrases():
    global PHRASES, CODE_TO_PHRASE, _PHRASES_BUILT
    if _PHRASES_BUILT:
        return
    _init_code_tables()
    PHRASES = _build_phrases()
    CODE_TO_PHRASE = {v: k for k, v in PHRASES.items()}
    _PHRASES_BUILT = True

def _build_phrases():
    phrases = {}
    idx = 0

    agent_phrases = [
        "authentication service is down", "database connection timeout",
        "connection pool exhausted", "cache layer is operational",
        "queue depth is normal", "queue depth is high",
        "memory usage is critical", "memory usage is high",
        "memory usage is normal", "rolling update in progress",
        "rolling update complete", "deploy to production",
        "deploy to staging", "backup completed successfully",
        "backup has failed", "migration in progress",
        "migration completed", "error rate is elevated",
        "error rate is normal", "latency is increasing",
        "latency is normal", "restart the service",
        "restart the authentication service", "check the system health",
        "check the database connection", "all services are running",
        "all services are healthy", "system is fully operational",
        "system is degraded", "system is down",
        "need immediate attention", "no action required",
        "investigating the issue", "resolution in progress",
        "escalating to primary node", "primary node is unreachable",
        "secondary node taking over", "failover complete",
        "load balancer is misconfigured", "tls certificate expiring",
        "disk space is low", "cpu usage is high",
        "network partition detected", "replica lag is increasing",
        "read replica is behind", "write throughput is degraded",
        "circuit breaker is open", "circuit breaker reset",
        "retry queue is building", "dead letter queue is growing",
        "health check is failing", "health check passed",
        "metrics dashboard updated", "logs rotated successfully",
        "configuration reloaded", "secret rotation complete",
        "audit log is full", "rate limiter engaged",
        "throttling requests", "dependency service is slow",
        "upstream timeout detected", "downstream service unavailable",
        "api gateway is throttling", "websocket connection dropped",
        "grpc channel is broken", "message broker is backlogged",
        "event processor is lagging", "stream processor restarting",
        "batch job completed", "batch job timed out",
        "scheduled task failed", "cron job is stuck",
        "data pipeline is stalled", "etl process completed",
        "data inconsistency detected", "checksum mismatch",
        "index rebuild in progress", "index rebuild complete",
        "query performance degraded", "slow query detected",
        "table lock detected", "vacuum complete",
        "wal file growing", "replication slot is full",
        "pgbouncer pool exhausted", "redis sentinel election",
        "kafka consumer lag", "elasticsearch cluster yellow",
        "elasticsearch cluster red", "elasticsearch cluster green",
        "prometheus scraping timeout", "grafana alert triggered",
        "pagerduty incident created", "on call rotation changed",
        "deployment pipeline is blocked", "build is failing",
        "test suite failed", "linting errors detected",
        "security scan found vulnerabilities", "dependency update available",
        "ssl certificate renewed", "dns propagation delay",
        "cdn cache purged", "origin server is slow",
        "edge function deployed", "serverless cold start detected",
        "lambda timeout warning", "s3 bucket permission changed",
        "iam policy updated", "vpc peering established",
        "subnet is out of ips", "nat gateway throttling",
    ]

    for phrase in agent_phrases:
        code = _next_code(idx)
        if code and phrase not in phrases:
            phrases[phrase] = code
            idx += 1

    try:
        import shivtext
        words = shivtext.load_dict()[:10000]
        for i in range(len(words)-1):
            bigram = f"{words[i]} {words[i+1]}"
            if bigram not in phrases:
                code = _next_code(idx)
                if code:
                    phrases[bigram] = code
                    idx += 1
        for i in range(len(words)-2):
            trigram = f"{words[i]} {words[i+1]} {words[i+2]}"
            if trigram not in phrases:
                code = _next_code(idx)
                if code:
                    phrases[trigram] = code
                    idx += 1
    except ImportError:
        pass
    return phrases

def _next_code(idx):
    if idx < len(_SAFE_1TOK):
        return _SAFE_1TOK[idx]
    uidx = idx - len(_SAFE_1TOK)
    if uidx < len(_UNSAFE_1TOK):
        return _UNSAFE_1TOK[uidx]
    midx = idx - len(_SAFE_1TOK) - len(_UNSAFE_1TOK)
    if midx < len(_MULTI_TOK):
        return _MULTI_TOK[midx]
    return None

def _is_code(token):
    """Token is a φ code if it's 2 chars and NOT in the English dictionary."""
    _init_code_tables()
    if len(token) != 2 or token[0] not in C62 or token[1] not in C62:
        return False
    return token not in _ENGLISH_WORDS


def new(load_cache=False):
    _ensure_phrases()
    s = {
        'phrases': dict(PHRASES),
        'code_to_phrase': dict(CODE_TO_PHRASE),
        'delta': [],
        'compositions': {},
        'comp_codes': {},
        'rev_comp': {},
        'threshold': 3,
    }
    return Session(s)


class Session:
    def __init__(self, s):
        self._s = s

    def encode(self, text):
        if not text or not text.strip():
            return ''
        s = self._s
        tokens = text.strip().split()
        sorted_phrases = sorted(s['phrases'], key=len, reverse=True)
        encoded_positions = set()
        i = 0

        while i < len(tokens):
            best_len = 0
            for phrase in sorted_phrases:
                p_tokens = phrase.split()
                plen = len(p_tokens)
                if i + plen <= len(tokens) and tokens[i:i+plen] == p_tokens:
                    if plen > best_len:
                        best_len = plen
            if best_len >= 2:
                for j in range(best_len):
                    encoded_positions.add(i + j)
                i += best_len
            else:
                i += 1

        result = []
        i = 0
        while i < len(tokens):
            if i in encoded_positions:
                for phrase in sorted_phrases:
                    p_tokens = phrase.split()
                    if tokens[i:i+len(p_tokens)] == p_tokens and i + len(p_tokens) <= len(tokens):
                        result.append(s['phrases'][phrase])
                        i += len(p_tokens)
                        break
                else:
                    result.append(tokens[i])
                    i += 1
            else:
                result.append(tokens[i])
                i += 1

        encoded = ' '.join(result)
        self._learn_compositions(result)
        return encoded

    def decode(self, text):
        if not text:
            return ''
        s = self._s
        tokens = text.strip().split()
        out, i = [], 0

        while i < len(tokens):
            tok = tokens[i]
            if _is_code(tok) and tok in s['code_to_phrase']:
                out.append(s['code_to_phrase'][tok])
            elif _is_code(tok) and tok in s['rev_comp']:
                parts = []
                for ct in s['rev_comp'][tok]:
                    parts.append(s['code_to_phrase'].get(ct, ct))
                out.append(' '.join(parts))
            else:
                out.append(tok)
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
        s = self._s
        code_tokens = [t for t in tokens if _is_code(t) and t in s['code_to_phrase']]
        for i in range(len(code_tokens) - 1):
            pair = f"{code_tokens[i]} {code_tokens[i+1]}"
            s['compositions'][pair] = s['compositions'].get(pair, 0) + 1
            if s['compositions'][pair] >= s['threshold'] and pair not in s['comp_codes']:
                for code in _SAFE_1TOK + _UNSAFE_1TOK:
                    if code not in s['code_to_phrase'] and code not in s['rev_comp']:
                        s['comp_codes'][pair] = code
                        s['rev_comp'][code] = code_tokens[i:i+2]
                        s['delta'].append({'type': 'comp', 'pair': pair, 'code': code})
                        break

    def _assign(self, value):
        s = self._s
        if isinstance(value, dict) and value.get('type') == 'comp':
            pair, code = value['pair'], value['code']
            s['comp_codes'][pair] = code
            s['rev_comp'][code] = pair.split()
            parts = []
            for p in pair.split():
                if p in s['code_to_phrase']:
                    parts.append(s['code_to_phrase'][p])
            s['code_to_phrase'][code] = ' '.join(parts) if parts else pair
