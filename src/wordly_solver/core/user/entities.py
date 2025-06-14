from dataclasses import dataclass

from wordly_solver.core.words.constants import Language


@dataclass
class User:
    language: Language
