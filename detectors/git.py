from detectors.base import Detector, Status
from utils.shell import run_quiet


class GitDetector(Detector):
    @property
    def name(self) -> str:
        return "Git"

    def detect(self) -> tuple[Status, str]:
        code, output = run_quiet("git --version")
        if code == 0 and "git version" in output.lower():
            parts = output.strip().split()
            version = parts[-1] if len(parts) >= 3 else output.strip()
            return Status.OK, version
        return Status.MISSING, "not found"
