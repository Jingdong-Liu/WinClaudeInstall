"""CC-Switch detector — checks if CC-Switch is installed."""

import os
from detectors.base import Detector, Status
from utils.shell import run_quiet


class CCSwitchDetector(Detector):
    @property
    def name(self) -> str:
        return "CC-Switch"

    def detect(self) -> tuple[Status, str]:
        # Check if cc-switch is in npm global packages
        code, output = run_quiet("npm list -g cc-switch")
        if code == 0:
            return Status.OK, "installed via npm"

        # Check Windows Start Menu / Program Files for CC-Switch
        prog_files = os.environ.get("ProgramFiles", r"C:\Program Files")
        cc_switch_paths = [
            os.path.join(prog_files, "CC-Switch"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "cc-switch"),
        ]
        for p in cc_switch_paths:
            if os.path.exists(p):
                return Status.OK, "installed"

        return Status.MISSING, "not installed"
