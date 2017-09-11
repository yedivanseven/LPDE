

class Grid:
    def __init__(self, x: int, y: int) -> None:
        self.__x = self.__integer_type_and_range_checked(x)
        self.__y = self.__integer_type_and_range_checked(y)

    @property
    def x(self) -> int:
        return self.__x

    @property
    def y(self) -> int:
        return self.__y

    @property
    def shape(self) -> (int, int):
        return self.__y, self.__x

    @property
    def size(self) -> int:
        return self.__x * self.__y

    @staticmethod
    def __integer_type_and_range_checked(value: int) -> int:
        if type(value) is not int:
            raise TypeError('Number of grid points must be an integer!')
        if not value > 0:
            raise ValueError('Number of grid points must be positive!')
        return value


if __name__ == '__main__':
    grid = Grid(10, 20)
    print(grid.x)
    print(grid.y)
