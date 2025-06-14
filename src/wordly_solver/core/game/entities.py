from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict


class WordlyLetterState(Enum):
    correct = auto()
    wrong_place = auto()
    incorrect = auto()


@dataclass
class WordlyLetter:
    letter: str
    state: WordlyLetterState


WordlyWord = Dict[int, WordlyLetter]  # Index in word: letter
