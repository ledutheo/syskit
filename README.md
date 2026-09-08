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

**Full workflow (PATH, doctor, troubleshooting):** [docs/install-and-doctor.md](docs/install-and-doctor.md)

Clone to `~/github/syskit`, then:

```bash
cd ~/github/syskit
./install.sh
syskit doctor
```

`./install.sh` creates `.venv`, installs editable `[dev]`, and symlinks `~/.local/bin/syskit`. `uv pip install -e .` does not create that symlink.

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

`./install.sh` already installs `[dev]`. Then:

```bash
ruff check .
ruff format .
mypy src/
pytest
```

See [docs/install-and-doctor.md](docs/install-and-doctor.md#development-same-clone) for uv, CI, and `syskit` not found.

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
