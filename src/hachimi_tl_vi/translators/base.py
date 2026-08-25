from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from ..model import SourceEntry


class Translator(ABC):
    @abstractmethod
    def translate_batch(self, entries: Sequence[SourceEntry]) -> dict[str, str]:
        """Return mapping uid -> translated Vietnamese text."""
        raise NotImplementedError
