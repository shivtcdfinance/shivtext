"""
shivtext v0.7.0 — Pro tier with license key + optional telemetry.

Free tier: 500 phrases baked in, no server, no key, works forever.
Pro tier: License key unlocks full 1,491 phrases + delta sync + composition learning.
"""
import os

# ── Free tier ──
FREE_PHRASES = 500

LICENSE_SERVER = "https://api.shivtext.io" if "SHIVTEXT_SERVER" not in os.environ else os.environ["SHIVTEXT_SERVER"]

def validate_key(key):
    """Validate license key against server. Returns session token or None."""
    pass

def fetch_delta(session_token, last_sync):
    """Fetch new phrases from server since last sync. Returns [(phrase, code), ...]."""
    pass

def report_usage(session_token, encode_count, decode_count):
    """Fire-and-forget usage ping. Anonymous, no content."""
    pass

def learn_composition(session_token, pair, code):
    """Submit learned phrase pair to server for global promotion checking."""
    pass
