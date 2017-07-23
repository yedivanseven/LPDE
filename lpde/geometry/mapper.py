from numpy import ndarray
from .boundingbox import BoundingBox
from .support import WidthOf
from .point import PointAt


class Mapper:
    def __init__(self, bounds: BoundingBox, support: WidthOf) -> None:
        self.__bounds = self.__box_type_checked(bounds)
        self.__width_of = self.__width_type_checked(support)

    def in_from(self, point: PointAt) -> ndarray:
        point = self.__point_type_checked(point)
        relative_position: ndarray = self.__relative_position_of(point)
        return self.__width_of.legendre_support * \
               relative_position / self.__bounds.window

    def out_from(self, point: ndarray) -> ndarray:
        return point*(self.__bounds.window/self.__width_of.legendre_support)+ \
               self.__bounds.center

    def __relative_position_of(self, point: PointAt) -> ndarray:
        relative_position = point.location - self.__bounds.center
        if any(2*relative_position.__abs__() > self.__bounds.window):
            raise ValueError('Point outside bounding box!')
        return relative_position

    @staticmethod
    def __box_type_checked(value: BoundingBox) -> BoundingBox:
        if not type(value) is BoundingBox:
            raise TypeError('Bounds must be of type <BoundingBox>!')
        return value

    @staticmethod
    def __width_type_checked(value: WidthOf) -> WidthOf:
        if not type(value) is WidthOf:
            raise TypeError('Support must be of type <WidthOf>!')
        return value

    @staticmethod
    def __point_type_checked(value: PointAt) -> PointAt:
        if not type(value) is PointAt:
            raise TypeError('Point must be of type <PointAt>!')
        return value

if __name__ == '__main__':
    from .window import Window

    center = PointAt(4, 4)
    window = Window(2, 2)
    box = BoundingBox(center, window)
    legendre_width = WidthOf(1)
    mapped = Mapper(box, legendre_width)

    point_a = PointAt(5, 3)
    mapped_point_a = mapped.in_from(point_a)
    print(mapped_point_a)

    remapped_point_a = mapped.out_from(mapped_point_a)
    print(remapped_point_a)





