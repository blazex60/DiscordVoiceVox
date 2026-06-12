<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-05-30 | Updated: 2026-05-30 -->

# logs

## Purpose
Application log output directory. `main.py` writes a new timestamped log file on each startup using Python's `logging.FileHandler`.

## Key Files

| File | Description |
|------|-------------|
| `discord-YYYY-MM-DD-HH-MM.log` | Timestamped log file created each time the bot starts; contains INFO+ messages from the `discord` logger |
| `sample.log` | Placeholder file to ensure the directory exists in version control |

## For AI Agents

### Working In This Directory
- Log files are runtime artifacts — do not commit them.
- When diagnosing issues, check the most recent `discord-*.log` file for tracebacks and WARNING/ERROR entries.
- The `BehindDetectHandler` in `main.py` watches for WebSocket lag warnings and posts notifications to a Discord channel.
- This directory must be writable by the bot process at startup.

### Testing Requirements
- No tests. Use log content for post-hoc debugging.

## Dependencies

### Internal
- `main.py` — creates and writes log files via Python `logging`

<!-- MANUAL: Any manually added notes below this line are preserved on regeneration -->
