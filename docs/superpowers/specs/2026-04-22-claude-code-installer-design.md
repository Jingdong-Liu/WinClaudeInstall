# Claude Code Installer GUI — Design Document

## Overview

A Windows desktop GUI tool that provides one-click environment detection, status display, and automated installation of Claude Code and its dependencies.

## Architecture

**Pattern**: Single-file modular Python application with tkinter GUI.

**Core Flow**:
1. **Detect** — Iterate through registered detectors, each returns `(status, detail)`
2. **Display** — Left panel shows results (✓/✗/⚠), right panel shows live log
3. **Install** — One-click button triggers fallback chain per missing dependency
4. **Log** — All output streams to GUI panel and `installer.log` file

## Components

### Detector Interface

```python
class Detector(ABC):
    name: str
    @abstractmethod
    def detect(self) -> tuple[Status, str]:
        pass
```

Status values: `OK`, `MISSING`, `WARNING`

Concrete detectors: Node.js, Git, Python, PowerShell, Bash, npm.

### Installer Interface

```python
class Installer(ABC):
    name: str
    priority: int
    @abstractmethod
    def install(self, log_callback) -> bool:
        pass
```

Concrete installers: npm global, winget, direct download + silent install.

### Fallback Chain

For each missing dependency, try strategies in priority order:
1. npm global install → fail → try next
2. winget install → fail → try next
3. Official installer download + silent execution

Each strategy has 5-minute timeout, 2 retries with 3-second delay.

### Command Executor (`utils/shell.py`)

```python
def run_stream(cmd: str, log_callback, cwd=None) -> int:
    """Async command execution with line-by-line output to log_callback."""
```

Uses `subprocess.Popen` with pipe-based stdout/stderr, reads lines in a worker thread.

## GUI Design

### Layout

Two-column + bottom button:
- **Left panel**: Treeview with environment check results (icon + name + version/detail)
- **Right panel**: ScrolledText for live installation log
- **Bottom**: "One-Click Install" button + "Refresh" button

### Status Icons
- ✓ Green: Ready
- ✗ Red: Missing (required)
- ⚠ Yellow: Warning (outdated, non-standard path)

### Interaction Flow
1. Auto-detect on launch, progress in log panel
2. Results update left list
3. "One-Click Install" → confirmation dialog (mixed mode): core deps (Node.js/npm) auto-installed, large deps (Git/Python/Bash) require user confirmation → install with live log → completion dialog
4. "Refresh" re-runs detection

## Error Handling

- **Timeout**: 5 minutes per command, then failover to next strategy
- **Permissions**: Detect admin rights, request UAC elevation for npm global installs
- **Network**: Auto-retry 2 times (3s delay), then switch strategy
- **Failover**: Never interrupt on single failure, try all strategies before reporting error
- **Logging**: All operations logged to `installer.log` file

## Extensibility

New detection items require:
1. New module in `detectors/`
2. Inherit `Detector`, implement `detect()`
3. Register in `main.py` `DETECTORS` list

## File Structure

```
claude-code-installer/
├── main.py                 # GUI entry + orchestration
├── detectors/
│   ├── __init__.py
│   ├── base.py             # Detector ABC
│   ├── node.py             # Node.js detection
│   ├── git.py              # Git detection
│   ├── python.py           # Python detection
│   ├── powershell.py       # PowerShell detection
│   ├── bash.py             # Bash detection
│   └── npm.py              # npm detection
├── installers/
│   ├── __init__.py
│   ├── base.py             # Installer ABC
│   ├── npm_installer.py    # npm install
│   ├── winget_installer.py # winget install
│   └── direct_installer.py # official download + silent install
├── utils/
│   ├── __init__.py
│   ├── shell.py            # command execution + log streaming
│   └── packager.py         # PyInstaller config
├── build.bat               # one-click build script
├── icon.ico                # app icon
├── main.spec               # PyInstaller spec
└── installer.log           # runtime log (auto-generated)
```

## Packaging

PyInstaller `--onefile --windowed` produces a single ~15-20MB .exe.
Build command: `pyinstaller --onefile --windowed --icon=icon.ico main.spec`
