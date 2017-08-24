

class Grid:
    def __init__(self, x: int, y: int) -> None:
        self.__x = self.__integer_type_and_range_checked(x)
        self.__y = self.__integer_type_and_range_checked(y)

    @property
    def x(self) -> float:
        return self.__x

    @property
    def y(self) -> float:
        return self.__y

    @staticmethod
    def __integer_type_and_range_checked(value: int) -> int:
        if type(value) is not int:
            raise TypeError('Number of grid points must be an integer!')
        if value < 1:
            raise ValueError('Number of grid points must be positive!')
        return value


if __name__ == '__main__':
    grid = Grid(10, 20)
    print(grid.x)
    print(grid.y)