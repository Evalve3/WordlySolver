import random
import time
from dataclasses import dataclass, field
from typing import Dict, Optional, List, Set

from util import get_all_english_word, measure_time


@dataclass
class WordlySearchDTO:
    exclude_letters: set
    positions_letter: Dict[int, str]  # Position in word number | str
    exclude_positions: Dict[int, Set[str]]

    max_count: Dict[str, int]

    wordly_len: int = 5  # how much letters in word


@dataclass
class LetterNode:
    letter_high: int  # letter number in word
    letter: str = None
    children: Dict[str, "LetterNode"] = field(default_factory=dict)
    parent: Optional["LetterNode"] = None

    visited: bool = False  # for dfs

    def get_full_word(self) -> str:
        """return word"""
        word = ""
        current_node = self
        while current_node.parent:
            word += current_node.letter
            current_node = current_node.parent

        return word[::-1]


class AllWordsTree:
    # TODO: все еще есть попытки? - вырезать как можно больше букв, которые все еще можно
    def __init__(self, init_words: List[str]):
        self.root = LetterNode(letter_high=0)

        for word in init_words:
            self.add_word(word)

    def add_word(self, word: str) -> None:
        current = self.root
        for idx, letter in enumerate(word):
            if letter not in current.children:
                current.children[letter] = LetterNode(letter=letter, parent=current, letter_high=idx + 1)
            current = current.children[letter]

    def wordly_dfs(self, dto: WordlySearchDTO, start_node: LetterNode = None) -> str | None:

        if not start_node:
            start_node = self.root

        if start_node.visited:
            return None

        if start_node.letter_high == dto.wordly_len:
            word = start_node.get_full_word()

            all_positions_letters = set()
            for letters in dto.exclude_positions.values():
                all_positions_letters.update(letters)
            if all_positions_letters.issubset(set(word)) and \
                    all(word.count(letter) <= dto.max_count.get(letter, dto.wordly_len) for letter in set(word)):
                return word

        start_node.visited = True

        if letter := dto.positions_letter.get(start_node.letter_high + 1):
            if letter not in start_node.children:
                return None

            reached = self.wordly_dfs(start_node=start_node.children[letter], dto=dto)

            if reached:
                return reached
        else:
            valid_children = [child for child in start_node.children.values() if
                              child.letter not in dto.exclude_letters]

            if dto.exclude_positions.get(start_node.letter_high + 1):
                valid_letters = {c.letter for c in valid_children} - dto.exclude_positions[start_node.letter_high + 1]

                valid_children = [child for child in valid_children if
                                  child.letter in valid_letters]

            if dto.max_count:
                current_word = start_node.get_full_word()

                letter_counts = dto.max_count.items()
                valid_children = [
                    valid_c for valid_c in valid_children
                    if not any(
                        (current_word + valid_c.letter).count(letter) > count
                        for letter, count in letter_counts
                    )
                ]

            if not valid_children:
                return None

            # чтобы при каждом запуске был разный результат
            random.shuffle(valid_children)

            for children in valid_children:
                if not children.visited:
                    reached = self.wordly_dfs(start_node=children, dto=dto)

                    if reached:
                        return reached

        return None


if __name__ == "__main__":
    random.seed(time.time())

    AllWordsTree = AllWordsTree(get_all_english_word(5))
    find_word = AllWordsTree.wordly_dfs(
        dto=WordlySearchDTO(
            exclude_letters={"a", "b", "r", "o", "e", "l", "s"},
            positions_letter={
                3: "u",
                5: 'e',
                4: "t"
            },
            exclude_positions={
            },
            max_count={
            }
        ),
    )

    print(find_word)
