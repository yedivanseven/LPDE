from enum import Enum


class Action(Enum):
    ADD: int = +1
    MOVE: int = 0
    DELETE: int = -1


if __name__ == '__main__':
    action = Action.ADD
    print(action)

    another_action = Action(-1)
    print(another_action)

