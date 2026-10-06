# Task 012: systemd service-ek és deploy script  *(lite)*

- **ID / Status / Type:** 012 · `done` (not run on the target host yet) · `behaviour-preserving` (no application code touched; adds ops scripts)
- **Branch:** `main` (the owner asked for direct commits to `main`) · **Created:** 2026-10-06

## What & why
`senechalweb.duckdns.org` was started by `run.sh` from the `isvorcz` crontab (`@reboot sleep 60 && sh run.sh`): background processes, secrets in plain text in the script, no restart after `git pull` without a reboot, no restart on crash. Replaced by systemd units plus a deploy script.

## Files touched
- `deploy/setup-systemd.sh` — one-off host setup: builds `/etc/senechal.env` (chmod 640) from the `export` lines of the old `run.sh`, writes `senechal.service` (`server.py`) and `senechal-ng.service` (`ng serve`), adds a sudoers rule for passwordless `systemctl restart`, removes the `run.sh` cron line (crontab backup first), stops the old processes, renames `run.sh` to `run.sh.old`, enables and starts the units.
- `deploy/deploy.sh` — `git pull --ff-only` in `senechal` and `AngrySenechal2`; `pip install` only if `requirements.txt` changed; `npm ci` + frontend restart only if `package-lock.json` changed; restarts `senechal`.

## Before / after
Before: reboot required to run new code. After: `deploy/deploy.sh` pulls and restarts the service; systemd restarts it on failure and at boot; logs in `journalctl -u senechal`.

## Operational impact (for the host)
- Run `bash deploy/setup-systemd.sh` once as the service user (needs sudo). Secrets move to `/etc/senechal.env`; delete `run.sh.old` and consider rotating the Discord token/secret.
- The frontend is still `ng serve` (dev server) as a unit; serving a `ng build` output from the reverse proxy would be better and makes `senechal-ng` unnecessary.
- Rollback: `sudo systemctl disable --now senechal senechal-ng`, `mv run.sh.old run.sh`, restore the crontab from `crontab.backup.*`.

## Documentation (required)
- [x] `documentation/CHANGELOG.md` entry added.
- [x] `pm/STATUS.md` refreshed.

## Verification & rollback
- **Checked:** `bash -n` on both scripts only. Not run on the target host.
- **Rollback:** `git revert <sha>` (repo); host rollback as above.
