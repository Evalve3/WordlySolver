import copy
import string
from typing import Set

import pytest

from wordly_solver.core.game.adapters.wordly_finder import WordlySearchDTO
from src.wordly_solver.data.wordly_tree import AllWordsTree

TEST_WORDS = {
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


def _get_test_tree(test_words: Set[str]) -> AllWordsTree:
    return AllWordsTree(test_words)


@pytest.fixture(scope="module")
def english_word5_tree() -> AllWordsTree:
    return _get_test_tree(TEST_WORDS)


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
        result = english_word5_tree.wordly_search(dto)
        if result:
            results.add(result)
    assert len(results) > 1


@pytest.mark.parametrize(
    "dto, expected",
    [
        (
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
                WordlySearchDTO(
                    exclude_letters=set(string.ascii_letters.lower()),
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
        dto: WordlySearchDTO, expected: str | None, english_word5_tree: AllWordsTree
):
    for _ in range(100):
        result = english_word5_tree.wordly_search(dto)

        assert result == expected


@pytest.mark.parametrize(
    "dto, expected",
    [
        (
                WordlySearchDTO(
                    exclude_letters=set(),
                    positions_letter={0: "a"},
                    exclude_positions={
                        3: {"e"},
                    },
                    max_count={},
                    wordly_len=5,
                ),
                ["aleft", "asess", None],
        ),
        (
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
                WordlySearchDTO(
                    exclude_letters={"a"},
                    positions_letter={0: "b"},
                    exclude_positions={2: {"s"}},
                    max_count={"o": 1},
                    wordly_len=5,
                ),
                ["birls", "begus", None],
        ),
    ],
)
def test_wordly_search_multiply_results(
        dto: WordlySearchDTO, expected: list[str | None]
):
    test_words = copy.deepcopy(TEST_WORDS)
    english_word5_tree = _get_test_tree(test_words)

    actual_get = set()
    for _ in range(len(expected)):
        result = english_word5_tree.wordly_search(dto)
        actual_get.add(result)
        assert result in expected
        if result is not None:
            test_words.remove(result)
            english_word5_tree = _get_test_tree(test_words)

    assert actual_get == set(expected)
