<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-05-30 | Updated: 2026-05-30 -->

# user_dict

## Purpose
User dictionary and generated audio storage. The dictionary part stores custom word-to-reading mappings (for correcting VOICEVOX pronunciation). The `audio_data/` subdirectory stores pre-generated WAV files partitioned by guild ID.

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `audio_data/` | Guild-partitioned generated audio WAV files (see `audio_data/AGENTS.md`) |

## For AI Agents

### Working In This Directory
- Dictionary files are watched at runtime by `watchfiles` (`awatch`) in `main.py`; changes are picked up without restarting the bot.
- The path to this directory is configured via the `DICT_LOC` environment variable (default: `./user_dict` relative to `main.py`).
- Audio files in `audio_data/` are keyed by UUID and should not be renamed or reorganized manually.

### Testing Requirements
- Add a custom word entry and verify the bot reads it with the corrected pronunciation in a live voice session.

## Dependencies

### Internal
- `main.py` — reads dictionary entries and writes audio files; watches for changes via `watchfiles`

### External
- `watchfiles` — filesystem watcher for hot-reloading dictionary changes

<!-- MANUAL: Any manually added notes below this line are preserved on regeneration -->
