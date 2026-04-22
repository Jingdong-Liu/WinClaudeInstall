from enum import Enum
from abc import ABC, abstractmethod


class Status(Enum):
    OK = "ok"
    MISSING = "missing"
    WARNING = "warning"


class Detector(ABC):
    """Base class for environment detectors.

    Subclass and implement detect(). Each detector checks
    one dependency and returns (status, human_readable_detail).
    """

    @property
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def detect(self) -> tuple[Status, str]:
        """Return (status, detail)."""
        ...
