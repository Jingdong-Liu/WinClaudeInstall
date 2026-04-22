import re
from detectors.base import Detector, Status
from utils.shell import run_quiet


class BashDetector(Detector):
    @property
    def name(self) -> str:
        return "Bash"

    def detect(self) -> tuple[Status, str]:
        code, output = run_quiet("bash --version")
        if code == 0 and "bash" in output.lower():
            version_line = output.strip().split("\n")[0]
            match = re.search(r"version\s+([\d.]+)", version_line, re.IGNORECASE)
            if match:
                return Status.OK, match.group(1)
            return Status.OK, "found"
        return Status.MISSING, "not found"
