from abc import ABC, abstractmethod

from wordly_solver.core.user.entities import User


class IdProvider(ABC):

    @abstractmethod
    def get_current_user(self) -> User:
        pass
