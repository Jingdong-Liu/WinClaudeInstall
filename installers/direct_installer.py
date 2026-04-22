import urllib.request
import os
import tempfile
from installers.base import Installer
from utils.shell import run_stream

INSTALLER_URLS = {
    "Node.js": "https://nodejs.org/dist/v20.11.0/node-v20.11.0-x64.msi",
    "Git": "https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe",
    "Python": "https://www.python.org/ftp/python/3.12.1/python-3.12.1-amd64.exe",
}

SILENT_FLAGS = {
    ".msi": "/quiet /norestart",
    ".exe": "/quiet /norestart",
}


class DirectInstaller(Installer):
    def __init__(self, dependency: str):
        self._dependency = dependency

    @property
    def name(self) -> str:
        return f"direct download ({self._dependency})"

    @property
    def priority(self) -> int:
        return 3

    def install(self, log_callback) -> bool:
        url = INSTALLER_URLS.get(self._dependency)
        if not url:
            if log_callback:
                log_callback(f"ERROR: No direct download URL for {self._dependency}")
            return False

        if log_callback:
            log_callback(f"Downloading {self._dependency} from {url}")

        try:
            ext = os.path.splitext(url)[1]
            fd, installer_path = tempfile.mkstemp(suffix=ext)
            os.close(fd)

            urllib.request.urlretrieve(url, installer_path)

            if log_callback:
                log_callback(f"Downloaded to {installer_path}")

            flag = SILENT_FLAGS.get(ext, "/S")
            cmd = f'"{installer_path}" {flag}'
            if log_callback:
                log_callback(f"Running: {cmd}")

            code = run_stream(cmd, log_callback, timeout=600)
            success = code == 0

            try:
                os.remove(installer_path)
            except OSError:
                pass

            if log_callback:
                log_callback(f"Direct install {'succeeded' if success else 'FAILED'} (exit {code})")
            return success

        except Exception as e:
            if log_callback:
                log_callback(f"ERROR: Direct install failed -- {e}")
            return False
