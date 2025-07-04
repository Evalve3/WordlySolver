from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Set

from wordly_solver.core.words.constants import Language


@dataclass
class WordlySearchDTO:
    exclude_letters: Set[str]
    positions_letter: Dict[int, str]  # Position in word number | str
    exclude_positions: Dict[int, Set[str]]

    max_count: Dict[str, int]

    wordly_len: int = 5  # how much letters in word


class WordlyFinder(ABC):
    @abstractmethod
    def wordly_search(self, dto: WordlySearchDTO, language: Language) -> str | None:
        pass

    @abstractmethod
    def get_exclude_word(
            self,
            forbidden_letters: set[str],
            language: Language,
            wordly_len: int
    ) -> str | None:
        """
            Get a word that excludes as many letters as possible
        """
        pass
