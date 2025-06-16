from dataclasses import dataclass
from typing import List

from wordly_solver.core.game.ports.wordly_finder import WordlyFinder
from wordly_solver.core.game.entities import WordlyWord
from wordly_solver.core.user.ports.id_provider import IdProvider
from wordly_solver.core.words.ports.words_gateway import WordsGateway


@dataclass
class GetExcludeWordDTO:
    current_words: List[WordlyWord]
    word_len: int


class GetExcludeWord:
    """
    Get a word that excludes as many letters as possible
    """

    def __init__(
            self,
            id_provider: IdProvider,
            words_gateway: WordsGateway,
            wordly_finder: WordlyFinder
    ):
        self.id_provider = id_provider
        self.words_gateway = words_gateway
        self.wordly_finder = wordly_finder

    async def execute(self, dto: GetExcludeWordDTO):
        pass
