import os
from utils.logger import setup_logger
from utils.shell import run_quiet, run_stream

def test_logger_creates_file():
    log_file = "_test_logger.log"
    logger = setup_logger(log_file)
    logger.info("test_message")
    assert os.path.exists(log_file)
    with open(log_file) as f:
        content = f.read()
    assert "test_message" in content
    for handler in logger.handlers:
        handler.close()
    logger.handlers.clear()
    os.remove(log_file)

def test_run_quiet_success():
    code, output = run_quiet("echo hello")
    assert code == 0
    assert "hello" in output

def test_run_quiet_failure():
    code, output = run_quiet("nonexistent_command_xyz")
    assert code != 0

def test_run_stream_success():
    lines = []
    code = run_stream("echo hello", lambda line: lines.append(line))
    assert code == 0
    assert any("hello" in line for line in lines)

def test_run_stream_timeout():
    lines = []
    code = run_stream("sleep 30", lambda line: lines.append(line), timeout=1)
    assert code == -1
    assert any("timed out" in line.lower() for line in lines)
