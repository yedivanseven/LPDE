from enum import Enum


class Signal(Enum):
    CONTINUE: int = 0
    STOP: int = 1


if __name__ == '__main__':
    control = Signal.CONTINUE
    print(control)

    another_control = Signal(1)
    print(another_control)