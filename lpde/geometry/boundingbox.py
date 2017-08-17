from numpy import ndarray
from .point import PointAt
from .window import Window


class BoundingBox:
    def __init__(self, center: PointAt, window: Window) -> None:
        self.__center = self.__point_type_checked(center)
        self.__window = self.__window_type_checked(window)
        lower = self.__center.position - self.__window.dimensions/2.0
        upper = self.__center.position + self.__window.dimensions/2.0
        self.__x_range, self.__y_range = tuple(zip(lower, upper))

    @property
    def center(self) -> ndarray:
        return self.__center.position

    @property
    def window(self) -> ndarray:
        return self.__window.dimensions

    @property
    def x_range(self) -> (float, float):
        return self.__x_range

    @property
    def y_range(self) -> (float, float):
        return self.__y_range

    def contain(self, point: PointAt) -> bool:
        point = self.__point_type_checked(point)
        x_inside = self.__x_range[0] <= point.position[0] <= self.__x_range[1]
        y_inside = self.__y_range[0] <= point.position[1] <= self.__y_range[1]
        return True if x_inside and y_inside else False

    contains = contain

    @staticmethod
    def __point_type_checked(value: PointAt) -> PointAt:
        if not type(value) is PointAt:
            raise TypeError('Center must be of type <PointAt>!')
        return value

    @staticmethod
    def __window_type_checked(value: Window) -> Window:
        if not type(value) is Window:
            raise TypeError('Window must be of type <Window>!')
        return value


if __name__ == '__main__':
    center = PointAt(-43, 57)
    window = Window(9, 8)
    bounding_box = BoundingBox(center, window)
    print(bounding_box.center)
    print(bounding_box.window)
    print(bounding_box.x_range)
    print(bounding_box.y_range)
