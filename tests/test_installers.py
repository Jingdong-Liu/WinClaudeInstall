from unittest.mock import patch

from installers.base import Installer
from installers.npm_installer import NpmInstaller


def test_npm_installer_exists():
    inst = NpmInstaller()
    assert inst.name == "npm global install"
    assert inst.priority == 1


def test_npm_installer_has_target():
    inst = NpmInstaller()
    assert "claude-code" in inst.target.lower()


def test_installer_has_target_abstract():
    # Verify NpmInstaller has target defined
    inst = NpmInstaller()
    assert inst.target == "@anthropic-ai/claude-code"


@patch("installers.npm_installer.run_stream")
def test_npm_installer_runs_correct_command(mock_run_stream):
    mock_run_stream.return_value = 0
    inst = NpmInstaller()
    result = inst.install(lambda msg: None)
    assert result is True
    mock_run_stream.assert_called_once()
    call_args = mock_run_stream.call_args
    assert "@anthropic-ai/claude-code" in call_args[0][0]
    assert "npm install -g" in call_args[0][0]
