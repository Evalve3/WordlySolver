from collections import defaultdict
from unittest.mock import create_autospec, AsyncMock, Mock

import pytest

from wordly_solver.core.game.contracts.wordly_finder import WordlySearchDTO, WordlyFinder
from wordly_solver.core.game.entities import WordlyLetter, WordlyLetterState, WordlyWord
from wordly_solver.core.game.usecases.exceptions import IncorrectInputError
from wordly_solver.core.game.usecases.get_suitable_word import GetSuitableWord, GetSuitableWordDTO
from wordly_solver.core.user.contracts.id_provider import IdProvider
from wordly_solver.core.user.entities import User
from wordly_solver.core.words.constants import Language
from wordly_solver.core.words.contracts.words_gateway import WordsGateway


def create_wordly_word(word: str, states: list[WordlyLetterState]) -> WordlyWord:
    return {i: WordlyLetter(value=char, state=state) for i, (char, state) in enumerate(zip(word, states))}


@pytest.fixture
def wordly_solver() -> WordlyFinder:
    return create_autospec(WordlyFinder)


@pytest.fixture
def id_provider() -> IdProvider:
    return create_autospec(IdProvider)


@pytest.fixture
def words_gateway() -> WordsGateway:
    return create_autospec(WordsGateway)


@pytest.fixture
def get_suitable_word(
        wordly_solver: WordlyFinder,
        id_provider: IdProvider,
        words_gateway: WordsGateway

):
    return GetSuitableWord(
        wordly_solver=wordly_solver,
        id_provider=id_provider,
        words_gateway=words_gateway
    )


@pytest.mark.parametrize(
    "current_words, expected_positions_letter, expected_exclude_positions",
    [
        # Test case 1: Empty input
        (
                [],
                {},
                {}
        ),
        # Test case 2: Single word with correct and wrong place
        (
                [create_wordly_word(
                    "CAT",
                    [WordlyLetterState.correct, WordlyLetterState.wrong_place, WordlyLetterState.incorrect]
                )],
                {0: 'C'},
                {1: {'A'}}
        ),
        # Test case 3: Multiple words
        (
                [
                    create_wordly_word(
                        "CAT",
                        [WordlyLetterState.correct, WordlyLetterState.wrong_place, WordlyLetterState.incorrect]
                    ),
                    create_wordly_word(
                        "DOG",
                        [WordlyLetterState.wrong_place, WordlyLetterState.correct, WordlyLetterState.incorrect]
                    )
                ],
                {0: 'C', 1: 'O'},
                {0: {'D'}, 1: {'A'}}
        )
    ]
)
def test_parse_correct_exclude_positions(get_suitable_word, current_words, expected_positions_letter,
                                         expected_exclude_positions):
    positions_letter, exclude_positions = get_suitable_word._parse_correct_exclude_positions(current_words)
    assert positions_letter == expected_positions_letter
    assert exclude_positions == expected_exclude_positions


@pytest.mark.parametrize(
    "current_words, positions_letter, exclude_positions, expected_exclude_letters, expected_max_count",
    [
        # Test case 1: No incorrect letters
        (
                [
                    create_wordly_word(
                        "CATS",
                        [
                            WordlyLetterState.correct,
                            WordlyLetterState.wrong_place,
                            WordlyLetterState.correct,
                            WordlyLetterState.wrong_place
                        ]
                    )
                ],
                {0: 'C', 2: 'T'},
                {1: {'A'}, 3: {'S'}},
                set(),
                {}
        ),
        # Test case 2: Single word with incorrect letter
        (
                [
                    create_wordly_word(
                        "CAA",
                        [WordlyLetterState.correct, WordlyLetterState.correct, WordlyLetterState.incorrect]
                    )
                ],
                {0: 'C', 1: 'A'},
                {},
                set(),
                {'A': 1}
        ),
        # Test case 3: Multiple words with multiple occurrences
        (
                [
                    create_wordly_word(
                        "CATS",
                        [
                            WordlyLetterState.correct,
                            WordlyLetterState.wrong_place,
                            WordlyLetterState.incorrect,
                            WordlyLetterState.incorrect
                        ]
                    ),
                    create_wordly_word(
                        "CANA",
                        [
                            WordlyLetterState.correct,
                            WordlyLetterState.wrong_place,
                            WordlyLetterState.correct,
                            WordlyLetterState.incorrect
                        ]
                    )
                ],
                {0: 'C', 2: 'N'},
                defaultdict(set, {1: {'A'}}),
                {'T', 'S'},
                {'A': 1}
        )
    ]
)
def test_parse_exclude_letters_max_count(
        get_suitable_word, current_words, positions_letter, exclude_positions,
        expected_exclude_letters, expected_max_count
):
    exclude_letters, max_count = get_suitable_word._parse_exclude_letters_max_count(
        current_words, exclude_positions, positions_letter
    )
    assert exclude_letters == expected_exclude_letters
    assert max_count == expected_max_count


