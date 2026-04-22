from installers.base import Installer
from utils.shell import run_stream

CLAUDE_CODE_PACKAGE = "@anthropic-ai/claude-code"


class NpmInstaller(Installer):
    @property
    def name(self) -> str:
        return "npm global install"

    @property
    def priority(self) -> int:
        return 1

    @property
    def target(self) -> str:
        return CLAUDE_CODE_PACKAGE

    def install(self, log_callback) -> bool:
        cmd = f"npm install -g {CLAUDE_CODE_PACKAGE}"
        if log_callback:
            log_callback(f"Running: {cmd}")
        code = run_stream(cmd, log_callback)
        success = code == 0
        if log_callback:
            log_callback(f"npm install {'succeeded' if success else 'FAILED'} (exit {code})")
        return success
