from numpy import array, ndarray, float64


class PointAt:
    def __init__(self, x: float, y: float) -> None:
        self.__x = self.__type_checked(x)
        self.__y = self.__type_checked(y)
        self.__position = array((self.__x, self.__y))

    @property
    def position(self) -> ndarray:
        return self.__position

    @staticmethod
    def __type_checked(value: float) -> float:
        if type(value) not in (int, float, float64):
            raise TypeError('Coordinate must be a number!')
        return float(value)


if __name__ == '__main__':
    center = PointAt(2, -3)
    print(center.position)