@pytest.mark.parametrize(
    "current_words, word_len, expected_dto",
    [
        # Test case 1: Empty input
        (
                [],
                3,
                WordlySearchDTO(
                    exclude_letters=set(),
                    positions_letter={},
                    exclude_positions={},
                    max_count={},
                    wordly_len=3
                )
        ),
        # Test case 2: Single word with mixed states
        (
                [
                    create_wordly_word(
                        "CAT",
                        [WordlyLetterState.correct, WordlyLetterState.wrong_place, WordlyLetterState.incorrect]
                    )
                ],
                3,
                WordlySearchDTO(
                    exclude_letters={'T'},
                    positions_letter={0: 'C'},
                    exclude_positions={1: {'A'}},
                    max_count={},
                    wordly_len=3
                )
        ),
        # Test case 3: Multiple words with complex states
        (
                [
                    create_wordly_word(
                        "CAT",
                        [WordlyLetterState.correct, WordlyLetterState.wrong_place, WordlyLetterState.incorrect]
                    ),
                    create_wordly_word(
                        "DOG",
                        [WordlyLetterState.wrong_place, WordlyLetterState.correct, WordlyLetterState.incorrect]
                    )
                ],
                3,
                WordlySearchDTO(
                    exclude_letters={'T', 'G'},
                    positions_letter={0: 'C', 1: 'O'},
                    exclude_positions={0: {'D'}, 1: {'A'}},
                    max_count={},
                    wordly_len=3
                )
        ),
        # Test case 4: Word with repeated letters and mixed states
        (
                [
                    create_wordly_word(
                        "CANA",
                        [
                            WordlyLetterState.correct,
                            WordlyLetterState.wrong_place,
                            WordlyLetterState.correct,
                            WordlyLetterState.incorrect
                        ]
                    )
                ],
                4,
                WordlySearchDTO(
                    exclude_letters=set(),
                    positions_letter={0: 'C', 2: 'N'},
                    exclude_positions={1: {'A'}},
                    max_count={'A': 1},
                    wordly_len=4
                )
        ),
        # Test case 5: All incorrect letters
        (
                [
                    create_wordly_word(
                        "CAT",
                        [WordlyLetterState.incorrect, WordlyLetterState.incorrect, WordlyLetterState.incorrect]
                    )
                ],
                3,
                WordlySearchDTO(
                    exclude_letters={'C', 'A', 'T'},
                    positions_letter={},
                    exclude_positions={},
                    max_count={},
                    wordly_len=3
                )
        ),
        # Test case 6: All correct letters
        (
                [
                    create_wordly_word(
                        "CAT",
                        [WordlyLetterState.correct, WordlyLetterState.correct, WordlyLetterState.correct]
                    )
                ],
                3,
                WordlySearchDTO(
                    exclude_letters=set(),
                    positions_letter={0: 'C', 1: 'A', 2: 'T'},
                    exclude_positions={},
                    max_count={},
                    wordly_len=3
                )
        ),
        # Test case 7: Mixed words with repeated letters across words
        (
                [
                    create_wordly_word(
                        "CATS",
                        [
                            WordlyLetterState.correct,
                            WordlyLetterState.wrong_place,
                            WordlyLetterState.incorrect,
                            WordlyLetterState.incorrect
                        ]
                    ),
                    create_wordly_word(
                        "CANA",
                        [
                            WordlyLetterState.correct,
                            WordlyLetterState.wrong_place,
                            WordlyLetterState.correct,
                            WordlyLetterState.incorrect
                        ]
                    )
                ],
                4,
                WordlySearchDTO(
                    exclude_letters={'T', 'S'},
                    positions_letter={0: 'C', 2: 'N'},
                    exclude_positions={1: {'A'}},
                    max_count={'A': 1},
                    wordly_len=4
                )
        )
    ]
)
def test_parse_to_wordly_search_dto(get_suitable_word, current_words, word_len, expected_dto):
    result = get_suitable_word._parse_to_wordly_search_dto(current_words, word_len)
    assert result == expected_dto


