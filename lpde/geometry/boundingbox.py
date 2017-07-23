from numpy import ndarray
from .point import PointAt
from .window import Window


class BoundingBox:
    def __init__(self, center: PointAt, window: Window) -> None:
        self.__center = self.__center_type_checked(center)
        self.__window = self.__window_type_checked(window)

    @property
    def center(self) -> ndarray:
        return self.__center.location

    @property
    def window(self) -> ndarray:
        return self.__window.dimensions

    @staticmethod
    def __center_type_checked(value: PointAt) -> PointAt:
        if not type(value) is PointAt:
            raise TypeError('Center must be of type <CenterAt>!')
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
