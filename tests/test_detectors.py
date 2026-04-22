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
