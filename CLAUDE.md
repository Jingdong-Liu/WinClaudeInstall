# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Windows GUI tool (Python + tkinter) that one-click installs Claude Code. Detects environment dependencies, displays status with ✓/✗/⚠ indicators, and auto-installs missing components via a fallback chain (npm → winget → direct download).

## Common Commands

```bash
# Run GUI
python main.py

# Run tests
python -m pytest tests/ -v

# Build standalone executable
build.bat
```

## Architecture

Pluggable ABC-based design with two core patterns:

**Detector pattern** — Each dependency has a class inheriting `Detector` (from `detectors/base.py`). `detect()` returns `(Status, detail)` where Status is `ok|missing|warning`. One file per dependency in `detectors/`.

**Installer pattern** — Each install method has a class inheriting `Installer` (from `installers/base.py`). `install(log_callback)` performs the install and returns bool. Installers are chained per dependency with priority ordering.

```
main.py                    → GUI entry point (InstallerApp), design constants, ttk styling
detectors/base.py          → Status enum, Detector ABC
detectors/{node,git,python,powershell,bash,npm}.py → Concrete detectors
installers/base.py         → Installer ABC (name, priority, target, install)
installers/{npm_installer,winget_installer,direct_installer}.py → Concrete installers
utils/shell.py             → run_stream() (live output), run_quiet() (silent check)
utils/logger.py            → File + console logging setup
tests/test_detectors.py    → 24 tests (mock-based)
tests/test_installers.py   → 4 tests (mock-based)
tests/test_shell.py        → 5 tests
```

## Adding a New Detector

1. Create `detectors/mydep.py` inheriting from `Detector`
2. Implement `name` property and `detect()` returning `(Status, detail)`
3. Export in `detectors/__init__.py`
4. Add to `DETECTORS` list in `main.py`

## Adding a New Installer Method

1. Create `installers/my_installer.py` inheriting from `Installer`
2. Set `name`, `priority`, `target` properties and implement `install(log_callback)`
3. Wire into the fallback chain in `main.py:_run_install()`

## Key Constraints

- Python 3.9+, Windows only (uses winget, PowerShell)
- GUI updates must use `root.after()` for thread safety
- Tests use `@patch` for mocking subprocess calls
- ttk uses "clam" theme with custom styles defined in `_setup_style()`
- Design constants (colors, fonts, spacing) are module-level in `main.py`
