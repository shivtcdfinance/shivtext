# shivlite

Lightweight chat compressor for LLM conversations.

- Zero dependencies
- Instant import — no disk I/O until first encode
- Optimized for 4–25 message chat threads
- Pure encode/decode — no session state, no composition learning

```python
import shivlite
compressed = shivlite.encode("Can you help me with something?")
original = shivlite.decode(compressed)
```

## Install

```bash
pip install shivlite
```

By Shiv.
