from unittest.mock import patch

from installers.base import Installer
from installers.npm_installer import NpmInstaller
from installers.bundled_installer import BundledInstaller


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


# ── BundledInstaller Tests ─────────────────────────────────────


def test_bundled_installer_properties():
    inst = BundledInstaller("Node.js")
    assert "bundled" in inst.name
    assert inst.priority == 2
    assert inst.target == "Node.js"


@patch("installers.bundled_installer.get_bundled_dir")
@patch("installers.bundled_installer.os.path.exists")
@patch("installers.bundled_installer.run_stream")
def test_bundled_installer_success(mock_run, mock_exists, mock_dir):
    mock_dir.return_value = "/fake/bundled"
    mock_exists.return_value = True
    mock_run.return_value = 0
    inst = BundledInstaller("Node.js")
    assert inst.install(lambda m: None) is True
    mock_run.assert_called_once()


@patch("installers.bundled_installer.get_bundled_dir")
@patch("installers.bundled_installer.os.path.exists")
def test_bundled_installer_file_not_found(mock_exists, mock_dir):
    mock_dir.return_value = "/fake/bundled"
    mock_exists.return_value = False
    inst = BundledInstaller("Node.js")
    assert inst.install(lambda m: None) is False


@patch("installers.bundled_installer.get_bundled_dir")
@patch("installers.bundled_installer.os.path.exists")
@patch("installers.bundled_installer.run_stream")
def test_bundled_installer_failure(mock_run, mock_exists, mock_dir):
    mock_dir.return_value = "/fake/bundled"
    mock_exists.return_value = True
    mock_run.return_value = 1
    inst = BundledInstaller("Node.js")
    assert inst.install(lambda m: None) is False


def test_bundled_installer_unknown_dependency():
    inst = BundledInstaller("UnknownDep")
    assert inst.install(lambda m: None) is False
