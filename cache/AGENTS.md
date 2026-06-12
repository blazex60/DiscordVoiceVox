<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-05-30 | Updated: 2026-05-30 -->

# cache

## Purpose
Persistent backing store for the in-memory voice synthesis cache. Reduces redundant TTS API calls by storing previously generated audio data keyed by text+speaker combinations.

## Key Files

| File | Description |
|------|-------------|
| `voice_cache.json` | JSON file storing cached voice data; loaded into `bot.voice_cache_dict` at startup and flushed periodically |

## For AI Agents

### Working In This Directory
- Do not edit `voice_cache.json` manually — it is managed entirely by `main.py` via `bot.voice_cache_dict` and `bot.voice_cache_counter_dict`.
- The cache is keyed by a combination of text content and speaker ID. Invalidation happens automatically when the cache counter exceeds a threshold.
- This directory should always be writable by the bot process.

### Testing Requirements
- No direct tests. Verify cache behavior by monitoring `bot.voice_cache_dict` in a running instance.

## Dependencies

### Internal
- `main.py` — reads/writes this directory at runtime

<!-- MANUAL: Any manually added notes below this line are preserved on regeneration -->
