# syskit

> Modern CLI toolkit for Arch Linux and Manjaro users.

Un outil en ligne de commande bien conçu pour rendre la gestion quotidienne d'Arch/Manjaro plus agréable et plus rapide.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/status-alpha-orange)

## ✨ Features

- **Beautiful CLI** built with Typer + Rich
- **System information** at a glance
- **Smart update** (pacman + AUR helpers)
- **Powerful cleanup** with dry-run mode
- **Better package search**
- **Quick config backup**

## 🚀 Installation

### From source (recommended for now)

```bash
git clone https://github.com/ledutheo/syskit.git
cd syskit

# One-command local install (venv + ~/.local/bin/syskit)
./install.sh

# Or manually with uv / pip
uv pip install -e .
# pip install -e .
```

After `./install.sh`, the `syskit` command is available globally via `~/.local/bin`.

### Usage

```bash
syskit --help
syskit doctor          # vérifie PATH, locale UTF-8, outils système
syskit info
syskit update
syskit clean --dry-run
syskit search firefox
syskit backup
```

## 📸 Screenshots

*(Screenshots coming soon)*

## 🛠 Development

```bash
# Install dev dependencies (includes ruff, mypy, pytest, build)
uv pip install -e ".[dev]"

# Run locally
python -m syskit.cli --help

# Lint + format + type check
ruff check .
ruff format .
mypy src/

# Run tests (works on any OS thanks to mocks)
pytest
```

## Roadmap

- [ ] Proper packaging & AUR release
- [ ] More commands (services, logs, hardware info...)
- [ ] Configuration file support
- [ ] Plugin system
- [ ] Shell completions (already partially supported)

## License

MIT © ledutheo

## Author

**ledutheo** — [github.com/ledutheo](https://github.com/ledutheo)
