from abc import ABC, abstractmethod


class Installer(ABC):
    """Base class for installers.

    Subclass and implement install(). Each installer tries one
    method to install a dependency. Returns True on success.
    """

    @property
    def name(self) -> str:
        raise NotImplementedError

    @property
    def priority(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def install(self, log_callback) -> bool:
        """Execute installation, stream log via log_callback.

        Returns True if installation succeeded.
        """
        ...
