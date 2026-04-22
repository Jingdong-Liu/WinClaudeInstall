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
