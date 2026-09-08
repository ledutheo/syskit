# Local install and `syskit doctor`

This is the workflow that actually puts `syskit` on your machine. Without it, `syskit` is not on `PATH`, the editable install is missing, and `syskit doctor` fails — even if you cloned the repo.

The README lists commands. This page is how you **get** those commands.

## What this workflow does

1. Create a virtualenv next to the clone.
2. Install syskit in editable mode (code changes apply without reinstalling).
3. Symlink `~/.local/bin/syskit` → `.venv/bin/syskit`.
4. Verify PATH, locale, pacman, and the clone with `syskit doctor`.

`./install.sh` is the supported path. `uv pip install -e .` is optional and does **not** create the `~/.local/bin` symlink.

## Setup

### Prerequisites

- Arch Linux or Manjaro
- Python 3.10+ (`python3`)
- `git`
- `pacman` (always present on those distros)
- `~/.local/bin` on `PATH` (see [Troubleshooting](#troubleshooting) if `syskit` is missing after install)

Optional: `yay` or `paru` (AUR updates), `gh` (GitHub auth check in doctor), `uv` (CI / alternate install).

### Clone location

Canonical clone:

```text
~/github/syskit
```

`syskit doctor` looks here first, then `~/syskit` (legacy). Keep the repo under one of those paths if you want the “source clone” check to pass.

```bash
mkdir -p ~/github
git clone git@github.com:ledutheo/syskit.git ~/github/syskit
cd ~/github/syskit
```

HTTPS clone: `https://github.com/ledutheo/syskit.git`.

### Install

```bash
cd ~/github/syskit
./install.sh
```

What the script does:

| Step | Result |
|------|--------|
| `python3 -m venv .venv` | Virtualenv at `~/github/syskit/.venv` (created if missing) |
| `pip install -e ".[dev]"` | Editable install including pytest, ruff, mypy |
| `ln -sf .venv/bin/syskit ~/.local/bin/syskit` | Global `syskit` command |

Open a new shell (or `hash -r`) so the shell picks up the symlink.

### Verify

```bash
syskit doctor
```

Exit `0` means PATH, UTF-8 locale, `pacman`/`git`/`python3`, clone, and (if present) the dev venv all look usable. Exit `1` lists failing checks — see [Troubleshooting](#troubleshooting).

`gh` is optional: not installed is a FAIL-style row (`optional — not installed`) and counts toward the failure count. Install GitHub CLI or ignore that row if you do not use it.

## Usage

After install, daily commands:

```bash
syskit --help
syskit doctor          # first check when something feels off
syskit info            # hostname, kernel, distro, uptime, RAM
syskit search firefox  # pacman -Ss, formatted table
syskit update          # sudo pacman -Syu, then yay or paru if present
syskit clean --dry-run # list orphans, cache, journal, user cache — no changes
syskit clean           # same, then confirm before sudo / deletions
syskit backup          # tar.gz of ~/.config, ~/.ssh, ~/.zshrc, ~/.gitconfig
syskit version
```

### Update

- Always runs `sudo pacman -Syu --noconfirm`.
- If `yay` or `paru` is on PATH, runs that helper next (`yay` first if both exist).
- No AUR helper: warning, still success if pacman succeeded.

### Clean

- `--dry-run` / `-d`: print planned actions only (no sudo, no prompt).
- Without dry-run: confirm, then orphans (`pacman -Rns`), `pacman -Sc`, journal vacuum (2 weeks), delete `~/.cache/thumbnails` and `~/.cache/mozilla/firefox` if they exist.

### Backup

Default archive: `~/backups/system-backup.tar.gz`. Override with `-o` / `--output`. Parent directories are created. The archive includes **SSH keys** if `~/.ssh` exists — treat the file as secret.

### Completions

Typer is built with `add_completion=True`. Show install instructions:

```bash
syskit --help
```

Or generate a script, for example:

```bash
syskit --show-completion zsh
```

## Development (same clone)

`install.sh` already installs `[dev]`. From the clone:

```bash
cd ~/github/syskit
source .venv/bin/activate   # optional; ~/.local/bin/syskit already uses this venv

ruff check .
ruff format .
mypy src/
pytest
```

CI (GitHub Actions) runs ruff, mypy, pytest on Python 3.10–3.12, then builds a wheel and runs `syskit version`. Tests mock `pacman`/`sudo`; they are safe on any OS.

Without `install.sh`, use uv (no global symlink):

```bash
uv pip install -e ".[dev]"
python -m syskit.cli --help
```

## Troubleshooting

### `syskit: command not found`

1. Re-run `./install.sh` from the clone.
2. Confirm the symlink: `ls -l ~/.local/bin/syskit` — it must point at `<clone>/.venv/bin/syskit`.
3. Put `~/.local/bin` on PATH. In zsh:

   ```bash
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   ```

4. `hash -r` or open a new terminal.
5. `syskit doctor` — check **syskit in PATH**.

### Doctor FAIL: `syskit source clone`

Doctor expects `~/github/syskit/pyproject.toml` (or `~/syskit/pyproject.toml`). A clone only under `~/Projects/` or another path fails this check even if the CLI works.

Fix: clone or move the repo to `~/github/syskit`, then `./install.sh` again so the symlink still matches.

### Doctor FAIL: `dev venv`

No `.venv` or that venv cannot `import syskit` / `pytest`. Run `./install.sh` from the clone doctor found (see the Detail column).

If you installed with `uv pip` / `pip` only, there is no `.venv` under the clone unless you created one. Use `./install.sh` for the doctor-supported layout.

### Doctor FAIL: `locale UTF-8`

`locale charmap` must report UTF-8. Typical fix on Manjaro:

```bash
# Ensure LANG is UTF-8 in ~/.zshrc, then:
localectl set-locale LANG=en_US.UTF-8   # or your locale
```

Grok TUI keyboard glitches are often the same issue.

### Doctor FAIL: `pacman` / `git` / `python3`

This CLI is for Arch/Manjaro. `pacman` missing means you are not on that stack (or PATH is stripped). `git` / `python3`: install with pacman.

### `sudo` password / pacman errors on `update` or `clean`

Those commands shell out to `sudo pacman` / `journalctl`. A failed sudo or pacman run shows as `Error: …`. Fix sudo, then retry. Use `clean --dry-run` first.

`run_command` captures stdout only; a successful pacman run with empty stdout is still treated as success.

### `uv: command not found` when following the README

`uv` is used in CI, not by `install.sh`. Install uv if you want that path, or ignore it and use `./install.sh`.

### Backup failed: no config paths found

None of `~/.config`, `~/.ssh`, `~/.zshrc`, `~/.gitconfig` exist. Unusual on a real user account; create at least one of those or pass `--output` after they exist.

### Tests fail with Rich / ANSI noise

Assertions should use stripped text (see `plain()` in `tests/test_cli.py`). Do not match raw escape codes.

### Reinstall from scratch

```bash
cd ~/github/syskit
rm -rf .venv
rm -f ~/.local/bin/syskit
./install.sh
syskit doctor
```
