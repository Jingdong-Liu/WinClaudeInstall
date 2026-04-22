from detectors.base import Detector, Status
from utils.shell import run_quiet


class NodeDetector(Detector):
    @property
    def name(self) -> str:
        return "Node.js"

    def detect(self) -> tuple[Status, str]:
        code, output = run_quiet("node --version")
        if code == 0 and output.startswith("v"):
            version = output
            # Extract major version
            try:
                major = int(version.split(".")[0].lstrip("v"))
                if major < 18:
                    return Status.WARNING, f"{version} (>= 18 recommended)"
            except (ValueError, IndexError):
                pass
            return Status.OK, version
        return Status.MISSING, "not found"
