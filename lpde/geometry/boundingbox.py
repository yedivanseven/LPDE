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
    def aspect(self) -> float:
        return self.__window.dimensions[1]/self.__window.dimensions[0]

    @property
    def x_range(self) -> (float, float):
        return self.__x_range

    @property
    def y_range(self) -> (float, float):
        return self.__y_range

    @property
    def extent(self) -> (float, float, float, float):
        return self.__x_range + self.__y_range

    @property
    def are_geo(self) -> bool:
        valid = True and -180.0 < self.__x_range[0] < self.__x_range[1] < 180.0
        valid = valid and -90.0 < self.__y_range[0] < self.__y_range[1] < 90.0
        return valid

    def contain(self, point: PointAt) -> bool:
        point = self.__point_type_checked(point)
        x_inside = self.__x_range[0] <= point.position[0] <= self.__x_range[1]
        y_inside = self.__y_range[0] <= point.position[1] <= self.__y_range[1]
        return True if x_inside and y_inside else False

    contains = contain
    is_geo = are_geo

    @staticmethod
    def __point_type_checked(value: PointAt) -> PointAt:
        if type(value) is not PointAt:
            raise TypeError('Center must be of type <PointAt>!')
        return value

    @staticmethod
    def __window_type_checked(value: Window) -> Window:
        if type(value) is not Window:
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
    print(bounding_box.is_geographically_valid)
