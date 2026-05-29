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

# Using uv (fastest)
uv pip install -e .

# Or with pip
pip install -e .
```

### Usage

```bash
syskit --help
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
# Install dev dependencies
uv pip install -e ".[dev]"

# Run locally
python -m syskit.cli --help
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
