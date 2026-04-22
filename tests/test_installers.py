from installers.base import Installer
from installers.npm_installer import NpmInstaller


def test_npm_installer_exists():
    inst = NpmInstaller()
    assert inst.name == "npm global install"
    assert inst.priority == 1


def test_npm_installer_has_target():
    inst = NpmInstaller()
    assert "claude-code" in inst.target.lower()
