"""Bundled installer — uses pre-packaged installers for offline fallback."""

import os
import sys

from installers.base import Installer
from utils.shell import run_stream

BUNDLED_FILES = {
    "Node.js": "node-v22.14.0-x64.msi",
    "Git": "Git-2.49.0-64-bit.exe",
    "Python": "python-3.13.2-amd64.exe",
    "Claude Code": "anthropic-ai-claude-code-2.1.119.tgz",
    "CC-Switch": "CC-Switch-v3.14.1-Windows.msi",
}

SILENT_FLAGS = {
    ".msi": "msiexec /i",
    ".exe": None,  # Handled per-exe below
}

EXE_SILENT_PARAMS = {
    # Node.js/Python .exe are MSI wrappers that support /quiet
    "node-": "/quiet /norestart",
    "python-": "/quiet /norestart",
    # NSIS electron-builder installers use /S
}


def get_bundled_dir() -> str:
    """Return the directory containing bundled installer files."""
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, "bundled")
    return os.path.join(os.path.dirname(__file__), "..", "bundled")


class BundledInstaller(Installer):
    def __init__(self, dependency: str):
        self._dependency = dependency

    @property
    def name(self) -> str:
        return f"bundled installer ({self._dependency})"

    @property
    def priority(self) -> int:
        return 2

    @property
    def target(self) -> str:
        return self._dependency

    def install(self, log_callback) -> bool:
        filename = BUNDLED_FILES.get(self._dependency)
        if not filename:
            if log_callback:
                log_callback(f"ERROR: No bundled installer for {self._dependency}")
            return False

        installer_path = os.path.join(get_bundled_dir(), filename)
        if not os.path.exists(installer_path):
            if log_callback:
                log_callback(f"  Skipped: bundled file not found: {filename}")
            return False

        ext = os.path.splitext(installer_path)[1]

        # .tgz files are npm tarballs — install via npm
        if ext == ".tgz":
            cmd = f'npm install -g "{installer_path}"'
            if log_callback:
                log_callback(f"Running: {cmd}")
            code = run_stream(cmd, log_callback, timeout=600)
            success = code == 0
            if log_callback:
                log_callback(f"Bundled tgz install {'succeeded' if success else 'FAILED'} (exit {code})")
            return success

        # Build the install command based on file type
        if ext == ".msi":
            # MSI must be invoked via msiexec with /i flag
            cmd = f'msiexec /i "{installer_path}" /qn /norestart'
        elif ext == ".exe":
            # Try to match known silent params, default to /S
            basename = os.path.basename(installer_path).lower()
            params = "/S"
            for prefix, silent in EXE_SILENT_PARAMS.items():
                if basename.startswith(prefix):
                    params = silent
                    break
            cmd = f'"{installer_path}" {params}'
        else:
            cmd = f'"{installer_path}" /S'

        if log_callback:
            log_callback(f"Running: {cmd}")
        code = run_stream(cmd, log_callback, timeout=600)
        success = code == 0
        if log_callback:
            log_callback(f"Bundled install {'succeeded' if success else 'FAILED'} (exit {code})")
        return success
