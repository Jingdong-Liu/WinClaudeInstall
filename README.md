# Claude Code Installer

A Windows GUI tool for one-click installation of [Claude Code](https://github.com/anthropics/claude-code).

## Features

- **Environment Detection** — Automatically checks for Node.js, Git, Python, PowerShell, Bash, and npm
- **Status Display** — Clear ✓/✗/⚠ indicators with version details
- **One-Click Install** — Installs all missing dependencies automatically
- **Real-Time Logging** — Live output panel shows every step
- **Fallback Chain** — Tries npm → winget → direct download for each missing dependency
- **Extensible** — Add new detectors by creating a single file and registering it

## Quick Start

### Run from source

```bash
python main.py
```

Requires Python 3.9+.

### Build standalone executable

```bash
build.bat
```

Output: `dist\ClaudeCodeInstaller\ClaudeCodeInstaller.exe`

### GUI progran
<img width="883" height="649" alt="image" src="https://github.com/user-attachments/assets/c171c155-4cdc-4903-9bf9-4943ce71e896" />

## Architecture

```
main.py                 → GUI entry point + orchestration
detectors/base.py       → Detector ABC (name, detect → status/detail)
detectors/*.py          → One file per dependency (Node, Git, Python, etc.)
installers/base.py      → Installer ABC (name, priority, target, install)
installers/*.py         → One file per install method (npm, winget, direct)
utils/shell.py          → Command execution with streaming + quiet modes
utils/logger.py         → File + console logging
tests/                  → Mock-based tests for all detectors and installers
```

### Adding a new detector

1. Create `detectors/mydep.py` inheriting from `Detector`
2. Implement `name` property and `detect()` method
3. Register in `main.py` `DETECTORS` list and `detectors/__init__.py`

## License

MIT
