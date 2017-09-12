from numpy import float64


class WidthOf:
    def __init__(self, width: float) -> None:
        self.__width = self.__type_and_range_checked(width)

    @property
    def legendre_support(self) -> float:
        return self.__width

    @staticmethod
    def __type_and_range_checked(value: float) -> float:
        if type(value) not in (int, float, float64):
            raise TypeError('Width must be a number!')
        if not 0.0 < value < 2.0:
            raise ValueError('Width must be between 0 and 2!')
        return float(value)


if __name__ == '__main__':
    width_of = WidthOf(1.2)
    print(width_of.legendre_support)
