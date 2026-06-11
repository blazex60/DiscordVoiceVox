<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-05-30 | Updated: 2026-05-30 -->

# guild_setting

## Purpose
Per-guild configuration storage. Each file is named `{guild_id}.json` and holds that guild's settings (auto-join channels, speaker preferences, alarm list, read-aloud options, etc.).

## Key Files

| File | Description |
|------|-------------|
| `{guild_id}.json` | Per-guild settings JSON (e.g., `9686.json`); schema is defined implicitly by `get_guild_setting` / `update_guild_setting` in `main.py` |

## For AI Agents

### Working In This Directory
- Never read or write these JSON files directly from cog or feature code. Always use `main.get_guild_setting(guild_id)` and `main.update_guild_setting(guild_id, key, value)`.
- Files are created on first access if they do not exist.
- The JSON schema is loosely typed — keys are added per-feature. Use `.get("key", default)` when reading to handle missing keys gracefully.

### Testing Requirements
- Verify settings round-trip by calling `update_guild_setting` then `get_guild_setting` and asserting the value matches.

## Dependencies

### Internal
- `main.py` — sole accessor via `get_guild_setting` / `update_guild_setting`

<!-- MANUAL: Any manually added notes below this line are preserved on regeneration -->
