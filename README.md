# shivtext

> **`pip install shivtext`** — one command, the entire φ-lang runtime is yours.

---

## Author

**Shiv Rao** — Dublin, Ireland.

- MSc Finance, Trinity College Dublin
- Private Equity Masters
- APA Credit Lending — Double 4.0 GPA

I build systems. Started with simple chat context management in early June 2026, and over 45 days — 588 sessions, 78,000+ messages, around 250 hours — that evolved into designing a communication protocol and publishing it as a pip library. I work through an AI agent operating system that I configured and extended myself. Most of my sessions run late at night, and the agent has been running alongside me since day one.

**Thinking pattern:** first-principles reasoning. Strip to essence, prove with numbers. Spec before code, correct before fast. Single-file zero-dependency architectures. Builds daemons, not cron jobs. Reverses decisions instantly when the logic flips.

**Interests:** compression theory, token economics, agent meshes, autonomous cloud computing, artificial language design, protocol specification.

---

## The journey log

29 steps. 45 days. 588 sessions. 78,442 messages. One pip library.

| # | Capability | What it unlocked |
|---|-----------|-----------------|
| 1 | Chat context management | Folder-based context for online models |
| 2 | Code-based agentic Python | Scripts that think, not just execute |
| 3 | GPT Atlas, Codex, Claude Code, Comet, Perplexity | Comparing the agent landscape |
| 5 | Agentic IDE usage | AI driving the editor |
| 6 | OS-level agentic (OpenClaw / Hermes) | AI controlling the machine |
| 7 | Web API connections + skill structure | Structured tool calling |
| 8 | Cloud storage: GitHub + skill sourcing | Versioned, cloneable agent knowledge |
| 9 | Skill size management | Efficient agent context windows |
| 10 | Tensor usage + Obsidian vault | Knowledge graph + note system |
| 11 | Micro tensors | Small, targeted knowledge units |
| 12 | Local model experiments | Offline inference, no API dependency |
| 13 | Cloud ↔ local read/write modelling | Hybrid compute architecture |
| 14 | Static web apps | Self-hosted UI |
| 15 | DMG app creation | Packaged macOS applications |
| 16 | Native GitHub cloning + usage | Git as infrastructure |
| 17 | Apify automation + AI business manager | Web scraping + task automation |
| 18 | GitHub workflows | CI/CD for AI pipelines |
| 19 | Cloud servers | Own compute, not rented inference |
| 20 | Multiple AI OS nodes | Mesh computing nodes |
| 21 | Shared resource communication + sync | Nodes that talk to each other |
| 22 | Notion bus mesh + Tailscale | Distributed knowledge backbone |
| 23 | Autonomous AI cloud computing system | Self-managing cloud compute |
| 24 | Micro language for AI moderating AI | Language as control surface |
| 25 | Full communication + language protocol | Protocol specification |
| 26 | Language-based architecture for autonomous web/physical computing | The blueprint |
| 27 | φ-lang v1 | First working language implementation |
| 28 | Dictionary + subscript-based context modulation | Token-optimized vocabulary |
| 29 | **Published shivtext to PyPI** | `pip install shivtext` — live |

---

## By the numbers

| Metric | Value |
|--------|-------|
| Sessions | 588 |
| Messages | 78,442 |
| Hours | ~250 across 45 days |
| Days elapsed | Jun 4 → Jul 20 (46 days) |
| Dictionary size | 82,834 token-optimized English words |
| Phrase codes | 1,491 single-token codes (collision-free) |
| Avg token savings | 40–50% per message |
| Dependencies | 0 (pure Python stdlib) |
| PyPI versions | 9 (v0.2 → v0.6.0) |

---

## The final product

```
pip install shivtext
       │
       ▼
┌─────────────────────────────┐
│  ϕdictionary  — 82K words   │
│  ϕphrase      — 1,563 codes │
│  ϕencyclopedia (future)     │
│  ϕreferences  (future)      │
└─────────────────────────────┘
```

**How it works:**

```
"authentication service is down"
        │
        ▼ encode
   "00"              (1 token vs 4 — 75% save)
        │
        ▼ decode
"authentication service is down" ✓
```

Dictionary-based disambiguation: if a 2-char token isn't in the English dictionary, it's a φ code. No prefix needed. Zero ambiguity.

---

## The collision bug — solved

φ-lang codes are 2 characters. ~36 English words are also 2 letters (`hi`, `go`, `no`, `be`, `we`, `in`, `on`, `at`). Typing `hi` collapsed the protocol — the receiver couldn't tell greeting from compressed code.

**Fix:** codes that collide with English words are filtered at assignment time. 1,491 safe codes used first. Decode: look up in code table. Not found → it's English. Zero runtime overhead. Zero ambiguity.

---

## Repos

| Repo | Purpose | Status |
|------|---------|--------|
| `shivtext` | Pip package | ✅ PyPI |
| `phi-lang-v4-five` | Codec engine (zero-deps) | ✅ GitHub |
| `mylib` | Dictionary engine (SymSpell) | 🔒 Private |
| `iloveyoutanvi` | Docs & legacy | 📦 Archive |

---

## What's next

- `ϕencyclopedia` — multi-language concept index
- `ϕreferences` — reusable scripts and patterns
- Agent-native integration — sessions that auto-decode φ
- Composition learning — repeated phrases → single codes
- Agent mesh transport — node-to-node φ communication

## Architecture evolution

| Version | Architecture | Result |
|---------|-------------|--------|
| v1 | Word-level encode (every word → 2-char code) | -50% tokens |
| v2 | Phrase-only encode (words → stay English) | +49% tokens |
| v3 | `^` prefix for disambiguation | +50% tokens |
| v4 | Dictionary-based disambiguation, no prefix | +62% tokens |
| v5 | Scope indexing, multi-tenant | In progress |

I'm scaling by deploying tools for our own system, and as part of research I open-source deprecated tools that perform at 70% efficiency. For example, φ-lang v2 — an in-house compression engine — compressed a 101KB skill file to 252 bytes.

---

**Contact:** Shiv.tcdfinance@gmail.com — engineers and quants only.

---

```
pip install shivtext
```

The IO terminal is yours.
