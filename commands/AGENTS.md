<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-05-30 | Updated: 2026-05-30 -->

# commands

## Purpose
Pycord cog modules containing slash command implementations that are too large or self-contained to live directly in `main.py`. Each file defines one `commands.Cog` subclass and a `setup(bot)` function so Pycord can load it dynamically.

## Key Files

| File | Description |
|------|-------------|
| `SetAlarmCommand.py` | `/setalarm` slash command — add, delete, and list scheduled TTS alarm messages per guild |

## For AI Agents

### Working In This Directory
- Every cog file must end with a `setup(bot)` function that calls `bot.add_cog(...)`.
- Cog classes import helper functions directly from `main` (e.g., `main.get_guild_setting`, `main.update_guild_setting`, `main.is_premium_check`). This circular import works because `main` is fully initialized before cogs are loaded.
- Premium-gated commands must call `await main.is_premium_check(...)` before executing the restricted logic.
- Always call `await ctx.defer()` at the start of command handlers that make async I/O calls.

### Testing Requirements
- Load the cog on a running bot instance and issue the slash command via Discord.
- Verify premium gating by testing with both a premium and non-premium user/guild.

### Common Patterns
- Use `discord.Option(required=False, ...)` with `autocomplete=discord.utils.basic_autocomplete(...)` for dynamic option lists (see `get_alarm_settings` in `SetAlarmCommand.py`).
- Return early with an error embed on validation failures rather than raising exceptions.

## Dependencies

### Internal
- `main` — `get_guild_setting`, `update_guild_setting`, `is_premium_check`

### External
- `py-cord` — `discord.ext.commands.Cog`, slash command decorators

<!-- MANUAL: Any manually added notes below this line are preserved on regeneration -->
