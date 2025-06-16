from abc import ABC, abstractmethod

from wordly_solver.core.words.constants import Language


class WordsGateway(ABC):

    @abstractmethod
    async def get_first_word(self, language: Language) -> str:
        pass
