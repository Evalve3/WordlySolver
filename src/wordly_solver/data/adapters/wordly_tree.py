import random
from dataclasses import dataclass, field
from typing import Dict, Optional, Set

from wordly_solver.core.game.contracts.wordly_finder import WordlySearchDTO, WordlyFinder
from wordly_solver.core.words.constants import Language


@dataclass
class LetterNode:
    letter_high: int  # value number in word
    letter: str
    children: Dict[str, "LetterNode"] = field(default_factory=dict)
    parent: Optional["LetterNode"] = None

    visited: bool = False  # for dfs

    def get_full_word(self) -> str:
        word = ""
        current_node = self
        while current_node.parent:
            assert current_node.letter
            word += current_node.letter
            current_node = current_node.parent

        return word[::-1]


class AllWordsTree(WordlyFinder):
    # TODO: поддержка нескольких языков
    def __init__(self, init_words: Set[str]) -> None:
        self.root = LetterNode(
            letter_high=0,
            letter=None,  # type: ignore
        )

        for word in init_words:
            self._add_word(word)

    def _add_word(self, word: str) -> None:
        current = self.root
        for idx, letter in enumerate(word):
            if letter not in current.children:
                current.children[letter] = LetterNode(
                    letter=letter, parent=current, letter_high=idx + 1
                )
            current = current.children[letter]

    def _reset_visited(self) -> None:
        def reset_node(node: LetterNode):
            node.visited = False
            for child in node.children.values():
                reset_node(child)

        reset_node(self.root)

    def wordly_search(
            self,
            dto: WordlySearchDTO,
            language: Language,  # TODO impl, tests
            start_node: LetterNode | None = None
    ) -> str | None:
        """DFS"""

        if not start_node:
            self._reset_visited()
            start_node = self.root

        if start_node.visited:
            return None

        if start_node.letter_high == dto.wordly_len:
            word = start_node.get_full_word()

            all_positions_letters = set()
            for letters in dto.exclude_positions.values():
                all_positions_letters.update(letters)
            if all_positions_letters.issubset(set(word)) and all(
                    word.count(letter) <= dto.max_count.get(letter, dto.wordly_len)
                    for letter in set(word)
            ):
                return word

        start_node.visited = True

        if letter := dto.positions_letter.get(start_node.letter_high):
            if letter not in start_node.children:
                return None

            reached = self.wordly_search(
                start_node=start_node.children[letter], dto=dto, language=language
            )

            if reached:
                return reached
        else:
            valid_children = [
                child
                for child in start_node.children.values()
                if child.letter not in dto.exclude_letters
            ]

            if dto.exclude_positions.get(start_node.letter_high):
                valid_letters = {
                                    c.letter for c in valid_children
                                } - dto.exclude_positions[start_node.letter_high]

                valid_children = [
                    child for child in valid_children if child.letter in valid_letters
                ]

            if dto.max_count:
                current_word = start_node.get_full_word()

                letter_counts = dto.max_count.items()
                valid_children = [
                    valid_c
                    for valid_c in valid_children
                    if not any(
                        (current_word + valid_c.letter).count(letter) > count
                        for letter, count in letter_counts
                    )
                ]

            if not valid_children:
                return None

            # difference result between runs
            random.shuffle(valid_children)

            for children in valid_children:
                if not children.visited:
                    reached = self.wordly_search(start_node=children, dto=dto, language=language)

                    if reached:
                        return reached

        return None
