import random
from dataclasses import dataclass, field
from typing import Dict, Optional, Set, Tuple

from wordly_solver.core.game.ports.wordly_finder import WordlySearchDTO, WordlyFinder
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
    """!!THREAD UNSAFE!!"""

    def __init__(
            self,
            init_words: Dict[
                Tuple[Language, int],  # Language, wordly_len
                Set[str]
            ]
    ) -> None:

        for to_init in init_words:
            setattr(
                self,
                f"{to_init[0].value}_root_len{to_init[1]}",
                LetterNode(
                    letter_high=0,
                    letter=None,  # type: ignore
                )
            )

        for lang, words in init_words.items():
            for word in words:
                self._add_word(word, lang[0])

    def _add_word(self, word: str, lang: Language) -> None:
        current = self._get_root_by_lang(lang, len(word))
        for idx, letter in enumerate(word):
            if letter not in current.children:
                current.children[letter] = LetterNode(
                    letter=letter, parent=current, letter_high=idx + 1
                )
            current = current.children[letter]

    def _reset_visited(self, lang: Language, wordly_len: int) -> None:
        def reset_node(node: LetterNode):
            node.visited = False
            for child in node.children.values():
                reset_node(child)

        reset_node(self._get_root_by_lang(lang=lang, wordly_len=wordly_len))

    def _get_root_by_lang(self, lang: Language, wordly_len: int):
        return getattr(self, f"{lang.value}_root_len{wordly_len}")

    def get_exclude_word(
            self,
            forbidden_letters: set[str],
            language: Language,
            wordly_len: int
    ) -> str | None:
        # Начинает обходить ветки, если в ветке встречается буква из запрещенных - откладывает ее дальнейшее обхождение на потом, возвращается на 1 уровень вверх и идет дальше по веткам (с того же места, где остановился, перебирая только  оставшихся детей). Если обойдя все ветки найти слово с 0 вхождений не получилось, начинает обходить то, что запомнил (ветки, где 1 раз встретилась буква из запрещенных). Там тот же принцип - встретил букву второй раз, отложил на потом. Как только он находит слово с текущим разрешенным количественном вхождений - возвращает
        self._reset_visited(lang=language, wordly_len=wordly_len)
        start_node = self._get_root_by_lang(lang=language, wordly_len=wordly_len)
        forbidden_count = 0
        pass

    #  def find_word_with_min_forbidden(
    #         self,
    #         lang: Language,
    #         word_length: int,
    #         forbidden_letters: Set[str]
    #     ) -> Optional[str]:
    #         """
    #         Находит слово с минимальным количеством запрещенных букв.
    #         Использует очередь с приоритетами для обработки веток по возрастанию
    #         количества запрещенных букв.
    #         """
    #         root = self._get_root_by_lang(lang, word_length)
    #         # Очередь с приоритетами: (кол-во запрещенных букв, текущий узел, список оставшихся детей)
    #         pq = PriorityQueue()
    #         pq.put((0, root, list(root.children.keys())))
    #
    #         while not pq.empty():
    #             forbidden_count, current_node, remaining_children = pq.get()
    #
    #             # Проверяем оставшихся детей текущего узла
    #             for child_letter in remaining_children[:]:
    #                 remaining_children.remove(child_letter)
    #                 child_node = current_node.children[child_letter]
    #
    #                 # Обновляем счетчик запрещенных букв
    #                 new_forbidden_count = forbidden_count + (1 if child_letter in forbidden_letters else 0)
    #
    #                 # Если это конец слова и допустимое количество запрещенных букв
    #                 if child_node.is_end:
    #                     return child_node.get_full_word()
    #
    #                 # Если есть дети, добавляем их в очередь
    #                 if child_node.children:
    #                     # Создаем новую очередь с оставшимися детьми
    #                     # (копируем, чтобы не модифицировать оригинал)
    #                     new_remaining = list(child_node.children.keys())
    #                     pq.put((new_forbidden_count, child_node, new_remaining))
    #
    #             # Если остались необработанные дети, возвращаем узел в очередь
    #             if remaining_children:
    #                 pq.put((forbidden_count, current_node, remaining_children))
    #
    #         return None  # Если не найдено подходящее слово

    def wordly_search(
            self,
            dto: WordlySearchDTO,
            language: Language,
    ) -> str | None:
        self._reset_visited(lang=language, wordly_len=dto.wordly_len)
        start_node = self._get_root_by_lang(lang=language, wordly_len=dto.wordly_len)

        def dfs(node: LetterNode) -> str | None:
            if node.visited:
                return None

            if not node.children and node.letter_high > 0:
                word = node.get_full_word()

                all_positions_letters = set()
                for letters in dto.exclude_positions.values():
                    all_positions_letters.update(letters)

                if all_positions_letters.issubset(set(word)) and all(
                        word.count(letter) <= dto.max_count.get(letter, dto.wordly_len)
                        for letter in set(word)
                ):
                    return word

            node.visited = True

            if letter := dto.positions_letter.get(node.letter_high):
                if letter not in node.children:
                    return None

                reached = dfs(node.children[letter])

                if reached:
                    return reached
            else:
                valid_children = [
                    child
                    for child in node.children.values()
                    if child.letter not in dto.exclude_letters
                ]

                if dto.exclude_positions.get(node.letter_high):
                    valid_letters = {
                                        c.letter for c in valid_children
                                    } - dto.exclude_positions[node.letter_high]

                    valid_children = [
                        child for child in valid_children if child.letter in valid_letters
                    ]

                if dto.max_count:
                    current_word = node.get_full_word()

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
                        reached = dfs(children)

                        if reached:
                            return reached

            return None

        return dfs(start_node)
