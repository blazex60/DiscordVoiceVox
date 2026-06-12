<!-- Generated: 2026-05-30 | Updated: 2026-05-30 -->

# DiscordVoiceVox

## Purpose
Discord bot that reads text messages aloud in voice channels using VOICEVOX TTS and related engines (COEIROINK, SHAREVOX, AIVOICE, AIVIS Speech). Audio is streamed to Discord voice channels via Lavalink. The bot supports premium subscription tiers via Stripe, stores per-guild and per-user settings in PostgreSQL, and runs as an auto-sharded bot across multiple deployment instances.

## Key Files

| File | Description |
|------|-------------|
| `main.py` | Core bot logic: all slash commands, voice synthesis, DB access, Lavalink integration, event handlers |
| `fast_sharded_bot.py` | `AutoShardedBot` subclass that respects Discord's `max_concurrency` when launching shards in parallel batches |
| `LavalinkClient.py` | Wavelink-compatible adapter over `lavalink.py`; handles node failover, track search, and audio playback |
| `requirements.txt` | Python package dependencies |
| `run.sh` | Shell script to start the bot process |
| `.env_temp` | Template listing all required environment variables with example values |
| `custom_emoji.json` | Custom emoji ID mapping used in bot responses |
| `audio.wav` | Sample WAV file used for testing audio playback |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `commands/` | Pycord cog modules for slash commands (see `commands/AGENTS.md`) |
| `cache/` | Runtime voice synthesis cache (see `cache/AGENTS.md`) |
| `guild_setting/` | Per-guild configuration JSON files (see `guild_setting/AGENTS.md`) |
| `user_dict/` | User dictionary entries and generated audio data (see `user_dict/AGENTS.md`) |
| `logs/` | Rotating application log files (see `logs/AGENTS.md`) |
| `.github/` | GitHub Actions CI/CD workflows (see `.github/AGENTS.md`) |

## For AI Agents

### Working In This Directory
- All secrets (tokens, DB credentials) live in `.env`; never hardcode them. Use `.env_temp` as the reference for required variables.
- `main.py` is the monolithic core — it imports from `fast_sharded_bot.py` and `LavalinkClient.py`. Cog modules in `commands/` import back into `main` for helper functions (`get_guild_setting`, `update_guild_setting`, `is_premium_check`).
- Bot state that must survive cog reloads is stored on `bot.*` attributes (initialized in `init_bot_state()`). Do not create new module-level globals for mutable state.
- Multiple deployment instances run simultaneously (see `.github/workflows/`). Configuration that differs per instance is set via environment variables, not code branches.

### Testing Requirements
- There is no automated test suite. Manual testing requires a running VOICEVOX server, a Lavalink server, and a PostgreSQL instance.
- Use `run.sh` to start the bot. Check `logs/` for runtime errors.

### Common Patterns
- Lavalink audio: generate a TTS audio URL/path → pass to `LavalinkWavelink.Playable.search()` → stream via `LavalinkVoiceClient`.
- Guild settings: always use `get_guild_setting(guild_id)` / `update_guild_setting(guild_id, key, value)` — never read/write `guild_setting/` JSON files directly from cog code.
- Premium checks: `await is_premium_check(user_or_guild_id, plan_tier)` before gating features.

## Dependencies

### Internal
- `commands/` — cog modules loaded dynamically at startup
- `guild_setting/` — runtime config storage
- `user_dict/` — custom pronunciation dictionary and audio cache
- `cache/` — in-memory voice cache backed by `voice_cache.json`

### External
- `py-cord` — Discord API wrapper with slash command support
- `lavalink` — Audio server client for streaming TTS output
- `asyncpg` — Async PostgreSQL driver
- `aiohttp` — HTTP client for VOICEVOX/TTS API calls
- `stripe` — Payment processing for premium subscriptions
- `ko2kana`, `romajitable`, `translators` — Text normalization and kana conversion
- `watchfiles` — Hot-reload of user dictionary changes
- `python-dotenv` — `.env` file loading

<!-- MANUAL: Any manually added notes below this line are preserved on regeneration -->
