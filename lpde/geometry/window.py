from numpy import array, ndarray


class Window:
    def __init__(self, width_x: float, height_y: float) -> None:
        self.__width_x = self.__type_and_range_checked(width_x)
        self.__height_y = self.__type_and_range_checked(height_y)
        self.__dimensions = array((self.__width_x, self.__height_y))

    @property
    def dimensions(self) -> ndarray:
        return self.__dimensions

    @staticmethod
    def __type_and_range_checked(length: float) -> float:
        if type(length) not in (int, float):
            raise TypeError('Width and height must be numbers!')
        if not length > 0:
            raise ValueError('Width and height must be > 0!')
        return float(length)

if __name__ == '__main__':
    window = Window(23, 56)
    print(window.dimensions)