TEST_ENG_USER = User(language=Language.ENG)


@pytest.mark.asyncio
async def test_execute_empty_current_words(get_suitable_word, words_gateway, id_provider):
    dto = GetSuitableWordDTO(current_words=[], word_len=3)

    id_provider.get_current_user = AsyncMock(return_value=TEST_ENG_USER)
    words_gateway.get_first_word = AsyncMock(return_value="CAT")

    result = await get_suitable_word.execute(dto)

    id_provider.get_current_user.assert_called_once()
    words_gateway.get_first_word.assert_called_once_with(language=Language.ENG)
    assert result == "CAT"


@pytest.mark.asyncio
async def test_execute_incorrect_word_length(get_suitable_word):
    current_words = [
        create_wordly_word("CAT", [WordlyLetterState.correct] * 3),
        create_wordly_word("DOGS", [WordlyLetterState.correct] * 4)
    ]
    dto = GetSuitableWordDTO(current_words=current_words, word_len=3)

    with pytest.raises(IncorrectInputError):
        await get_suitable_word.execute(dto)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "current_words, expected_result, expected_search_dto",
    [
        # Test case 1: Single word valid input
        (
                [
                    create_wordly_word(
                        "CAT",
                        [WordlyLetterState.correct, WordlyLetterState.wrong_place, WordlyLetterState.incorrect]
                    )
                ],
                "CAR",
                WordlySearchDTO(
                    exclude_letters={'T'},
                    positions_letter={0: 'C'},
                    exclude_positions={1: {'A'}},
                    max_count={},
                    wordly_len=3
                )
        ),
        # Test case 2: Multiple words valid input
        (
                [
                    create_wordly_word(
                        "CAT",
                        [WordlyLetterState.correct, WordlyLetterState.wrong_place, WordlyLetterState.incorrect]
                    ),
                    create_wordly_word(
                        "DOG",
                        [WordlyLetterState.wrong_place, WordlyLetterState.correct, WordlyLetterState.incorrect]
                    )
                ],
                "COD",
                WordlySearchDTO(
                    exclude_letters={'T', 'G'},
                    positions_letter={0: 'C', 1: 'O'},
                    exclude_positions={0: {'D'}, 1: {'A'}},
                    max_count={},
                    wordly_len=3
                )
        ),
        # Test case 3: No suitable word found
        (
                [
                    create_wordly_word(
                        "CAT",
                        [WordlyLetterState.correct, WordlyLetterState.correct, WordlyLetterState.correct]
                    )
                ],
                None,
                WordlySearchDTO(
                    exclude_letters=set(),
                    positions_letter={0: 'C', 1: 'A', 2: 'T'},
                    exclude_positions={},
                    max_count={},
                    wordly_len=3
                )
        )
    ]
)
async def test_execute(get_suitable_word, wordly_solver, id_provider, current_words, expected_result,
                       expected_search_dto):
    dto = GetSuitableWordDTO(current_words=current_words, word_len=3)
    id_provider.get_current_user = AsyncMock(return_value=TEST_ENG_USER)
    wordly_solver.wordly_search = Mock(return_value=expected_result)

    result = await get_suitable_word.execute(dto)

    id_provider.get_current_user.assert_called_once()
    wordly_solver.wordly_search.assert_called_once_with(
        dto=expected_search_dto,
        language=Language.ENG
    )
    assert result == expected_result
