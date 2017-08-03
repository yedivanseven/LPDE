from enum import Enum


class Control(Enum):
    CONTINUE: int = 0
    STOP: int = 1


if __name__ == '__main__':
    control = Control.CONTINUE
    print(control)

    another_control = Control(1)
    print(another_control)