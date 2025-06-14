from collections import defaultdict
from dataclasses import dataclass
from typing import List, Set, Dict

from wordly_solver.core.game.adapters.wordly_finder import WordlyFinder
from wordly_solver.core.game.entities import WordlyWord, WordlyLetterState
from wordly_solver.core.game.usecases.exceptions import IncorrectInputError
from wordly_solver.core.user.adapters.id_provider import IdProvider
from wordly_solver.core.words.adapters.words_gateway import WordsGateway


@dataclass
class GetSuitableWordDTO:
    word_history: List[WordlyWord]
    word_len: int


def _letter_count_in_exclude_positions(
        letter: str,
        exclude_positions: Dict[int, Set[str]]
) -> int:
    return sum(1 for exclude_set in exclude_positions.values() if letter in exclude_set)


def _letter_count_in_positions_letter(
        letter: str,
        positions_letter: Dict[int, str]
) -> int:
    return sum(1 for value in positions_letter.values() if value == letter)


class GetSuitableWord:
    def __init__(
            self,
            wordly_solver: WordlyFinder,
            id_provider: IdProvider,
            words_gateway: WordsGateway,
    ):
        self.wordly_solver = wordly_solver
        self.id_provider = id_provider
        self.words_gateway = words_gateway

    async def execute(self, dto: GetSuitableWordDTO) -> str:
        # TODO: подробить на _методы для тестов
        current_user = await self.id_provider.get_current_user()

        if len(dto.word_history) == 0:
            return await self.words_gateway.get_first_word(
                language=current_user.language
            )

        if not all((len(word) == dto.word_len for word in dto.word_history)):
            raise IncorrectInputError()

        positions_letter: Dict[int, str] = {}
        exclude_positions: Dict[int, Set[str]] = defaultdict(set)

        for wordly_word in dto.word_history:
            for idx, letter in wordly_word.items():
                if letter.state == WordlyLetterState.correct:
                    positions_letter[idx] = letter.letter
                elif letter.state == WordlyLetterState.wrong_place:
                    exclude_positions[idx].add(letter.letter)

        exclude_letters: Set[str] = set()
        max_count: Dict[str, int] = {}

        for wordly_word in dto.word_history:
            for idx, letter in wordly_word.items():
                if not letter.state == WordlyLetterState.incorrect:
                    # already calculated
                    continue

                in_exclude_positions = any(
                    letter.letter in exclude_positions[pos]
                    for pos in exclude_positions.keys()
                )
                in_position_letters = letter.letter in positions_letter.values()

                if not (in_position_letters or in_exclude_positions):
                    exclude_letters.add(letter.letter)
                elif letter.letter in max_count:
                    continue  # already calculated

                count = 0
                if in_exclude_positions:
                    count += _letter_count_in_exclude_positions(letter.letter, exclude_positions)
                if in_position_letters:
                    count += _letter_count_in_positions_letter(letter.letter, positions_letter)

                max_count[letter.letter] = count

        return ""
