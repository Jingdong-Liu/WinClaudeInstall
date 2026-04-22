from detectors.base import Detector, Status
from detectors.node import NodeDetector
from detectors.git import GitDetector
from detectors.python import PythonDetector
from detectors.powershell import PowerShellDetector
from detectors.bash import BashDetector
from detectors.npm import NpmDetector

__all__ = [
    "Detector",
    "Status",
    "NodeDetector",
    "GitDetector",
    "PythonDetector",
    "PowerShellDetector",
    "BashDetector",
    "NpmDetector",
]
