from enum import Enum


class Action(Enum):
    ADD: int = +1
    MOVE: int = 0
    DELETE: int = -1
