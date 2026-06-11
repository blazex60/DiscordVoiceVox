<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-05-30 | Updated: 2026-05-30 -->

# workflows

## Purpose
GitHub Actions CD pipelines that deploy the bot to production and staging servers via SSH on every push to the relevant branch.

## Key Files

| File | Description |
|------|-------------|
| `main.yml` | Deploys to all production instances on push to `master` (`git pull` on 6 server paths) |
| `dev.yml` | Deploys to single staging instance on push to `dev` (`git pull` on `/root/bots/DiscordVoiceVox-a`) |

## For AI Agents

### Working In This Directory
- Both workflows use `appleboy/ssh-action` with secrets `HOST`, `PORT`, `USER`, `SECRET_KEY` configured in GitHub repository settings.
- `main.yml` pulls to 6 separate deployment paths: `/root/DiscordVoiceVox` and 5 instances under `/home/len/DiscordVoiceVox-{c,d,e,z,h}`. This reflects the multi-instance deployment model — changes to `master` propagate to all production shards simultaneously.
- `dev.yml` targets only `/root/bots/DiscordVoiceVox-a` for pre-production testing.
- These workflows only run `git pull`; the bot process must be restarted separately on the servers (presumably via a process manager like `systemd` or `pm2`).

### Testing Requirements
- Verify CD by pushing a commit and confirming the SSH deploy step completes without error in the Actions tab.
- Do not add steps that auto-restart the bot process without coordinating with the server operators.

## Dependencies

### External
- `appleboy/ssh-action` — SSH deployment action
- `actions/checkout@v2` — repository checkout

<!-- MANUAL: Any manually added notes below this line are preserved on regeneration -->
