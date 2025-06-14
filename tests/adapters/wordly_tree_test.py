import copy
import string
from typing import Set, Dict

import pytest

from wordly_solver.core.game.contracts.wordly_finder import WordlySearchDTO
from wordly_solver.core.words.constants import Language
from wordly_solver.data.adapters.wordly_tree import AllWordsTree

TEST_ENG_WORDS = {
    "abaca",
    "aband",
    "adeem",
    "aleft",
    "ascon",
    "asess",
    "babes",
    "bases",
    "begum",
    "begus",
    "birls",
    "booms",
    "yetts",
    "valve",
    "verst",
    "vower",
    "weals",
    "wifes",
    "muted",
    "cutey",
    "fumes",
    "gauge",
    "lutes",
}

TEST_RU_WORDS = {
    "океан",
    "будка",
    "кошка",
    "питон"
}


def _get_test_tree(test_words: Dict[Language, Set[str]]) -> AllWordsTree:
    return AllWordsTree(test_words)


@pytest.fixture(scope="module")
def english_word5_tree() -> AllWordsTree:
    return _get_test_tree(
        {
            Language.ENG: TEST_ENG_WORDS,
            Language.RU: TEST_RU_WORDS
        }
    )


def test_wordly_search_randomness(english_word5_tree: AllWordsTree):
    dto = WordlySearchDTO(
        exclude_letters={"a"},
        positions_letter={},
        exclude_positions={},
        max_count={},
        wordly_len=5,
    )
    results = set()
    for _ in range(100):  # Run multiple times to check randomness
        result = english_word5_tree.wordly_search(dto, language=Language.ENG)
        if result:
            results.add(result)
    assert len(results) > 1


@pytest.mark.parametrize(
    "language, dto, expected",
    [
        (
                Language.ENG,
                WordlySearchDTO(
                    exclude_letters={"a", "b", "r", "o", "l", "s"},
                    positions_letter={2: "t", 4: "d"},
                    exclude_positions={},
                    max_count={},
                    wordly_len=5,
                ),
                "muted",
        ),
        (
                Language.ENG,
                WordlySearchDTO(
                    exclude_letters={"a", "b", "r", "o", "l", "s"},
                    positions_letter={2: "t", 4: "d"},
                    exclude_positions={},
                    max_count={"m": 0},
                    wordly_len=5,
                ),
                None,
        ),
        (
                Language.ENG,
                WordlySearchDTO(
                    exclude_letters=set(string.ascii_letters.lower()),
                    positions_letter={},
                    exclude_positions={},
                    max_count={},
                    wordly_len=5,
                ),
                None,
        ),
        (
                Language.RU,
                WordlySearchDTO(
                    exclude_letters={"б", "п", "т"},
                    positions_letter={2: "ш", 4: "а"},
                    exclude_positions={},
                    max_count={},
                    wordly_len=5,
                ),
                "кошка",
        ),
        (
                Language.RU,
                WordlySearchDTO(
                    exclude_letters={"ш"},
                    positions_letter={0: "о"},
                    exclude_positions={},
                    max_count={},
                    wordly_len=5,
                ),
                "океан",
        ),
        (
                Language.RU,
                WordlySearchDTO(
                    exclude_letters={"о", "к", "е", "а", "н", "б", "у", "д", "т"},
                    positions_letter={},
                    exclude_positions={},
                    max_count={},
                    wordly_len=5,
                ),
                None,
        ),
    ],
)
def test_wordly_search_one_result(
        language: Language, dto: WordlySearchDTO, expected: str | None, english_word5_tree: AllWordsTree
):
    for _ in range(100):
        result = english_word5_tree.wordly_search(dto, language=language)
        assert result == expected


@pytest.mark.parametrize(
    "language, dto, expected",
    [
        (
                Language.ENG,
                WordlySearchDTO(
                    exclude_letters=set(),
                    positions_letter={0: "a"},
                    exclude_positions={3: {"e"}},
                    max_count={},
                    wordly_len=5,
                ),
                ["aleft", "asess", None],
        ),
        (
                Language.ENG,
                WordlySearchDTO(
                    exclude_letters={"b", "f", "y"},
                    positions_letter={1: "e"},
                    exclude_positions={},
                    max_count={},
                    wordly_len=5,
                ),
                ["verst", "weals", None],
        ),
        (
                Language.ENG,
                WordlySearchDTO(
                    exclude_letters={"a", "s"},
                    positions_letter={4: "m"},
                    exclude_positions={},
                    max_count={},
                    wordly_len=5,
                ),
                ["begum", None],
        ),
        (
                Language.ENG,
                WordlySearchDTO(
                    exclude_letters=set(),
                    positions_letter={0: "a"},
                    exclude_positions={},
                    max_count={"a": 2, "e": 1, "s": 2},
                    wordly_len=5,
                ),
                ["aband", "aleft", "ascon", None],
        ),
        (
                Language.ENG,
                WordlySearchDTO(
                    exclude_letters={"a"},
                    positions_letter={0: "b"},
                    exclude_positions={2: {"s"}},
                    max_count={"o": 1},
                    wordly_len=5,
                ),
                ["birls", "begus", None],
        ),
        (
                Language.RU,
                WordlySearchDTO(
                    exclude_letters=set(),
                    positions_letter={0: "о"},
                    exclude_positions={},
                    max_count={},
                    wordly_len=5,
                ),
                ["океан", None],
        ),
        (
                Language.RU,
                WordlySearchDTO(
                    exclude_letters={"п", "б"},
                    positions_letter={2: "ш"},
                    exclude_positions={},
                    max_count={},
                    wordly_len=5,
                ),
                ["кошка", None],
        ),
    ],
)
def test_wordly_search_multiply_results(
        language: Language, dto: WordlySearchDTO, expected: list[str | None], english_word5_tree: AllWordsTree
):
    actual_get = set()
    test_words = copy.deepcopy({Language.ENG: TEST_ENG_WORDS, Language.RU: TEST_RU_WORDS})
    current_words = test_words[language]

    for _ in range(len(expected)):
        tree = _get_test_tree(test_words)
        result = tree.wordly_search(dto, language=language)
        actual_get.add(result)
        assert result in expected
        if result is not None and result in current_words:
            current_words.remove(result)
            test_words[language] = current_words

    assert actual_get == set(expected)
