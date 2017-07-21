

class WidthOf:
    def __init__(self, width: float) -> None:
        self.__width = self.__type_and_range_checked(width)

    @property
    def legendre_support(self) -> float:
        return self.__width

    @staticmethod
    def __type_and_range_checked(width: float) -> float:
        if type(width) not in (int, float):
            raise TypeError('width must be a number!')
        if not 0.0 < width < 2:
            raise ValueError('Width must be between 0 and 2!')
        return float(width)

if __name__ == '__main__':
    width_of = WidthOf(1.2)
    print(width_of.legendre_support)
