from detectors.base import Detector, Status
from utils.shell import run_quiet


class NpmDetector(Detector):
    @property
    def name(self) -> str:
        return "npm"

    def detect(self) -> tuple[Status, str]:
        code, output = run_quiet("npm --version")
        if code == 0:
            version = output.strip()
            try:
                major = int(version.split(".")[0])
                if major < 9:
                    return Status.WARNING, f"{version} (>= 9 recommended)"
            except (ValueError, IndexError):
                pass
            return Status.OK, version
        return Status.MISSING, "not found"
