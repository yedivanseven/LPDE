from typing import Union
from numpy import ndarray, dtype
from .boundingbox import BoundingBox
from .support import WidthOf
from .point import PointAt


class Mapper:
    def __init__(self, bounds: BoundingBox, support: WidthOf) -> None:
        self.__bounds = self.__boundingbox_type_checked(bounds)
        self.__width_of = self.__width_type_checked(support)
        self.__legendre_interval = (-self.__width_of.legendre_support/2.0,
                                    +self.__width_of.legendre_support/2.0)
        self.__in_scale = self.__width_of.legendre_support/self.__bounds.window
        self.__out_scale = 4.0 / self.__bounds.window.prod()

    @property
    def legendre_interval(self) -> (float, float):
        return self.__legendre_interval

    @property
    def bounds(self) -> BoundingBox:
        return self.__bounds

    def in_from(self, point: PointAt) -> ndarray:
        point = self.__point_type_and_range_checked(point)
        relative_position = point.position - self.__bounds.center
        return relative_position * self.__in_scale

    def out(self, density: Union[dtype, ndarray]) -> Union[dtype, ndarray]:
        return density * self.__out_scale

    @staticmethod
    def __boundingbox_type_checked(value: BoundingBox) -> BoundingBox:
        if type(value) is not BoundingBox:
            raise TypeError('Bounds must be of type <BoundingBox>!')
        return value

    @staticmethod
    def __width_type_checked(value: WidthOf) -> WidthOf:
        if type(value) is not WidthOf:
            raise TypeError('Support must be of type <WidthOf>!')
        return value

    def __point_type_and_range_checked(self, value: PointAt) -> PointAt:
        if type(value) is not PointAt:
            raise TypeError('Point must be of type <PointAt>!')
        if not self.__bounds.contain(value):
            raise ValueError('Point lies outside bounding box!')
        return value


if __name__ == '__main__':
    from .window import Window
    from numpy import float64

    center = PointAt(4, 4)
    window = Window(2, 2)
    box = BoundingBox(center, window)
    legendre_width = WidthOf(1)
    mapped = Mapper(box, legendre_width)

    point = PointAt(5, 3)
    mapped_point = mapped.in_from(point)
    print(mapped_point)

    remapped_density = mapped.out(float64(0.25))
    print(remapped_density)

    print(mapped.legendre_interval)





