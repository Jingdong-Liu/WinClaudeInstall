"""Claude Code detector — checks if @anthropic-ai/claude-code is installed globally."""

from detectors.base import Detector, Status
from utils.shell import run_quiet


class ClaudeCodeDetector(Detector):
    @property
    def name(self) -> str:
        return "Claude Code"

    def detect(self) -> tuple[Status, str]:
        code, output = run_quiet("claude --version")
        if code == 0:
            version = output.strip().split("\n")[-1].strip()
            return Status.ok, version
        # Try npm list as fallback
        code2, output2 = run_quiet("npm list -g @anthropic-ai/claude-code")
        if code2 == 0:
            # Extract version from npm list output
            for line in output2.strip().split("\n"):
                if "@anthropic-ai/claude-code" in line:
                    parts = line.split("@")
                    if len(parts) >= 3:
                        return Status.ok, f"v{parts[-1]}"
            return Status.ok, "installed"
        return Status.missing, "not installed"
