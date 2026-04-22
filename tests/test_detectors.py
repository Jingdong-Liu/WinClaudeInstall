from unittest.mock import patch

from detectors.base import Status, Detector
from detectors.node import NodeDetector

def test_status_enum():
    assert Status.OK.value == "ok"
    assert Status.MISSING.value == "missing"
    assert Status.WARNING.value == "warning"

def test_node_detector_exists():
    det = NodeDetector()
    assert det.name == "Node.js"

def test_node_detector_returns_result():
    det = NodeDetector()
    status, detail = det.detect()
    assert status in (Status.OK, Status.MISSING)
    assert isinstance(detail, str)
    if status == Status.OK:
        assert "v" in detail  # version string like v20.11.0


@patch("detectors.node.run_quiet")
def test_node_detector_missing(mock_run_quiet):
    mock_run_quiet.return_value = (-1, "")
    det = NodeDetector()
    status, detail = det.detect()
    assert status == Status.MISSING
    assert "not found" in detail


@patch("detectors.node.run_quiet")
def test_node_detector_old_version_warning(mock_run_quiet):
    mock_run_quiet.return_value = (0, "v16.20.0")
    det = NodeDetector()
    status, detail = det.detect()
    assert status == Status.WARNING
    assert "18 recommended" in detail


@patch("detectors.node.run_quiet")
def test_node_detector_good_version(mock_run_quiet):
    mock_run_quiet.return_value = (0, "v20.11.0")
    det = NodeDetector()
    status, detail = det.detect()
    assert status == Status.OK
    assert "v20.11.0" == detail


from detectors.git import GitDetector
from detectors.python import PythonDetector
from detectors.powershell import PowerShellDetector
from detectors.bash import BashDetector
from detectors.npm import NpmDetector

def _test_detector(det_class, expected_name):
    det = det_class()
    assert det.name == expected_name
    status, detail = det.detect()
    assert status in (Status.OK, Status.MISSING)
    assert isinstance(detail, str)

def test_git_detector():
    _test_detector(GitDetector, "Git")

def test_python_detector():
    _test_detector(PythonDetector, "Python")

def test_powershell_detector():
    _test_detector(PowerShellDetector, "PowerShell")

def test_bash_detector():
    _test_detector(BashDetector, "Bash")

def test_npm_detector():
    _test_detector(NpmDetector, "npm")
