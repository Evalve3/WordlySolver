from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict


class WordlyLetterState(Enum):
    correct = auto()
    wrong_place = auto()
    incorrect = auto()


@dataclass
class WordlyLetter:
    value: str
    state: WordlyLetterState


type WordlyWord = Dict[int, WordlyLetter]  # Index in word: value
