from detectors.base import Detector, Status
from utils.shell import run_quiet


class PowerShellDetector(Detector):
    @property
    def name(self) -> str:
        return "PowerShell"

    def detect(self) -> tuple[Status, str]:
        for cmd in ['pwsh -Command "$PSVersionTable.PSVersion.ToString()"',
                     'powershell -Command "$PSVersionTable.PSVersion.ToString()"']:
            code, output = run_quiet(cmd)
            if code == 0 and output.strip():
                version = output.strip()
                try:
                    major = int(version.split(".")[0])
                    if major < 5:
                        return Status.WARNING, f"PowerShell {version} (5+ recommended)"
                except (ValueError, IndexError):
                    pass
                return Status.OK, f"{version}"
        return Status.MISSING, "not found"
