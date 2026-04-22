from installers.base import Installer
from utils.shell import run_stream


WINGET_PACKAGES = {
    "Node.js": "OpenJS.NodeJS.LTS",
    "Git": "Git.Git",
    "Python": "Python.Python.3.12",
    "npm": "OpenJS.NodeJS.LTS",
}


class WingetInstaller(Installer):
    def __init__(self, dependency: str):
        self._dependency = dependency

    @property
    def name(self) -> str:
        return f"winget install ({self._dependency})"

    @property
    def priority(self) -> int:
        return 2

    @property
    def target(self) -> str:
        return WINGET_PACKAGES.get(self._dependency, self._dependency)

    def install(self, log_callback) -> bool:
        package_id = self.target
        cmd = f'winget install --id {package_id} --silent --accept-package-agreements --accept-source-agreements'
        if log_callback:
            log_callback(f"Running: {cmd}")
        code = run_stream(cmd, log_callback, timeout=600)
        success = code == 0
        if log_callback:
            log_callback(f"winget install {'succeeded' if success else 'FAILED'} (exit {code})")
        return success
