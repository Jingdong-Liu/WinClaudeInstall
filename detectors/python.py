from detectors.base import Detector, Status
from utils.shell import run_quiet


class PythonDetector(Detector):
    @property
    def name(self) -> str:
        return "Python"

    def detect(self) -> tuple[Status, str]:
        for cmd in ["python --version", "python3 --version"]:
            code, output = run_quiet(cmd)
            if code == 0 and "python" in output.lower():
                parts = output.strip().split()
                version = parts[-1] if len(parts) >= 2 else output.strip()
                try:
                    major, minor = map(int, version.split(".")[:2])
                    if major == 3 and minor < 9:
                        return Status.WARNING, f"{version} (>= 3.9 recommended)"
                except (ValueError, IndexError):
                    pass
                return Status.OK, version
        return Status.MISSING, "not found"
