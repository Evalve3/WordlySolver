from collections import defaultdict
from dataclasses import dataclass
from typing import List, Set, Dict, Tuple

from wordly_solver.core.game.contracts.wordly_finder import WordlyFinder, WordlySearchDTO
from wordly_solver.core.game.entities import WordlyWord, WordlyLetterState
from wordly_solver.core.game.usecases.exceptions import IncorrectInputError
from wordly_solver.core.user.contracts.id_provider import IdProvider
from wordly_solver.core.words.contracts.words_gateway import WordsGateway


@dataclass
class GetSuitableWordDTO:
    current_words: List[WordlyWord]
    word_len: int


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

    def _calculate_count_in_exclude_positions(
            self,
            letter: str,
            exclude_positions: Dict[int, Set[str]]
    ) -> int:
        return sum(1 for exclude_set in exclude_positions.values() if letter in exclude_set)

    def _calculate_count_in_positions_letter(
            self,
            letter: str,
            positions_letter: Dict[int, str]
    ) -> int:
        return sum(1 for value in positions_letter.values() if value == letter)

    def _parse_correct_exclude_positions(
            self,
            current_words: List[WordlyWord],
    ) -> Tuple[
        Dict[int, str],  # correct
        Dict[int, Set[str]]  # exclude
    ]:
        positions_letter: Dict[int, str] = {}
        exclude_positions: Dict[int, Set[str]] = defaultdict(set)
        for wordly_word in current_words:
            for idx, letter in wordly_word.items():
                if letter.state == WordlyLetterState.correct:
                    positions_letter[idx] = letter.value
                elif letter.state == WordlyLetterState.wrong_place:
                    exclude_positions[idx].add(letter.value)

        return positions_letter, exclude_positions

    def _parse_exclude_letters_max_count(
            self,
            current_words: List[WordlyWord],
            exclude_positions: Dict[int, Set[str]],
            positions_letter: Dict[int, str]
    ) -> Tuple[
        Set[str],  # exclude
        Dict[str, int]  # max_count
    ]:
        exclude_letters: Set[str] = set()
        max_count: Dict[str, int] = {}

        for wordly_word in current_words:
            for idx, letter in wordly_word.items():
                if not letter.state == WordlyLetterState.incorrect:
                    # already calculated
                    continue

                in_exclude_positions = any(
                    letter.value in exclude_positions[pos]
                    for pos in exclude_positions.keys()
                )
                in_position_letters = letter.value in positions_letter.values()

                if not (in_position_letters or in_exclude_positions):
                    exclude_letters.add(letter.value)
                elif letter.value in max_count:
                    continue  # already calculated

                count = 0
                if in_exclude_positions:
                    # noinspection PyTypeChecker
                    count += self._calculate_count_in_exclude_positions(letter.value, exclude_positions)
                if in_position_letters:
                    # noinspection PyTypeChecker
                    count += self._calculate_count_in_positions_letter(letter.value, positions_letter)

                if count != 0:  # already in exclude
                    max_count[letter.value] = count

        return exclude_letters, max_count

    def _parse_to_wordly_search_dto(
            self,
            current_words: List[WordlyWord],
            word_len: int
    ) -> WordlySearchDTO:

        positions_letter, exclude_positions = self._parse_correct_exclude_positions(
            current_words
        )

        exclude_letters, max_count = self._parse_exclude_letters_max_count(
            current_words, exclude_positions, positions_letter
        )

        return WordlySearchDTO(
            exclude_letters=exclude_letters,
            positions_letter=positions_letter,
            exclude_positions=exclude_positions,
            max_count=max_count,
            wordly_len=word_len
        )

    async def execute(self, dto: GetSuitableWordDTO) -> str | None:
        current_user = await self.id_provider.get_current_user()

        if len(dto.current_words) == 0:
            return await self.words_gateway.get_first_word(
                language=current_user.language
            )

        if not all((len(word) == dto.word_len for word in dto.current_words)):
            raise IncorrectInputError()

        result = self.wordly_solver.wordly_search(
            dto=self._parse_to_wordly_search_dto(
                current_words=dto.current_words,
                word_len=dto.word_len
            ),
            language=current_user.language
        )

        return result
